# Changelog

All notable changes to **Sentinel Forge — Personal Development** are documented
here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project aims to follow [Semantic Versioning](https://semver.org/).

> History before this file was reconstructed from the Git log; dates are the
> commit dates. The project is on the **v0.9 release-candidate track** (a feature
> freeze + stabilization phase — see `docs/SDLC_STATUS.md`).

## [Unreleased]

### Added
- **Continuous Integration** — a GitHub Actions workflow (`.github/workflows/ci.yml`)
  runs `py_compile` and the unit-test suite on every push and pull request to
  `main`, on Python 3.11 and 3.13 (Windows). Automated Verification & Validation
  gate (IEEE SWEBOK).
- **Engineering wiki** — architecture, the 37-table database schema, a
  feature→method map, the fixed-bug history, testing/QA, SDLC posture, the
  development workflow, a CS glossary, and running session notes.
- This `CHANGELOG.md`.

### Changed
- **README** corrected: test count `24 → 34`; entry-point and launcher names
  updated from the historical `book_reader.py` / `run_book_reader.bat` to the
  current `sentinel_personal_development.py` / `run_sentinel.bat`.

## [0.9.0-rc1] — 2026-06-27

The stabilization increment: begin paying down structural and process debt while
keeping the product feature-complete.

### Added
- **Accessibility — hands-free spoken dictation commands.** `lyceum/dictation_commands.py`
  converts spoken punctuation ("period", "question mark"), formatting ("new line",
  "new paragraph", "tab"), and capitalization ("cap", "caps on/off", "all caps")
  into the characters they name, on the Whisper input path. Lets a user who
  cannot type punctuate, format, and capitalize entirely by voice. +10 unit tests.
- **Atomic database transactions.** `lyceum/db/study_db.py: transaction()` — an
  ACID-Atomicity context manager (commit on success, `ROLLBACK` on any error).
- **Pure functional core (`lyceum/`).** Extracted `metrics.py` (progress math) and
  `text_norm.py` (read-aloud text normalization) out of the GUI class, each
  unit-tested in isolation.
- **Read-aloud text normalization** — numbers, currency, percents, ordinals, and
  common abbreviations are expanded to their spoken form before TTS, applied at a
  highlight-safe seam so follow-along stays in sync.
- **Wheel of Life** — honest baseline→target progress and a roundness-trend graph.
- **First automated test suite** — now **34 unit tests**, all passing (progress
  kernels, DB atomicity, speech normalizer, dictation commands).
- **SDLC status & methodology declaration** (`docs/SDLC_STATUS.md`).

### Changed
- Four parent/child deletes (`budget_items`+`paychecks`, `system_steps`+`systems`,
  `habit_marks`+`habits`, `pert_steps`+`pert_plans`) are now single atomic units.
- Goals progress now uses the shared, tested accountability kernel
  `progress_pct = (current − baseline) / (target − baseline)`.

### Fixed
- **Non-atomic deletes** could orphan child rows if interrupted mid-operation
  (`d92afb3`). Now wrapped in `transaction()` and covered by a rollback test.

## [0.8.x] — 2026-06 (pre-changelog, summarized from Git history)

### Added
- AI Chat Assistant integrated across panels; onboard local AI (`ai_brain.py`,
  Ollama); AI web-search context; "Explain selection" tutor.
- Dockable floating read-aloud toolbar with dynamic sentence highlighting
  (PR #49); explicit accessibility toolbar (text +/−, OpenDyslexic overlay).
- Major Definite Purpose marquee; flexible time-audit intervals.

### Changed
- **Windows 11 native integration**: Immersive Dark Mode; WASAPI-compliant audio;
  native output-driver compliance for TTS.

### Fixed
- Read-aloud reliability: thread-safety race that cleared fresh highlights
  (`99950c3`); stale `tk.END` indexing leaving AI replies unhighlighted
  (`bcdcfdf`); continuous TTS halting after one chunk on `tk.TclError`
  (`85906f5`); newline parsing error in TTS (`d0917be`); command-line length
  limit bypassed via a temp file (`8dca41d`); `for…else` syntax error (`d00ef47`).

[Unreleased]: https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/compare/main...HEAD
