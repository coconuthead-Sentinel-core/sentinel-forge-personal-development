---
name: clinical-science-gate
description: The evidence admission rule for ALL projects — no claim, citation, feature rationale, or research summary enters a repo without verification against real, current (2026) peer-reviewed literature. Use whenever handling research material, evidence claims, "studies show" statements, citations, or any feature justified by science — BEFORE the claim touches code, docs, or commit messages.
---

# Clinical Science Gate — Strict Clinical Science 2026

Permanent guardrail, set by the project owner and applying to **every
project, no matter what it is**. The standard: if a university professor
bound by a code of ethics could not sign this claim without answering to
the board of trustees, it does not enter the repo.

## The rule

A claim is admitted ONLY when all four checks pass:

1. **The citation is real.** Search for it and confirm the paper exists —
   author, year, journal, and finding all match. This project has already
   caught fabricated references inside otherwise-plausible research
   documents ("Pijpker et al. 2025", "Cortese et al. 2024 JAMA
   Psychiatry" — neither exists). AI-generated research summaries mix
   genuine science with invented sources IN THE SAME PARAGRAPH; the only
   defense is checking every reference yourself.
2. **The finding says what the claim says.** Effect sizes, populations,
   and outcomes as published — no rounding a "small effect in children"
   up to "proven to work." When the real number is small (e.g. digital
   ADHD interventions, SMD ≈ 0.2), the docs say small.
3. **The label matches the evidence tier.**
   - Peer-reviewed RCT / meta-analysis → may be cited as evidence.
   - Practice guideline / standards body (WCAG, BDA) → cite as guideline.
   - Trade book / industry method (5-Second Rule, V2MOM) → label it
     trade literature; name the plausible mechanism if a real one exists;
     NEVER the word "proven."
   - No source → the claim does not ship.
4. **No clinical claims, ever.** Software here provides scaffolding —
   external memory, cues, structure — assistive like glasses or a hearing
   aid. It never diagnoses, never treats, and never assigns anyone a
   condition. Diagnoses belong to clinicians.

## Procedure when handed research material

1. Extract every citation and every codebase claim it makes.
2. Verify citations (web search); verify codebase claims against the
   actual code — audits written against READMEs or memory drift.
3. Record the verdict in the project docs (this repo's model:
   `docs/wiki/Review-ImprovementAudit.md` — a citation table with
   ✅ real / ❌ not found, premises checked, per-item adopt/reject).
4. Adopt IDEAS that survive; never copy the document's prose or code
   (supplied sample code has contained real bugs).
5. Fabricated citations are kept out and named in the record, so the
   next assistant knows they were already caught.

## Failure examples already on the record (keep them out)

- "Specialized dyslexia fonts are proven" — FALSE as stated; controlled
  studies (Wery & Diliberto 2017; Kuster et al. 2017, Annals of
  Dyslexia) found no objective benefit. Spacing helps (Zorzi et al.
  2012, PNAS); fonts are honored as personal preference, labeled as such.
- "Writing goals programs the subconscious" — restated as the
  retrieval-practice effect (Roediger & Karpicke 2006).
- "Program your reticular activating system" — restated as goal-priming
  and motivation (Oettingen 2014).
