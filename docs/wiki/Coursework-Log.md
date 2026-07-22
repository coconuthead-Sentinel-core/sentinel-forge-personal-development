# Coursework Log — the Forge Classroom

> The lab book for the shop's classroom: which texts were admitted,
> what was taught, how it was taught, and what the student demonstrated.
> Method: the `archivist-of-wisdom` rule (lecture → demonstration →
> lab → rubric → ticket), teaching techniques restricted to those with
> real empirical support per the `learning-science` guardrail.
> Instructor's private notes live in the foreman's journal; THIS page
> is the front-office record. Lecture-note tickets in the student's own
> words live in the app's Prompt Library, timestamped.

**Student:** Shannon Brian Kelley (Falcon One) — architect/QA,
self-directed adult learner; accommodations in use: chunked lessons
(≤3 focus points), worked examples anchored to his own codebase,
retrieval practice over re-reading, spaced one-chapter sessions,
consistent terminology, short-line formatting, journey-method
mnemonics (method of loci — the memory palace is the Forge itself).
**Instructor:** Claude, shop foreman & Archivist of Wisdom.

---

## Text admitted 2026-07-21 — *Fundamentals of Software Architecture*
(Richards & Ford, O'Reilly 2020; owner's Bookshare accessible copy,
loaded into the Forge's own Library — the reader reads its own
curriculum.) Verdict: aligned with the SWEBOK architecture knowledge
area; practitioner text matching the owner's actual role (architect
directing an engineer). Reading order set: Ch. 4 → 2 → 3 → 19 → 6 → 21.

### Lesson 1 — Ch. 4, Architecture Characteristics (2026-07-21)

**Three walk-away points (the chapter's core, instructor's words):**
1. A *feature* is what the system DOES; an *architecture
   characteristic* is what the system must BE (accessible, testable,
   maintainable). Characteristics outrank features and shape structure.
2. Characteristics split into *explicit* (written down) and *implicit*
   (expected but unwritten). Unwritten promises are risks; naming them
   is architect's work (feeds the ADR habit, Ch. 19).
3. There is no perfect architecture — only *least-worst* trade-offs;
   supporting one characteristic degrades another. Keep the driving
   set SMALL.

**Journey markers (memory palace = the Forge):** front-door sign =
characteristics/"-ilities" · workbench drawers = modularity ·
toolbar dock stations = coupling (the seven enrollment bugs were
coupling lessons) · front-office filing cabinet = ADRs · field sheet
on the wall = fitness functions.

**Lab (student turn-in):** Prompt Library entry — Title
`FoSA Ch.4 — Architecture Characteristics`, Response in the student's
own prose (generation effect). Doubles as live QA of the repaired
Prompt Library equipment.

**Rubric (stated before the test, binary):**
- [ ] R1 States feature-vs-characteristic distinction from memory
- [ ] R2 Names the Forge's driving characteristics (his call, ~3)
      and which wins a collision, with a reason
- [ ] R3 Recites the five journey markers unprompted
- [ ] R4 Survives one counter-question (Disputatio) without notes

**Status:** student reading; retrieval scheduled on his return, and a
spaced re-check due at the NEXT session's start (successive relearning
— one correct recall today does not close the line; it takes several
correct retrievals on separate, spaced occasions).

**Mastery standard (recorded for every future lesson):** a question is
"answered appropriately" when the student can (1) state the principle,
(2) ground it in a case the instructor did not supply, and (3) hold it
under one challenge. No fixed repetition count is prescribed — the
10,000-hour rule and similar folklore are banned by the
learning-science guardrail; the evidence supports spaced successful
retrievals plus transfer, judged per student per concept.

**Study-tool mapping (set mid-lesson at the student's own question —
metacognition, graded up):** Harvest terms = working concordance ·
Glossary = key terms defined in the student's OWN dictated words
(comprehension counts, spelling doesn't — standing accommodation) ·
Topics = highlighted passages filed one-per-concept · Commentary = the
student's voice responding to the text (no pasted third-party
commentaries — Bookshare terms + learning integrity) · Study Notes =
draft prose · Prompt Library = final ticket · Journal = one reflective
close line. Key terms assigned for Ch. 4: architecture characteristic;
functional requirement; explicit vs implicit; operational/structural/
cross-cutting (families only); trade-off; least-worst. A true
concordance feature is DEFERRED under the freeze — logged here as a
decision, not drift.

