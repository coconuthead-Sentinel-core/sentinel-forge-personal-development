# Changelog

All notable changes to **Sentinel Forge — Personal Development** are documented
here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project aims to follow [Semantic Versioning](https://semver.org/).

> History before this file was reconstructed from the Git log; dates are the
> commit dates. The project is on the **v0.9 release-candidate track** (a feature
> freeze + stabilization phase — see `docs/SDLC_STATUS.md`).

## [Unreleased]

### Fixed
- **Read-aloud garbled backtick code spans — now atomic.** The normalizer ran
  its English rules over inline code, so `` `1024` `` was read as the year
  "ten twenty-four" and abbreviation replacement could corrupt tokens inside
  paths. Code spans are now exempt from ALL linguistic expansion and use a
  minimal code-reading form instead (`_` → "underscore", `/` → "slash",
  everything else verbatim) — standard TTS text-analysis practice (Sproat
  et al. 2001; Jurafsky & Martin). Externally proposed; **verified against
  the real code first** — the report's specific mechanism (slash/underscore/
  extension expansion rules) did not exist here, but the underlying defect
  and fix direction were real. +6 tests.
- **A− / A+ looked like "nonfunctional plugs" — they were working invisibly.**
  The breadcrumb log proved every click fired (16→32pt), but only three
  surfaces scaled (Glossary / Commentary / Topics pane) — a user watching
  Study Notes or the Journal saw nothing move, and the size silently pinned
  at the 32pt ceiling. Fix: **Study Notes editor and Journal body now scale
  too** (all five prose surfaces move together; navigation lists stay
  fixed), tour text updated, and the stuck persisted size was reset.

### Added
- **`scope-first` skill — the fourth permanent guardrail** (owner's order,
  2026-07-13): no code until a four-part scope statement (in-scope,
  explicit OUT-of-scope, acceptance criteria, lifecycle target) and a
  blueprint exist at project onset; scope changes are explicit logged
  decisions, never drift ("churn code" is the named failure mode).
  Anchored to ISO/IEC/IEEE 12207, SWEBOK, IEEE 29148, and Boehm's
  cost-of-change (1981). Installed project-level and user-level. Per the
  skill's own retroactive clause, this project's baseline was written:
  **`docs/SCOPE.md`** — including the 5–10-year lifecycle target, the
  stdlib-first stack rationale, and the named structural risk (single-file
  Tk shell) with its documented decomposition seam.
