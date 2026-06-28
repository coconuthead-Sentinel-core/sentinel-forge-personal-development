# Database Schema

*Reviewed 2026-06-27 against `aea48c8`. Source of truth:
[`lyceum/db/study_db.py`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/blob/main/lyceum/db/study_db.py).*

## Engine & location

- **Engine:** SQLite 3 (via Python's stdlib `sqlite3` — no external DB server).
- **File:** `study.db` at `~\OneDrive\Documents\BookReader\study.db`
  (`STUDY_DIR` / `STUDY_DB`). User content is here; OneDrive backs it up.
- **Foreign keys are enforced:** every connection runs
  `PRAGMA foreign_keys = ON` (SQLite disables FK enforcement by default — this is
  a common silent-data-corruption trap and is explicitly avoided here).
- **Schema is idempotent:** `STUDY_SCHEMA` is all `CREATE TABLE IF NOT EXISTS`,
  run by `init_study_db()` on every launch. Safe to run repeatedly.
- **One lightweight migration** is hand-coded: `goals` gains `baseline` and
  `target_level` columns via `ALTER TABLE` guarded by a `PRAGMA table_info`
  check, because `CREATE IF NOT EXISTS` cannot add columns to an existing table.

## Data-access API (the only way the app touches the DB)

| Function | Contract |
| --- | --- |
| `connect()` | Fresh connection, FK enforcement on. Caller closes it. |
| `db_query(sql, params)` | Read; returns `list[tuple]`. Always closes. |
| `db_exec(sql, params)` | Single write; commits; returns `lastrowid`. Always closes. |
| `transaction()` | **Context manager for multi-statement atomic units** (see below). |

### The `transaction()` primitive — ACID Atomicity

```python
with transaction() as con:
    con.execute("DELETE FROM child  WHERE parent_id=?", (pid,))
    con.execute("DELETE FROM parent WHERE id=?",        (pid,))
# both land, or neither does
```

`sqlite3`'s connection context manager **commits on a clean exit** and issues a
**`ROLLBACK` if the block raises**, so a crash partway through leaves the DB
exactly as it was — no orphaned children, no half-deleted records. This is the
**'A' (Atomicity)** of **ACID**. It was added to fix a real atomicity violation
(deletes that ran as two independently auto-committed statements) — see
[Former Bugs §6](Former-Bugs-and-Regressions.md#6-non-atomic-deletes-acid-violation).
Four parent/child delete units now use it: `budget_items`+`paychecks`,
`system_steps`+`systems`, `habit_marks`+`habits`, `pert_steps`+`pert_plans`.

## Table catalog (37 tables)

Grouped by subsystem. `created_at`/`updated_at` are ISO-8601 text throughout
(SQLite has no native datetime type — dates are stored as `TEXT`, a deliberate,
conventional choice).

### Reading & study content

| Table | Purpose / key columns |
| --- | --- |
| `highlights` | Saved highlights: `book`, `start_offset`, `end_offset`, `color`. Indexed by book. |
| `topics` / `topic_entries` | Topic notebooks (master-detail); `topic_entries.topic_id` **CASCADE-deletes**. |
| `bookmarks` | Per-book saved positions. |
| `glossary` | Term/definition; `term` is `UNIQUE COLLATE NOCASE`. |
| `journal` | Dated free-text journal entries. |
| `study_notes` | Legacy single-blob note (`CHECK (id=1)`); migrated into… |
| `study_note_entries` | …the master-detail Study Notes archive (one row per saved note). |
| `prompt_library` | Standalone prompt+response archive (separate from the Books vault). |
| `prompts` | Prompt-engineering worksheet (purpose, refs, iterations, tools…). |

### Planning, goals & habits

| Table | Purpose / key columns |
| --- | --- |
| `eisenhower` | Four-quadrant matrix, one row per quadrant (PK = quadrant). |
| `matrix_pomodoros` / `matrix_task_log` | Focus-block ticker; completed task lines optionally link to the active pomodoro. |
| `day_blocks` | Time-blocked day plan (slot order, duration, `is_current`). |
| `planner_tasks` | Sunsama-style daily planner (`day`, `minutes`, `sort_order`). |
| `workflow_folders` | Named workflow folders (`name` unique NOCASE). |
| `goals` (+ `baseline`,`target_level`) | Ziglar goal worksheet; tied to a Wheel life-area; `progress` 0–100. |
| `goal_checkins` | Timestamped 1–10 self-ratings → honest measured progress (not estimated). |
| `goal_journal` | Daily "rewrite your 10 goals from memory"; one row per day (`entry_date` UNIQUE). |
| `wheel_of_life` | Dated 7-spoke self-assessment snapshots (mental…social, each 1–10). |
| `systems` / `system_steps` | A→B→Z checklists; steps ordered, `done` flag. |
| `lead_measures` / `lead_measure_marks` | 4DX lead measures + per-day check-offs (PK = measure+day → streaks). |
| `lag_measures` | 4DX lag results (current/target/unit) paired with leads. |
| `weekly_roles` | Covey Quadrant-II weekly roles (one row per role per Monday). |
| `not_to_do` | Tracy "not-to-do" rules **and** Clear site-blocklist (`kind` = rule\|site). |
| `master_tasks` | Idea Warehouse: ABCDE priority, `big_three` flag, `scheduled_day`. |
| `habits` / `habit_marks` | Habit-stack formula + 2-minute version; per-day marks (PK = habit+day). |
| `pert_plans` / `pert_steps` | Back-from-the-future PERT scheduling (target date + weighted steps). |
| `v2mom_goals` | V2MOM intake; `values_why` and `obstacles` required to save. |
| `vision_images` | Blue-Sky vision-board slideshow images + captions. |
| `daily_review` | After-Action Review; one per day (`review_date` UNIQUE), optional 1–5 rating. |
| `audits` | Stored audit records (grade, mentor note, `findings_json`). |
| `appointments` | Implementation-intentions with a clock time; drives T-60/-30/-15 Windows reminders; mirrors to `planner_tasks`. |

### Finance suite

| Table | Purpose / key columns |
| --- | --- |
| `paychecks` / `budget_items` | Pay-Yourself-First: locked `saved` cut + spendable allocations (atomic delete pair). |
| `small_expenses` | Latte Factor fast-entry ledger. |
| `expenses` | Financial-defense categorized expense ledger. |
| `dream_buckets` | Targeted savings buckets with image + progress. |
| `wishlist` | 7/30-day purchase delay; `unlock_at` gate; status waiting\|bought\|dropped. |
| `smart_contract` / `raises` | Save-More-Tomorrow wedge contract (id=1) + logged raises. |
| `subscriptions` | Zero-Based / KWINK audit of recurring charges. |
| `asset_holdings` | Three-Bucket allocation (security\|growth\|dream). |

### Accessibility / voice

| Table | Purpose / key columns |
| --- | --- |
| `voice_corrections` | Personal dictation correction dictionary: `heard` (lowercased key, UNIQUE) → `meant`, with `hits` count. Adapts Whisper at the **text layer** (the model can't be retrained locally) and biases it via `initial_prompt`. |

### Time tracking

| Table | Purpose / key columns |
| --- | --- |
| `time_log` | Winner's Time Log: one row per chimed interval; weekly pie sums `minutes` by `category`. |

## Schema conventions worth knowing

- **Surrogate keys:** every table has an `INTEGER PRIMARY KEY` (SQLite rowid
  alias) except junction/singleton tables that use a natural composite or
  fixed PK (`lead_measure_marks(measure_id, day)`, `habit_marks(habit_id, day)`,
  `eisenhower(quadrant)`, `smart_contract(id CHECK id=1)`).
- **Indexes** are declared for every column the app filters or joins on
  (`idx_*_date`, `idx_*_status`, etc.) — read-path performance is intentional,
  not accidental.
- **`COLLATE NOCASE` UNIQUE** on human-typed keys (`glossary.term`,
  `workflow_folders.name`) prevents "Python" vs "python" duplicates.
- **Referential integrity** is expressed where it's enforced
  (`topic_entries → topics ON DELETE CASCADE`); other parent/child pairs rely on
  the application-level `transaction()` because they predate FK constraints.
  *Future hardening:* migrate the remaining app-level cascades to declared
  `ON DELETE CASCADE` foreign keys.
