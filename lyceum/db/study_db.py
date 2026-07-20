"""SQLite study database — paths, schema, and low-level query helpers."""
from __future__ import annotations

import contextlib
import os
import sqlite3
import sys
import tempfile

from lyceum.db import db_location

# STUDY_DIR holds user sidecar content (excerpts, session.json, HANDOFF, Workflow)
# and is intentionally inside OneDrive — those are plain files the companion
# platform also reads, and they sync safely.
STUDY_DIR = os.path.expanduser(r"~\OneDrive\Documents\BookReader")
# The LIVE database, however, is opened from a LOCAL (non-synced) directory to
# avoid OneDrive's background daemon racing SQLite's file locks (see db_location).
# Older installs kept it at STUDY_DIR/study.db; that file is migrated once.
_LEGACY_DB = os.path.join(STUDY_DIR, "study.db")
STUDY_DB = db_location.live_db_path()


@contextlib.contextmanager
def temp_study_db():
    """Blessed DB isolation for headless tests and smoke scripts.

    Points ``STUDY_DB`` at a fresh temp file for the duration, asserts it is
    NOT the live database, and restores + deletes it on exit. Use this
    instead of hand-rolling the redirect — forgetting to patch ``STUDY_DB``
    (while only setting a legacy ``DB_PATH``) is exactly what leaked test
    rows into the real study.db twice; see Former-Bugs-and-Regressions.
    """
    global STUDY_DB
    fd, tmp = tempfile.mkstemp(suffix=".study.db")
    os.close(fd)
    prev = STUDY_DB
    STUDY_DB = tmp
    db_location.assert_not_live_db(STUDY_DB)   # loud failure if it's live
    try:
        yield tmp
    finally:
        STUDY_DB = prev
        try:
            os.remove(tmp)
        except OSError:
            pass

