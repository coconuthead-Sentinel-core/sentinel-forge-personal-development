# White-Paper Notes — raw material (append-only)

> Working title: **"Neurodivergent-First by a Neurodivergent Architect:
> Designing, Testing, and Shipping a Local-First Personal-Development
> Workstation with AI-Assisted Development."**
> Practice: every README/docs update leaves 1–3 sentences here. When
> enough accumulates, notes feed the skeleton in [Whitepaper-Outline](Whitepaper-Outline.md), which becomes the white paper's outline.
> Framing rules (owner's decision, July 2026): lead with engineering;
> public disclosure stays at the README's existing line
> (ADHD/dyslexia/dysgraphia); one paper anchored here, citing Imprint
> and strata-console as the "one assistant design, three shipped
> dashboards" replication proof.

---

- **2026-07-11 — Review-readiness pass.** Accuracy is the polish that
  matters: the README claimed 34 tests while the suite held 172; a
  top-down review treated every stale claim as a defect. Lesson for the
  paper: documentation drift is a bug class, and single-developer
  projects need scheduled doc audits just like dependency updates.
- **2026-07-11 — "Numbers need a picture."** Dyscalculia turned into a
  design law: every raw figure ships with a gauge, meter, or
  translation (months of survival fuel, hours of life). Accessibility
  requirements stated as engineering laws — not accommodations — is the
  paper's central thesis in miniature.
- **2026-07-11 — Archive, never delete.** A 300-file cleanup froze the
  UI (per-file Recycle-Bin calls on OneDrive-synced files, on the UI
  thread); the fix reframed the operation entirely — "remove" became
  "move to archive," matching the user's trust requirement that files
  never leave the laptop. UX vocabulary is a safety feature.

- **2026-07-11 (evening) — Self-documenting maintenance loop.** The
  project now includes an assistant-maintained operations page
  (Assistant-Notes.md): every README review triggers a read-execute-
  update cycle over the wiki, closing the loop between documentation
  and action. A development methodology detail for the paper: the
  documentation is not just ABOUT the system — it is part of the
  system''s control loop.

- **2026-07-11 (late) — Rebuild blueprint as insurance.** The project
  now carries its own reconstruction plans (Rebuild-Blueprint.md):
  language-portable pseudocode of the foundation, threading circuits,
  data plumbing, and room-by-room build order with acceptance gates —
  written after an earlier project WAS lost. Estimated replacement
  cost drops from months to 8-12 sessions. Documentation as disaster
  insurance is a paper-worthy practice for solo developers.

- **2026-07-11 (late) — Template library discipline.** The owner
  maintains a blank-template source library (the Codex) with a written
  policy: templates stay blank; projects copy and fill their own
  copies. The rebuild pack (docs/rebuild-pack/, 8 filled inventories
  from the engineering template pack) demonstrates the discipline —
  reusable process assets, per-project instances. That separation is
  itself an SDLC maturity marker worth a paragraph in the paper.

- **2026-07-11 (late) — Spreadsheet as floor plan.** The rebuild pack
  gained an Excel floor plan: colored cell blocks draw the rooms, and
  symbol fixtures (🔌 thread seams, 🚿 outputs, 🧊 storage) link to
  tables naming the exact code home of every outlet and pipe. For a
  dyscalculic, spatially-thinking owner, a grid the eye can walk
  through communicates architecture better than prose — accessibility
  applied to the documentation itself.

- **2026-07-12 — The harvest loop closes read→remember.** The Knowledge
  Harvester mines term/definition pairs from any Library book into the
  FSRS deck, with a checkbox preview keeping the human in the loop. It
  shipped in two gated sprints: a pure-logic core practiced against a
  real 1.9M-character corpus until junk hits reached zero, then a thin
  UI. Method note for the paper: the mockup-first protocol (three
  verifiable no-harm proofs before a single project line changed) is
  the AI-era version of a design review.

- **2026-07-12 — Mirror discipline as routine.** A README review now
  runs as a standing protocol: hash-verify GitHub/OneDrive/laptop,
  execute the wiki instruction queue, update the operations page.
  The pasted copy under review was itself one commit stale — caught
  because verification compares hashes, not impressions.

- **2026-07-12 — Pattern reuse as a feature multiplier.** The Commentary
  tab was rebuilt to match the Glossary tab (structured, searchable
  SQLite store) — same layout, same CRUD shape, a new additive table.
  Proving the store against a temp DB before touching the UI made the
  build near-bugless. Consistency is not just UX polish; a reused,
  already-proven pattern is the cheapest reliable code a solo dev writes.

- **2026-07-12 — Review-gated integration.** A full Excel 365 Bible
  (~2.87M chars) was reviewed top-down before any code: most of it
  (Excel UI, VBA, Power Query) correctly ruled OUT of a local study
  app; the one real-CS fit — a spreadsheet formula engine (tokenizer →
  recursive-descent parser → evaluator) — was prototyped and proven
  (20/20 checks) in pseudocode BEFORE a line of feature code. Disciplined
  scoping (what NOT to build) is itself the senior-engineering signal.

- **2026-07-12 — Formula engine shipped (Excel Bible → real CS).** The
  review-gated build landed: a tokenizer → recursive-descent parser →
  tree-walking evaluator (lyceum/formula.py) for Excel-style formulas,
  proven in pseudocode first (20 checks) then built in two sprints
  (27 tests) and wired into the assistant so it reports the totals it
  writes into spreadsheets. A textbook parsing artifact, delivered
  additively — the strongest single CS demonstration in the codebase.

- **2026-07-12 — Review #2, and the extra-mile lens.** A Word 2010
  textbook (~1.38M chars) reviewed top-down: nearly all of it ruled OUT
  (Word UI, mail merge, track changes). The one real-CS fit —
  readability analysis (Flesch-Kincaid, a syllable-counting NLP kernel)
  — was chosen precisely BECAUSE it serves the neurodivergent-first
  thesis: an objective difficulty warning for a dyslexic reader. The
  reviewer-noticing move is framing, not features: not "I copied a Word
  metric" but "I turned a readability algorithm into an accessibility
  guardrail." Proven in pseudocode (3 proofs) before any code.

- **2026-07-12 — Readability engine shipped (Word 2010 → accessibility).**
  A Flesch-Kincaid analyzer (syllable-counting NLP kernel + two published
  formulas) now stamps every saved excerpt with an objective difficulty
  badge ("📖 Grade 8 · Plain") beside the subjective cognitive-load zone.
  The design was chosen for the thesis, not the novelty: a difficulty
  WARNING for a dyslexic reader. Proven in pseudocode (3 proofs, caught
  2 bugs), then 2 gated sprints (15 tests + runtime proof). The clearest
  example in the codebase of turning a textbook feature into a
  disability-specific guardrail.

- **2026-07-12 — Review #3: prompt engineering as a rubric analyzer.** A
  Microsoft 365 Copilot book (~594K chars) reviewed top-down: nearly all
  ruled OUT (enterprise deployment, security, licensing — not CS). The
  one teachable-CS fit — a prompt-quality analyzer scoring against the
  prompt-engineering rubric (persona/task/context/format/specificity) —
  is original heuristic code over public canon, professor-approvable,
  and turns the AI Chat into a teaching tool for a user LEARNING to work
  with AI. Proven in pseudocode (3 proofs / 15 checks) before any code.

- **2026-07-12 — Prompt Coach shipped (Copilot book → teaching tool).**
  A rubric analyzer (role/task/context/format/specificity) now scores
  the AI-Chat draft live and teaches the biggest fix as the user types,
  with an ✨ Improve button that grafts the missing parts. Chosen for the
  learner: it turns the assistant into a tutor for the very skill —
  prompting — the owner is studying. Original heuristic code over public
  prompt-engineering canon; proven in pseudocode (15 checks) then two
  gated sprints (22 tests). Fourth textbook reviewed → fourth pure-logic
  lyceum kernel, all additive.

- **2026-07-12 — Review #4: Power Automate as an ECA engine.** The
  Power Automate books (~749K chars) reviewed top-down: cloud connectors
  and the flow designer ruled OUT; the one canonical-CS fit — the
  trigger→condition→action model IS the Event-Condition-Action rule
  engine (active-database triggers, production rule systems, workflow
  architecture — recognized on every campus worldwide). A pure decision
  engine (no side effects; the shell executes, human-in-the-loop) proven
  in pseudocode (3 proofs / 22 checks incl. malformed-rule safety)
  before any code. The through-line of the whole review series: name the
  textbook construct, implement it purely, prove it, keep it additive.

- **2026-07-12 — ECA engine shipped (Power Automate → automation).** An
  Event-Condition-Action rule engine (lyceum/automation.py) — the
  textbook construct under every workflow product — now fires on real
  app events (a completed focus block) and SUGGESTS actions, never
  performing them: a pure decision function, the shell + human decide.
  This completes a four-textbook arc: Excel Bible → formula engine, Word
  2010 → readability, Copilot → prompt coach, Power Automate → ECA. Four
  canonical CS kernels, each proven in pseudocode first, each additive
  and pure. The pattern IS the portfolio thesis.

- **2026-07-12 — Review #5: Shannon entropy from the cert books.** The
  M365 certification books (~759K chars) reviewed top-down: cloud/tenant
  admin, Teams, exam prep all ruled OUT; the one canonical-CS fit — the
  identity-security material rests on SHANNON ENTROPY (information
  theory, 1948), the single most universally-taught algorithm in CS. A
  password-strength estimator (search-space + distribution entropy,
  attacker-favorable minimum), private by design (no storage/network),
  proven exact against closed-form values (20 checks) before any code.
  Fifth textbook, fifth canonical pure-logic kernel — the method holds.

- **2026-07-12 — Shannon entropy shipped (M365 cert → strength meter).**
  A password-strength estimator built on Shannon entropy (the most
  universally-taught algorithm in CS) — search-space + distribution
  entropy, attacker-favorable minimum, private by design (pure function,
  no storage/network/logging). This closes a FIVE-textbook arc: Excel
  Bible → formula engine, Word 2010 → readability, Copilot → prompt
  coach, Power Automate → ECA engine, M365 cert → entropy. Five canonical
  CS kernels, each proven in pseudocode first, each additive and pure.
  The repeatable method — review, extract the textbook construct, prove,
  build safely — is the portfolio thesis made concrete.

- **2026-07-12 — Accessibility as adjustable, evidence-based formatting.**
  The study panels gained a floating-toolbar A− / A+ text-size control and
  a Format ▾ dropdown of reading presets (OpenDyslexic, ADHD-focus,
  dysgraphia) — each preset a documented triple of font, size delta, and
  line-leading drawn from Rello & Baeza-Yates (ASSETS 2013) and the British
  Dyslexia Association style guide, not invented. The what-to-apply is a
  pure kernel (lyceum/legibility.py) proven in a throwaway prototype (3
  proofs / 14 checks) before any UI, then wired live to all three panes.
  Two method notes for the paper: (1) accessibility stated as a *user-
  adjustable* spec — the reader picks the preset — respects that ADHD,
  dyslexia, and dysgraphia are different needs, not one "accessible mode";
  (2) a clipped-controls bug (the tab bar and docked toolbar ran off the
  right edge, leaving Minimize/Undock unclickable) was fixed with a
  wrapping-flow container and *measured* shut by a headless proof that
  asserts no control's edge exceeds the window at a cruel 760px width —
  UI correctness treated as a testable invariant, not an eyeball check.
  Companion lesson logged the same day: headless tests must isolate the
  live database, not just a secondary path, or they silently pollute real
  user data.

- **2026-07-12 — One workflow, three panels (parser-first, again).** The
  owner asked for the same three-step flow — paste into a main box, save,
  then click an entry and hear it read with highlighting — across the
  Topics, Commentary, and Glossary tabs. The parsing was extracted to a
  pure kernel (lyceum/entry_parse.py) and proven headlessly (18 tests)
  before the UI: the first draft swallowed a fresh un-indented term into
  the previous definition, a bug the tests caught and an indented-
  continuation rule fixed. The read-aloud reused the existing floating-
  toolbar highlight-and-speak engine rather than a second copy — pointing
  it at each panel's read-pane on selection. Two accessibility lessons for
  the paper: (1) a consistent interaction grammar across panels lowers
  cognitive load for a neurodivergent user more than any single feature;
  (2) reusing one proven output path (speech) instead of duplicating it is
  both cheaper and safer than re-implementing per surface.
- **Uniform panels + consolidated controls (2026-07-12).** The Topics,
  Glossary and Commentary tabs were re-cut to the Journal panel's exact
  shape — header → `list | content` → one primary button — with their
  button rows and paste boxes removed and the actions consolidated onto
  the floating toolbar (the app's fixed "home base") plus a right-click
  menu. The design thesis: for an ADHD/dyslexia-first tool a *single
  consistent interaction grammar with a stable command locus* beats
  per-panel affordances — fewer, predictable controls lower cognitive
  load more than richer ones. Two display bugs surfaced and were fixed in
  the same pass — accessibility font-scaling must target reading surfaces
  only (never navigation indexes), and any user string placed in a modal
  must be length-capped — reinforcing that accessibility features carry
  their own failure modes worth documenting.
- **The toolbar as a fixed "safe spot" (2026-07-12).** The floating toolbar
  was refined into one uniform command cluster present in every panel: a
  traffic light with the word ABOVE each colored lamp (green Add, yellow
  Save, red Delete) and A−/A+ drawn as road-marker signs that hold one white
  and one black at all times. Thesis for the paper: for a visual/tactile,
  ADHD/dyslexia learner, borrowing UNIVERSAL real-world signal grammar
  (traffic lights, road markers) collapses the learning curve toward zero —
  the control is recognized, not read — and a command locus that never moves
  is itself an accessibility feature. (Owner-articulated design; the engineer
  translated it to Tk canvas primitives, noting Tk's shape limits honestly.)
- **Input as a toolbar verb (2026-07-12).** The last modal boxes (New-topic,
  the renames, glossary look-up) were made non-modal and toolbar-driven: no
  OK/Cancel, a universal right-click clipboard menu, and commit via Enter or
  the toolbar's yellow Save. The point for the paper: once a fixed command
  cluster exists, folding even text entry into it removes the last "foreign"
  modal step — the user never leaves the safe spot, which for an ADHD/dyslexia
  learner is the difference between flow and friction. Engineering caveat worth
  recording: this trades a synchronous modal (`value = prompt()`) for an async
  callback (`prompt(on_commit=…)`), so each call site had to be split into
  open-input + commit — a deliberate, tested refactor, not a cosmetic swap.
- **Self-examination made mechanical: the Job Readiness audit (2026-07-13).**
  Shannon asked the real question — "what's gonna be real world for a human to
  get a real world job?" — and the answer became a six-pillar rubric (Story,
  Proof, Skills, People, Pipeline, Interview) where every 0–4 level is written
  in plain language and every level below max carries ONE concrete next action.
  Thesis for the paper: for an ADHD learner, an honest audit only works when
  the output is a single next move rather than a score — the meter gives the
  picture, but the "👉 Next move" line is the feature. Same functional-core
  discipline as always: pure kernel, 15 headless tests, then the Tk shell.
- **Fact-checking an AI research audit before letting it touch the work
  (2026-07-13).** Shannon brought an external "evidence-based improvement
  audit"; the review found it mixed genuine science (Zorzi 2012, Kollins 2020,
  Gollwitzer 2006) with at least two fabricated citations ("Pijpker 2025",
  "Cortese 2024 JAMA Psychiatry"), two false premises about this codebase, and
  buggy sample code. Method for the paper: verify every citation, check every
  premise against the real code, adopt ideas but never prose or code —
  the same nothing-ships-unproven rule the kernels live by, applied to
  research claims. Outcome: a docs honesty pass shipped same-day and three
  evidence-backed sprints blueprinted in pseudocode (two-lapse streak
  protocol, WCAG contrast gate, V2MOM if-then line).
- **The handoff as a deliverable (2026-07-13).** Shannon's consolidation
  order turned two vetted references (the fact-checked improvement audit and
  the neurodivergence check-in review) into a third: a desktop-assistant
  handoff whose first instruction is "re-derive the pseudocode yourself
  before coding." Thesis for the paper: in a multi-assistant workflow the
  artifact that transfers is not code but VERIFIED REASONING — pseudocode
  plus admission rules ("Strict Clinical Science 2026") — so each assistant
  re-proves the design instead of trusting the last one. Bill Sentinel was
  queued the same way: prospective-memory scaffolding (automation-tracking +
  timed cues) specified as evidence first, kernel pseudocode second, code
  deliberately last.
- **Guardrails promoted from prose to skills (2026-07-13).** Shannon ordered
  the two standing rules — Strict Clinical Science 2026 and classroom
  textbook CS — turned into permanent, project-agnostic assistant skills
  (`clinical-science-gate`, `classroom-code`), with the desktop assistant
  instructed to mirror them as user-level skills across all projects.
  Thesis for the paper: a rule that lives in a README is advice; a rule
  that loads into every assistant session as a skill is POLICY — the owner
  encoded his acceptance bar ("would a CS professor bound by a code of
  ethics sign this?") into the tooling itself, so it survives assistant
  handoffs, new projects, and context loss.
- **The middle ground as method (2026-07-13, evening).** A second external
  framework proposal arrived (six guardrails, four packaging options);
  review-before-action found it ~70% convergent with the two skills already
  shipped — independent convergence being itself evidence the rules are
  real — plus one genuinely new domain. The adopted middle ground: a third
  skill (learning-science: retrieval practice, spacing, worked examples
  with fading, expertise reversal, delayed JOL; neuromyths blocked with
  their debunking citations) and interview-ownership language in Job
  Readiness. The rejected mechanism matters for the paper: paste-in
  charters and per-session bootstrap prompts were declined BECAUSE they
  impose the prospective-memory burden this project exists to remove —
  the accessibility lens applied to the development process itself.

- **2026-07-13 — Two-lapse protocol: tone as an engineering artifact.** The
  Never-Miss-Twice banner was rewired through a pure kernel
  (lyceum/streaks.py) so ONE missed day speaks compassion (amber) and only
  two consecutive misses trigger the red fresh-start-plus-exact-time
  prompt — with a UNIT TEST that gates the amber message for shame-free
  language. For the paper: when the evidence says self-compassion speeds
  lapse recovery (Neff 2003), message TONE becomes a testable requirement,
  not copywriting — the first test in the codebase that asserts kindness.

- **2026-07-13 — Contrast as a measurable, not an opinion.** A WCAG kernel
  (lyceum/wcag.py, the W3C formulas verbatim) turned "is this readable?"
  into arithmetic: every reading surface passed AA with headroom, and four
  button colors measured short — filed as findings with proposed same-hue
  hexes for the owner's decision, per the never-silently-recolor rule.
  Method note for the paper: accessibility review of a shipped UI can be a
  PURE-FUNCTION audit — no screenshots, no judgment calls, just published
  math over the palette constants.

- **2026-07-13 — Bill Sentinel: the quietest screen is the goal.** The
  bills panel inverts the usual dashboard instinct: its success state is
  SILENCE — every bill on autopay, one green line, nothing to remember
  (automation/defaults over memory, Thaler & Benartzi 2004). For the ADHD
  prospective-memory thesis this is the purest example yet: the feature's
  KPI is how little the user must attend to it. Also a small honesty
  artifact: the panel states on its face that the app cannot pay bills —
  scaffolding, not agency.

- **2026-07-13 — The owner's mission statement (for the paper's opening).**
  Shannon articulated the project's "why" through a story he watched — a
  young man written off by public school (autism + case-specific learning
  disorders), taught by his mother in his safe place at his own pace, GED
  at 18, now a science professor in Canada. Labeled honestly: an ANECDOTE
  (n=1), proof of possibility, not a method. But its mechanisms map
  one-to-one onto the dashboard's evidence-backed machinery: a
  predictable low-load environment (the fixed toolbar "home base"),
  fit-the-tool-to-the-brain (the design laws), self-paced multimodal
  access (TTS/dictation/legibility), spacing and retrieval over years
  (FSRS), and recovery-first tone (the two-lapse protocol). The paper's
  claim, in the owner's calibration: software cannot do what that mother
  did and must never claim to — it can be the safe place that is always
  available. Scaffolding: glasses for executive function. He also stated
  the boundary rule in his own words: clinically diagnosed ADHD /
  dyslexia / dysgraphia / dyscalculia; autism monitored "within reason,
  within scope, within human limits" — calibrated watching without
  self-diagnosis, the same posture the science gate enforces in code.

- **2026-07-16 — Reward-Draw (variable-ratio rewards, honestly engineered).**
  The dashboard's first variable-reward mechanic: Focus-block completions
  draw from a 70/25/5 tier pool — quiet green dot, a quote card sourced
  from the owner's own library, or a rare gold flash. The kernel keeps the
  operant-conditioning mechanism (variable-ratio schedules; Ferster &
  Skinner, 1957) while deliberately removing the casino's cruelty: a
  12-draw pity guarantee bounds every drought, blank events earn nothing,
  unsourced quotes are refused at write time, and the append-only
  reward_log is both audit trail and the pity counter's memory.

- **2026-07-16 — Ambience (comfort bed, honestly labeled).** A Library
  button plays a locally-synthesized quiet loop (wind/rain/ocean/
  binaural) under the read-aloud voice on its own output stream. The
  science gate did its job twice here: the "Superlearning/Lozanov
  hemisphere-synchronization" framing from the source transcript was
  rejected as a neuromyth, and the binaural option ships labeled "NOT
  proven to improve learning" — the mixed entrainment literature does
  not support an efficacy claim. The owner's "hear it twice at once"
  idea was redirected to sequential re-listening: simultaneous
  duplicate speech streams interfere rather than reinforce.

- **2026-07-20 — Prompt Library archive repair (owner-led QA).** A field
  test with real content — the owner filing a job-search exchange —
  surfaced that the Prompt Library's Save lamp was unwired and its
  Delete lamp hard-deleted, the project's only remaining destructive
  path. The repair generalizes the archive-never-delete law to a second
  surface: rows take an `archived_at` tombstone while a Markdown copy
  with YAML front-matter lands in an OneDrive-synced folder — the local
  file IS the cloud backup, with no cloud service claimed. Notable for
  the paper: the defect was found by human-in-the-loop QA against the
  design laws, not by the automated suite, and the fix ordering (file
  written before the database row is tombstoned) encodes a
  never-lose-the-only-copy invariant.

- **2026-07-20 — Portfolio audit & hours ledger.** The evidence trail itself
  became a deliverable: commit-session estimation (git-hours heuristic,
  reproducible from public history) documents 174+ engineering hours across
  27 repositories, published in `docs/PORTFOLIO_AUDIT.md` with its method
  and limits stated — a floor, not a ceiling, and priced only as documented
  labor. Engineering-first framing: honest attribution of the AI-assisted
  workflow is presented as a credibility feature, not a disclaimer.

- **2026-07-21 — The invisible-success defect class (QA weekend).** Four
  owner-found defects in 36 hours shared one signature: the code worked
  but gave no visible proof (Save unwired or confirmation hidden; mic and
  font-scaling never enrolled for new surfaces). The breadcrumb-first
  method resolved each field report to one of three verdicts — never
  fired / wrong values / fired invisibly — in a single log read, and every
  fix shipped same-day with a mainloop smoke as runtime proof. For the
  paper: enrollment-by-registration UIs (dock maps, mic targets, scaling
  loops) need a checklist item per new surface, or the fourth instance of
  this class will not be the last.

- **2026-07-21 — Owner-defined acceptance gates.** The proprietor now
  writes his own close-out criteria before re-testing: the Prompt
  Library section clears only on three observable proofs in one
  Pomodoro (font growth on screen, dictated text landing, an archive
  file appearing on disk). For the paper: UAT maturity showed up as the
  stakeholder converting vague "re-test it" into binary, sensory
  acceptance checks — evidence the visible-feedback defect class
  taught a transferable QA habit.

- **2026-07-21 — Fifth instance, prediction confirmed.** The enrollment
  defect class claimed its predicted fifth member: the Session Start
  handoff box was a Label — the one surface whose entire job is to be
  handed back to the assistant was the one surface that could not be
  copied. The owner caught it by trying to *use* the workflow end-to-end
  (session close → relaunch → brief the assistant), not by inspecting
  features in isolation — evidence for the paper that workflow-level UAT
  finds a class of defect feature-level QA structurally cannot. Repair
  followed the house method: pure kernel (enable→replace→disable, locks
  even on error), fake-widget contract tests plus real-Tk clipboard
  proofs, then enrollment in the existing right-click menu pattern.

- **2026-07-21 — Sixth instance: the menu itself.** The invisible-failure
  class reached the remediation tooling: the right-click menu's "Select
  all" — added everywhere as part of earlier repairs — silently crashed
  on every single-line field, because its helper spoke only the
  multi-line Text API. The owner localized it from the screen alone
  ("the highlight needs to occur at the beginning… select all should be
  there") without knowing the widget taxonomy — evidence that precise
  UAT narration plus a screenshot can pin a defect to one callback. For
  the paper: fixes that enroll surfaces into a shared control must test
  the control against every widget species it's attached to, or the
  repair propagates the class it repairs.

- **2026-07-21 — Seventh instance: the repair repeats the class.** The
  box rebuilt hours earlier to fix the copy defect was itself missing
  from a sibling registry (the reader's aim), so text-to-speech spoke
  every pane but the new one. The predicted failure mode is now
  empirical: a surface must enroll in EVERY per-surface registry
  (clipboard, mic, reader, scaling), and a fix that enrolls in some but
  not all ships the next defect with the current one. The checklist
  item is no longer advice; it is the sixth and seventh data points.
  Same session, test-infrastructure corollary: growing the GUI suite
  exposed a Tcl re-init fault that silently converted green tests to
  skips — a wobbling suite count is itself a defect in the evidence
  chain, fixed by sharing one Tk interpreter per test process.

- **2026-07-21 — Reproduce before you believe the symptom's name.** The
  owner reported the Prompt Library window "bigger than the screen"; a
  controlled reproduction (real display, big font, docked toolbar, 14
  seeded entries) proved the window geometry innocent and convicted the
  layout: font-relative height requests let A+ balloon the content
  until the packer starved the last-packed widgets to 1px. Two symptoms
  ("window too big", "list stops at 12") shared the one root cause. For
  the paper: the user's vocabulary names the experience, not the
  defect — the experiment translates between the two, and a fix shipped
  against the reported name rather than the proven cause would have
  changed the window and repaired nothing.

- **2026-07-21 — The classroom joins the shop.** The collaboration
  gained a formal pedagogical layer: an admitted-texts rule (sources
  triangulated and reviewed before entering the curriculum), lessons
  run lecture→demonstration→lab→rubric with the codebase itself as the
  worked-example corpus, and the owner's accessible reader used to
  study the very architecture text that describes it. For the paper:
  the same evidence discipline that governs code claims now governs
  teaching methods — techniques admitted only with empirical support,
  folklore (learning styles, hour-count mastery rules) explicitly
  barred — and the coursework artifacts double as QA of the equipment
  they're written in.

- **2026-07-22 — Ninth instance: the mute control.** Mid-coursework,
  the owner reported the harvest-approval checkboxes as unclickable;
  instrumented reproduction showed they worked perfectly and were
  simply invisible — a near-black indicator with a black checkmark on
  the dark theme rendered checked and unchecked identical. The class
  now has a second face: beyond controls that fire without visible
  effect, controls whose STATE cannot be read are equally defective —
  a working checkbox the user cannot see is a dead checkbox. Repair
  added redundant visibility: high-contrast indicator, enlarged click
  targets, and a live count on the commit button, so state is proven
  three ways per toggle.

- **2026-07-22 — The breadcrumbs ran the test before the tester could.**
  The owner scheduled twenty minutes to "test the timer"; the pomo
  breadcrumb log had already run the test — a full evening of real
  cycles showing the transition machinery flawless AND a 20-minute
  block stretched to 61 wall-clock minutes across a laptop sleep. The
  tick-counting countdown was replaced with a wall-clock deadline
  kernel (drift-immune by construction, provable headless). For the
  paper: instrumentation converts field time into archival evidence —
  the cheapest QA session is the one the logs already ran, and the
  timer defect class (trusting ticks over clocks) is old enough to
  have a textbook name and still shipped in v1.
