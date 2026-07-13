# Scope Statement — Sentinel Forge, Personal Development

> Written retroactively per the `scope-first` skill (§4): the scope below is
> reconstructed from the shipped truth of the repository and baselined on the
> owner's sign-off. From this point, work is checked against it; changes to
> it are explicit logged decisions (one line in `Assistant-Notes.md` §5),
> never drift. Standards frame: ISO/IEC/IEEE 12207 · SWEBOK · IEEE 29148.

_Baselined: 2026-07-13 · Owner: Shannon Brian Kelley · Maintainers: owner
(architect/QA) + AI coding assistant._

## 1. In scope

- A **native Windows desktop workstation** for one user: reading
  (docx/pdf/md/txt/rtf/html) with accessibility-first rendering and TTS,
  Whisper voice dictation, study workspace (Notes / Topics / Glossary /
  Commentary / Journal / Matrix / Planner), personal-development dashboard
  (goals, habits, streaks, focus, time audit), the finance suite, and the
  Library with zone-tagged excerpts.
- **Neurodivergent-first design laws** (Working-With-The-Architect §3) as
  binding requirements, not preferences.
- **Local-first, single user**: one SQLite file, files never leave the
  laptop, archive-never-delete everywhere.
- The **engineering discipline itself**: functional core (`lyceum/`) with
  headless tests, design-law linter, additive-only migrations, the wiki as
  the system's control loop, three-way mirror (laptop / OneDrive / GitHub).
- Evidence-based behavioral features **only after** passing
  `clinical-science-gate`; study features per `learning-science`.

## 2. Out of scope (explicit)

- **Cloud services, accounts, telemetry, or any network dependency** for
  core function (the localhost platform link is optional and degrades
  gracefully).
- **Multi-user, sync-server, or mobile** versions.
- **macOS / Linux ports** (declared descope for v1.0; Tk keeps the door
  open, nothing is built for it).
- **Executing financial transactions** — the money tools compute and cue;
  they never move money. Bill Sentinel cannot pay bills and says so.
- **Clinical claims or diagnosis** — the software is scaffolding
  (external memory, cues, automation-tracking), never treatment.
- **Non-stdlib runtime dependencies for core logic** (`lyceum/` is
  standard-library only; optional parsers/voice degrade gracefully).
- The **2.0 Tauri re-platform** (parked in `ROADMAP_2.0_GAMIFICATION.md`
  by the "stay the course" decision).

## 3. Acceptance criteria (how "done" is known)

- Every feature ships through the `sentinel-sprint` pipeline: pure kernel →
  headless tests green BEFORE UI → visible feedback wired → smoke under a
  real `mainloop()` → design-law linter green → paperwork current.
- The full suite is green at every merge to `main`; CI proves it on
  Python 3.11 and 3.13.
- The owner can perform each shipped workflow on his real ~1097×617
  display — a control that does nothing is a defect.
- All three mirrors verify byte-identical at the same commit hash.

## 4. Lifecycle target

- **Horizon: 5–10 years** as a daily-use tool, single owner, maintained by
  owner + AI assistant.
- **Stack chosen for that horizon**: CPython + Tkinter + SQLite — all with
  multi-decade stability records; documented runtime (Python 3.11+, 3.13
  tested). Optional dependencies are isolated behind try/except and the app
  runs without them.
- **Rebuildability**: `Rebuild-Blueprint.md` + `Database-Schema.md` +
  README must stay sufficient for a from-scratch reconstruction
  (estimated 8–12 sessions — documentation as disaster insurance).
- **Named structural risk + seam**: the single-file Tk shell
  (~26k lines). The decomposition seam is documented in
  `Feature-Catalog.md` — each `open_*` family lifts into its own module on
  the `lyceum/` pattern when the time comes. Named here while it is cheap.
