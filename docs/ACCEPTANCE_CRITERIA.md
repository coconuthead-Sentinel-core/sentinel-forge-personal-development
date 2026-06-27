# Sentinel Forge — Requirements & Acceptance Criteria

- **Project:** Sentinel Forge — Personal Development
- **Stakeholder / acceptor:** Shannon Brian Kelley
- **Target version:** v0.9 (release candidate)
- **Status:** DRAFT — awaiting stakeholder review & sign-off
- **Standard:** ISO/IEC/IEEE 29148 (requirements engineering). This is the
  lightweight Software Requirements Specification (SRS) called for in
  `docs/SDLC_STATUS.md`, exit criterion #1.

> **Purpose.** A feature is only "done" when there is a **written, observable
> test of done** that the stakeholder can check. This document lists each
> capability as a requirement plus an **acceptance criterion** — a concrete thing
> you can *see happen*. The human (Shannon) performs the acceptance pass: open the
> app, exercise each item, and tick **Pass** or **Fail**. Failures become the
> punch list before release.

## How to run the acceptance pass

1. Launch the app (`run_sentinel.bat`).
2. For each row below, do the action and confirm the "Acceptance criterion (done = …)".
3. Mark `[x]` Pass or note the defect.
4. When every **must-have (M)** row passes, sign the block at the bottom.

Priority: **M** = must-have for v0.9 · **S** = should-have · **C** = could-have.

---

## 1. Functional requirements — Reading & accessibility (core mission)

| ID | Requirement | Acceptance criterion (done = …) | Pri | Pass? |
|---|---|---|---|---|
| FR-R1 | Open a book in each format | A `.docx`, `.pdf`, `.txt`, `.md`, and `.html` file each open and display readable text | M | [ ] |
| FR-R2 | Read aloud with follow-along | Pressing read speaks the text *and* the spoken sentence is highlighted in sync | M | [ ] |
| FR-R3 | Continuous read does not stall | Read-aloud continues across multiple sentences/paragraphs without halting | M | [ ] |
| FR-R4 | Spoken-form normalization | "$32", "50%", "Dr.", "21st" are *spoken* as words, not symbols | S | [ ] |
| FR-R5 | Adjustable text & dyslexia overlay | Text grows/shrinks; OpenDyslexic overlay toggles; ≥1 highlight color works | M | [ ] |
| FR-R6 | Voice dictation (Whisper) | Speaking inserts transcribed text into the focused field | S | [ ] |
| FR-R7 | Hands-free dictation commands | Saying "period / new line / cap hello" yields `. \n Hello` | S | [ ] |
| FR-R8 | Save zone-tagged excerpt | Saving writes a `.md` with YAML front-matter (zone, source, timestamp) | M | [ ] |
| FR-R9 | Library zone filter | The Library lists excerpts and filters by GREEN/YELLOW/RED | S | [ ] |

## 2. Functional requirements — Study & planning

| ID | Requirement | Acceptance criterion (done = …) | Pri | Pass? |
|---|---|---|---|---|
| FR-S1 | Session Start/End continuity | Start writes a handoff note; relaunch shows where you left off | S | [ ] |
| FR-S2 | Goals with honest progress | A goal shows progress = (current−baseline)/(target−baseline); backsliding shows 0% | M | [ ] |
| FR-S3 | Habits & streaks | Marking a habit done updates its streak; "never miss twice" rule fires | S | [ ] |
| FR-S4 | Eisenhower matrix & planner | Tasks persist across restart in the matrix and weekly planner | S | [ ] |
| FR-S5 | Appointment reminders | An appointment schedules Windows reminders that flash even with the app closed | C | [ ] |
| FR-S6 | Onboard AI (if Ollama present) | "Explain selection" returns a grounded explanation; absent Ollama, app still runs | C | [ ] |

## 3. Functional requirements — Finance suite

| ID | Requirement | Acceptance criterion (done = …) | Pri | Pass? |
|---|---|---|---|---|
| FR-F1 | Pay Yourself First | A paycheck locks the savings cut first; budget refuses to dip into it | S | [ ] |
| FR-F2 | Persistence | Money entered in any finance tool is still there after a restart | M | [ ] |
| FR-F3 | Simulators compute | Compound, fee-checker, and critical-mass tools produce sane numbers + charts | C | [ ] |
| FR-F4 | Atomic deletes | Deleting a paycheck removes its budget items with no orphans left behind | M | [ ] |

## 4. Non-functional requirements (ISO/IEC 25010 quality)

| ID | Requirement | Acceptance criterion (done = …) | Pri | Pass? |
|---|---|---|---|---|
| NFR-1 | Windows 11 native, no console flashing | App launches via `run_sentinel.bat` with no console window popping up | M | [ ] |
| NFR-2 | Offline / no API keys | App fully usable with no internet connection | M | [ ] |
| NFR-3 | Graceful degradation | With an optional dependency uninstalled, only that feature is disabled; app runs | M | [ ] |
| NFR-4 | UI never freezes | Long actions (read-aloud, transcription) don't freeze the window | M | [ ] |
| NFR-5 | Data safety | Closing mid-edit does not corrupt `study.db`; data survives restart | M | [ ] |
| NFR-6 | Correct text handling | Accented/Unicode text displays correctly (no mojibake) | S | [ ] |
| NFR-7 | High-DPI crispness | Text is crisp (not blurry) on a scaled display | S | [ ] |

## 5. Process / Definition of Done (the release gate)

| ID | Gate item | Done = … | Pass? |
|---|---|---|---|
| DOD-1 | Automated tests green | `python -m unittest discover -s tests` → all pass (currently 34/34) | [ ] |
| DOD-2 | CI passing | The GitHub Actions CI badge is green on `main` | [ ] |
| DOD-3 | Syntax floor | `py_compile` clean on the app + `ai_brain.py` | [ ] |
| DOD-4 | Docs current | README, CHANGELOG, and wiki reflect the shipped version | [ ] |
| DOD-5 | Version tagged | `v0.9-rc1` tag exists on the release commit | [ ] |
| DOD-6 | Visual QA pass | Every must-have (M) row above is ticked Pass | [ ] |

---

## Stakeholder sign-off

By signing, I accept that the must-have requirements above have been verified and
that v0.9 meets the agreed Definition of Done.

- **Accepted by:** _____________________________ (Shannon Brian Kelley)
- **Date:** ______________
- **Version accepted:** v0.9-rc____
- **Outstanding (deferred to post-v0.9):** _______________________________________

> Note for the acceptor: items marked **S/C** that fail do **not** block v0.9 —
> record them in "Outstanding." Only failing **M** items block release.
