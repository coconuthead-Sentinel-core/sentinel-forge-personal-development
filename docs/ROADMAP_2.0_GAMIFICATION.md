# Sentinel Forge 2.0 — Gamification Vision & Roadmap

> Status: **PLANNED VISION** (research document, integrated 2026-07-08).
> Nothing below is implemented unless marked ✅. This framing is
> deliberate: planned features are described as planned — no
> enterprise-grade / production-ready / clinically-validated claims.

## Positioning statement

Sentinel Forge 2.0 is a local-first Windows personal-development
workstation that turns focus, reading, money defense, habit recovery,
and self-review into a neurodivergent-friendly game loop. It combines a
tested Python/SQLite functional core with adaptive questing, accessible
reading tools, and privacy-preserving AI assistance. The goal is not to
gamify distraction; the goal is to make real-world progress visible,
rewarding, and easier to restart.

## Design principle: dopamine, but not addiction

Real action → instant response → visible progress → connected to a life
goal → obvious next step.

- **Reward effort, not perfection** — "showed up for 5 minutes" earns
  nearly as much as "finished 90."
- **Reward recovery** — a missed day creates a rescue quest, never a
  shame screen (Never Miss Twice → Streak Rescue Mode).
- **Reward real-world protection** — rent covered, leak skipped,
  savings sealed, focus block ended.
- **Never reward risky financial behavior** — the SEC has flagged
  game-like trading features for encouraging risk. The Forge gamifies
  financial DEFENSE (Core Four, savings, audits, cooldowns, education)
  — never stock picking, options, crypto, leverage, or trading streaks.
  North star = CFPB financial well-being: security and freedom of
  choice.

## The Forge — four systems, one question

App opens with ONE question: *"What are we protecting or building
today?"* — max three choices (W3C cognitive-accessibility: limit major
choices):

| System | Contents | Status |
|---|---|---|
| 🔥 The Fire — Focus | Do Now, Pomodoro, 5-4-3-2-1, Time Log | ✅ features exist; quest wrapper planned |
| 📚 The Library — Knowledge | books, excerpts, Ask Library, glossary, **FSRS flashcards** | ✅ core + SRS engine (`lyceum/srs.py`); Recall Duel UI planned |
| 🛡 The Shield Wall — Money Defense | Core Four, Pay-First, Run Rate, leaks, Wishlist | ✅ all tools exist; game layer planned |
| 🧭 The North Star — Purpose | MDP banner, Vision Board, V2MOM, Daily 10, AAR | ✅ all exist; XP wiring planned |

**Key insight from the research review: nearly every 2.0 mechanic maps
onto a feature that already ships in v0.9.** The work is connective
tissue (quests, XP, seasons), not new verticals.

## Loops

- **10-minute loop (ADHD activation):** open → one mission → 5-4-3-2-1
  → focus → small action → instant reward → "keep going / pause / bank
  the win?"
- **Daily loop:** one A-1 mission → one focus block → one saved note →
  one protected resource → AAR → "Forge Lit."
- **Weekly loop:** Scoreboard review → lead/lag → skill-tree progress →
  one bottleneck → next week's Boss Fight.
- **Season loop:** 7/30/66-day campaigns (66-day season aligns with the
  habit-automaticity literature average — with wide individual
  variation, and we say so).

## Planned data model (additive, event-sourced)

`events` (append-only actions), `quests`, `skills`, `xp_ledger`
(append-only — XP is DERIVED from real events, never a fragile
counter), `streaks`, `player_profile` (mode/Hexad/sensory prefs),
`unlock_state`, `reward_settings`, `ai_insights`.
`memory_review_log` (✅ shipped, Sprint 1) already follows this
event-sourced pattern.

## Personalization

- **Experience styles:** High Energy / Balanced / Sensory-Neutral
  (respect `prefers-reduced-motion`; sound/haptics optional, never the
  only feedback channel).
- **Age presets:** Young-adult (identity, streaks), Adult (stability,
  money defense, career ladder), Senior (clarity, dignity, legacy,
  recovery-first, never childish).
- **Hexad types** (Achiever / Free Spirit / Philanthropist / Socializer
  / Player / Disruptor): same backend, different presentation layer.
  Research basis: gamification effects are context- and user-dependent
  (Hamari); SDT (autonomy/competence/relatedness) is the backbone.

## Accessibility engine (the operating system of the app)

Every screen answers: What is this? What do I do next? How long will it
take? What happens when I finish? Hard rules: ≤5 major choices per
screen, one primary button, one active mission, wizards for big
processes, rescue paths for misses, handoff note at session end.
Dyslexia reading mode per BDA style guide (plain sans-serif, 1.5 line
height, left-aligned, soft background, sentence highlighting + TTS —
✅ largely shipped today).

## Architecture decision (deferred — honest note)

The research recommends Tauri + React/Fluent UI (Python sidecar) or
WinUI 3 for the 2.0 shell. That is a **separate, major project
decision**, not an incremental sprint. Current plan: keep the tested
Tk shell + `lyceum/` core, build the game layer as pure-logic modules
first (same pattern as `lyceum/srs.py`), and revisit the shell rewrite
only when the game engine is proven. Phased AI: local Whisper +
retrieval now (✅), optional local LLM adapter next, Windows AI APIs
only after the shell is stable, cloud strictly opt-in.

## 90-day build order (from the research, adapted)

1. **Days 1–15 — game engine backend:** Quest / RewardEvent /
   SkillTrack / StreakState / Season / UserMode as `lyceum/` pure-logic
   + additive tables, tests first.
2. **Days 16–30 — one vertical, completely:** the Focus Quest loop
   (open → mission → 5-4-3-2-1 → focus → reward → AAR → XP). This is
   the demo.
3. **Days 31–45 — Money Defense layer** (Shield Wall, Vault Lock, Leak
   Hunt, Cooling Chamber, Run-Rate Battery — education/calculators
   only).
4. **Days 46–60 — Knowledge Quest layer** (Knowledge Spark, Discovery
   Link, Memory Tile, **Recall Duel on the shipped FSRS core**, Map
   Nodes).
5. **Days 61–75 — accessibility + personalization** (3 sensory modes,
   age presets, Hexad quiz).
6. **Days 76–90 — README v2, demo video, architecture diagram, feature
   status table (implemented vs planned), accessibility + financial-
   ethics statements.**

## The killer demo (one heroic loop)

Open app → North Star: *"Earn my CS Degree by 2028"* → one mission:
"25-minute GitHub study sprint" → 5-4-3-2-1 GO → Focus Mode dims the
world → timer builds a glowing forge object → save one excerpt → Ask
Library surfaces a related note → AAR → Focus XP + Knowledge Spark +
streak protected → *"You moved the degree forward today."*

## Source notes / caveats

Market-size figures (e.g. "$36B → $112B") are directional vendor
estimates, not verified facts. Gamification research is positive but
context-dependent; superficial rewards fatigue users. Senior-adult
gamification evidence is thinner (low-certainty meta-analyses) — design
respectfully. Financial gamification stays strictly on the
defense/education side of the SEC's digital-engagement-practices line.
