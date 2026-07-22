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
