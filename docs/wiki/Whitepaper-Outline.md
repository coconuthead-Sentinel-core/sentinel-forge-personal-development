# White Paper — Skeletal Outline (develop slowly; textbook structure)

> Working title: **"Neurodivergent-First by a Neurodivergent Architect:
> Designing, Testing, and Shipping a Local-First Personal-Development
> Workstation with AI-Assisted Development."**
>
> Structure follows the standard technical-report / experience-paper
> form a university instructor expects (adapted IMRaD). Each section
> lists: *what goes here* (the textbook convention), *what a grader
> looks for*, and *evidence already on hand*. Status boxes make
> progress visible. Raw material accumulates in
> [Whitepaper-Notes](Whitepaper-Notes.md); flesh sections out from
> there, slowly, one at a time.

---

## Front matter 🔲

- **Title, author, date, version.**
- **Abstract (write LAST):** 150–250 words — problem, approach, what
  was built, how it was evaluated, one-sentence takeaway.
- **Keywords:** accessibility engineering; neurodivergent-first design;
  local-first software; AI-assisted development; spaced repetition;
  desktop applications.
- *Grader looks for:* an abstract that summarizes results, not
  intentions.

## 1. Introduction & Motivation 🔲

- The problem: mainstream productivity tools impose cognitive costs on
  ADHD/dyslexic/dysgraphic/dyscalculic users; the author is the domain
  expert on the user.
- The thesis: accessibility requirements stated as **engineering laws**
  (not accommodations) produce a better product for everyone.
- Contributions list (bulleted, verifiable): the workstation, the
  design-law catalog, the AI-assisted architect/implementer workflow,
  the replication across three dashboards.
- *Grader looks for:* a falsifiable thesis and a numbered contributions
  list. *Evidence on hand:* README "Why it exists"; Working-With-The-
  Architect design-law table.

## 2. Background & Related Work 🔲

- Prior tools (Anki-class SRS, planners, money apps) and why each
  misses the neurodivergent case.
- Research anchors, used honestly: Self-Determination Theory, the Hexad
  user-type model, FSRS scheduling literature, W3C cognitive
  accessibility guidance, BDA dyslexia style guide.
- *Grader looks for:* citations that are load-bearing, not decorative;
  vendor market numbers flagged as directional (see
  ROADMAP_2.0_GAMIFICATION.md source notes).

## 3. Requirements & Design Laws 🔲

- The accessibility profile → requirement → law → feature chain.
- The catalog: one primary action per screen; numbers need a picture;
  rescue never shame; archive never delete; visible confirmation for
  every action; window-fit from screen metrics; reading surfaces honor
  the user's font.
- *Grader looks for:* traceability — each law traced to a need and to
  the feature that implements it. *Evidence:* Working-With-The-
  Architect.md; Feature-Catalog.md.

## 4. System Design & Architecture 🔲

- Functional core / imperative shell; `lyceum/` package map; SQLite
  with an atomic `transaction()` primitive; additive-only migrations.
- The local-first stance (privacy, no keys, loopback-only AI) and the
  context-source seam (web / OneDrive / attachments feed a small local
  model).
- One diagram (block architecture) + one table (module
  responsibilities).
- *Grader looks for:* a diagram they can quiz you on. *Evidence:*
  Architecture.md; Codebase-Map.md; docs/SRS_MODULE.md.

## 5. Implementation Notes 🔲

- Selected case studies, one page each, problem → decision → result:
  (a) FSRS integration with proven review atomicity and deterministic
  scheduling; (b) the document writer (model text → real .docx/.xlsx
  with live formulas); (c) the read-aloud stack and the winsound
  regression; (d) the archive-not-delete Library workflow.
- *Grader looks for:* honest trade-off discussion, not a feature tour.
  *Evidence:* Former-Bugs-and-Regressions.md; commit history.

## 6. Evaluation 🔲

- **Quantitative:** 172 headless automated tests (atomicity, rollback,
  determinism, idempotency); test-growth timeline 24 → 34 → 172.
- **Qualitative:** longitudinal single-user field use (the author,
  daily); documented defect discoveries and turnarounds.
- **Replication:** the same assistant design ported to two more shipped
  dashboards (Imprint, strata-console) with their own suites.
- Threats to validity (textbook requirement): n=1 user, author-as-
  evaluator bias, single platform.
- *Grader looks for:* the threats-to-validity paragraph — its presence
  is what separates a paper from marketing.

## 7. The Development Methodology (the novel part) 🔲

- Architect/QA human + AI implementer: relay-memo specs
  (RELAY-SRS-001 as the exhibit), human-in-the-loop merge boundaries,
  three-way mirroring, branch hygiene, headless verification under a
  real mainloop.
- What the human uniquely contributed (scope, judgment, honesty
  charter, acceptance) vs. what the AI contributed (implementation,
  tests, regression archaeology).
- *Grader looks for:* candor about the division of labor — this section
  is unusual and must be defensible line by line.

## 8. Limitations & Future Work 🔲

- Declared descopes (macOS/Linux, platform two-way sync); the parked
  2.0 re-platform decision and WHY staying the course was chosen
  (teardown-avoidance reasoning — cite the instructor's principle).
- Future: the gamification engine per the 90-day plan; FSRS parameter
  optimization after ~1,000 logged reviews.

## 9. Conclusion 🔲

- Restate thesis + strongest evidence in one paragraph. No new claims.

## References 🔲

- Format consistently (IEEE or APA — pick one, stay with it).
- Candidates already identified: SDT; Hexad (Waterloo); FSRS/py-fsrs;
  W3C cognitive accessibility; BDA style guide; CFPB financial
  well-being scale.

## Appendices 🔲

- A: design-law table (full). B: test inventory by suite. C: the
  RELAY-SRS-001 spec (as a workflow exhibit). D: screenshots.

---

**How to develop this slowly (the classroom way):** one section pass
per sitting, never more. Draft → let it rest → revise on the next
pass. Sections 3, 4, and 6 first (they're mostly assembled from
existing evidence); Abstract absolutely last. Disclosure line per the
owner's standing rule: the README's public framing, nothing beyond it.
