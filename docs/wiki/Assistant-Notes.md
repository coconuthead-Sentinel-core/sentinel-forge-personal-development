# Assistant Notes — self-maintained project state & instructions

> **Standing protocol (Shannon's order, 2026-07-11):** every time the
> README is shown or checked, the assistant must (1) open this page,
> (2) read ALL wiki notes, (3) execute any instructions left in §5
> below, (4) update this page — summary, V&V, TODO — and (5) mirror the
> repo to laptop + OneDrive + GitHub. This page is written BY the
> assistant FOR the assistant; Shannon may drop instructions into §5
> at any time.

_Last updated: 2026-07-12 (formula engine — Excel Bible integration) · updated by: Claude (Fable 5)_

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

- **215 automated tests, all green** (headless; temp DBs; injectable
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