STUDY_SCHEMA = """
CREATE TABLE IF NOT EXISTS highlights (
    id INTEGER PRIMARY KEY,
    book TEXT NOT NULL,
    start_offset INTEGER NOT NULL,
    end_offset INTEGER NOT NULL,
    text TEXT,
    color TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_highlights_book ON highlights(book);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS topic_entries (
    id INTEGER PRIMARY KEY,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    source_book TEXT,
    source_offset INTEGER,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entries_topic ON topic_entries(topic_id);

CREATE TABLE IF NOT EXISTS bookmarks (
    id INTEGER PRIMARY KEY,
    book TEXT NOT NULL,
    position INTEGER NOT NULL,
    label TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bookmarks_book ON bookmarks(book);

CREATE TABLE IF NOT EXISTS glossary (
    id INTEGER PRIMARY KEY,
    term TEXT NOT NULL COLLATE NOCASE UNIQUE,
    definition TEXT NOT NULL,
    source TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Commentary store (2026-07-12): a structured, searchable set of
-- commentary entries (title + body), modeled on the glossary table so
-- the Commentary tab works like the Glossary tab. Title is NOT unique
-- (unlike glossary term) — you may keep several notes with similar
-- titles. Additive; the file-based commentary viewer still works.
CREATE TABLE IF NOT EXISTS commentaries (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT NOT NULL DEFAULT '',
    source TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_commentaries_title
    ON commentaries(title COLLATE NOCASE);

CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY,
    entry_date TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_journal_date ON journal(entry_date);

CREATE TABLE IF NOT EXISTS eisenhower (
    quadrant TEXT PRIMARY KEY,
    body TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS study_notes (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    body TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL
);

-- Study Notes archive: one row per saved note entry (master-detail). The old
-- single-blob study_notes row is migrated into the first entry on first run.
CREATE TABLE IF NOT EXISTS study_note_entries (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    body TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_study_note_entries ON study_note_entries(updated_at);

-- Eisenhower Matrix task-completion ticker.
-- matrix_pomodoros: one row per focus block started via the Matrix timer.
-- matrix_task_log: one row per completed task line (checkbox [ ] -> [x]),
-- with optional link to the active pomodoro for per-block + daily + best
-- aggregate statistics.
CREATE TABLE IF NOT EXISTS matrix_pomodoros (
    id INTEGER PRIMARY KEY,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration_minutes INTEGER NOT NULL DEFAULT 25,
    completed_count INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_matrix_pom_when ON matrix_pomodoros(started_at);

CREATE TABLE IF NOT EXISTS matrix_task_log (
    id INTEGER PRIMARY KEY,
    task_text TEXT NOT NULL DEFAULT '',
    quadrant TEXT NOT NULL DEFAULT 'do',     -- do | delegate | eliminate | schedule
    completed_at TEXT NOT NULL,
    pomodoro_id INTEGER                       -- nullable: null = no active block
);
CREATE INDEX IF NOT EXISTS idx_matrix_log_when ON matrix_task_log(completed_at);
CREATE INDEX IF NOT EXISTS idx_matrix_log_pom ON matrix_task_log(pomodoro_id);

CREATE TABLE IF NOT EXISTS day_blocks (
    id INTEGER PRIMARY KEY,
    block_date TEXT NOT NULL,
    slot_order INTEGER NOT NULL,
    duration_min INTEGER NOT NULL,
    title TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    done INTEGER NOT NULL DEFAULT 0,
    is_current INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_blocks_date ON day_blocks(block_date);

CREATE TABLE IF NOT EXISTS workflow_folders (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    date_label TEXT NOT NULL DEFAULT '',
    color TEXT NOT NULL DEFAULT 'green',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(name COLLATE NOCASE)
);

CREATE TABLE IF NOT EXISTS audits (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    subject TEXT NOT NULL DEFAULT '',
    overall_grade TEXT NOT NULL DEFAULT '',
    mentors_note TEXT NOT NULL DEFAULT '',
    findings_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompts (
    id INTEGER PRIMARY KEY,
    prompt TEXT NOT NULL DEFAULT '',
    purpose TEXT NOT NULL DEFAULT '',
    refs TEXT NOT NULL DEFAULT '',
    iterations TEXT NOT NULL DEFAULT '',
    ai_tools TEXT NOT NULL DEFAULT '',
    input_type TEXT NOT NULL DEFAULT '',
    output_type TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Prompt Library: a standalone archive of prompt + response pairs,
-- deliberately separate from the Books library (which is .md files on
-- disk). Surfaced by the green "Prompt Library" toolbar button.
CREATE TABLE IF NOT EXISTS prompt_library (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    prompt TEXT NOT NULL DEFAULT '',
    response TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    archived_at TEXT                      -- NULL = active; set = archived, row kept
);

-- Daily Planner (Sunsama-style): one row per task, assigned to a day,
-- with a time estimate and done flag. Surfaced by the 🗓 Planner study tab.
CREATE TABLE IF NOT EXISTS planner_tasks (
    id INTEGER PRIMARY KEY,
    day TEXT NOT NULL,                 -- YYYY-MM-DD
    title TEXT NOT NULL DEFAULT '',
    minutes INTEGER NOT NULL DEFAULT 25,
    done INTEGER NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_planner_day ON planner_tasks(day);

-- Zig Ziglar Performance Planner, folded into the 🗓 Planner calendar.
-- wheel_of_life: one row per dated self-assessment snapshot, each of the
-- 7 "spokes" rated 1 (poor) - 10 (excellent). Keeping snapshots lets you
-- watch the wheel get rounder over time.
CREATE TABLE IF NOT EXISTS wheel_of_life (
    id INTEGER PRIMARY KEY,
    snapshot_date TEXT NOT NULL,       -- YYYY-MM-DD
    mental INTEGER NOT NULL DEFAULT 5,
    spiritual INTEGER NOT NULL DEFAULT 5,
    physical INTEGER NOT NULL DEFAULT 5,
    family INTEGER NOT NULL DEFAULT 5,
    financial INTEGER NOT NULL DEFAULT 5,
    career INTEGER NOT NULL DEFAULT 5,
    social INTEGER NOT NULL DEFAULT 5,
    created_at TEXT NOT NULL
);

-- goals: Ziglar's goal-setting worksheet. Each goal is tied to one life
-- area (a Wheel spoke) and carries the "why", obstacles, what you need,
-- a plan of action, target date, and a 0-100 progress reading.
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',
    life_area TEXT NOT NULL DEFAULT 'mental',
    why TEXT NOT NULL DEFAULT '',          -- benefits / what's in it for me
    obstacles TEXT NOT NULL DEFAULT '',
    skills_needed TEXT NOT NULL DEFAULT '',
    people_needed TEXT NOT NULL DEFAULT '',
    action_plan TEXT NOT NULL DEFAULT '',
    target_date TEXT NOT NULL DEFAULT '',  -- YYYY-MM-DD or ''
    progress INTEGER NOT NULL DEFAULT 0,   -- 0-100
    status TEXT NOT NULL DEFAULT 'active', -- active | done | parked
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_goals_area ON goals(life_area);

-- Idea Warehouse (Ziglar's "master list" / idea warehouse): capture every
-- task the moment it comes to mind so nothing is trusted to memory. Each
-- item carries an ABCDE priority (A=must-do … E=eliminate), a "Big Three"
-- flag (the Rule of Three — the 3 tasks worth 90% of the value), and, once
-- scheduled onto the calendar, the day it was sent to.
CREATE TABLE IF NOT EXISTS master_tasks (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT '',      -- '' or A | B | C | D | E
    big_three INTEGER NOT NULL DEFAULT 0,   -- 1 = a "Big Three" for today
    scheduled_day TEXT NOT NULL DEFAULT '', -- YYYY-MM-DD once sent to calendar
    status TEXT NOT NULL DEFAULT 'open',    -- open | done | scheduled
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_master_status ON master_tasks(status);

-- Quadrant-II weekly roles (Covey): organize the week by the roles you play
-- (Student, Parent, CNA, …) and set 1-2 important-but-not-urgent goals for
-- each, so planning rises above day-to-day urgency. One row per role per week.
CREATE TABLE IF NOT EXISTS weekly_roles (
    id INTEGER PRIMARY KEY,
    week_monday TEXT NOT NULL,        -- YYYY-MM-DD, the Monday of the week
    role TEXT NOT NULL DEFAULT '',
    goal1 TEXT NOT NULL DEFAULT '',
    goal2 TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_roles_week ON weekly_roles(week_monday);

-- Compelling Scoreboard (4 Disciplines of Execution): track 2-3 daily LEAD
-- measures (the activities you control — "studied 20 min" — not lag results
-- like "lost 5 lbs"). `lead_measures` holds the definitions; `lead_measure_marks`
-- records which measure was checked off on which day, so streaks can be counted.
CREATE TABLE IF NOT EXISTS lead_measures (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS lead_measure_marks (
    measure_id INTEGER NOT NULL,
    day TEXT NOT NULL,                 -- YYYY-MM-DD
    done INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    PRIMARY KEY (measure_id, day)
);
CREATE INDEX IF NOT EXISTS idx_lmm_day ON lead_measure_marks(day);

-- "Not-To-Do" list (Brian Tracy) + distraction blocklist (James Clear's
-- "make it invisible"). kind='rule' is a low-value behavior to STOP doing
-- (a commitment you keep by seeing it); kind='site' is a domain the blocker
-- redirects in the hosts file while a focus block is active.
CREATE TABLE IF NOT EXISTS not_to_do (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL DEFAULT '',
    kind TEXT NOT NULL DEFAULT 'rule',   -- 'rule' (behavior) | 'site' (domain)
    sort_order INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nottodo_kind ON not_to_do(kind);

-- "Winner's Time Log" (Zig Ziglar) / time audit (Brian Tracy, James Clear):
-- a low-friction chime from 5 min to 2 hr asks "what did you just work on?" and
-- one tap files the answer here. One row per logged interval; the weekly pie
-- chart sums `minutes` by `category`. Tracking where the minutes actually go
-- is, in Ziglar's words, a "freeing factor," not a limiting one.
CREATE TABLE IF NOT EXISTS time_log (
    id INTEGER PRIMARY KEY,
    log_date TEXT NOT NULL,             -- YYYY-MM-DD (used by the weekly chart)
    logged_at TEXT NOT NULL,            -- HH:MM the interval was filed
    category TEXT NOT NULL DEFAULT '',  -- "A-1 Task" | "Studying" | "Distracted" …
    note TEXT NOT NULL DEFAULT '',
    minutes INTEGER NOT NULL DEFAULT 60,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_timelog_date ON time_log(log_date);

-- "After-Action Review" (Brian Tracy / James Clear): experience alone doesn't
-- improve you — EVALUATED experience does. One reflection per day, two
-- questions ("what did I do right?" / "what would I do differently?") plus an
-- optional 1-5 self-rating, so the week can be reviewed and habits fine-tuned.
CREATE TABLE IF NOT EXISTS daily_review (
    id INTEGER PRIMARY KEY,
    review_date TEXT NOT NULL UNIQUE,   -- YYYY-MM-DD, one review per day
    did_right TEXT NOT NULL DEFAULT '',
    do_differently TEXT NOT NULL DEFAULT '',
    rating INTEGER NOT NULL DEFAULT 0,  -- 0 = unrated, else 1-5
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- "Pay Yourself First" (George S. Clason / Bach): a part of all you earn is
-- yours to keep. Each paycheck's savings cut (gross * save_pct) is recorded
-- here and locked into the Financial Independence balance BEFORE the rest is
-- budgeted. `budget_items` then allocates only the spendable remainder.
CREATE TABLE IF NOT EXISTS paychecks (
    id INTEGER PRIMARY KEY,
    pay_date TEXT NOT NULL,            -- YYYY-MM-DD
    gross REAL NOT NULL DEFAULT 0,
    save_pct REAL NOT NULL DEFAULT 10, -- percent paid to yourself first
    saved REAL NOT NULL DEFAULT 0,     -- gross * save_pct/100 (the locked cut)
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS budget_items (
    id INTEGER PRIMARY KEY,
    paycheck_id INTEGER NOT NULL,      -- draws from this paycheck's spendable
    category TEXT NOT NULL DEFAULT '',
    amount REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_budget_paycheck ON budget_items(paycheck_id);

-- "Latte Factor" (David Bach): the small daily leaks — coffees, snacks,
-- subscriptions — that sink the ship. Fast-entry of any purchase; the weekly
-- total shows what slipped through and what it could have become if saved.
CREATE TABLE IF NOT EXISTS small_expenses (
    id INTEGER PRIMARY KEY,
    spend_date TEXT NOT NULL,          -- YYYY-MM-DD
    amount REAL NOT NULL DEFAULT 0,
    label TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_smallexp_date ON small_expenses(spend_date);

-- "Dream Bucket" (Dave Ramsey): save cash for big goals (fridge, washer,
-- dryer, car) to avoid debt. A visual progress bar fills as you transfer in
-- money you saved by skipping a purchase — an instant dopamine reward.
CREATE TABLE IF NOT EXISTS dream_buckets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    target REAL NOT NULL DEFAULT 0,
    saved REAL NOT NULL DEFAULT 0,
    emoji TEXT NOT NULL DEFAULT '🎯',
    image_path TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 7-Day Purchase Delay (the "30-day rule" / frugality): fast money decisions
-- are usually poor ones. A wanted non-essential is locked with a countdown;
-- you can't mark it "bought" until the timer hits zero — by then the urge has
-- usually cooled and you let it go. Dropped items tally "money kept".
CREATE TABLE IF NOT EXISTS wishlist (
    id INTEGER PRIMARY KEY,
    item TEXT NOT NULL DEFAULT '',
    price REAL NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    unlock_at TEXT NOT NULL,                  -- ISO; buying allowed only after
    status TEXT NOT NULL DEFAULT 'waiting',   -- waiting | bought | dropped
    decided_at TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_wishlist_status ON wishlist(status);

-- "Save More Tomorrow" (Thaler/Benartzi) + the Wedge Theory: commit FUTURE
-- money. A signed contract says that when you get a raise, half the increase
-- is swept to savings before you ever see it. One contract row (id=1) plus a
-- log of raises and the monthly/annual savings each one wedged off.
CREATE TABLE IF NOT EXISTS smart_contract (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    signed INTEGER NOT NULL DEFAULT 0,
    signer TEXT NOT NULL DEFAULT '',
    base_wage REAL NOT NULL DEFAULT 0,
    current_wage REAL NOT NULL DEFAULT 0,
    hours_per_week REAL NOT NULL DEFAULT 40,
    wedge_pct REAL NOT NULL DEFAULT 50,
    signed_at TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS raises (
    id INTEGER PRIMARY KEY,
    old_wage REAL NOT NULL,
    new_wage REAL NOT NULL,
    wedge_pct REAL NOT NULL DEFAULT 50,
    hours_per_week REAL NOT NULL DEFAULT 40,
    monthly_wedge REAL NOT NULL DEFAULT 0,
    annual_wedge REAL NOT NULL DEFAULT 0,
    raised_at TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Zero-Based Budgeting auditor: every recurring charge must re-earn its place.
-- Every ~90 days the audit walks each one and asks "knowing what you know now,
-- would you sign up for this again today?" — a No cancels the drain.
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL DEFAULT '',
    amount REAL NOT NULL DEFAULT 0,
    cycle TEXT NOT NULL DEFAULT 'monthly',   -- monthly | yearly
    active INTEGER NOT NULL DEFAULT 1,
    last_reviewed TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- V2MOM "Why" engine (Sinek's Why + Robbins' V2MOM): a major goal can't be
-- saved until you've written your WHY (values) and named the OBSTACLES in the
-- way. Vision/Values/Methods/Obstacles/Measurement — knowing why beats how.
CREATE TABLE IF NOT EXISTS v2mom_goals (
    id INTEGER PRIMARY KEY,
    vision TEXT NOT NULL DEFAULT '',
    values_why TEXT NOT NULL DEFAULT '',     -- the WHY (required to save)
    methods TEXT NOT NULL DEFAULT '',
    obstacles TEXT NOT NULL DEFAULT '',      -- required to save
    if_then TEXT NOT NULL DEFAULT '',        -- optional implementation intention
    measurement TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active',    -- active | done | parked
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Daily "10-Goal" spiral notebook (Brian Tracy): each morning, rewrite your
-- top 10 goals FROM MEMORY in the present tense ("I earn $80,000 …"). Writing
-- them daily programs them into the subconscious. One row per day; what stays
-- top-of-mind day to day reveals what matters most.
CREATE TABLE IF NOT EXISTS goal_journal (
    id INTEGER PRIMARY KEY,
    entry_date TEXT NOT NULL UNIQUE,   -- YYYY-MM-DD, one per day
    goals TEXT NOT NULL DEFAULT '',     -- the goals, newline-separated
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- A→B→Z systems / checklists (James Clear: systems beat goals; Brian Tracy:
-- a checklist makes success 10x likelier). A 'system' is the big goal (Z); its
-- ordered steps are the process. You only ever need to know the next step (B).
CREATE TABLE IF NOT EXISTS systems (
    id INTEGER PRIMARY KEY,
    goal TEXT NOT NULL DEFAULT '',      -- the destination (Z)
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS system_steps (
    id INTEGER PRIMARY KEY,
    system_id INTEGER NOT NULL,
    step TEXT NOT NULL DEFAULT '',
    done INTEGER NOT NULL DEFAULT 0,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_steps_system ON system_steps(system_id);

-- Lag measures (4DX): the RESULTS you ultimately want (lose 20 lbs, earn
-- $80k) — you can't manage these directly. They pair with the lead_measures
-- (the daily activities you DO control) to make the lead-vs-lag link explicit.
CREATE TABLE IF NOT EXISTS lag_measures (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL DEFAULT '',
    current REAL NOT NULL DEFAULT 0,
    target REAL NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- Habit stacking + Two-Minute Rule (James Clear). Each habit is a formula —
-- "After I [cue], I will [new habit]" — with a 2-minute gateway version that
-- makes starting trivial. habit_marks logs the days done so streaks can build.
CREATE TABLE IF NOT EXISTS habits (
    id INTEGER PRIMARY KEY,
    cue TEXT NOT NULL DEFAULT '',          -- the existing habit (anchor)
    new_habit TEXT NOT NULL DEFAULT '',    -- the new behavior
    two_min TEXT NOT NULL DEFAULT '',      -- the 2-minute gateway version
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS habit_marks (
    habit_id INTEGER NOT NULL,
    day TEXT NOT NULL,                      -- YYYY-MM-DD
    created_at TEXT NOT NULL,
    PRIMARY KEY (habit_id, day)
);

-- Bill Sentinel (Sprint F): prospective-memory scaffolding for bills. The
-- app cannot pay anything — it tracks which bills are AUTOMATED (autopay,
-- green, silent) and cues the ones that still depend on memory. Rows are
-- archived, never deleted.
CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    amount_cents INTEGER NOT NULL DEFAULT 0,
    due_day INTEGER NOT NULL DEFAULT 1,      -- 1-31, clamped to month end
    autopay INTEGER NOT NULL DEFAULT 0,      -- 1 = automated (the goal state)
    last_paid TEXT,                           -- YYYY-MM-DD of last manual pay
    archived INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- PERT "back from the future" planner: start from the target date and schedule
-- every milestone BACKWARD to reveal when each must begin — and what to do today.
CREATE TABLE IF NOT EXISTS pert_plans (
    id INTEGER PRIMARY KEY,
    goal TEXT NOT NULL DEFAULT '',
    target_date TEXT NOT NULL DEFAULT '',   -- YYYY-MM-DD (the ideal future result)
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pert_steps (
    id INTEGER PRIMARY KEY,
    plan_id INTEGER NOT NULL,
    name TEXT NOT NULL DEFAULT '',
    weeks REAL NOT NULL DEFAULT 1,          -- duration in weeks
    sort_order INTEGER NOT NULL DEFAULT 0,  -- chronological order (first..last)
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pert_steps ON pert_steps(plan_id);

-- "Blue-Sky" vision board (Tracy / Robbins): images of the life you want,
-- compiled into a daily slideshow (optional music) to vividly program the
-- reticular activating system before each day begins.
CREATE TABLE IF NOT EXISTS vision_images (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL DEFAULT '',
    caption TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Financial-defense expense ledger (The Millionaire Next Door): capture and
-- categorize every expense over months to see where the money actually goes.
-- The four "Core Defense" categories (Rent/Utilities/Food/Transportation) are
-- surfaced against the Core Four targets so survival needs are clearly met.
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY,
    spend_date TEXT NOT NULL,              -- YYYY-MM-DD
    amount REAL NOT NULL DEFAULT 0,
    category TEXT NOT NULL DEFAULT 'Other',
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(spend_date);

-- Three-Bucket asset allocation (Tony Robbins): split your money across a
-- Security bucket (can't-afford-to-lose: cash/bonds/TIPS), a Risk/Growth
-- bucket (stocks/equities/real estate), and a Dream bucket (strategic
-- splurges). Each holding lives in one bucket; the mix is your allocation.
CREATE TABLE IF NOT EXISTS asset_holdings (
    id INTEGER PRIMARY KEY,
    bucket TEXT NOT NULL DEFAULT 'security',   -- security | growth | dream
    name TEXT NOT NULL DEFAULT '',
    amount REAL NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

-- Appointments / implementation-intentions with a real clock time. Built from
-- the Idea Warehouse "Intention" builder: stating WHO/WHERE and an exact time
-- makes follow-through far more likely (James Clear). Each appointment is
-- mirrored onto the day-level Planner (planner_id links the row) AND drives up
-- to three Windows-scheduled reminders (T-60/-30/-15 min) that flash a
-- light-teal OpenDyslexic alert — so the reminder fires even with the app
-- closed. when_dt is local wall-clock 'YYYY-MM-DD HH:MM'.
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL DEFAULT '',         -- the behavior / what ("get a haircut")
    who TEXT NOT NULL DEFAULT '',           -- who you're meeting
    location TEXT NOT NULL DEFAULT '',      -- where you're supposed to be
    when_dt TEXT NOT NULL,                  -- 'YYYY-MM-DD HH:MM' (local)
    notes TEXT NOT NULL DEFAULT '',
    planner_id INTEGER,                     -- linked planner_tasks row, if mirrored
    status TEXT NOT NULL DEFAULT 'open',    -- open | done | cancelled
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_appt_when ON appointments(when_dt);

-- Voice Memory: a personal dictation correction dictionary. Whisper can't be
-- retrained locally, so instead we learn at the TEXT layer — each row maps a
-- phrase the recognizer kept producing (`heard`, stored lowercased as the
-- match key) to what the user actually meant (`meant`). _append_dictation
-- applies these to every dictated phrase, and the distinct `meant` terms also
-- bias Whisper via initial_prompt. `hits` counts how often it's been applied
-- (so the list can surface the most valuable fixes). Accent/pronunciation
-- adaptation, the practical way.
CREATE TABLE IF NOT EXISTS voice_corrections (
    id INTEGER PRIMARY KEY,
    heard TEXT NOT NULL,                 -- lowercased key (what Whisper produced)
    meant TEXT NOT NULL,                 -- the replacement the user wants
    hits INTEGER NOT NULL DEFAULT 0,     -- times auto-applied
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_voice_heard ON voice_corrections(heard);

-- Goal check-ins: a timestamped 1-10 self-rating logged repeatedly over the
-- life of a goal. Combined with the goal's baseline + target_level (added to
-- the goals table), this turns the vague Progress % into a measured journey —
-- progress = (latest - baseline) / (target - baseline) — and gives a real
-- series to graph. Honest descriptive tracking, no estimation.
CREATE TABLE IF NOT EXISTS goal_checkins (
    id INTEGER PRIMARY KEY,
    goal_id INTEGER NOT NULL,
    value INTEGER NOT NULL,        -- 1-10 self-rating at logged_at
    logged_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_goal_checkins ON goal_checkins(goal_id, logged_at);

-- Job-readiness check-ins: one honest self-audit per day across the six
-- pillars hiring actually checks (lyceum/job_readiness.py). scores is the
-- kernel's JSON encoding {pillar: 0-4}; pct is the derived 0-100 readiness so
-- history can be listed without re-deriving. Same-day saves REPLACE the day's
-- row (one honest look per day); rows are never deleted — the history is the
-- point.
CREATE TABLE IF NOT EXISTS job_readiness_checks (
    id INTEGER PRIMARY KEY,
    check_date TEXT NOT NULL UNIQUE,   -- YYYY-MM-DD
    scores TEXT NOT NULL,              -- JSON {pillar_key: 0-4}
    pct INTEGER NOT NULL,              -- derived readiness 0-100
    note TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_job_readiness_date
    ON job_readiness_checks(check_date);

-- ── Spaced-repetition memory training (RELAY-SRS-001, Sprint 1) ────────────
-- Additive only. Scheduling is delegated to py-fsrs (MIT); lyceum/srs.py is
-- the sole writer. fsrs_card_json is the single source of truth for scheduler
-- state; due/state/lapses/reps are denormalized copies kept in step by
-- srs.py so plain SQL can answer "what's due" without deserializing JSON.

CREATE TABLE IF NOT EXISTS memory_decks (
    deck_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,          -- e.g. 'Glossary', 'Peg System 00-99'
    deck_type   TEXT NOT NULL DEFAULT 'basic'  -- 'basic' | 'glossary' | 'peg'
                CHECK (deck_type IN ('basic','glossary','peg','palace','faces')),
    created_at  TEXT NOT NULL,                 -- ISO 8601 UTC
    archived    INTEGER NOT NULL DEFAULT 0     -- 0/1; soft delete, never hard-delete
);

CREATE TABLE IF NOT EXISTS memory_cards (
    card_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id         INTEGER NOT NULL REFERENCES memory_decks(deck_id),
    front           TEXT NOT NULL,             -- prompt (term, number, image path label)
    back            TEXT NOT NULL,             -- answer (definition, peg word, name)
    media_path      TEXT,                      -- optional image (faces, vision-board style)
    source_kind     TEXT NOT NULL DEFAULT 'manual'
                    CHECK (source_kind IN ('manual','glossary','excerpt','peg','palace','faces')),
    source_ref      TEXT,                      -- glossary term / excerpt doc_id / peg number
    zone            TEXT NOT NULL DEFAULT 'GREEN'
                    CHECK (zone IN ('GREEN','YELLOW','RED')),
    cognitive_load  INTEGER CHECK (cognitive_load BETWEEN 1 AND 10),
    tags            TEXT NOT NULL DEFAULT '[]',  -- JSON array, lowercase_underscore
    fsrs_card_json  TEXT NOT NULL,             -- authoritative: py-fsrs Card.to_dict() as JSON
    due             TEXT NOT NULL,             -- ISO 8601 UTC, denormalized for fast queries
    state           TEXT NOT NULL DEFAULT 'new'
                    CHECK (state IN ('new','learning','review','relearning')),
    lapses          INTEGER NOT NULL DEFAULT 0,
    reps            INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL,
    suspended       INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_memory_cards_due
    ON memory_cards (suspended, due);
CREATE INDEX IF NOT EXISTS idx_memory_cards_deck
    ON memory_cards (deck_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_memory_cards_source
    ON memory_cards (source_kind, source_ref)
    WHERE source_ref IS NOT NULL;              -- prevents duplicate glossary imports

-- Append-only: never UPDATE or DELETE — this is the FSRS optimizer's future
-- training data and the dashboard's lead-measure feed.
CREATE TABLE IF NOT EXISTS memory_review_log (
    review_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id         INTEGER NOT NULL REFERENCES memory_cards(card_id),
    rating          INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 4),
                    -- 1=Again 2=Hard 3=Good 4=Easy (py-fsrs Rating values)
    reviewed_at     TEXT NOT NULL,             -- ISO 8601 UTC
    review_duration_ms INTEGER,                -- optional; UI supplies later
    scheduled_days  REAL,                      -- interval FSRS assigned at this review
    state_before    TEXT NOT NULL,
    state_after     TEXT NOT NULL,
    session_load    INTEGER CHECK (session_load BETWEEN 1 AND 10)
                    -- optional cognitive-load stamp for the session
);

CREATE INDEX IF NOT EXISTS idx_review_log_card ON memory_review_log (card_id);
CREATE INDEX IF NOT EXISTS idx_review_log_time ON memory_review_log (reviewed_at);

-- ── Reward-Draw: variable-ratio reward engine (Sprint: Reward-Draw v1) ──────
-- Additive only. lyceum/reward_engine.py is the sole writer. The pool holds
-- unlockable payloads; every entry MUST carry a named source from the owner's
-- library (the engine refuses unsourced payloads — honesty gate). The log is
-- append-only: it is the pity-guarantee's memory and the audit trail; never
-- UPDATE or DELETE.

CREATE TABLE IF NOT EXISTS reward_pool (
    pool_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    tier        TEXT NOT NULL
                CHECK (tier IN ('STANDARD','UNCOMMON','RARE')),
    payload     TEXT NOT NULL,                 -- what the user sees (quote, flourish)
    source      TEXT NOT NULL,                 -- named library source; never blank
    retired     INTEGER NOT NULL DEFAULT 0,    -- 0/1; soft retire, never hard-delete
    created_at  TEXT NOT NULL                  -- ISO 8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_reward_pool_tier ON reward_pool (retired, tier);

CREATE TABLE IF NOT EXISTS reward_log (
    reward_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    event       TEXT NOT NULL,                 -- the completion that earned it
    tier        TEXT NOT NULL
                CHECK (tier IN ('STANDARD','UNCOMMON','RARE')),
    payload     TEXT NOT NULL,
    source      TEXT NOT NULL,
    created_at  TEXT NOT NULL                  -- ISO 8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_reward_log_time ON reward_log (created_at);
"""


