---
name: classroom-code
description: The textbook computer-science rule for ALL projects — SDLC stages in order, pseudocode before code, tests before UI, functional code only (a control that does nothing is a defect), honest reporting, and the paperwork/mirror duty after every change. Use at the start of ANY implementation work, on any project, before the first line of code is written.
---

# Classroom Code — Textbook Computer Science Only

Permanent guardrail, set by the project owner and applying to **every
project, no matter what it is**. The standard: code a university CS
professor would accept in a classroom. No pie in the sky, no "maybe it'll
turn out okay," no cleverness that isn't in a textbook. Real-world,
actionable, standards-anchored computer science (ISO/IEC/IEEE 12207,
IEEE SWEBOK) — the same discipline this project documents in
`docs/SDLC_STATUS.md`.

## The five stages, always in order (each gates the next)

1. 🟥 **Requirements** — state the rule the feature implements in ONE
   plain sentence. If it takes a paragraph, it isn't understood yet.
   Evidence-based features pass the `clinical-science-gate` skill FIRST.
2. 🟨 **Design** — work it out in PSEUDOCODE before any code. When
   following another assistant's blueprint, RE-DERIVE the pseudocode in
   your own words and reconcile differences before building; never
   transcribe on trust. Data gets a schema before it gets a screen;
   migrations are additive; records archive, never delete.
3. 🟦 **Implementation** — functional core / imperative shell: pure,
   UI-free logic in its own module; the UI only calls it. Match the
   codebase's existing idiom. No new dependencies the project's
   constraints forbid (this app's core is standard-library only).
4. 🟩 **Testing** — headless unit tests on the pure core, GREEN BEFORE
   ANY UI. Tests run against isolated fixtures, never live user data
   (`temp_study_db()` here — the live-DB leak happened twice before the
   guard existed). Then verify the wired feature end-to-end (here: a
   smoke test under a real `mainloop()`), and run every static gate the
   project has (design-law linter).
5. 🟪 **Maintenance** — the paperwork IS the deliverable: CHANGELOG,
   wiki/notes, README counts, then commit → push → merge → delete the
   session branch → mirror every clone as an exact copy of main.

## Functional code only

- A button, menu item, or control that does nothing is a DEFECT, not a
  placeholder. Every action produces visible feedback (a ✓, a status
  line, a meter) — invisible success reads as broken.
- No stub files, no dead code left "for later." Removed code's design
  survives in the blueprint docs, not in the source.
- UI paths get verified on the real hardware/display before being
  declared working — headless probes have passed while real clicks
  failed (the A−/A+ Canvas bug).

## Honest reporting (the code-of-ethics clause)

- Report outcomes faithfully: failing tests are reported failing, with
  output; skipped steps are named as skipped; nothing is called done
  until verified.
- No inflation: "enterprise-grade," "production-ready," and "proven"
  are banned unless a standard or study actually says so.
- When work cannot be completed from the current environment (e.g. a
  mirror on another machine), the record says so explicitly and assigns
  it — silence is a false report.
