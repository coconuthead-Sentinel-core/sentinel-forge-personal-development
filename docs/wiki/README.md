# Sentinel Forge — Personal Development · Engineering Wiki

> Native Windows desktop **reading & personal-development workstation** built
> neurodivergent-first (dyslexia / ADHD / dysgraphia): neural read-aloud with
> follow-along highlighting, offline Whisper voice dictation, a zone-tagged book
> Library, and a tabbed Study/Focus workspace.

**Repository:** [`coconuthead-Sentinel-core/sentinel-forge-personal-development`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development)
**Owner / sole developer / primary user:** Shannon Brian Kelley (*Coconut head*)
**Working version:** v0.9 (release-candidate track)
**Wiki last reviewed:** 2026-06-27 · against commit `aea48c8`

---

## Purpose of this wiki

This is the **engineering knowledge base** for the project. It is written to the
standard a university software-engineering course would expect — grounded in
named references (ISO/IEC/IEEE 12207, IEEE SWEBOK, McCabe, Fowler, Bernhardt) —
and it doubles as **session notes for the next coding assistant**. Read
[Session Notes & Handoff](Session-Notes-and-Handoff.md) first if you are resuming
work; it tells you exactly where things stand and what to touch next.

## Page index

| Page | What it covers |
| --- | --- |
| [Architecture](Architecture.md) | Functional core / imperative shell; the God-Object reality; layering & threading model |
| [Codebase Map](Codebase-Map.md) | File-by-file tour; the `BookReader` class anatomy; where each subsystem lives |
| [Database Schema](Database-Schema.md) | All 37 SQLite tables documented; the ACID `transaction()` primitive |
| [Feature Catalog](Feature-Catalog.md) | Every user-facing feature mapped to the method that implements it |
| [Former Bugs & Regressions](Former-Bugs-and-Regressions.md) | Every notable bug fixed, named with the CS concept behind it, and how it's now guarded |
| [Testing & QA](Testing-and-QA.md) | The 34-test suite, what each test locks in, and the V&V gaps |
| [SDLC & Process](SDLC-and-Process.md) | Methodology declaration, life-cycle position, exit criteria |
| [Development Workflow](Development-Workflow.md) | The laptop→GitHub sync rule, branching policy, build & release |
| [Glossary of CS Concepts](Glossary-of-CS-Concepts.md) | Plain-language definitions of every concept this codebase uses |
| [Rebuild Blueprint](Rebuild-Blueprint.md) | Disaster-recovery house plans: pseudocode blueprint to reconstruct the whole app in days, not months |
| [Assistant Notes](Assistant-Notes.md) | Assistant-maintained project state, V&V status, TODO, and instruction queue — checked on every README review |
| [Working With The Architect](Working-With-The-Architect.md) | Accessibility-first collaboration guide: how to build for and work with the project owner |
| [Whitepaper Notes](Whitepaper-Notes.md) | Append-only raw material for the portfolio case-study white paper (1-3 sentences per docs update) |
| [Review — Excel 365 Bible](Review-Excel365Bible.md) | Clinical CS review of the Excel Bible → what integrates (a formula engine) with proven pseudocode |
| [Whitepaper Outline](Whitepaper-Outline.md) | Skeletal outline in standard technical-report form — flesh out one section per sitting |
| [Session Notes & Handoff](Session-Notes-and-Handoff.md) | Running log for future sessions; current state and next actions |

## Thirty-second orientation

- **One language, one process.** Python 3.11+ desktop app. The GUI is **Tkinter**
  (standard library). No web server, no cloud — *local-first by design*.
- **One big UI class.** `sentinel_personal_development.py` (~23.6k LOC) is the
  **imperative shell**: a single `BookReader` class with ~590 methods. This is a
  known **God Object** (see [Architecture](Architecture.md)); decomposition is in
  progress, not finished.
- **A growing pure core.** Reusable, UI-free, unit-tested logic is being
  extracted into the **`lyceum/`** package (`db`, `metrics`, `text_norm`,
  `dictation_commands`, `reminders`). This is the **functional core**.
- **Data lives in SQLite** (`study.db`) plus Markdown excerpt files with YAML
  front-matter. Schema: [Database Schema](Database-Schema.md).
- **Everything degrades gracefully.** Every optional dependency (Whisper, pypdf,
  Ollama, …) is imported in a `try/except`; if it's missing, that one capability
  switches off and the app still runs.

## Ground truth & sync model

The Desktop working copy lives **inside OneDrive**
(`C:\Users\sbrya\OneDrive\Desktop\Sentinel-Forge`), so the laptop copy and the
OneDrive copy are the *same files*. The canonical flow is **laptop → commit →
push to GitHub `main`**; GitHub `main` is the single source of truth. See
[Development Workflow](Development-Workflow.md).