def init_study_db() -> None:
    """Create the study database and its tables if they don't exist."""
    try:
        os.makedirs(STUDY_DIR, exist_ok=True)          # sidecars (OneDrive)
    except OSError as e:
        print(f"[lyceum.db] Could not create {STUDY_DIR}: {e}", file=sys.stderr)
    try:
        os.makedirs(db_location.live_db_dir(), exist_ok=True)   # live DB (local)
    except OSError as e:
        print(f"[lyceum.db] Could not create live DB dir: {e}", file=sys.stderr)
        return
    # One-time, non-destructive migration of any older OneDrive-resident DB to the
    # new local location. MUST run before connect() creates an empty live file.
    db_location.migrate_legacy_if_needed(STUDY_DB, _LEGACY_DB)
    try:
        con = connect()
        con.executescript(STUDY_SCHEMA)
        # Lightweight migration: add baseline/target columns to an older goals
        # table (CREATE IF NOT EXISTS won't add columns to an existing table).
        try:
            have = {r[1] for r in con.execute(
                "PRAGMA table_info(goals)").fetchall()}
            for col in ("baseline", "target_level"):
                if col not in have:
                    con.execute(
                        f"ALTER TABLE goals ADD COLUMN {col} "
                        "INTEGER NOT NULL DEFAULT 0")
        except sqlite3.Error:
            pass
        # Additive migration: V2MOM if-then plan line (implementation
        # intentions — Gollwitzer & Sheeran 2006). Optional, never required.
        try:
            have = {r[1] for r in con.execute(
                "PRAGMA table_info(v2mom_goals)").fetchall()}
            if "if_then" not in have:
                con.execute("ALTER TABLE v2mom_goals ADD COLUMN if_then "
                            "TEXT NOT NULL DEFAULT ''")
        except sqlite3.Error:
            pass
        # Additive migration: prompt_library.archived_at — entries archive,
        # never delete (owner QA find 2026-07-20). NULL = active.
        try:
            have = {r[1] for r in con.execute(
                "PRAGMA table_info(prompt_library)").fetchall()}
            if "archived_at" not in have:
                con.execute("ALTER TABLE prompt_library "
                            "ADD COLUMN archived_at TEXT")
        except sqlite3.Error:
            pass
        con.commit()
        con.close()
    except sqlite3.Error as e:
        print(f"[lyceum.db] DB init error: {e}", file=sys.stderr)
    # Best-effort: drop a consistent, frozen backup into the synced folder so the
    # user keeps an OneDrive copy without the live file ever being sync-contended.
    try:
        db_location.snapshot(STUDY_DB,
                             os.path.join(db_location.backup_dir(STUDY_DIR), "study.db"))
    except Exception:
        pass