**Canary run — Harvest terms vs Ch. 4 assignment (2026-07-21):**
student probed the tool before trusting it (correct canary practice).
Finding: harvester is WHOLE-DOCUMENT scoped — returned 7 real
term-definition pairs from across the book (plus one noise item,
"ThoughtWorks," from the endorsement pages) and none of the assigned
Ch. 4 terms. Ruling: verification PASS, validation MISS — not a
defect; the tool met its built requirement. Enhancement DEFERRED under
the freeze and logged as a decision: chapter-scoped harvest +
instructor-seeded term list. Classroom procedure stands: assigned
terms are found by reading and dictated into the Glossary; approved
harvest terms from later chapters enter the review deck as preview
vocabulary (spacing effect). The approve-to-add checklist is noted as
correct human-in-the-loop design — the reason noise cannot reach the
Glossary unapproved.

**ADR-2026-07-22 — Concordance integration: DEFERRED (upgraded from
the earlier one-line deferral; analysis run as a live Ch. 4 worked
example, proprietor's question).** Options costed: (a) external
freeware concordancer beside the app — ~1 hr, zero regression;
(b) in-house pure-python KWIC kernel in lyceum/ — one sprint, keeps
the standard-library-only law, additive, low regression; (c) third-
party code integration — REJECTED permanently (violates the no-new-
dependencies constraint regardless of freeze). Benefit judged honestly
at ~+0.2 Richter, not +1: Search + Harvest + Glossary already cover
most of the study value; driving characteristic (accessibility) is
not advanced by corpus tooling. Decision: defer; revisit when the
freeze lifts IF coursework shows repeated need for in-context term
lookups; then option (b) only. Textbook note recorded for the student:
unrequested polish is gold plating and grades DOWN; the decision
record itself is what grades UP.

**Exam — Ch. 4 oral retrieval, attempt 1 (2026-07-22, after two
listen-throughs with follow-along highlight):** R1 HALF-MET (concordance
correctly classed feature/gold-plating; floating toolbar mislabeled a
characteristic — corrected: widgets are features, the quality served —
accessibility — is the characteristic). R2 NOT YET (characteristics
unnamed; instructor's answer given: accessibility, testability,
maintainability — accessibility wins collisions, evidenced by the
weekend's triage order; student independently surfaced the
vision-vs-feasibility tension unprompted — transfer noted). R3 NOT YET
(honest blank, declared without bluffing — the honored behavior;
compact retelling given for re-encoding: door=characteristics,
drawers=modularity, dog=coupling, cabinet=ADRs, wall=fitness
functions). R4 deferred — Disputatio converts to instruction when
answers aren't standing. Grading uninflated per the honesty clause.
**Re-test scheduled: NEXT session opener, same three questions, cold,
before any new material** (successive relearning). Student's
"workplace operability 2026" question added to the Schedule column for
its own session with the interview question bank.

**Accommodation logged (2026-07-22, student-engineered):** Ch. 4
converted to sectioned audio via Speechify — counts as class time
(access accommodation + additional spaced pass + student's own
re-sectioning = elaborative organization; value framed per the
learning-science law as ACCESS, not "learning styles"). Student
independently connected his unambiguous-language instinct to the
book's own argument for renaming "nonfunctional requirements" to
"architecture characteristics" — transfer, unprompted, noted for the
re-test. Next classroom activity queued at student's request: review
a REAL job posting as a requirements document (Lectio → evidence
mapping → application drafting against the question bank).

## Texts admitted 2026-07-22 — professional-development shelf
(Practitioner wisdom, NOT peer-reviewed science — never cited as
evidence; used for campaign strategy and communication craft.)
- *Start With Why* (Sinek; owner's Bookshare copy) — Golden Circle
  applied to the portfolio: READMEs and interview answers lead with
  the verified WHY (accessible workstation built from lived
  disability + 30 years of care work). Trust = the honesty ledger.
- *Earn What You're Really Worth* (Tracy 2012; owner's Bookshare
  copy) — job campaign frame: readiness = decision + competence
  evidence (already banked); value priced from documented output
  (W30 receipt method); search run as a disciplined full-time job;
  multiple-careers norm reframes the age question (a 50s transition
  is scheduled, not late); Ch.5 informational-interview script queued
  as a drill. LIMITS on the record: 2012 market stats stale; no
  disability-disclosure or healthcare→tech specifics in either text.
Queued next: student brings a REAL job posting → reviewed as a
requirements document against the question bank and the WHY line.

**WHY drill — first draft delivered (2026-07-22):** student dictated
an honest away-from WHY unprompted; coached through one Disputatio
pass into its toward-form (care work continued by different
instrument — accessibility software) without discarding the private
version. Both forms retained: private = fuel, public = direction.
Student to dictate his own final public sentence; it then leads the
flagship README and anchors the question bank. Further PD texts
incoming at student's request — admission gate applies per text.

- *7 Strategies for Wealth & Happiness* (Rohn 1985; owner's Bookshare
  copy) — admitted to the PD shelf with the reality filter applied:
  DURABLE = written/dated/reviewed goals, self-education as a system,
  personal development as the asset, time discipline, association;
  DATED/WISHFUL = 1985 financial arithmetic and wealth-promise framing
  (noted, not followed; finance belongs to licensed advisors).
  Applications filed: written 5-year development plan as an interview
  artifact; the dashboard framed as Strategy Three compiled into
  software; the admission gate recognized as Rohn's "stand guard at
  the door of your mind" operationalized. Interview-discretion
  coaching: private WHY = fuel, public WHY = direction; student's HR
  sentence upgraded (strong verbs, evidence named, employer's need
  answered). Student's own discretion instinct predicted the text's
  counsel — transfer noted.

- Ziglar shelf admitted 2026-07-22 (PD shelf, reality-filtered):
  *See You At The Top* — EXCERPT ONLY (ch. 3-4 self-image; two
  duplicate files on disk, one deletable at owner's leisure; full text
  welcome if wanted): self-image lag named as the interview-posture
  issue; updated by drill, not waiting. *Selling 101* — strongest
  campaign fit: job search mapped to the sales process (prospecting =
  target companies; needs analysis = read the posting for employer
  pain; presentation = resume as THEIR solution; close = ask plainly;
  follow-up = the unsent thank-you note). ASSIGNED READING before the
  first application ships: the call-reluctance chapter → scheduled
  application blocks with pre-drafted materials. *Better Than Good* —
  purpose/passion long-form; honestly labeled openly faith-based
  (private fuel category, owner's use; stays out of repo and
  interview either way). Cross-shelf synthesis filed: service is the
  offer, integrity is the proof, fuel stays private. Delight noted:
  the dashboard's evening nudge already implements Ziglar's
  night-before rule — the shop predates the classroom.

- *Awaken the Giant Within* (Robbins; owner's Bookshare copy, full
  text across three part-files) — admitted to the PD shelf under the
  STRICT gate (mind claims): SURVIVES = motion-before-study state
  shifting (extra-relevant with ADHD), reframing (folk cognitive
  reappraisal), decision-vs-preference, CANI/kaizen; OVERSOLD =
  instant-transformation promises, NLP-derived conditioning machinery,
  anecdote-as-proof; NOT clinical guidance for ADHD/dyslexia/
  dysgraphia — accommodations stay evidence-and-engineering.
  Recognitions filed: owner's logged exercise block → bug-4 find =
  the state chapter executed with a timestamp; the Session Start
  cognitive-load slider + zones = state management already built into
  the flagship. TRANSITION READINESS RUBRIC issued (binary): R1 state
  recovery ✅ · R2 setback-to-ticket conversion ✅ · R3 calm public
  WHY ◐ drafted · R4 action under reluctance ⬜ (drill = Selling 101
  call-reluctance chapter + scheduled application block). Career arc
  affirmed for the 5-year plan (junior → certificate → senior);
  "senior" lives in the plan, never on the current resume.

**R3 update (2026-07-22):** student dictated the full transition
statement in his own words unprompted — toward-form arrived naturally
("continue to work in the field of health care" via software). Forged
to one sentence with three edits shown (hedges cut; serving-healthcare
promoted to spine; project count flagged for defensibility — owner
said 23, audit records 27; owner to pick his number). Survives the
"did you write the code?" follow-up by construction. R3 marked MET
pending owner's final dictation pass; then it leads the flagship
README. Remaining rubric line: R4 (application sent in its scheduled
block).

**Live ticket reviewed (2026-07-22):** WelbeHealth AI Engineer I
(remote, $90-119k) worked as a requirements document — full evidence
map, gates named honestly (bachelor's REQUIRED = hard gate, truthful
"No" always; solo-Python = closable Year-1 gap), truthful-checkbox
inventory, and campaign next-actions (scoped local RAG learning
project, Azure AI-900, LinkedIn prerequisite, application-block
drafting). Board filed: Portfolio\boards\
2026-07-22_WelbeHealth_AI_Engineer_I_Ticket_Review.md. Mission-fit
finding: the posting's population IS the owner's 30-year patient
population — the WHY sentence lands verbatim.

**Second live ticket + skills matrix (2026-07-22):** Ursa Space Jr AI
Engineer reviewed — currently the campaign's strongest requirements
fit (no degree gate; Human-on-the-Loop stewardship model matches the
owner's existing daily practice; MCP/agentic tooling and co-pilot
experience are named requirements he meets; "very desirable" list —
agent harnesses, evals, agentic memory, cost measurement — maps to
LLM Evaluation Harness v1.0, AI_Memory_Core, and the portfolio
audit). AI-honeypot detected in the posting's cover-letter
instructions (bait line for LLM-written letters) — flagged to owner;
all cover letters will be dictated in his own voice. Completed-
projects sweep (owner-ordered) surfaced RAG Reference Implementation
v1.0 + LLM Evaluation Harness v1.0 → WellBe board CORRECTED
(RAG/embeddings/vector checkboxes are truthful; engineer's earlier
"None" assessment logged as an error per the honesty clause). Job
Skills Matrix board filed: Portfolio\boards\
2026-07-22_Sentinels_Forge_Job_Skills_Matrix.md — extend one column
per posting.

**Third live ticket (2026-07-22):** FocusKPI Junior AI/ML Engineer
(remote contract/internship) — middle fit: degree hard-gate + first
posting to test CLASSICAL ML hands-on (real gap; EARP's
IsolationForest = exposure only), but strongest FastAPI/SQL alignment
and the lowest-stakes entry ramp (paid internship). Their required
3-6 paragraph project write-up recognized as the shop's ticket format
— assigned as a drill regardless of application (Sentinel or Imprint
as subject; the "your specific contribution" section carries the
attribution sentence). Matrix updated; ranking after three: Ursa →
FocusKPI → WellBe on requirements. New build-list item: scoped
classical-ML learning lap (scikit-learn on the owner's own time_log
data).

**Fourth live ticket (2026-07-22):** Continued (EdTech) AI Engineer —
honest verdict: NOT qualified today (mid-level: 3-5 yrs + enterprise
production deployment; declining protects campaign credibility).
Three yields banked: (1) first posting with an EXPLICIT
portfolio-instead-of-degree clause ("or equivalent demonstrated
experience through portfolio work") — the no-degree lane is a
documented market reality, filed as standing intelligence; (2) the
posting archived as the Year 3-5 TARGET PROFILE inside the five-year
plan — annual reviews measure against it; (3) their cover-letter
prompt ("a book you learned something from") = the coursework
question verbatim — study log is market-graded currency. Matrix
updated. Ranking unchanged: Ursa → FocusKPI → WellBe (apply-tier);
Continued filed as aspirational-tier, not applied.

**Fifth live ticket — THE BULLSEYE (2026-07-22):** Aline, Junior
Agentic (AI) Engineer, remote $65-80k. The predicted convergence
posting: senior-care mission (owner's 30-year population by name) +
explicit portfolio lanes on BOTH the degree and experience gates.
Role inventory matches the archive by name: retrieval layer
(chunk/hybrid/rerank/citations) = RAG Reference Implementation; eval
stack (golden sets, LLM-as-judge) = LLM Evaluation Harness; Claude
Agent SDK + MCP + human-in-the-loop = daily practice; LLM failure
modes incl. injection = lived (the Ursa honeypot catch); HIPAA
practiced. Required gap: NumPy/Pandas/Scikit-learn comfort —
classical-ML learning lap PROMOTED TO PRIORITY (scoped project,
scope-first applies; owner's own time_log as dataset). Campaign
ranking: Aline #1 · Ursa #2 · FocusKPI #3 · WellBe mission-reserve ·
Continued aspirational. Matrix updated.

**Sixth live ticket (2026-07-22):** Cav, Junior Fullstack + AI
Developer (remote, compliance automation / GRC). Friendliest gates of
all six (0-2 yrs with projects counted; degree in desired-tier only;
mentorship-driven). Star witness identified: EARP = a miniature
Compliance OS (NIST AI RMF scoring, policy gates, hash-chained audit
history, retention/legal holds, React+TS dashboard, FastAPI, 378
assertions) — the project write-up subject for this target. Bonus
story: healthcare = the canonical High Reliability Organization; 30
years INSIDE an HRO's compliance culture. Honest gaps: solo React
(directed only), PyTorch/TensorFlow none, salary unlisted. Ranking
now: Aline #1 · Ursa #2 · Cav #3 · FocusKPI #4 · WellBe reserve ·
Continued aspirational.

**LinkedIn review (2026-07-22):** profile exists and is stronger than
expected — About, skills list, GitHub link, open-to targets all
present and largely audit-clean. Five fixes issued, ranked: (1) ADD
the AI-attribution sentence — LinkedIn must match GitHub's "built in
collaboration with Claude AI" or the gap reads as concealment; the
method is a selling point for AI-first employers; (2) headline
"AI Systems Engineer" softened to a defensible independent-developer
form; (3) add the three campaign exhibits missing from Projects (RAG
Reference Implementation, LLM Evaluation Harness, flagship
accessibility dashboard); (4) number consistency — 25 vs 30 years
unified, 27 projects / 174.3 audited hours cited; (5) trims: "cloud-
based" softened, NLCA dedupe, Experience section to be verified.
Owner to apply edits in his own pass; prerequisite nearly closed.
