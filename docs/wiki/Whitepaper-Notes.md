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
