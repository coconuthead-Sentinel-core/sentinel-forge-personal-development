# SDLC & Process

*Mirrors and links the in-repo
[`docs/SDLC_STATUS.md`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/blob/main/docs/SDLC_STATUS.md).
Reviewed 2026-06-27 against `aea48c8`. Reference standards: ISO/IEC/IEEE 12207
(life-cycle processes), ISO/IEC/IEEE 29148 (requirements), the IEEE SWEBOK Guide,
the Scrum Guide (Schwaber & Sutherland), and Fowler, *Refactoring*.*

## 1. Methodology declaration

**Model: iterative & incremental development, run as a single-developer Kanban
flow.** Declared explicitly because an undocumented methodology is the first
thing a reviewer flags.

- **Why not Waterfall / V-Model:** both demand a complete, frozen requirements
  spec *before* design and code. This project's requirements **emerged
  continuously** as the user discovered needs. The work was always iterative —
  each feature a small increment — so imposing Waterfall retroactively would be
  dishonest.
- **Why Kanban over full Scrum:** Scrum's ceremonies and roles assume a *team*.
  With **one developer**, the textbook recommendation is **Kanban**: a visible
  board (Backlog → In progress → In review/testing → Done), a **WIP limit** to
  stop scope creep, and continuous delivery. Each "lab" here is one Kanban card
  carried to Done **with tests**.

## 2. Where the project sits in the SDLC

The central finding: **the product is more mature than the process artifacts.**

| SDLC phase (ISO/IEC/IEEE 12207) | Product state | Process-artifact state |
| --- | --- | --- |
| Requirements | Implicitly satisfied (features exist & work) | ❌ No written SRS |
| Architecture / Design | Implemented, but as one large class | ⚠️ Partly documented (metrics + refactor plan + this wiki) |
| Implementation | ✅ Feature-complete on Windows 11 | ⚠️ High-complexity hotspots remain |
| Testing / V&V | ⚠️ Began this cycle (first automated tests) | ⚠️ 34 unit tests; no integration/system record |
| Release / Deployment | ⚠️ Build defined; standalone build "Planned" | ⚠️ No version tag, changelog, or QA gate |
| Maintenance | Ongoing | n/a |

**Verdict a professor would give:** *"Your code is at Beta / stabilization. Your
paperwork is at Inception. Before any stakeholder handoff, the paperwork has to
catch up to the product."* (This wiki is part of that catch-up.)

## 3. Measured implementation facts (via Python `ast`)

- **1 class · 953 functions · ~23.6k LOC.** `BookReader` = **590 methods** →
  **God Object** (violates the Single Responsibility Principle).
- **McCabe cyclomatic complexity:** 831 simple (≤10), 81 moderate, 38 complex,
  **3 untestable (>50):** `_build_goals_panel` (66), `open_idea_warehouse` (60),
  `_ftb_read_toggle` (58).
- **Progress already made:** pure functional core extracted (`lyceum/metrics.py`,
  `lyceum/text_norm.py`, `lyceum/dictation_commands.py`) and an atomic DB
  primitive (`lyceum/db/study_db.py: transaction()`), each with tests.

## 4. Windows 11 conformance checklist

| Item | Status | Note |
| --- | --- | --- |
| Runs on Win 11, no console flashing | ✅ | All `subprocess` use `CREATE_NO_WINDOW`, list-args (no `shell=True`) |
| Correct text handling | ✅ | UTF-8 I/O throughout (avoids the `cp1252` trap) |
| GUI thread-safety | ✅ | Workers marshal to UI via `root.after(...)` |
| Offline / no API keys | ✅ | Local-only by design |
| Per-user scheduled reminders (no admin) | ✅ | `Register-ScheduledTask`, per-user |
| Packaging defined | ⚠️ | PyInstaller one-folder; standalone target still "Planned" |
| **High-DPI awareness** | ❌ | No DPI declaration → blurry text on scaled displays |
| Code signing | ❌ | Unsigned → SmartScreen warning if distributed |
| Modern installer (MSIX) | ❌ | Folder-copy only; fine for personal use, not Store-grade |
| Data location | ⚠️ | `study.db` under OneDrive → possible sync conflicts |

**Read:** correct and well-behaved **for personal use on Windows 11**; **not yet
"signed installer / Microsoft Store" grade** (needs DPI awareness, signing, MSIX
— which only matter if you distribute).

## 5. Exit criteria before stakeholder handoff (Definition of Done)

1. [ ] Requirements / feature inventory written, with acceptance criteria.
2. [x] Methodology declared (`docs/SDLC_STATUS.md` + this wiki).
3. [~] Test suite started — **34 unit tests**; QA gate still informal.
4. [~] Worst-case *logic* extracted to tested pure functions; UI-level
   decomposition of the CC>50 builders deferred to visual QA.
5. [x] God-Object reduction **underway** via incremental Extract-Module
   (`lyceum/db`, `metrics`, `text_norm`, `dictation_commands`).
6. [ ] Version tag + CHANGELOG; standalone build moved "Planned" → built.
7. [x] User documentation (README + this wiki).
8. [ ] Stakeholder acceptance review (sign-off against the written criteria).

## 6. Current recommendation: stabilize, don't expand

The dominant risk now is **scope creep** — new modules add untested surface.
Standard practice:

- **Feature freeze for v0.9.** Stop adding new features.
- **Refactor continuously (Fowler):** clean code *as you touch it*, not as a
  separate rewrite.
- **Run a hardening increment:** finish criteria 1, 3, 4, 6.
- **Then cut a release candidate** and hold an acceptance review.

> One-line answer to "are we writing new code, refactoring, or finishing?":
> **Finish.** Freeze, refactor + test + document to the exit criteria, then hand
> a release candidate to the stakeholder.
