---
name: scope-first
description: The scope-and-blueprint rule for ALL projects — no code is written until a scope statement (in-scope, OUT-of-scope, acceptance criteria, lifecycle target) and a blueprint exist at project onset, and every later scope change is an explicit logged decision, never drift. Use at the START of any new project, feature, or research intake — while the first paperwork is being filled out, before the first line of pseudocode.
---

# Scope First — No Blueprint, No Build

Permanent guardrail, set by the project owner and applying to **every
project from now on**. The failure mode this skill exists to prevent has a
name: **churn code** — code written without a defined scope and blueprint,
which wanders, gets discarded, and teaches a lesson instead of shipping a
product. "I learned something" is a fine outcome for an exercise; it is a
DEFECT report for a project.

Standards anchor: software scope definition and change control are core
project processes in **ISO/IEC/IEEE 12207** and the **SWEBOK** (Software
Requirements + Software Engineering Management KAs); requirements
baselining and change management follow **ISO/IEC/IEEE 29148**. The cost
of correcting a wrong direction grows the later it is caught (Boehm,
*Software Engineering Economics*, 1981) — which is why scope is fixed at
the START, while the paperwork is being filled out.

## 1. At project onset — before ANY pseudocode or code

Write the **scope statement** into the project's founding paperwork
(README, charter, or the project's Assistant-Notes). It has four parts,
none optional:

1. **In scope** — what this project WILL do, in plain sentences a
   professor could grade.
2. **Out of scope** — what it will NOT do, stated explicitly. An empty
   out-of-scope list means the scope was not thought through; the most
   valuable engineering decisions are the ones that rule things OUT.
3. **Acceptance criteria** — how we will KNOW each in-scope item is done
   (testable, observable — "the suite proves X", "the owner can do Y on
   his real screen").
4. **Lifecycle target** — how long this must live and who maintains it
   (e.g. "3–5 years, single maintainer + AI assistant"). Technology
   choices must answer to this number: boring, standard, stdlib-first
   stacks for long lifecycles; every dependency is a liability with a
   shorter life than the project.

Then the **blueprint**: architecture + pseudocode for the first build
(classroom-code Stage 2 does the per-feature version; this skill requires
the PROJECT-level plan to exist first — the rooms before the furniture).

## 2. Baseline and change control (anti-churn)

- Once written, the scope statement is the **baseline**. Work is checked
  against it: any task that serves no in-scope item is flagged BEFORE it
  is built, not discovered after.
- Scope may change — projects learn — but a change is an **explicit,
  logged decision**: one line in the project log stating what moved
  in/out and why, approved by the owner. Silent scope growth is the
  drift this skill forbids.
- Research material, book reviews, and proposals are checked against the
  baseline the same way: an idea that is out of scope is PARKED with a
  note, not built because it was interesting. (Evidence claims also pass
  `clinical-science-gate` — separate rule, same gate posture.)

## 3. The lifecycle questions (asked at onset, revisited at each release)

- Where is this in 5 years? Does the stack still run? (Prefer platforms
  with decade-scale stability records; document the runtime version.)
- Can a NEW maintainer rebuild it from the repo alone? (A rebuild
  blueprint + schema doc + README must make the answer yes.)
- Is the data safe over the lifecycle? (Additive-only migrations;
  archive, never delete; documented backup path.)
- What is the single biggest structural risk, and where is the seam to
  fix it? (Name it in the docs while it is cheap to name.)

## 4. Definition of done for this skill's own check

At any project's start, the assistant confirms — in writing, in the
project log — that the four-part scope statement and the blueprint exist
BEFORE implementation begins. If the owner brings work with no scope
statement, the assistant's FIRST deliverable is the scope statement, not
code. On existing projects, the check is retroactive: reconstruct the
scope from the shipped truth, get the owner's sign-off, then hold the
line against it.
