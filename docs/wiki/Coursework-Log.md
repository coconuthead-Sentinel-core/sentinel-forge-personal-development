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
