# Assistant Notes — self-maintained project state & instructions

> **Standing protocol (Shannon's order, 2026-07-11):** every time the
> README is shown or checked, the assistant must (1) open this page,
> (2) read ALL wiki notes, (3) execute any instructions left in §5
> below, (4) update this page — summary, V&V, TODO — and (5) mirror the
> repo to laptop + OneDrive + GitHub. This page is written BY the
> assistant FOR the assistant; Shannon may drop instructions into §5
> at any time.

_Last updated: 2026-07-13 (💼 Job Readiness audit — six-pillar real-world job self-examination, kernel + Planning-hub window) · updated by: Claude_

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
- ✅ 2026-07-12 — Topics read/write pane: two fixes Shannon reported. (1) The
  pane is now the canonical scrollable Text (Text + vertical + **horizontal**
  scrollbars, `wrap=NONE`) so the **bottom bar slides long lines into view**;
  given the larger split share. (2) `_apply_study_legibility` was missing
  `_topic_compose`, so **A−/A+ never resized it** — added (font+spacing, wrap
  kept NONE). Textbook scrollable-text pattern. Suite 326. *(done)*
- ✅ 2026-07-12 — Topics "A−/A+ and slider don't work" — root-caused by HEADLESS
  PROBE (scratchpad/probe_*.py), not by eyeballing. Proof: `_topic_compose` IS a
  Text(wrap=none) with BOTH scrollbars, and a simulated A+ canvas click DID
  resize it (16→18→20→22). The real gap: `_on_topic_selected` CLEARED the pane,
  so A−/A+ resized an EMPTY pane and the slider had nothing to scroll while the
  user looked at the clipped entry LIST above. Fix: `_on_topic_selected` now
  AUTO-LOADS the most-recent entry into the pane, so readable text is present to
  resize/slide immediately. Verified end-to-end headlessly. LESSON: a launch
  smoke that never OPENS the study workspace never builds the tab — probe the
  actual widget tree. Suite 326. *(done)*
- ✅ 2026-07-12 — A−/A+ "empty plugs" root cause: the road-marker **Canvas**
  version didn't receive real clicks in the `_FlowFrame` toolbar, while the
  traffic-light **Buttons** in the same bar always did (differential evidence).
  Reverted A−/A+ to `tk.Button` (styled white/black plates); `.invoke()` probe
  confirms resize (18→20→22→20) + toggle. Added a breadcrumb log
  (`%LOCALAPPDATA%\SentinelForge\fontsize_debug.log`) so a future "nothing
  happens" report is verifiable on-machine, not guessed. `_ftb_make_font_marker`
  / `_round_rect` left as dead code. Suite 326. *(done)*
- ✅ 2026-07-13 — Shannon's ask ("what's gonna be real world for a human to get
  a real world job? … additive, no teardown") → **💼 Job Readiness audit**
  BUILT via /sentinel-sprint. Pure kernel `lyceum/job_readiness.py` (six
  pillars: Story/Proof/Skills/People/Pipeline/Interview, 0–4 rubric each;
  `readiness` → pct+band+badge, `next_moves` weakest-first with foundational
  tie-break, `compare` deltas, tolerant encode/decode). Additive
  `job_readiness_checks` table (UNIQUE check_date; same-day save REPLACES —
  one honest look per day; never deleted). Shell: `open_job_readiness` in the
  Planning hub (💼 Job Ready, ACCENT_EMERALD) — live meter canvas + band
  badge, rubric text follows each slider, "👉 Next move" line, save shows
  delta vs previous check, sliders prefill from last check. Sprint 1: 15
  tests incl. temp_study_db round-trip; Sprint 2: xvfb mainloop smoke
  (open → slide → save → resave-replaces → reopen-prefills). Suite 341.
  Design-law linter green. *(done)*
- ✅ 2026-07-13 — External improvement audit vetted (see
  `Review-ImprovementAudit.md`): citations fact-checked (2 fabricated, kept
  out), premises checked against the real code (2 false), per-item verdicts
  recorded. **Sprint A shipped**: README evidence-honesty pass (RAS →
  goal-priming; subconscious → retrieval practice; savings-refusal →
  pre-commitment; All Seasons → honest "fixed target allocation, simplified
  public mix"; 5-4-3-2-1 → trade-book + implementation-intention mechanism;
  V2MOM → Benioff attribution) + legibility.py real font-null-result
  citations. *(done)*
- ⏳ 2026-07-13 — QUEUED from the vetted audit (pseudocode ready in
  `Review-ImprovementAudit.md` §4; run each as a /sentinel-sprint):
  **Sprint B** two-lapse streak protocol (`lyceum/streaks.py`: first miss =
  amber self-compassion, second consecutive = red fresh-start prompt; wire
  into the Never-Miss-Twice banner). **Sprint C** WCAG contrast kernel
  (`lyceum/wcag.py`) + palette AA test gate — probe the current palette
  FIRST and show Shannon any failing pair before recoloring anything.
  **Sprint D** V2MOM "If ⟨obstacle⟩, then I will ⟨action⟩" field (additive
  column; encouraged, not required). Sprint E (inverse-volatility All
  Seasons view) is PARKED unless Shannon asks.
- ✅ 2026-07-13 — Shannon's consolidation order executed: (1) dead code
  removed (`_round_rect`/`_ftb_make_font_marker`); no empty/stub files
  found; (2) **`docs/DESKTOP_ASSISTANT_HANDOFF.md` created** — the third
  reference distilled from Review-ImprovementAudit.md + the check-in
  review, carrying the "Strict Clinical Science 2026" admission rule, the
  sprint queue (B streaks / C WCAG / D if-then / **F Bill Sentinel**, all
  in pseudocode), paperwork duties, and the real-hardware dead-button
  audit; (3) README opens with the desktop-assistant guardrails;
  (4) everything merged to `main`, session branch deleted. OneDrive +
  Desktop mirrors are the DESKTOP assistant's first mechanical step (cloud
  session cannot reach them). *(done)*
