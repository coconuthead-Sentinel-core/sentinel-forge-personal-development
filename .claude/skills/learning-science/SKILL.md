---
name: learning-science
description: The evidence-based learning rule for ALL projects — study features, review scheduling, teaching explanations, and learning workflows use only techniques with real empirical support (retrieval practice, spacing, worked examples with fading) and never encode known neuromyths (learning styles, the 10,000-hour rule). Use when building or modifying any study/learning/review feature, when scheduling practice, or when explaining concepts to the owner.
---

# Learning Science — Evidence-Based Techniques Only

Permanent guardrail, companion to `clinical-science-gate` (which governs
whether a claim may be cited at all; THIS skill governs which learning
techniques may be built or taught). Applies to every project. The
standard is the same professor test: a cognitive-psychology instructor
could assign this list from the textbook without correction.

## ADMITTED techniques (build and teach these)

1. **Retrieval practice / practice testing** — recalling from memory
   beats re-reading (Roediger & Karpicke, 2006, Psychological Science;
   rated HIGH utility in Dunlosky et al., 2013, Psychological Science in
   the Public Interest). Already implemented here: Daily 10 Goals
   (recall from memory), SRS review.
2. **Spacing / distributed practice** — spread study over time (Cepeda
   et al., 2006, Psychological Bulletin meta-analysis; HIGH utility in
   Dunlosky et al., 2013). Implemented here: FSRS scheduling
   (`lyceum/srs.py`) — the scheduler IS the spacing policy; do not
   hand-roll intervals around it.
3. **Worked examples with fading, for novices** — novices learn faster
   studying worked solutions than solving cold (Sweller's cognitive
   load theory; Atkinson, Derry, Renkl & Wortham, 2000, Review of
   Educational Research). Teach new material as: full worked example →
   partially completed → learner completes → learner solves.
4. **Expertise reversal — fade the scaffolds** — guidance that helps a
   novice becomes redundant and can HURT once skill grows (Kalyuga,
   Ayres, Chandler & Sweller, 2003, Educational Psychologist). As the
   owner's skill increases on a topic, reduce worked examples and shift
   to retrieval and problem-solving; a fixed scaffold forever is a bug.
5. **Metacognitive checks / judgment of learning** — self-assessments
   made immediately after study are inflated (the illusion of knowing);
   DELAYED self-testing gives honest signal (Nelson & Narens, 1990
   framework; Dunlosky et al., 2013). Before "I know this": close the
   material, wait, retrieve.
6. **Interleaving** — mixing problem types outperforms blocking for
   discrimination-heavy skills (MODERATE utility in Dunlosky et al.,
   2013 — label it moderate, not proven-for-everything).

## BLOCKED neuromyths (never build, never teach, never encode)

- **Learning-styles matching** ("he's a visual learner, so teach
  visually") — no adequate evidence that matching instruction to a
  preferred style improves learning (Pashler, McDaniel, Rohrer & Bjork,
  2008, PSPI). Offering multiple MODALITIES for ACCESS is fine (see
  below); prescribing by "style" is the myth.
- **The 10,000-hour rule** — deliberate practice explains ~4% of
  performance variance in education and <1% in professions (Macnamara,
  Hambrick & Oswald, 2014, Psychological Science meta-analysis).
  Practice matters; the magic number is popularization, not science.
- **Multiple-intelligences instruction** — no controlled evidence that
  MI-based instruction improves outcomes; treat as unvalidated framing.
- Folk claims of the "10% of the brain" / "right-brained learner" type.

## The access-vs-efficacy distinction (do not confuse these)

Accommodations — TTS read-aloud, dictation, larger text, line spacing,
predictable layout, chunking — are ACCESS tools. They are justified by
accessibility standards and personal fit (WCAG; BDA guidance), and they
do NOT need learning-efficacy trials to be legitimate, the same way
glasses don't need an RCT. Never claim an access tool improves
learning outcomes unless a study actually shows it; never drop an
access tool because it "only" provides access or comfort. (On the
record here: specialized dyslexia fonts show no objective reading
benefit — Wery & Diliberto 2017; Kuster et al. 2017 — and OpenDyslexic
stays available as the owner's honored preference.)

## Application procedure

1. New topic for the owner → worked example first, small chunks, then
   fade (techniques 3 → 4).
2. Material worth keeping → into spaced retrieval (FSRS), not re-reading
   (techniques 1 → 2).
3. "Do I know it?" → delayed retrieval check, never same-moment
   confidence (technique 5).
4. Any proposed study feature or teaching method not on the admitted
   list → run it through `clinical-science-gate` before building.
