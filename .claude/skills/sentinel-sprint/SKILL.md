---
name: sentinel-sprint
description: Build a new Sentinel Forge capability the proven way — extract a pure kernel, test it headless, wire it into the Tk shell with visible feedback, smoke-test under a real mainloop, then log and mirror. Use when adding any feature to sentinel_personal_development.py that starts from a source (a book to mine, a feature request, a design idea).
---

# Sentinel Sprint

The repeatable pipeline this project has shipped ~8 features with (FSRS, the
formula engine, readability, the prompt coach, the ECA engine, password
strength, entry-parse, legibility). Follow it in order — each step gates the
next. Nothing ships that skipped a step.

## When to use
Any new capability for **Sentinel Forge — Personal Development** derived from a
source: a book to mine, a feature request, or a design idea.

## The pipeline
1. **Extract the rule.** Name the pure algorithm or decision the feature needs.
   Keep it UI-free and describable in one sentence.
2. **Build the kernel** in `lyceum/<name>.py` — no Tkinter, no I/O it doesn't
   own. Pure functions / small dataclasses. This is the part that gets tested.
3. **Test it headless.** Add `tests/test_<name>.py`; run
   `python -m unittest discover -s tests`. Must be **green before any UI**.
   - Touches the database? Wrap it in `study_db.temp_study_db()` — never the
     live DB. (`db_location.assert_not_live_db` will fail loudly if you slip.)
4. **Wire into the shell.** Call the kernel from
   `sentinel_personal_development.py`. Every action needs **visible feedback**
   (a "✓ Saved", a status line, a meter) — invisible success reads as broken.
5. **Smoke-test under a real `mainloop()`.** Worker `after()` callbacks
   silently fail without one (learned twice; now standard).
6. **Obey the design laws** (`docs/wiki/Working-With-The-Architect.md` §3):
   size windows from `winfo_screenwidth/height`; tuple `pady` only in
   `.pack()/.grid()`; numbers need a picture; files archive, never delete.
   Run the design-law linter (`python -m unittest tests.test_designlaws`).
7. **Log it.** Append to `CHANGELOG.md`, one to three sentences to
   `docs/wiki/Whitepaper-Notes.md`, and a `§5` entry in
   `docs/wiki/Assistant-Notes.md`.
8. **Ship it.** Branch per session → commit → push → **pull BOTH clones**
   (`Desktop\Sentinel-Forge` + the OneDrive clone) → delete the branch.

## Guardrails
- Honesty over polish — no "enterprise-grade" / "production-ready".
- One primary action per screen; five major choices or fewer (ADHD load).
- Lead with the outcome; one clarifying question maximum.
- Verify audio/UI paths on the **real hardware** before trusting them.
