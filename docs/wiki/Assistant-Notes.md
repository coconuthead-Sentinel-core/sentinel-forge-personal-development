# Assistant Notes — self-maintained project state & instructions

> **Standing protocol (Shannon's order, 2026-07-11):** every time the
> README is shown or checked, the assistant must (1) open this page,
> (2) read ALL wiki notes, (3) execute any instructions left in §5
> below, (4) update this page — summary, V&V, TODO — and (5) mirror the
> repo to laptop + OneDrive + GitHub. This page is written BY the
> assistant FOR the assistant; Shannon may drop instructions into §5
> at any time.

_Last updated: 2026-07-12 (Study-panel uniformity + reading sliders; then DB-isolation guard, design-law linter, /sentinel-sprint skill) · updated by: Claude (Opus 4.8)_

---

## 1. Project summary (current state)

Sentinel Forge — Personal Development: v0.9 release-candidate, in the
**v1.0 close-out** ("stay the course" decision on record; the 2.0
Tauri re-platform is parked in `ROADMAP_2.0_GAMIFICATION.md`).
Architecture: functional core (`lyceum/`, headless-tested) /
imperative shell (single-file Tk app). Data: SQLite with atomic
`transaction()`, additive-only migrations, live DB in %LOCALAPPDATA%
with OneDrive snapshots.

Shipped on the RC track (July 2026): FSRS memory training (Sprints
1+2 per RELAY-SRS-001 — engine + 🧠 Review window + Scoreboard
wiring), AI-chat context sources (🌐 web / ☁ OneDrive / 📎 attachments
incl. Excel), 📄 real Word/Excel document drafting, 🐢/🐇 read-speed
control, Library archive-not-delete workflow (bulk + per-file),
Library-as-study-hub tab buttons, validated Prompt-Library ➕ Add,
floating-toolbar dock targets + ❓ tour, review-readiness repo hygiene
+ wiki refresh + white-paper skeleton.

Sibling proof (separate repos, deliberate ports not imports): Imprint
v1.1 and strata-console v1.1 — one assistant design, three shipped
dashboards.

## 2. Verification status (did we build it right?)

- **312 automated tests, all green** (headless; temp DBs; injectable
  clocks; proven review-log atomicity; deterministic FSRS).
- UI flows verified by headless smoke scripts under a REAL
  `mainloop()` (worker `after()` delivery silently fails without one —
  learned twice, now standard practice).
- Three-way mirror verified by commit hash `860e80e2c19b` and
  byte-identical README fingerprints across GitHub / OneDrive clone /
  laptop install / session worktree (2026-07-11 check).
- Single `main` branch per repo; work branches are created per session
  and deleted after merge (standing order).

## 3. Validation status (did we build the right thing?)

- Owner uses the app daily (reading, study, money tools); defects he
  reports are reproduced headlessly, fixed, and regression-noted in
  `Former-Bugs-and-Regressions.md` (July batch: orphaned saves, silent
  audio, constructor-tuple crashes — all fixed).
- Library repurposed for Coursera study (his real Module-4 prep) —
  the archive workflow and study-hub buttons came from that live need.
- Open validation risk: n=1 user; mitigations documented in the
  white-paper outline's threats-to-validity section.

## 4. TODO — v1.0 close-out (in order)

1. 🔲 **Tagging UI** for the excerpt `tags: []` field (schema ready;
   README roadmap item).
2. 🔲 **README v1.0 pass**: version bump v0.9 → v1.0, add screenshots /
   demo GIF, feature-status table (implemented vs planned).
3. 🔲 **Declare descopes** in the README: macOS/Linux ports and
   platform two-way sync are OUT of v1.0 (deliberate).
4. 🔲 **Bug-shakeout period**: Shannon's daily use for ~2 weeks; fix
   what he reports; keep suite green.
5. 🔲 **Stamp v1.0** + portfolio entry (résumé bullet + demo loop).
6. 🔲 White paper: flesh outline §3 (Requirements & Design Laws) first,
   then §4, §6 — one section per sitting, notes keep dripping.
7. 🔲 Backlog (post-1.0): voice-note recording; FSRS parameter tuning
   after ~1,000 logged reviews; Scoreboard flashcard lead-measure
   auto-claims a slot when one frees up (already coded, waits
   politely); 2.0 game engine per the 90-day plan.

## 5. Instructions queue (execute on every README check, then mark done)

- ✅ 2026-07-11 — Create this page, seed summary/V&V/TODO, index it,
  mirror to laptop + OneDrive. *(done — this commit)*
- ✅ 2026-07-11 — Standing: append 1–3 sentences to
  `Whitepaper-Notes.md` on every README/docs touch. *(active habit)*
- ✅ 2026-07-11 (late) — Create Rebuild-Blueprint.md (house-plans pseudocode seed file for full reconstruction). *(done)*
- ✅ 2026-07-11 (late) — Fill the Codex engineering template pack for this project -> docs/rebuild-pack/ (8 documents; Codex source left blank per its policy). *(done)*
- ✅ 2026-07-12 — Knowledge Harvester approved ("build it in sprints") and shipped: Sprint 1 lyceum/harvest.py + 10 tests; Sprint 2 Library 🧠 Harvest terms button + preview-approve window. Suite 182. *(done)*
- ✅ 2026-07-12 — Commentary tab rebuilt as a Glossary-style structured store (commentaries table, search/list/read-pane/Add/Edit/Delete/Import); window-fit sweep (11 dialogs). *(done)*
- ✅ 2026-07-12 — Excel 365 Bible reviewed → formula engine BUILT (lyceum/formula.py, tokenizer/parser/evaluator) + wired into doc_writer (compute_totals). Sprint 1: 23 tests; Sprint 2: 4 tests + runtime proof. Suite 215. *(done)*
- ✅ 2026-07-12 — Word 2010 book reviewed → readability engine BUILT (lyceum/readability.py, Flesch-Kincaid + syllable kernel) + wired into excerpt save (front-matter reading_grade/label + status badge). Sprint 1: 15 tests; Sprint 2: runtime proof. Suite 230. *(done)*
- ✅ 2026-07-12 — Copilot book reviewed → Prompt Coach BUILT (lyceum/prompt_coach.py, rubric analyzer) + wired live under AI Chat input (score/band/tip + ✨ Improve button). Sprint 1: 18 tests; Sprint 2: runtime proof. Suite 248. *(done)*
- ✅ 2026-07-12 — Power Automate reviewed → ECA rule engine BUILT (lyceum/automation.py, pure decision engine) + wired to focus_completed (human-in-the-loop suggestion). Sprint 1: 17 tests; Sprint 2: runtime proof. Suite 265. *(done)*
- ✅ 2026-07-12 — M365 cert books reviewed → Shannon-entropy strength BUILT (lyceum/password_strength.py) + 🔒 Password Strength utility (live, local, private). Sprint 1: 15 tests; Sprint 2: runtime proof. Suite 280. *(done)*
- ✅ 2026-07-12 — Study-tab paste-and-save + 🔊 Read on all three panels
  (Topics, Commentary, Glossary): lyceum/entry_parse.py (parse_glossary /
  split_title_body, 18 tests) + paste boxes, 💾 Save, and shared
  _study_read_pane reusing the floating-toolbar highlight/speak engine.
  Suite 298. *(done)*
- ✅ 2026-07-12 — Accessibility pass on the Study panels: lyceum/legibility.py
  (pure preset→spec kernel, 14 tests) + floating-toolbar A− / A+ / Format ▾
  (OpenDyslexic / ADHD focus / Dysgraphia / Dyslexia presets) applied live
  to Topics/Commentary/Glossary panes + persisted; _FlowFrame wrapping
  container fixes the clipped tab bar + docked toolbar (Minimize/Undock/
  rightmost tabs were unreachable). 3 proofs (kernel 14, no-clip measure,
  live-apply 15). Suite 312. *(done)*
- ⚠️ 2026-07-12 — Housekeeping: earlier headless smoke scripts connected to
  the LIVE study.db (they set DB_PATH but study data lives in
  lyceum.db.study_db.STUDY_DB). Test rows (ZZ Smoke Topic, Chapter 1,
  Entropy/Heap/Stack glossary, Romans 8 commentary, "First note here"
  entries) leaked into the real DB and were surgically removed (backup in
  session scratchpad). Smoke scripts now monkeypatch STUDY_DB to a temp
  path. LESSON: always redirect BOTH DB_PATH and study_db.STUDY_DB in
  headless tests.
- ✅ 2026-07-12 — Study-panel uniformity + reading sliders. Re-cut
  Topics/Glossary/Commentary to the Journal layout (header → `list | content`
  → one primary button); removed in-panel button rows + paste boxes; Add/Remove
  via the floating toolbar (added `_glossary/_commentary_remove_from_toolbar`);
  secondary actions on a right-click menu; horizontal reading slider on all
  three read surfaces. Fixed two display bugs — A−/A+ was scaling the nav lists
  (Topics index clipped off-screen); delete-topic confirm ballooned on a huge
  pasted title (now a 60-char preview). Suite 312. *(done)*
- ✅ 2026-07-12 — Tooling sprint: (1) **live-DB pollution guard**
  (`db_location.assert_not_live_db`/`is_live_db` + `study_db.temp_study_db()`)
  makes the twice-seen live-DB leak a loud failure; (2) **design-law linter**
  (`lyceum/lint_designlaws.py`, AST) — Rule A (constructor tuple pad) gated at
  zero, Rule B (hardcoded geometry) advisory; (3) **/sentinel-sprint** skill
  formalizes the build pipeline. +13 tests (325 total). *(done)*
- ⚠️ 2026-07-12 — Linter's first catch: **4 hardcoded `.geometry("WxH")`**
  (lines ~2876, 12489, 15856, 16659). `620x680` exceeds the owner's ~617px
  effective height → likely clipped. NEXT: size these 4 dialogs from
  `winfo_screenwidth/height`, then promote Rule B to a hard gate.
- ✅ 2026-07-12 — Acted on the linter's finding: all 4 hardcoded
  `.geometry("WxH")` calls (Explain, Session End, Prompt Library, Add-to-topic)
  now route through `_fit_dialog` (screen-relative, centered, clamped). The
  Session-End `620x680` was clipping the owner's ~617px height. **Rule B
  promoted to a hard test gate** (linter now enforces zero A and zero B).
  Suite 326. *(done)*
- ✅ 2026-07-12 — Floating toolbar: **traffic-light action group** (green ➕ Add
  · yellow 💾 Save · red ➖ Remove) + **universal `_ftb_action_save`**
  context-dispatch (journal → notes → active "💾 Save" button → Ctrl+S), works
  in every panel incl. Topics/Glossary/Commentary (commits their Add/Edit box).
  **A−/A+ recast as one black/white toggle** (last-pressed white, other black;
  re-applied on dock/undock). Launch smoke-tested — no init errors. Suite 326.
  *(done)*
- ✅ 2026-07-12 — Toolbar cluster refined to Shannon's spec: traffic light now
  shows the WORD above each lamp (Add/green · Save/yellow · Delete/red — red
  relabeled from "Remove"); A−/A+ redrawn as road-marker canvas plates forming
  the black/white toggle (new helpers `_round_rect` + `_ftb_make_font_marker`).
  Pseudocode captured in `Rebuild-Blueprint.md` §10 (per "pseudocode as clone
  documents"). Launch smoke-tested — canvas cluster builds clean; suite 326.
  ⚠️ Appearance NOT visually verified (app runs under Python, which is on the
  Computer-Use deny list, so no screenshot) — Shannon to eyeball and request
  tweaks (shape/size/shade). *(done)*
- ✅ 2026-07-12 — Toolbar-driven inputs rolled out (Shannon verified the pilot,
  said "roll it out"). New `_prompt_inline` (non-modal; right-click
  Cut/Copy/Paste/Clear/Select-all; Enter or yellow Save commits; Esc/✕ cancels)
  replaces modal `_prompt_for_text` at ALL call sites — New topic, Rename topic,
  Rename bookmark, Glossary Look-up. `_ftb_action_save` commits an open inline
  box first (`_ftb_inline_input`). README bumped **280→326** + toolbar / panel
  / guardrails features + roadmap ticks. Local scratch (`test_dpi.py`,
  `test_sd.py`) cleared. Suite 326. *(done)*
- ✅ 2026-07-12 — Topics regression fixed (Shannon: "you should be able to read
  the text within that section"). The uniformity pass had removed the
  paste-and-save box, leaving NO way to add or read entry text. Restored as a
  toolbar-driven **read/write pane** below the entries list (`_topic_compose`):
  click an entry → loads full text to read (accessibility font honored);
  right-click paste; yellow Save → `_topics_save_from_toolbar` INSERTs
  (blank-line split) or UPDATEs the loaded entry, then reloads so it stays
  readable and re-Save can't duplicate. New: `_on_topic_selected`,
  `_load_topic_entry_into_pane`, `_topic_compose_clear`,
  `_select_topic_entry_by_id`. Suite 326. *(done)*
- (empty — Shannon or the assistant may append instructions here; the
  next README check executes them)

## 6. Notes to future self

- The copy Shannon RUNS is `Desktop\Sentinel-Forge` — after every
  push, pull there, or he sees stale code.
- His scoreboard slots are full with his own measures — never evict.
- Grep for swallowed exceptions FIRST when "X doesn't work."
- Check `voice_debug.log` for anything voice-related.
- Read `Working-With-The-Architect.md` before communicating anything
  complicated; dignity-first, outcome-first, one question max.
