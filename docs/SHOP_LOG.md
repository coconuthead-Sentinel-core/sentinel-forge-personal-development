# Shop Log — Sentinel Forge, Personal Development

> The daily engineering logbook: one dated entry per working session, with
> both parties' input and a signoff. Standard professional practice (the
> engineering notebook; records-keeping per ISO/IEC/IEEE 12207) — adapted
> from the Codex `08_BUILD_EVIDENCE_AND_SIGNOFF_CHECKLIST` template per the
> Template Library Policy (templates stay blank in the Codex; this is the
> project's filled copy). Newest entry on top. The engineer writes the
> close-of-session entry; the proprietor adds direction, decisions, and
> field reports (defects seen on the real screen).

**Roles** — Proprietor / architect / QA: **Shannon Brian Kelley** ·
Coding engineer: **Claude (Anthropic)**.

---

## Entry template (copy for each session)

```
### YYYY-MM-DD — session close
- Proprietor's direction today:
- Work completed (engineer):
- Evidence: suite count · mirrors hash · logs/probes referenced
- Defects found / fixed:
- Decisions made (and by whom):
- Decisions PENDING (owner's call):
- Next session opens with:
Signoff — Prepared by: engineer · Reviewed by: proprietor ·
Decision: draft | ready_for_review | approved | blocked
```

---

### 2026-07-21 (early) — QA sweep continues (same working session)

- **Proprietor's direction:** one item at a time, Eisenhower order;
  exercise break logged ☕ 30 min; extreme-ownership books check ordered.
- **Work completed (engineer):** bugs 2–4 fixed/shipped/mirrored same
  hour — ⏱ Time Check dispatch + visible save · 🎤 mic enrollment
  (4 boxes) · 🔡 A−/A+ legibility enrollment + open-at-persisted-size.
  All breadcrumb-diagnosed first, per standing method.
- **Evidence:** smokes 9/9 · 5/5 · 5/5 under real mainloop (temp DB);
  suite 422 green ×3; main `9ef5610`; three clones verified identical;
  foreman's journal + boards current; owner re-tests ✅ on Prompt
  Library toolbar/save/title-mic (his screenshots).
- **Decisions PENDING (owner):** unchanged (branches, Recycle Bin, E:
  drive, stale clone, dirty trees) — E: still disconnected.
- **Weekly receipt readiness:** time_log (both parties' punches) +
  CHANGELOG + field sheet + this log = compile-ready; formatting job is
  Imprint's first work order (field sheet §D).
- **Proprietor's update (later same day):** Prompt Library CLOSE-OUT
  scheduled, not clear yet — one 25-min Pomodoro, three checks on the
  real screen: (1) A+ grows the letters, (2) mic dictates a Title,
  (3) red lamp archives an entry → `.md` appears in `Prompt Archive\`.
  Three ✅ = section clear → next field-sheet line. Gate filed on the
  field sheet (Testing-and-QA.md).

Signoff — Prepared by: **Claude (engineer)** · Reviewed by: **Shannon
Brian Kelley (proprietor)** · Decision: **ready_for_review**

---

### 2026-07-20 — session close (stabilization declared; QA triaged)

- **Proprietor's direction today:** feature freeze confirmed by his own
  call — "use the equipment that's already built; no further development;
  test what we have and document the QA." Portfolio put on an HR footing.
  QA work prioritized through the Eisenhower method, all four quadrants,
  displayed on the board and filed here (below).
- **Work completed (engineer):** Prompt Library repair shipped (Save
  handler wired, Delete→archive per the law, toolbar auto-docks;
  12 tests; suite 410→422; smoke 5/5) · portfolio audit + hours ledger
  (27 repos, 571 commits, 174.3 h documented; COCOMO ceiling ~96
  person-months labeled as model estimate; honest A/B/C tiering —
  "industrial grade" not claimed) · 7 merged child branches deleted on
  GitHub, 7 unmerged reported · field QA session sheet added to
  Testing-and-QA.md · this triage.
- **Evidence:** suite 422 green · main `0565102` + docs · both clones
  mirrored same-day · archives: Prompt Archive folder created on first
  use · E: drive DISCONNECTED — 4th-copy verification pending.
- **Defects found / fixed:** Prompt Library (3-in-1, proprietor's field
  report) — fixed and shipped; owner re-test pending (sheet §A). ·
  ⏱ Time Check popup outside the dispatch chain (proprietor's blocker,
  filed before break — "can't save the A-1 work") — dock slot + yellow
  Save/Enter commit + clipboard menu + "✏ note saved" on the status
  line; smoke 9/9 on temp DB; suite 422 green; re-test on sheet §B.
- **Decisions made:** stabilization phase governs; Q4 exclusions are
  deliberate and in writing (no new features, no new doc products, no
  runtime QA for Tier B/C without a stakeholder ask).
- **Decisions PENDING (owner's call):** 7 unmerged branches · Recycle
  Bin emptying (verdict: safe) · stale capital-D clone · June backup
  folder → E: · dirty trees (QNF-GitHub 8, Imprint 1, Claude AI 9).
- **Next session opens with:** proprietor's field-sheet results; every
  ❌ becomes a defect report; engineer triages and fixes under the freeze.

**Filed pseudocode (canonical copy — matches the board shown 2026-07-20):**

```text
ALGORITHM QAPipelineTriage                // Eisenhower, all four quadrants planned
INPUT:  27 products, 1 field QA sheet, 1 proprietor on his day off
OUTPUT: every product honestly labeled tested / partially tested / untested
INVARIANT: feature freeze holds - nothing new gets built; nothing ships
           claiming "QA tested" until its sheet is clean

1    Q1 DO NOW (urgent + important) - today, inside a 25-min block:
1.1      field sheet A - Prompt Library repair (step 7, awaiting owner's eyes)
1.2      field sheet B - Ambience REAL audio, Reward-Draw, AAR dock
                                          // never verified on this laptop
2    Q2 SCHEDULE (important, not urgent) - one per session this week, on the Planner:
2.1      field sheet C full timer sweep ; field sheet D Imprint end-to-end
2.2      Tier-A repo passes: strata-console, Quantum-Nexus-Forge, earp-prompts
2.3      nudge timers: observe over the week ; plug in E: drive, verify 4th copy
3    Q3 DELEGATE (to the engineer - Claude):
3.1      re-run automated suites before any ship ; read breadcrumb logs after sessions
3.2      triage every X into a defect report -> fix -> mirror ; keep all copies exact
4    Q4 DON'T DO (deliberately, in writing):
4.1      no new features ; no new documentation products      // freeze is the law
4.2      no runtime QA for Tier B/C repos - docs + templates have no runtime;
         revisit only on a stakeholder ask
5    FOR EACH completed line -> log pass/fail + note on the wiki sheet; fail -> CALL engineer
6    ASSERT before any product is offered for payment: its QA sheet is clean
     and its tier label is honest
7    STOP -> proprietor returns from break, starts the timer, works Q1
```

Signoff — Prepared by: **Claude (engineer)** · Reviewed by: **Shannon
Brian Kelley (proprietor)** · Decision: **ready_for_review**

---

### 2026-07-16 (late) — field report from the road test → fixed same night

- **Proprietor's field report (QA on the real screen):** "floating
  microphone toolbar is not available in After-Action Review." Verified
  in code: correct — the earlier fix wired the AAR into the traffic
  light's *dispatch chain*, but the window was never added to the
  toolbar's **dock map**, so the bar (with its mic) had nowhere to live
  there. Two different mechanisms; QA caught the second one.
- **Fix (engineer, house pattern):** `"review"` added to the dock
  `window_map` · "Dock to After-Action Review" added to the dock menu ·
  Study-window re-dock-on-open precedent applied to the AAR. Closed
  window falls back to main.
- **Evidence:** smoke 3/3 under real mainloop (dock host created inside
  the AAR window; re-dock to main; safe fallback when closed) · linter
  8/8 · suite **410** green · shipped to main + both mirrors same night.
- **Breadcrumbs for QA (proprietor's order, same night):** the standing
  method extended — new `qa_debug.log` records toolbar dispatch claims
  and fallthroughs, dock moves, reward draws (tier + drought), and
  ambience events; method + field-report workflow documented in
  Testing-and-QA.md. Verified live: smokes re-run, trail read back.
- **Next:** proprietor re-tests on the laptop — open the AAR, undock the
  bar (or use the dock menu), confirm the mic dictates into both boxes.

Signoff — Prepared by: **Claude (engineer)** · Reviewed by: **Shannon
Brian Kelley (proprietor)** · Decision: **ready_for_review**

---

### 2026-07-16 — session close (Reward-Draw sprint)

- **Proprietor's direction:** verify all mirrors ("go for a home run" —
  done: GitHub = OneDrive = Desktop = backup at `861aea0`, Desktop
  fast-forwarded 126 commits); build the pseudocode-display skill (done,
  user-level); gate the NotebookLM BrainTrust gamification transcript
  (done — 1 of 4 proposals passed); then his call: **"let's build this
  thing"** — the Reward-Draw sprint, paperwork after, owner laptop test
  to follow.
- **Work completed (engineer):** `lyceum/reward_engine.py` (variable-ratio
  70/25/5, 12-draw pity guarantee, named-source honesty gate, no-work-no-
  reward, append-only `reward_log`) + 2 additive tables in `study_db` +
  15 headless tests + Focus-Mode wiring (quiet dot / library quote card /
  rare gold flash + chime) + mainloop smoke (4/4 checkpoints). Paperwork:
  CHANGELOG, Whitepaper-Notes, Assistant-Notes §5, README (test count
  379→400 fixed; roadmap ✅ added).
- **Evidence:** suite **400** green (14 skips, standard) · design-law
  linter 8/8 · smoke `SMOKE PASS` · work on session branch
  `claude/sentinel-personal-dev-7cd21f`.
- **Defects found / fixed:** README test-count claim was stale (379 vs
  385 actual at session open; 400 at close — fixed at close).
- **Decisions made (and by whom):** pity limit 12, sourced-payloads law,
  kernel/shell split — proposed by engineer, approved by proprietor
  ("let's build this thing"). Rejected from the BrainTrust transcript
  (engineer, science gate): "85% of happiness" stat, "top 1% fitness"
  claim, auto-email accountability (consent design needed first).
- **Second build same session — 🌧 Ambience:** proprietor asked for a
  Library button playing background sound (wind + binaural beats) under
  the read-aloud voice. Science gate applied: binaural-beats-for-learning
  labeled honestly UNPROVEN (mixed literature); "same material twice
  simultaneously" vetoed (speech-stream interference) in favor of
  sequential re-listen. Built: `lyceum/ambience.py` (pure synthesis,
  seamless loops, AmbiencePlayer on the existing sounddevice dep) + 🌧
  Library chooser with verbatim honesty labels. 10 tests; suite **410**;
  linter green; chooser + degrade path smoke-passed. NOTE: real audio-out
  NOT verifiable on this bench (worktree python lacks sounddevice) —
  laptop must verify sound on the metal.
- **Third build same session — 🪞 AAR joins the toolbar (proprietor's QA
  find):** Shannon, working as human-in-the-loop QA, spotted that the
  After-Action Review window sat outside the floating-toolbar dispatch.
  Wired in the house pattern: green Add → today's entry, yellow Save →
  commit shown day, red Delete → clears TODAY's draft only and REFUSES
  past days (archive law: history is never deleted). Smoke 6/6 under a
  real mainloop with a temp DB; suite 410 green.
- **Decisions PENDING (owner's call):** laptop road test of BOTH sprints
  — Reward-Draw toasts (all three tiers) and Ambience audio on real
  speakers/headphones — BEFORE merge to main + mirror; curate the starter
  quote pool (8 seeded entries — add/retire via the service).
- **Next session opens with:** proprietor's laptop verdict on Reward-Draw
  + Ambience; if green → merge to main, mirror both clones, delete
  session branch. Queued next: Audio Review Track (export WAV,
  question→pause→answer retrieval format — boarded 2026-07-16).
  Portfolio README-audit work order still queued.

**SHIPPED (proprietor's order, same evening):** "Yes. Do that now." —
merged to main at `3f68103`, pushed to GitHub, both mirrors pulled;
Mirror-Verify pass: 3 clones + origin/main identical (commit + file
hashes), status clean everywhere. Laptop road test of the three
features (Reward-Draw toasts · 🌧 Ambience audio · AAR traffic light)
now happens ON main — defects found there open the next work order.

Signoff — Prepared by: **Claude (engineer)** · Reviewed by: **Shannon
Brian Kelley (proprietor)** · Decision: **approved**

---

### 2026-07-13 (evening) — session close + WORK ORDER filed

- **Proprietor's direction:** vet an external TTS diagnosis (done — half
  wrong about our code, real defect underneath fixed); make the breadcrumb
  method standing practice (done); establish the shop log (done); review
  the December-era `Claude AI` folder for employment relevance (done —
  read-only); then his call: the next body of work is a **full top-down
  README audit of every GitHub repo** through the new guardrails — review,
  don't rebuild — before anything is "handed to the professor."
- **Evidence:** suite 385 green · mirrors `f9e0e5c`+ · `tts-norm`
  breadcrumb live · Claude-AI-folder findings logged in session record.
- **Safety flag raised:** the proprietor's old work-history file contains
  SSN/DL/references — keep local, never in any repo or synced page.
  December-era resume language ("5 years hands-on development", personal
  FastAPI/DevOps skill claims) FAILS the science gate — do not reuse; the
  honest "designed/directed/validated, AI-assisted" framing stands.
- **📋 WORK ORDER — PORTFOLIO README AUDIT (queued, opens next session):**
  - **Scope:** all ~26 GitHub repos. Per repo: top-down README review →
    clear name, honest claims (science gate), current state, and a
    **"Skills demonstrated"** framing that is interview-defensible.
    Review only — NO rebuilding, no feature work.
  - **Out of scope:** code changes beyond README/docs; renaming
    `Sentinel-of-sentinel-s-Forge` without the owner's explicit call
    (hands-off list); any new dashboards.
  - **Order:** batch 1 = the strong four (Sentinel Forge, Imprint, EARP,
    strata-console) — these carry the résumé; batch 2 = the reference
    implementations; batch 3 = concept/template packs (label honestly as
    concept work). Estimate: 2–3 sessions.
  - **Acceptance:** each README passes the professor test; portfolio
    reads truthfully to a hiring manager in under a minute.
- **Sentinel status:** shakeout continues (proprietor on night shift);
  v1.0 forecast unchanged (pickup last week of July). WCAG decision still
  pending (owner, ~10 min).
- **Next session opens with:** proprietor's shakeout report, then
  "start the audit" → batch 1.

Signoff — Prepared by: **Claude (engineer)** · Reviewed by: **Shannon
Brian Kelley (proprietor)** · Decision: **ready_for_review**

---

### 2026-07-13 — session close

- **Proprietor's direction today:** pick up the cloud handoff verbatim;
  build the sprint queue; establish the `scope-first` guardrail ("no
  blueprint, no build"); keep everything textbook clinical classroom
  science; begin the v1.0 bug-shakeout test period; be token-mindful —
  maintenance only, no new construction; adopt the breadcrumb method as
  standing practice; stand up this shop log.
- **Work completed (engineer):** PR #52 merged + session branch deleted;
  three guardrail skills mirrored user-level, then a fourth built
  (`scope-first`) with the project's retroactive baseline `docs/SCOPE.md`;
  Sprints **B** (two-lapse streak protocol), **C** (WCAG contrast kernel +
  palette audit), **D** (V2MOM if-then line), **F** (🧾 Bill Sentinel)
  shipped through the full pipeline; A−/A+ visible-effect fix (all five
  prose surfaces now scale; stuck 28pt size reset); TTS code-span
  atomicity fix (externally proposed, verified against real code first);
  `tts-norm` breadcrumb added to `voice_debug.log`.
- **Evidence:** suite **341 → 385 green** (14 skipped); design-law linter
  0/0; live `study.db` byte-verified untouched after every run; mirrors
  (laptop = OneDrive = GitHub) at **`95c1716`** at close; breadcrumbs:
  `fontsize_debug.log` (proved A−/A+ clicks fired), `voice_debug.log`.
- **Defects found / fixed:** A−/A+ scaled only 3 of 5 prose surfaces
  (invisible success — fixed); TTS ran English normalization over backtick
  code spans (fixed, +6 tests). Both found during the proprietor's live
  shakeout — the road test is earning its time.
- **Decisions made:** overdue semantics for bills (no payment history ⇒
  never "overdue") — engineer, logged; Sprint F reminder-machinery feed
  deferred with reason — engineer, logged; shop log established at
  project level per Codex policy — both.
- **Decisions PENDING (owner's call):** the four WCAG button colors
  (proposed same-hue hexes in Assistant-Notes §5); tagging UI — build
  small or formally descope in SCOPE.md; README v1.0 coherence pass
  timing.
- **Next session opens with:** proprietor's shakeout defect list (panel +
  what was clicked); then the detail-and-paperwork pass toward the v1.0
  stamp. Delivery-readiness estimate at close: ~92% (construction 100%
  of scope; remaining: quiet road test + final paperwork).

**Foreman's forecast (filed 2026-07-13, computed via the dashboard's own
logic — PERT backward from the v1.0 stamp; exit gate = 5 consecutive
quiet shakeout days; defect cost ≈ 1 day each, per this week's measured
turnaround):** best case **~Jul 20** · expected **~Jul 24–27** ·
conservative **no later than ~Aug 1**, else re-baseline. Customer-facing
promise: **pickup last week of July.** Sole item waiting on the
proprietor: the WCAG color decision (~10 min). Sole item waiting on the
calendar: quiet days.

Signoff — Prepared by: **Claude (engineer)** · Reviewed by: **Shannon
Brian Kelley (proprietor)** · Decision: **ready_for_review**
