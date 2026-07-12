# Clinical Review — *Microsoft 365 Copilot At Work* → Sentinel Forge

> Top-down review of the 2-file *Microsoft 365 Copilot At Work*
> (~594K chars, ~13+ chapters) against one question: **what here is
> real, university-teachable computer science that adds to Sentinel
> Forge — additively, no teardown, professor-approvable?** Gate
> honored: reviewed and proven in pseudocode before any feature code.
> Reviewed 2026-07-12. (Five related Copilot files on disk —
> Copilot-for-M365, two GitHub-Copilot-Certification, a redesign essay,
> a copilot-instructions demo — were scanned and are out of scope: same
> deployment/product themes.)

## What the book is

A business/practitioner guide to **deploying and using Microsoft 365
Copilot**: an AI intro, Copilot overview, prompt engineering, security &
Purview planning, rollout planning, licensing, Business Chat, and
department use-cases. Most of it is organizational rollout material —
valuable to an IT admin, not transferable CS.

## Part-by-part verdict

| Area | Verdict | Why |
| --- | --- | --- |
| AI intro, Copilot overview, Business Chat tour | **SKIP** | Product orientation, not algorithms. |
| Security / Purview / compliance / licensing / rollout planning | **SKIP** | Enterprise deployment governance — no place in a local single-user study app; not CS coursework. |
| Department use-cases (Word/Excel/Teams/Outlook Copilot) | **SKIP** | Driving Microsoft's product. |
| **Ch 3 — Prompt Engineering** | **BUILD** | Prompt engineering is a legitimate, taught university CS/AI subject. Its rubric (persona/task/context/format/specificity) maps to a real heuristic **rubric-analyzer** — bounded, testable, additive. **This is the pick.** |

## The BUILD: `lyceum/prompt_coach.py` — a prompt-quality analyzer

**What it is (the CS).** A rubric-linting / heuristic text-analysis
artifact. It scores a prompt against the established prompt-engineering
rubric and returns prioritized, actionable coaching:

```pseudocode
analyze(prompt):
    for component in [role, task, context, format, specific]:
        detected = component.detector(prompt)   # keyword/shape heuristic
    score = weighted sum of detected components   (0..100)
    tips  = suggestions for the MISSING components,
            ordered by weight (biggest win first)
    return {score, band, components{...}, tips[...]}

weights: task 30, role 20, context 20, format 20, specific 10
```

**Why it is professor-approvable and additive.**
- **Academic, allowable, on any campus.** Prompt engineering is taught
  in university AI/HCI/software courses in 2025; a rubric-based
  text-quality analyzer (like a linter or a writing-feedback tool) is
  standard NLP/SE coursework. Nothing proprietary is copied — the
  *concept* (name a role, a task, context, a format) is public canon;
  the implementation is original heuristic code. A professor could
  tutor this in a lab without hesitation.
- **On-thesis for the owner.** Shannon is *learning to work with AI*. A
  coach that scores his prompt and teaches the missing component as he
  types turns the existing AI Chat + Prompt Library into a teaching
  tool — pedagogy, not a gimmick.
- **Architecture.** Pure logic, no Tkinter, deterministic → drops into
  `lyceum/` beside `metrics.py`, `srs.py`, `formula.py`, `readability.py`.
  Additive: a NEW file; plugs into AI Chat / Prompt Library without
  changing their behavior.
- **Safe.** Read-only analysis of a text string. Cannot break, delete,
  or alter anything. Zero risk.

## Proof (pseudocode tested BEFORE any real coding — the gate)

Prototype `scratchpad/prompt_coach_proto.py`, three proofs, **15 checks
all pass**:
1. **Discrimination** — a rich prompt (role + task + context + format +
   specifics) scores 100 / Excellent; a vague one-liner ("tell me about
   stuff") scores 0 / Needs work.
2. **Detectors** — each rubric detector fires on a targeted example
   (role, task, format, context) and correctly abstains when the
   component is absent.
3. **Determinism, ordering, edges** — output is deterministic; tips are
   ordered by the weight of what's missing (a missing 30-pt task is
   coached before a missing 20-pt role); empty input is safe and still
   returns a tip; score bounded 0–100.

## Recommendation & scope

- **Phase 1 (ready to build):** `lyceum/prompt_coach.py` +
  `tests/test_prompt_coach.py`, surfaced as a live **prompt score +
  one tip** under the AI Chat input and in the Prompt Library editor
  ("Prompt quality: 60 · Fair — add a desired format").
- **Phase 2 (deferred):** a "✨ Improve my prompt" button that applies
  the top tip as a template.
- **Out of scope:** everything else in the book (deployment, security,
  licensing, product tours) — taking it would be neither CS nor
  additive.

Gate satisfied: review complete, pseudocode proven (15/15). Awaiting the
Architect's go to begin Phase 1.
