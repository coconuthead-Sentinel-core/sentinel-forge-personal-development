# Clinical Review — *Power Automate Cookbook / Deep Dive* → Sentinel Forge

> Top-down review of the 4-file Power Automate set (*Cookbook* +
> *Deep Dive* + index, ~749K chars, 30 chapters) against one question:
> **what here is textbook, worldwide-recognized computer science that
> adds to Sentinel Forge — additively, no teardown?** Gate honored:
> reviewed and proven in pseudocode before any feature code.
> Reviewed 2026-07-12.

## What the book is

A hands-on guide to building **Power Automate flows**: triggers (when X
happens), conditions (if this), actions (do that), connectors to
Microsoft cloud services (SharePoint, Forms, Outlook, Teams),
approvals, schedules, loops. Most of it is cloud-connector recipes and
the flow-designer UI — driving Microsoft's product, not transferable CS.

## Part-by-part verdict

| Area | Verdict | Why |
| --- | --- | --- |
| Getting started, connectors (SharePoint/Forms/Outlook/Teams), approvals, business-process flows | **SKIP** | Cloud-service integration + product UI. A local, offline study app has no place for cloud connectors; not CS coursework. |
| Expressions, variables, loops, error handling *inside the designer* | **SKIP** | Teaches Power Automate's own expression language, not portable CS. |
| **The trigger → condition → action model itself** | **BUILD** | This IS the **Event-Condition-Action (ECA) rule engine** — a textbook CS construct recognized on every university campus. A small, correct ECA engine is additive, pure, and testable. **This is the pick.** |

## The BUILD: `lyceum/automation.py` — an ECA rule engine

**What it is (the CS, and why any professor recognizes it).** The
Event-Condition-Action pattern is a *named, canonical* construct taught
worldwide:
- **Active-database triggers** — database-systems courses (a trigger is
  literally an ECA rule).
- **Production rule systems / expert systems** (RETE) — AI courses.
- **Event-driven / workflow architecture** — software-engineering
  courses.
Every workflow product — Power Automate, IFTTT, Zapier — is an ECA
engine underneath. A professor in Dubai, Taipei, Sydney, Bangalore, the
EU, or the Americas identifies ECA on sight; a senior engineer expects
it to be *academically correct*, and this one is.

```pseudocode
Rule = {name, trigger, conditions:[(fact, op, value)], actions:[...]}

evaluate(event, facts, rules):
    fired = []
    for rule in rules:
        if rule.trigger != event:      continue
        if any condition fails:        continue
        fired += rule.actions
    return fired          # PURE: decides what fires, performs nothing

operators: == != < > <= >= contains in
```

**Critical safety property.** The engine only **decides** which actions
should fire — it performs **no** side effects. The imperative shell
decides whether/how to execute them (human-in-the-loop). So the engine
can never break, delete, or alter anything: it is a pure function from
(event, facts, rules) to a list of action names. Malformed rules
(unknown operator, missing fact, wrong shape) are **skipped, never
raised**.

**Why it's additive and useful here.** Sentinel Forge already emits
natural events — a focus block completes, a habit is checked, a streak
is reached, an excerpt is saved — and already has actions — mark a
Scoreboard measure, celebrate, remind. An ECA engine lets the user
declare *"WHEN focus_completed AND minutes ≥ 25, THEN mark my
'studied' measure"* — real personal automation, entirely local. New
file in `lyceum/` beside `formula.py`, `readability.py`,
`prompt_coach.py`; zero edits to existing behavior to exist.

## Proof (pseudocode tested BEFORE any real coding — the gate)

Prototype `scratchpad/automation_proto.py`, three proofs, **22 checks
all pass**:
1. **ECA core** — a rule fires only when its trigger matches the event
   AND every condition passes; a failed condition, a mismatched trigger,
   and a different rule's trigger all behave correctly.
2. **Operators** — every comparison and membership operator
   (`== != < > <= >= contains in`) evaluates correctly, and returns
   False when unmet.
3. **Robustness/safety** — all matching rules fire in definition order;
   disabled rules skip; no-match returns empty; **malformed rules and a
   non-dict entry are skipped without crashing**; missing fact / unknown
   operator → no fire; deterministic; an `explain()` helper reports why
   a rule did or didn't fire.

## Recommendation & scope

- **Phase 1 (ready to build):** `lyceum/automation.py` +
  `tests/test_automation.py`, plus one demonstration wiring — e.g. a
  built-in rule *"WHEN focus_completed AND minutes ≥ 25 → suggest
  marking the Scoreboard"* surfaced as a status suggestion (human
  approves the action). Smallest safe surface, engine stays pure.
- **Phase 2 (deferred):** a small rules editor (add/enable/disable
  personal WHEN→THEN rules) persisted in study.db.
- **Out of scope:** cloud connectors, the flow-designer UI, Microsoft
  service integrations — neither CS nor local-first-additive.

Gate satisfied: review complete, pseudocode proven (22/22). Awaiting the
Architect's go to begin Phase 1.