- **🧾 Bill Sentinel (Sprint F — the owner's own ask)** — prospective-memory
  scaffolding for bills. Pure kernel `lyceum/bills.py` (`next_due` with
  month-end clamping, `classify`, `next_action`) + a Money-hub card and
  window: every bill shows 🟢 automated / quiet / 🟡 due soon / 🔴 overdue,
  and ONE next-action line leads the panel (first red, else first amber,
  else "set up autopay for …"). Actions: add, mark paid, autopay toggle,
  send an amber/red bill to today's planner, archive (never delete). The
  goal state is every bill green (autopay) so the app goes quiet —
  automation and defaults beat remembering (Thaler & Benartzi 2004);
  the panel says plainly that the app cannot pay bills. Additive `bills`
  table; 17 tests incl. February clamping and next-action priority.
  Design decision (reconciled from the blueprint): a bill with no payment
  history is never called "overdue" — no evidence a cycle was missed.
- **V2MOM if-then line (Sprint D)** — the goal intake gains one **optional**
  field under Obstacles: *"If <your obstacle> happens, then I will …"*
  (implementation intentions roughly double follow-through — Gollwitzer &
  Sheeran 2006, meta-analytic d≈0.65). Stored in an **additive**
  `v2mom_goals.if_then` column (old tables migrate in place, data intact);
  the required fields are unchanged — the flow is not stiffened. 3 tests.
- **WCAG contrast kernel (Sprint C)** — `lyceum/wcag.py`: the W3C
  relative-luminance and contrast-ratio formulas with the AA thresholds
  (4.5:1 normal / 3:1 large) and an `audit_pairs` findings helper; 9 tests
  anchored to published W3C values. First palette audit: **all reading
  pairs pass AA (5.7–17.1)**; four white-label button colors fall short of
  AA-normal and are logged as **findings with proposed same-hue
  replacements** in `Assistant-Notes.md` §5 — the owner decides; nothing
  was recolored.
- **Two-lapse streak protocol (Sprint B)** — `lyceum/streaks.py`, a pure
  kernel behind the 📅 Never Miss Twice banner. ONE missed day is now an
  **amber rest-day encouragement** ("a rest day, not a broken chain" —
  self-compassion speeds lapse recovery, Neff 2003); only a **second
  consecutive miss** escalates to the **red fresh-start prompt** that asks
  for an exact time (fresh-start effect, Dai/Milkman/Riis 2014;
  implementation intentions, Gollwitzer & Sheeran 2006). Previously the
  banner went red on ANY yesterday-miss. 9 tests incl. a shame-free-language
  gate on the amber message.
- **`learning-science` skill** (`.claude/skills/learning-science/`) — the
  third permanent guardrail, from the vetted middle ground of the external
  framework proposal: study/review features and teaching use only
  techniques with real empirical support — retrieval practice (Roediger &
  Karpicke 2006; Dunlosky et al. 2013), spacing via FSRS (Cepeda et al.
  2006), worked examples with fading (Atkinson et al. 2000), expertise
  reversal (Kalyuga et al. 2003), delayed judgment-of-learning (Nelson &
  Narens 1990) — and known neuromyths are blocked with their debunking
  citations (learning-styles matching, Pashler et al. 2008; the
  10,000-hour rule, Macnamara et al. 2014). Includes the
  access-vs-efficacy distinction: accommodations are legitimate as access
  and are never claimed as learning outcomes. Handoff §6 now mirrors all
  THREE skills and specifies the no-drift fallback (bootstrap prompts are
  generated verbatim from the SKILL.md files, never re-summarized).
- **Interview-ownership framing in Job Readiness** — the Story and
  Interview pillar next-steps now teach defensible ownership language
  ("I built…", "I implemented…", answers in situation → action → result
  form) so practice matches what a candidate must say in the room.
  Adopted from the same proposal's career guardrail; the rejected parts
  (paste-in charters, per-session bootstrap prompts as the primary
  mechanism) are on the record in the session notes.
- **Permanent guardrail skills** — `.claude/skills/clinical-science-gate/`
  (the Strict Clinical Science 2026 evidence admission rule: verify every
  citation, label by evidence tier, no clinical claims) and
  `.claude/skills/classroom-code/` (textbook-CS SDLC in order, pseudocode
  first, tests before UI, functional code only, honest reporting). Written
  project-agnostic — Shannon's standing rules for ALL projects. The desktop
  handoff (§6) instructs the desktop assistant to install them as
  user-level mirror skills so they load everywhere.
- **Handoff memo** (`docs/HANDOFF_MEMO_2026-07-13.md`) — the state-of-the-
  world accounting: what merged in PR #50, and the six open items that only
  the desktop machine can finish (branch delete, both mirrors, mirror
  skills, dead-button audit, sprint queue, vetting the ~202 research files).
- **Desktop-assistant handoff** (`docs/DESKTOP_ASSISTANT_HANDOFF.md`) — the
  third reference, distilled from the vetted improvement audit and the
  2026-07-13 neurodivergence-research check-in: the "Strict Clinical Science
  2026" admission rule, the sprint queue in pseudocode (two-lapse streak
  protocol, WCAG contrast gate, V2MOM if-then line, **Bill Sentinel** —
  prospective-memory scaffolding for bills), the per-sprint paperwork duty,
  and the real-hardware dead-button audit. README now opens with the
  guardrails and points the desktop assistant at it.

### Removed
- Dead code: `_round_rect` / `_ftb_make_font_marker` (the Canvas road-marker
  A−/A+ that never received clicks; reverted to Buttons on 2026-07-12 and
  left as dead code since). Pseudocode preserved in `Rebuild-Blueprint.md` §10.
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
