# Engineering Project Build Checklist — Sentinel Forge rebuild

- Project name: Sentinel Forge — Personal Development
- Build name: Full reconstruction (disaster-recovery rebuild)
- Owner: Shannon Brian Kelley (architect/QA) + AI coding assistant (implementer)
- Date: 2026-07-11
- Status: approved (standing paperwork; refresh on each release)

## Build checklist
- [x] Project objective is defined — restore functional parity with commit-of-record (see 08).
- [x] Build scope is defined — 9 phases per Rebuild-Blueprint §8 (foundation → toolbar/polish).
- [x] Required inputs are listed — this pack, `docs/wiki/Rebuild-Blueprint.md`, `docs/wiki/Database-Schema.md`, README, `requirements.txt`.
- [x] Owners are assigned — Shannon: scope, acceptance, merge; assistant: implementation, tests.
- [x] Architecture documents are available — `docs/wiki/Architecture.md`, Codebase-Map, blueprint.
- [x] Dependencies are identified — inventory 05.
- [x] Build environment is defined — inventory 04.
- [x] Risks are recorded — top three: (1) audio stack must be verified ON HARDWARE (pyaudio regression precedent); (2) UI thread discipline (worker→after() only); (3) additive-only schema or user data is lost.
- [x] Output artifacts are defined — inventory 02.
- [x] Validation steps are defined — phase gates (blueprint §8) + full suite green + owner field-use.
- [x] Handoff path is known — commit → push GitHub main → pull BOTH clones (Desktop\Sentinel-Forge is the copy the owner runs).

## Build readiness notes
- Objective: rebuild in 8–12 sessions using pre-answered decisions; never pay for a documented trap twice.
- Scope: desktop app + lyceum core + tests + docs. OUT: platform two-way sync, macOS/Linux (declared descopes).
- Known blockers: none at time of writing.
- Required approvals: Shannon merges to main (human-in-the-loop boundary).

## Signoff
- Build coordinator: Shannon Brian Kelley
- Review status: approved
