# Changelog

All notable changes to **Sentinel Forge — Personal Development** are documented
here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project aims to follow [Semantic Versioning](https://semver.org/).

> History before this file was reconstructed from the Git log; dates are the
> commit dates. The project is on the **v0.9 release-candidate track** (a feature
> freeze + stabilization phase — see `docs/SDLC_STATUS.md`).

## [Unreleased]

### Added
- **💼 Job Readiness audit** — the real-world job self-examination. A pure
  kernel (`lyceum/job_readiness.py`) scores six pillars a hiring process
  actually checks (Story, Proof, Skills, People, Pipeline, Interview) 0–4
  against plain-language rubrics; readiness is the share of the 24 rubric
  points, and the **next move** is always the concrete step above the lowest
  pillar (foundational order breaks ties). Wired into the Planning hub as
  **💼 Job Ready**: live meter + band badge (🔴 COLD START → 🏆 OFFER READY),
  per-pillar rubric text that follows the slider, one saved check-in per day
  (same-day saves replace, history is never deleted), delta vs the previous
  check-in on save, and slider prefill from the last check. New
  `job_readiness_checks` table (additive). 15 new tests incl. a
  `temp_study_db()` round-trip; smoke-tested under a real `mainloop()`.
- **Continuous Integration** — a GitHub Actions workflow (`.github/workflows/ci.yml`)
  runs `py_compile` and the unit-test suite on every push and pull request to
  `main`, on Python 3.11 and 3.13 (Windows). Automated Verification & Validation
  gate (IEEE SWEBOK).
- **Engineering wiki** — architecture, the 37-table database schema, a
  feature→method map, the fixed-bug history, testing/QA, SDLC posture, the
  development workflow, a CS glossary, and running session notes.
- This `CHANGELOG.md`.
- **Live-DB pollution guard** — `lyceum.db.assert_not_live_db` / `is_live_db`
  plus a `study_db.temp_study_db()` isolation context that refuses the live
  `study.db`, closing the recurring "headless run wrote to real data" bug class
  (`tests/test_db_isolation_guard.py`).
- **Design-law linter** (`lyceum/lint_designlaws.py`) — an AST check for the
  codebase's known UI traps: tuple `pady/padx` in a widget constructor
  (**Rule A**, regression-gated at zero) and hardcoded `.geometry("WxH")`
  literals (**Rule B**). `tests/test_designlaws.py`. First run flagged **4**
  hardcoded window sizes (one exceeds the owner's effective screen height).
- **`/sentinel-sprint` skill** (`.claude/skills/sentinel-sprint/`) — the proven
  kernel → test → wire → smoke → log → mirror pipeline, formalized as a
  project-local Claude Code skill.
- **Floating-toolbar traffic light + universal Save.** The action group is now
  green **➕ Add** → yellow **💾 Save** → red **➖ Remove**, same spot and colors
  in every panel. New `_ftb_action_save` context-dispatches like Add/Remove — it
  saves the Journal entry or Study Notes directly, and elsewhere commits the
  active panel/dialog's own Save (e.g. the Topics/Glossary/Commentary Add-Edit
  boxes) or fires `Ctrl+S`. The **A− / A+** buttons became a single black/white
  toggle: the last-pressed is white, the other black — a glanceable memory of
  which way you last sized the text.
- **Toolbar refined to a labeled, real-world control cluster.** Each action is
  now a **word above a colored lamp** — **Add** over green, **Save** over
  yellow, **Delete** over red (red relabeled from "Remove"). **A− / A+** are
  redrawn as **road-marker signs** (rounded canvas plates, large
  dyslexia-legible letter) forming the black/white toggle. Zero-instruction
  recognition for a visual/tactile, ADHD/dyslexia learner; identical in every
  panel. Pseudocode captured in `docs/wiki/Rebuild-Blueprint.md` §10.
- **Toolbar-driven text inputs (non-modal).** The New-topic, Rename-topic,
  Rename-bookmark, and Glossary Look-up boxes lost their OK/Cancel buttons and
  became non-modal `_prompt_inline` inputs: a right-click clipboard menu
  (Cut/Copy/Paste/🧹 Clear/Select-all) plus **Enter or the floating toolbar's
  yellow Save** to commit, Esc/✕ to cancel. The toolbar is the command locus
  even for entering text.

### Changed
- **Evidence-honesty pass on the README** (from the vetted July 2026 external
  improvement audit — see the new wiki page
  `Review-ImprovementAudit.md` for the full fact-check, per-item verdicts,
  and the Sprint B/C/D pseudocode blueprint). Claims now name their real
  mechanisms and citations: Vision Board "RAS programming" → goal-priming
  (Oettingen 2014); 10-Goals "subconscious" → retrieval practice (Roediger &
  Karpicke 2006); Pay-Yourself-First "refuses" labeled a pre-commitment
  device (Thaler & Benartzi 2004); All Seasons relabeled the simplified
  public Robbins mix, a fixed target allocation — not risk parity, not
  "Dalio's exact"; 5-4-3-2-1 labeled trade-book origin with an
  implementation-intention mechanism (Gollwitzer 1999); V2MOM attributed to
  Benioff/Salesforce. `lyceum/legibility.py` docstring adds the real
  specialized-font null results (Wery & Diliberto 2017; Kuster et al. 2017).
  Two citations in the source audit were found fabricated and kept OUT.
- **A− / A+ are real Buttons again (they were dead "empty plugs").** The
  road-marker **Canvas** version did not receive real clicks in the flow-layout
  toolbar — while the traffic-light **Buttons** in the same bar always did. A−/A+
  are now `tk.Button`s (styled as white/black sign plates), so clicking them
  reliably resizes the Study reading panes; the black/white toggle is preserved.
  A one-line breadcrumb log (`%LOCALAPPDATA%\SentinelForge\fontsize_debug.log`)
  records each click for on-machine verification.
- **README** corrected: test count `24 → 34`; entry-point and launcher names
  updated from the historical `book_reader.py` / `run_book_reader.bat` to the
  current `sentinel_personal_development.py` / `run_sentinel.bat`.
- **Study panels unified (Topics · Glossary · Commentary → Journal layout).**
  All three now follow the clean Journal anatomy — header → `[list | content]`
  → a single primary `+ Add/New` button. The multi-button rows and the
  paste-and-save boxes were removed; **Add / Remove route through the floating
  toolbar** (context-dispatched, with new `_glossary_remove_from_toolbar` /
  `_commentary_remove_from_toolbar` handlers), and secondary actions
  (Edit / Rename / Delete / Read / Import) moved to a **right-click menu** on
  the list. Reduces on-screen button count for a neurodivergent-first workflow.
- **Reading sliders.** Each Study read surface (Topics entries list, Glossary
  definition, Commentary pane) gained a **horizontal scrollbar** along the
  bottom so long lines can be slid into view and reviewed instead of clipping.

### Fixed
- **Study navigation lists no longer blow up with A− / A+.** The text-size
  control (`_apply_study_legibility`) was scaling the Topics/Glossary/Commentary
  index *lists* together with the reading text, so sizing up enlarged and
  **clipped the lists off-screen**. Scaling now applies only to the reading
  panes; the lists stay fixed and legible (matching the Journal list, which was
  already exempt — the reason it never exhibited the bug).
- **Delete-topic confirmation can no longer balloon off-screen.** When a topic
  title was a large pasted block (e.g. a whole AI reply), the confirm dialog
  grew until its Yes/No buttons left the visible area. It now shows a
  60-character single-line preview of the title.
- **Topics entries were unaddable/unreadable after the uniformity pass — fixed.**
  The Topics tab now has a **read/write pane** below the entries list: click an
  entry to READ its full text (word-wrapped, honoring your A−/A+ size),
  right-click to **paste** new content, and the **yellow toolbar Save** keeps it
  (blank lines split a paste into several entries; editing a loaded entry
  updates it in place, no duplicates).
- **Topics read/write pane: horizontal slider + working A−/A+.** The pane is now
  the canonical scrollable-Text widget (Text + vertical **and** horizontal
  scrollbars, `wrap=NONE`), so the **bottom bar slides a long line into view**.
  And `_apply_study_legibility` now includes this pane, so **A− / A+ actually
  resize it** (it had been left out of the resize list — the reason it appeared
  to "do nothing"). Selecting a topic now **auto-loads its most-recent entry
  into the pane**, so readable text is present to resize/slide immediately
  (before, the pane was cleared on select — the slider/resize acted on an empty
  pane and looked dead while the clipped entry list drew the eye). The pane also
  gets the larger share of the split for comfortable reading.
- **4 hardcoded window sizes removed** (Explain, Session End, Prompt Library,
  Add-to-topic) — routed through the screen-relative `_fit_dialog` helper. The
  Session-End dialog's `620x680` exceeded the owner's ~617 px effective height
  and clipped its bottom. Design-law linter **Rule B (hardcoded geometry) is now
  a hard test gate** so it can never regress.

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
