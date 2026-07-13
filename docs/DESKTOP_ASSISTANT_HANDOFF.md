# Desktop Assistant Handoff — Sentinel Forge, Personal Development

**Written for: the desktop coding assistant (Claude, built by Anthropic) on
Shannon's machine.** This is the third reference, distilled from two vetted
sources: (1) `docs/wiki/Review-ImprovementAudit.md` — the fact-checked July
2026 improvement audit with per-item verdicts; (2) the 2026-07-13 check-in
review of the neurodivergence research material (recorded in
`docs/wiki/Assistant-Notes.md` §5 and `Whitepaper-Notes.md`). Follow it in
order. Do not start coding until step 2 is done in YOUR OWN pseudocode.

---

## 0. The admission rule (Shannon's standing guardrail)

**"Strict Clinical Science 2026. Classroom textbook computer science.
Functional code that works."** Concretely:

- A claim enters this repo ONLY with a real, verified citation. Two
  fabricated references have already been caught and kept out ("Pijpker
  2025", "Cortese 2024 JAMA Psychiatry") — verify EVERY citation yourself
  before it touches docs or code, even when a research summary says
  "proven". No trade-book claim gets the word "proven"; label it honestly.
- No feature ships on "maybe it'll turn out okay". The pipeline is
  `.claude/skills/sentinel-sprint`: pure kernel → headless tests green →
  wire into the shell with visible feedback → smoke under a real
  `mainloop()` → design-law linter → CHANGELOG + wiki → ship.
- A button that does nothing is a defect, not a placeholder. (See §4.)
- Diagnoses belong to clinicians. Software here provides SCAFFOLDING
  (external memory, cues, automation-tracking) — assistive, like glasses
  or a hearing aid — and never makes clinical claims.

## 1. State of the repo as handed off (2026-07-13)

- Everything is merged to `main`; session branches are deleted after merge.
- Suite: 341 tests green (339 headless / 341 under a display), design-law
  linter green (Rules A and B are hard gates).
- Shipped this cycle: 💼 Job Readiness audit (six-pillar kernel
  `lyceum/job_readiness.py` + Planning-hub window) and the README
  evidence-honesty pass (every claim now names its real mechanism and a
  verified citation).
- Known dead code was removed (`_round_rect`/`_ftb_make_font_marker`).
- The ~202 research files from the laptop sessions are NOT in this repo
  yet. When Shannon adds them: vet before use, exactly per §0.

## 2. Your first task — re-derive the pseudocode

Read the two sources, then WRITE YOUR OWN pseudocode for each queued
sprint below (do not copy the blueprints — re-derive them; where yours
disagrees, say so and reconcile before coding). Only then implement, one
sprint at a time, each through the full sentinel-sprint pipeline.

### Sprint queue (order matters)

**Sprint B — two-lapse streak protocol** (evidence: self-compassion after a
lapse speeds recovery, Neff 2003; fresh-start effect, Dai/Milkman/Riis
2014; implementation intentions, Gollwitzer & Sheeran 2006)
```
kernel lyceum/streaks.py:
  classify_lapse(done_today, missed_yesterday, missed_day_before)
      -> done_today | active | first_miss | recovery
  lapse_message(state, streak, best) -> (text, level)
      first_miss -> AMBER, encouragement ("a rest day, not a broken chain")
      recovery   -> RED, fresh-start prompt + ask for an exact time
tests: all 4 states; first miss is amber and shame-free
wire:  Never-Miss-Twice banner (currently red on ANY yesterday-miss)
```

**Sprint C — WCAG contrast kernel + palette gate**
```
kernel lyceum/wcag.py: relative_luminance, contrast_ratio (W3C formula),
  meets_aa(ratio, large)
tests: black/white=21.0, symmetry, W3C examples; then gate every (fg,bg)
  text pair from the app palette at AA
rule:  probe the palette FIRST; a failing pair is a FINDING to show
  Shannon with a proposed hex — never silently recolor his app
```

**Sprint D — V2MOM if-then line** (Gollwitzer d≈0.65)
```
additive column v2mom_goals.if_then; one Entry under Obstacles:
  "If <your obstacle> happens, then I will …" — ENCOURAGED, not required
  (do not stiffen Shannon's existing flow)
```

**Sprint F — Bill Sentinel** (the check-in's real ask: prospective-memory
scaffolding for bills; evidence: automation/defaults beat memory — Thaler
& Benartzi 2004; specific timed cues beat intention)
```
kernel lyceum/bills.py (pure; inject today):
  next_due(due_day, today) -> date          # handles month ends
  classify(bill, today) ->
      autopay        -> GREEN  "automated — nothing to remember"
      manual, >7d    -> OK     (quiet)
      manual, <=7d   -> AMBER  "due in Nd — pay or set up autopay"
      manual, past   -> RED    "overdue Nd — pay today"
  next_action(bills) -> the ONE line: first red, else first amber,
      else "set up autopay for <first manual bill>" else all-clear
schema (additive): bills(id, name, amount_cents, due_day 1-31,
  autopay 0/1, last_paid, created_at)  -- archive, never delete
wire: Money hub panel; feed planner_tasks + the existing appointments
  T-60/-30/-15 reminder machinery for manual bills; one primary action;
  the goal state is EVERY bill green (autopay) so the app goes quiet
tests: month-end due dates, each classification, next_action priority,
  temp_study_db round-trip
honesty: the app cannot pay bills — it tracks automation and cues what
  is not yet automated; say exactly that in the panel
```

Parked (only if Shannon asks): Sprint E inverse-volatility All Seasons
view (pure Python, educational label; scipy is banned — stdlib core).

## 3. After EVERY sprint (the paperwork is not optional)

CHANGELOG.md entry → 1-3 sentences in `docs/wiki/Whitepaper-Notes.md` →
`docs/wiki/Assistant-Notes.md` §5 mark done (+ suite count) → README
feature/test-count updates → `Feature-Catalog.md` + `Database-Schema.md`
rows for any new table/window → commit → push → merge to main → **delete
the session branch** → **mirror BOTH clones (Desktop\Sentinel-Forge and
the OneDrive clone) as EXACT clones of main** (`git pull` in each; no
stray files).

## 4. Real-hardware verification duty (you have the screen; the cloud
assistant does not)

- **Dead-button audit:** Shannon reports buttons that do not work. Walk
  every panel; `.invoke()` every Button headlessly AND click on the real
  display (the A−/A+ bug was invisible headlessly — Canvas clicks died
  only in the real flow toolbar). Log each dead control in Assistant-Notes
  §5 with its panel, then fix through the pipeline. A button with no
  visible effect counts as dead — every action needs visible feedback.
- Verify window fit on Shannon's ~1097×617 effective display (linter Rule
  B guards new code; eyeball the rest).
- Read `docs/wiki/Working-With-The-Architect.md` before touching UI.

## 5. Working with Shannon (from the same two sources)

Lead with the outcome; one clarifying question maximum. One primary action
per screen; five major choices or fewer. Honesty over polish — never
"enterprise-grade", never inflate evidence. He does daily check-ins
(sleep/food/hydration per the agreement) — respect the cadence, and match
his additive rule: improve, never tear down.