- ⏳ 2026-07-13 — FOR THE DESKTOP ASSISTANT: follow
  `docs/DESKTOP_ASSISTANT_HANDOFF.md` §2 — re-derive each queued sprint in
  your own pseudocode BEFORE coding, then B → C → D → F through the full
  /sentinel-sprint pipeline; §4 dead-button audit on real hardware
  (Shannon reports non-working buttons — find, log here, fix). Mirror both
  clones after every merge.
- ✅ 2026-07-13 (later) — Shannon's guardrails made PERMANENT as skills:
  `.claude/skills/clinical-science-gate/` (evidence admission rule) +
  `.claude/skills/classroom-code/` (textbook-CS/functional-code rule),
  project-agnostic by design. `docs/HANDOFF_MEMO_2026-07-13.md` created
  from the session accounting; handoff §6 added — the desktop assistant
  must install BOTH as user-level mirror skills (all projects) before any
  other work. *(done)*
- ✅ 2026-07-13 (evening) — External "Guardrail Framework" proposal
  reviewed at Shannon's request (planning first, no action), then the
  approved middle ground built verbatim: (1) **`learning-science` skill**
  — third permanent guardrail; admitted techniques with verified canonical
  citations (Kalyuga 2003 and Macnamara 2014 re-verified by search this
  session), neuromyths blocked, access-vs-efficacy distinction encoded;
  (2) **Job Readiness Story/Interview steps** now teach ownership language
  + STAR framing (kernel text only; rubric-shape tests unchanged, suite
  339 green); (3) handoff §6 mirrors all three skills + verbatim-
  concatenation fallback for surfaces without skills (single source of
  truth, no drift); README guardrail #4 added. REJECTED from the
  proposal, on the record: paste-in charters / per-session bootstrap
  prompts as the primary mechanism (prospective-memory burden — skills
  load automatically), six vague guardrails over three enforceable ones,
  and unverifiable claims ("interview-safe", "Microsoft's expectations").
  *(done)*
