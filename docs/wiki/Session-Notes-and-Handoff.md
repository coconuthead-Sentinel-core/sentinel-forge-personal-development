# Session Notes & Handoff

*The running log for the next coding assistant (human or AI). Read this first
when resuming. Newest entry at the top. Each entry: date · what changed · why ·
what's next. Reviewed 2026-06-27 against `aea48c8`.*

---

## ⏱ Current state at a glance (as of 2026-06-27)

- **Branch:** `main` · **HEAD:** `aea48c8` · clean, laptop = OneDrive = GitHub.
- **Version:** v0.9 (release-candidate track). **Tests:** 34/34 passing.
- **Phase:** stabilization / hardening. **Feature freeze recommended** — resist
  adding new panels; finish the [exit criteria](SDLC-and-Process.md#5-exit-criteria-before-stakeholder-handoff).
- **Entry point:** `sentinel_personal_development.py` (run `run_sentinel.bat`).
- **Total commits:** 208.

### Top of the to-do list (highest leverage first)
1. **Add CI** — a GitHub Actions workflow running `py_compile` + `unittest` on
   every push/PR. Closes the biggest "2026 classroom" gap and protects `main`.
2. **Tag `v0.9-rc1`** and start **`CHANGELOG.md`** (Keep a Changelog format).
3. **Reconcile docs:** README says **24** tests → it's **34**; README quick-start
   says `book_reader.py` → it's `sentinel_personal_development.py`.
4. **Write the SRS / feature-acceptance inventory** (exit criterion #1) — the
   [Feature Catalog](Feature-Catalog.md) is 80% of the raw material.
5. **High-DPI awareness** (`SetProcessDpiAwareness`) — fixes blurry text on
   scaled displays; the one open Windows-11 polish item that affects daily use.
6. **Keep extracting the God Object:** next clean targets are the finance pure
   maths (`_compound_series`, `_critical_mass`, `_wedge_split`,
   `_fee_future_value`) → a `lyceum/finance.py` with tests.

---

## How to work on this project (orientation for a new assistant)

1. **Sync rule is sacred:** edit the live install at
   `C:\Users\sbrya\OneDrive\Desktop\Sentinel-Forge`, then **commit and push to
   `main`**. Laptop and OneDrive are the same files. See
   [Development Workflow](Development-Workflow.md).
2. **Before committing:** `python -m py_compile sentinel_personal_development.py`
   then `python -m unittest discover -s tests`. Green or it doesn't ship.
3. **Docs → `main` directly; risky code → branch → PR.**
4. **The owner is learning to program.** Explain the *why*, name the CS concept
   (link the [Glossary](Glossary-of-CS-Concepts.md)), and anchor it to his own code.
   Coach professional framing; correct overclaiming honestly.
5. **Respect the feature freeze.** New feature requests are real, but the
   stabilization plan says *finish first*. If a feature is approved over the
   freeze, log it here with the rationale (that's how the dictation-commands
   feature was handled).
6. **The big file is organized by feature** — find a subsystem in the
   [Codebase Map](Codebase-Map.md), then search the method name.

---

## Log

### 2026-06-27 — Engineering wiki created
- **What:** Stood up this GitHub wiki (10 pages) documenting architecture, the
  37-table schema, the full feature→method map, the fixed-bug history with CS
  framing, the test suite, SDLC posture, and the dev workflow. Enabled the wiki
  on the repo (was disabled).
- **Why:** Make the paperwork catch up to the product (the standing finding in
  `docs/SDLC_STATUS.md`) and leave durable session notes for future assistance.
- **Next:** items 1–6 above; keep this page current as work lands.

### 2026-06-27 — Accessibility: hands-free spoken dictation commands  (`aea48c8`)
- **What:** `lyceum/dictation_commands.py` — pure `apply_dictation_commands()`
  turns spoken "period/comma/question mark", "new line/paragraph/tab", and
  "cap/caps on/all caps" into the characters they name. Wired into the Whisper
  path in `_append_dictation`, right after Voice Memory corrections (defensive:
  returns input unchanged on error).
- **Why:** core accessibility — lets a user who can't type punctuate, format, and
  capitalize entirely by voice. Stakeholder-approved over the freeze.
- **Tests:** +10 (`tests/test_dictation_commands.py`) → suite 34/34.
- **Deferred (on purpose):** "scratch that"/voice editing (stateful, needs the
  widget) and NATO/phonetic spelling (ambiguous in free speech — belongs in the
  Spelling Helper as an explicit mode). Both post-v0.9 backlog.

### 2026-06-27 — Stabilization increment (`d92afb3`, `1f8b3a8`, `13060ab`, `77b306b`)
- **What:** Added the ACID `transaction()` primitive and made four parent/child
  deletes atomic. Extracted the pure progress kernel (`lyceum/metrics.py`) and
  read-aloud normalizer (`lyceum/text_norm.py`), each with tests. Wheel of Life
  now reports honest baseline→target progress + roundness trend. Read-aloud text
  normalization applied at a highlight-safe seam.
- **Why:** begin the hardening phase — reduce the God Object, prove atomicity,
  make progress math honest and testable.

### 2026-05-28 — Consolidation (from `Sentinel-Forge_Next_Session_Note.md`)
- **What:** Established GitHub as the single source of truth; filled the 8
  build-inventory templates (`docs/build-inventory/`). Found **7 copies** of the
  app file; proved by diff the live Desktop version was newer/correct than the
  GitHub copy.
- **Lesson recorded:** *compare before you destroy.* The copy nearly crowned
  "official" was missing ~300 lines of newer work.

### Earlier — feature build-out & bug fixes (selected, from git history)
- Dockable floating TTS toolbar (PR `#49`, `feat/dockable-toolbar`).
- Onboard local AI assistant installed (`ai_brain.py`, Ollama).
- A run of read-aloud reliability fixes — see the full writeup in
  [Former Bugs & Regressions](Former-Bugs-and-Regressions.md): thread-safety race,
  `tk.END` staleness, single-chunk halt, newline parser error, ARG_MAX temp-file
  bypass, `for…else` syntax fix.

---

## Parking lot (ideas explicitly deferred, not lost)
- Voice-note recording (MediaRecorder or `pyaudio`).
- Tagging UI for the excerpt `tags: []` field (schema already supports it).
- Two-way sync with the Sentinel Forge platform (web-dashboard zone write-back).
- "Scratch that" / voice editing; NATO-alphabet spelling mode.
- macOS / Linux ports (Tk is portable; Piper has Linux builds).
- Migrate remaining app-level delete cascades to declared FK `ON DELETE CASCADE`.