def connect() -> sqlite3.Connection:
    """Return a fresh connection. Each caller closes it after use."""
    con = sqlite3.connect(STUDY_DB)
    con.execute("PRAGMA foreign_keys = ON")
    return con


def db_query(sql: str, params: tuple = ()) -> list[tuple]:
    con = connect()
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


def db_exec(sql: str, params: tuple = ()) -> int:
    """Execute a write; return the last inserted rowid (or 0)."""
    con = connect()
    try:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid or 0
    finally:
        con.close()


@contextlib.contextmanager
def transaction():
    """One atomic unit of work — ACID's 'A' (Atomicity).

    Use for any logical operation made of MORE THAN ONE statement that must
    all succeed or all fail together (e.g. delete a parent row and its child
    rows, or wipe-and-reinsert a set). Within the block, run statements on the
    yielded connection::

        with transaction() as con:
            con.execute("DELETE FROM child  WHERE parent_id=?", (pid,))
            con.execute("DELETE FROM parent WHERE id=?",        (pid,))

    sqlite3's connection context manager commits on a clean exit and issues a
    ROLLBACK if the block raises, so a crash partway through leaves the database
    exactly as it was — no orphaned or half-written rows. The connection is
    always closed afterward.
    """
    con = connect()
    try:
        with con:          # commit on success; ROLLBACK on any exception
            yield con
    finally:
        con.close()