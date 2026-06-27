# Sentinel Forge — SDLC Status & Methodology Declaration

- **Project:** Sentinel Forge — Personal Development
- **Owner / stakeholder:** Shannon Brian Kelley (also the primary user)
- **Document date:** 2026-06-27
- **Working version:** v0.9 (release-candidate track; supersedes the 2026-05-28 "MVP" label)
- **Prepared with:** Claude (AI by Anthropic), working only from the local repository

> Purpose: state, in the language used by software-engineering courses worldwide,
> **which methodology this project follows**, **where it sits in the software
> development life cycle (SDLC)**, and **what remains before a stakeholder
> acceptance handoff**. Reference standards: ISO/IEC/IEEE 12207 (life-cycle
> processes), ISO/IEC/IEEE 29148 (requirements), the IEEE SWEBOK Guide, the
> Scrum Guide (Schwaber & Sutherland), and Fowler, *Refactoring*.

---

## 1. Methodology declaration

**Chosen model: iterative & incremental development, run as a single-developer
Kanban flow.** This is now declared explicitly because, until this document, the
methodology was *undocumented* — a gap a professor would flag first.

**Why not Waterfall or the V-Model.** Both require a complete, stable
requirements specification *before* design and coding. This project's
requirements emerged and changed continuously (features were added as the user
discovered needs). Imposing Waterfall retroactively would be dishonest. The
work has, in fact, always been *iterative* — each feature was a small increment.

**Why Kanban over full Scrum.** Scrum's ceremonies (sprint planning, daily
stand-up, sprint review, retrospective) and roles (Product Owner, Scrum Master,
Dev Team) assume a *team*. With one developer, the textbook recommendation is
**Kanban**: a visible board (Backlog → In progress → In review/testing → Done),
a **work-in-progress (WIP) limit** to stop scope creep, and continuous delivery.
Each "lab" in this project is one Kanban card carried to Done *with tests*.

---

## 2. Where we are in the SDLC (clinical assessment)

The central finding: **the product is more mature than the process artifacts.**

| SDLC phase (ISO/IEC/IEEE 12207) | Product state | Process-artifact state |
| --- | --- | --- |
| Requirements | Implicitly satisfied (features exist & work) | ❌ No written requirements spec (SRS) |
| Architecture / Design | Implemented, but as one large class | ⚠️ Now partly documented (metrics + refactor plan) |
| Implementation (coding) | ✅ Feature-complete, runs on Windows 11 | ⚠️ High-complexity hotspots remain |
| Testing / V&V | ⚠️ Began this cycle (first automated tests) | ⚠️ 8 unit tests; no integration/system test record |
| Release / Deployment | ⚠️ Build defined; standalone build "Planned" | ⚠️ No version tag, changelog, or QA gate |
| Maintenance | Ongoing | n/a |

**Plain-language verdict a professor would give:** *"Your code is at Beta /
stabilization. Your paperwork is at Inception. Before any stakeholder handoff,
the paperwork has to catch up to the product."*

---

## 3. Requirements status (ISO/IEC/IEEE 29148)

- No formal Software Requirements Specification exists. `requirements.txt` is a
  Python **dependency** manifest, not a requirements document.
- **Action:** produce a lightweight requirements/feature inventory with
  acceptance criteria (what "working" means for each module). For a personal
  app the stakeholder and user are the same person, so acceptance criteria can
  be short, but they must be **written down** to be testable.

## 4. Implementation status (measured this cycle, via Python `ast`)

- Size: **1 class, 953 functions, ~23.6k LOC**. `BookReader` holds **590
  methods** → **God Object** anti-pattern (Single Responsibility Principle).
- Cyclomatic complexity (McCabe): 831 simple (≤10), 81 moderate, 38 complex,
  **3 untestable (>50)**: `_build_goals_panel` (66), `open_idea_warehouse` (60),
  `_ftb_read_toggle` (58).
- Progress already made toward the standard: extracted a **pure functional core**
  (`lyceum/metrics.py`) and an **atomic transaction primitive**
  (`lyceum/db/study_db.py: transaction()`), each with tests.

## 5. Testing / QA status (IEEE 829 / SWEBOK V&V)

- **8 automated unit tests, all passing** (`tests/` — first in the project):
  6 for the progress math, 2 proving database **atomicity** (commit + rollback).
- Manual verification: GUI panels build on a withdrawn Tk root; app confirmed
  to launch and "blend with Windows 11."
- **Gap:** no integration/system test record; coverage is narrow (core logic
  only). A QA gate (what must pass before release) is not yet defined.

## 6. Windows 11 conformance checklist

| Item | Status | Note |
| --- | --- | --- |
| Runs on Windows 11, no console flashing | ✅ | All `subprocess` calls use `CREATE_NO_WINDOW`, list-args (no `shell=True`) |
| Correct text handling | ✅ | UTF-8 file I/O throughout (avoids the `cp1252` trap) |
| GUI thread-safety | ✅ | Worker threads marshal to the UI via `root.after(...)` |
| Offline / no API keys | ✅ | Local-only by design |
| Per-user scheduled reminders (no admin) | ✅ | `Register-ScheduledTask`, per-user |
| Packaging defined | ⚠️ | PyInstaller one-folder build; standalone target still "Planned" |
| **High-DPI awareness** | ❌ | No DPI declaration → blurry text on scaled displays |
| Code signing | ❌ | Unsigned → SmartScreen warning if distributed |
| Modern installer (MSIX) | ❌ | Folder-copy only; fine for personal use, not Store-grade |
| Data location | ⚠️ | `study.db` under OneDrive → possible sync conflicts |

**Read:** the app is **correct and well-behaved for personal use on Windows 11**.
It is **not yet "signed installer / Microsoft Store" grade** — that needs DPI
awareness, signing, and MSIX, which only matter if you distribute it.

---

## 7. Exit criteria before stakeholder handoff

A professor's release checklist for *this* project (Definition of Done):

1. [ ] Requirements / feature inventory written, with acceptance criteria.
2. [x] Methodology declared (this document).
3. [ ] Test suite expanded to cover the core logic of each major module; QA gate
       defined ("all tests green + manual smoke test of every window").
4. [ ] The 3 untestable functions (CC>50) decomposed to ≤10.
5. [ ] God-Object refactor *plan* documented (incremental Extract Class).
6. [ ] Version tag + CHANGELOG; standalone build moved from "Planned" → built.
7. [x] User documentation (README present).
8. [ ] Stakeholder acceptance review (sign-off against the written criteria).

---

## 8. Recommendation: stop adding features; enter a stabilization phase

The dominant risk now is **scope creep** — new modules add untested surface
area. Standard practice:

- **Stop writing new features.** Declare feature freeze for v0.9.
- **Refactor continuously, per Fowler:** clean up code *as you touch it* when
  adding tests or fixing bugs — not as a separate rewrite.
- **Run a stabilization (hardening) increment:** items 1, 3, 4, 5, 6 above.
- **Then cut a release candidate** and hold a stakeholder acceptance review
  against the written criteria.

> One-line answer to "are we still writing new code, or refactoring, or
> finishing?": **Finish.** Freeze features, refactor + test + document to the
> exit criteria, then hand a release candidate to the stakeholder.