- ✅ 2026-07-13 — Desktop pickup of the cloud handoff. PR #52 (memo) merged
  (CI green both Pythons); session branch `claude/…-j10gax` confirmed deleted;
  all three copies at parity; **three guardrail skills mirrored user-level**
  (`~/.claude/skills/`: clinical-science-gate, classroom-code,
  learning-science) and confirmed loading. **Dead-button audit (headless
  half): 0 Buttons without a command or click binding** across the dashboard
  + study workspace (static probe); real-display half awaits Shannon's
  reports. *(done)*
- ✅ 2026-07-13 — **Sprint B shipped**: two-lapse streak protocol.
  `lyceum/streaks.py` (classify_lapse + lapse_message) + 9 tests incl. a
  shame-free-language gate; Never-Miss-Twice banner rewired (one miss →
  AMBER encouragement; two consecutive → RED fresh-start + exact-time ask).
  Pseudocode re-derived per classroom-code before building; smoke probe
  showed the live RED banner on a seeded two-miss habit. Suite **350**.
  *(done)*
- ✅ 2026-07-13 — **Sprint C shipped**: WCAG contrast kernel.
  `lyceum/wcag.py` (W3C relative-luminance + contrast-ratio + AA
  thresholds + `audit_pairs`) + 9 tests anchored to W3C values
  (b/w=21.0, the #767676/#777777 AA boundary). Palette audited.
  **FINDINGS for Shannon (his call — no silent recolor):** every READING
  pair passes AA comfortably (5.7–17.1); four white-label BUTTON colors
  fail AA-normal: ACCENT_GREEN #16a34a (3.30 → propose **#15803d**),
  ACCENT_CYAN #0891b2 (3.68 → **#0e7490**), ACCENT_MIC #0ea5e9
  (2.77 → **#0369a1**), ACCENT_AMBER #d97706 (3.19 → **#b45309**).
  All proposals keep the hue, just darker. Suite **359**. *(done)*
- ✅ 2026-07-13 — **Sprint D shipped**: V2MOM if-then line. Additive
  `v2mom_goals.if_then` column (PRAGMA-guarded ALTER, old rows intact) +
  one OPTIONAL field under Obstacles in the intake ("If <obstacle> happens,
  then I will …"); required fields unchanged. Deviation from blueprint
  noted per classroom-code: used the window's `_field` ScrolledText idiom
  (with the mic hook) instead of a bare Entry — house style. 3 tests
  (old-schema migration, round-trip, optionality). Suite **362**. *(done)*
- ✅ 2026-07-13 — **Sprint F shipped**: 🧾 Bill Sentinel. Kernel
  `lyceum/bills.py` (month-end-clamped `next_due`, `classify`,
  `next_action`) + additive `bills` table + Money-hub card + window (one
  next-action line, add/mark-paid/autopay-toggle/to-planner/archive,
  honesty line "this app cannot pay bills"). 17 tests; smoke probe showed
  RED-first prioritization live. Reconciled decision vs blueprint: no
  payment history ⇒ never "overdue" (no evidence of a missed cycle).
  **Deferred, explicitly:** wiring manual bills into the appointments
  T-60/-30/-15 machinery — that machinery is time-of-day based and bills
  have only a due DAY; the planner feed (user-in-the-loop "📅 To planner")
  covers the cue instead. Revisit if Shannon wants timed reminders.
  Suite **379**. *(done)*
- ✅ 2026-07-13 — **`scope-first` skill built and installed** (Shannon's
  order: "you gotta have a blueprint" — anti-churn guardrail #4). Rule: at
  project onset, WHILE paperwork is being filled out, a four-part scope
  statement (in / explicit OUT / acceptance criteria / lifecycle target) +
  blueprint must exist before any code; scope changes = explicit logged
  one-liners here in §5. Installed to `.claude/skills/scope-first/` and
  user-level. Retroactive clause executed: **`docs/SCOPE.md`** baselines
  THIS project (5–10-yr lifecycle, stdlib-first stack rationale, named
  structural risk + seam). README guardrail #5 added. Docs-only change;
  suite re-run green. *(done)*
- ✅ 2026-07-13 — A−/A+ "dead plugs" report RESOLVED by the breadcrumb log
  (fontsize_debug.log): every click fired, 16→32pt, pane font really
  changed — but only Glossary/Commentary/Topics-pane scaled, so watching
  Study Notes/Journal showed nothing (invisible success = broken), and the
  size pinned at the 32pt ceiling. Fix: `_study_notes_widget` +
  `_journal_body` added to `_apply_study_legibility` (5 prose surfaces
  scale together; lists stay fixed); tour updated; persisted size reset
  28→16. LESSON: a scaling control must visibly affect the surface the
  user is LOOKING AT, or scope the control to the active tab. *(done)*
- ✅ 2026-07-13 — TTS code-span patch (external proposal, VERIFIED before
  applying): the report claimed our normalizer expands `/`, `_`, and file
  extensions — those rules do NOT exist in `text_norm.py` (diagnosis of
  someone else's pipeline). What WAS real: English rules ran over backtick
  spans (`1024` → "ten twenty-four" via the year rule; plain-replace
  abbreviations could corrupt path tokens). Fix: `_CODE_SPAN` split; code
  spans exempt from all expansion, minimal code-reading form (underscore/
  slash named). Citation check: Sproat 2001 + Jurafsky & Martin real; the
  proposal's "WCAG 2.2 non-visual readability guidelines" is not a real
  section name. +6 tests (21 in module). Suite **385**. *(done)*
- ✅ 2026-07-13 — **Shop Log established** (`docs/SHOP_LOG.md`): a daily
  open/close engineering logbook with both parties' input + signoff,
  adapted from the Codex `08_BUILD_EVIDENCE_AND_SIGNOFF_CHECKLIST` per the
  Template Library Policy (filled copies live in the PROJECT, never the
  Codex). Vetted as academically correct (engineering-notebook practice;
  ISO/IEC/IEEE 12207 records-keeping). HONEST FINDING: the Paperwork
  folder contains NO daily-session template — the signoff checklist is the
  closest ancestor; the daily cadence was created here, in-project.
  First close-of-session entry written for 2026-07-13. Standing duty: the
  engineer writes a close entry each working session. *(done)*
- ✅ 2026-07-16 — NotebookLM BrainTrust review (262-file "Google stamp"
  gamification transcript) gated through clinical-science + learning-science:
  one of four proposals cleared on the first pass → **Reward-Draw BUILT**
  (`lyceum/reward_engine.py`: variable-ratio 70/25/5, 12-draw pity
  guarantee, named-source honesty gate, no-work-no-reward, append-only
  `reward_log`) + wired to `focus_completed` (quiet dot / library quote
  card / rare gold flash + chime). Rejected from the same transcript:
  "85% of happiness" (no source), "top 1% fitness" (real guideline is WHO
  150–300 min/wk), auto-email accountability (needs consent design).
  Sprint: 15 tests + mainloop smoke; suite **400**. README count fixed
  379→400. Owner laptop test PENDING before merge to main + mirror. *(this
  session)*
- ✅ 2026-07-16 (later) — NotebookLM "Superlearning Audio Engine" proposal
  gated: Lozanov/hemisphere-sync framing REJECTED (neuromyth; never
  replicated), subliminal-tape lineage REJECTED (debunked), simultaneous
  duplicate-voice "hear it twice" REJECTED (stream interference) →
  **Ambience BUILT instead** (`lyceum/ambience.py`: pure synthesis of
  wind/rain/ocean/binaural seamless loops + AmbiencePlayer on
  sounddevice, its own stream, mixes WITH the voice) + 🌧 Library button
  with chooser (Quiet/Medium; claims rendered verbatim from KINDS;
  binaural labeled "NOT proven to improve learning — needs headphones").
  10 tests incl. label-honesty tests; mainloop smoke (chooser + graceful
  degrade proven; REAL audio-out could not be verified on this bench —
  no sounddevice in the worktree python — verify on the laptop, where
  dictation already uses it). Suite **410**; README 400→410. Queued
  honest follow-up: Audio Review Track (export WAV, question→pause→
  answer retrieval format) — boarded, not yet built. *(this session)*
- ✅ 2026-07-16 (QA) — Shannon, as human-in-the-loop QA, found the AAR
  window outside the floating-toolbar dispatch → wired in the house
  pattern (`_review_context_active` + 3 handlers + 3 chain lines +
  window hooks). Delete obeys the archive law (today's draft only; past
  days refused). Smoke 6/6 under mainloop w/ temp DB; suite 410 green;
  no new unit tests (wiring-only; runtime proof is the smoke). *(this
  session)*
- ✅ 2026-07-20 (QA) — Shannon field-tested the Prompt Library by filing
  a real job-search exchange: yellow Save had NO handler in the dispatch
  chain, red Delete hard-deleted (archive-law violation), and the bar
  wasn't there on open. Repair: `lyceum/prompt_archive.py` kernel
  (Markdown render + Windows-safe filenames), `archived_at` additive
  migration (NULL = active), `_prompt_lib_save_from_toolbar` in the Save
  chain, Delete → archive (file written FIRST, row tombstoned second,
  .md lands in "Prompt Archive" beside Books = OneDrive-backed), auto-
  dock-on-open, tour cards updated. 12 tests on temp DB; suite 422
  green; smoke 5/5 under a real mainloop. Pseudocode boarded + filed in
  the commit message. *(this session)*
- ✅ 2026-07-21 (QA sweep, cont.) — three more owner finds, same
  invisible-success class, all breadcrumb-diagnosed and shipped same-day:
  ⏱ Time Check outside the dispatch chain (dock slot + Save/Enter commit
  + "✏ note saved" on its face); 🎤 mic never enrolled in Prompt Library
  Title/Prompt/Response + Time Check note (4 FocusIn enrollments); 🔡
  A−/A+ never enrolled Prompt Library boxes (legibility loop + open at
  persisted size + prompt_lib breadcrumb field). Smokes 9/9, 5/5, 5/5;
  suite 422 green throughout; shared time_log now carries both parties'
  punches. *(this session)*
- (empty — Shannon or the assistant may append instructions here; the
  next README check executes them)

## 6. Notes to future self

- **Breadcrumb-first debugging is standing practice (Shannon's order,
  2026-07-13).** When a control or output "doesn't work" on his screen,
  the FIRST move is to read (or add) a breadcrumb log at the seam, then
  diagnose from recorded facts — never guess-and-patch. Existing
  breadcrumbs: `voice_debug.log` (every voice change / read-aloud /
  TTS subprocess + `tts-norm:` before→after normalization lines) and
  `fontsize_debug.log` (every A−/A+ click with sizes) — both in
  `%LOCALAPPDATA%\SentinelForge\`. This method solved the A−/A+ case in
  one file read. New user-facing pathways get a breadcrumb at build time.
- The copy Shannon RUNS is `Desktop\Sentinel-Forge` — after every
  push, pull there, or he sees stale code.
- His scoreboard slots are full with his own measures — never evict.
- Grep for swallowed exceptions FIRST when "X doesn't work."
- Check `voice_debug.log` for anything voice-related.
- Read `Working-With-The-Architect.md` before communicating anything
  complicated; dignity-first, outcome-first, one question max.
