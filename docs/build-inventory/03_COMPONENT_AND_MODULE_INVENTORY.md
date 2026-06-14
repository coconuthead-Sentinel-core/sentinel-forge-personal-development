# Component and Module Inventory — Sentinel Forge

## Document metadata
- **Project name:** Sentinel Forge
- **Owner:** Shannon Brian Kelley
- **Date:** 2026-05-28

> The app is a single Python file (`book_reader.py`, ~9,200 lines, one
> `BookReader` class with ~246 methods). The rows below are the logical
> subsystems *inside* that file plus the supporting scripts.

## Components
| Component ID | Component Name | Type | Responsibility | Build Path | Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| C-001 | BookReader app | Executable / UI | Entire Tkinter desktop app; window, menus, topbar, status | `book_reader.py` | Shannon | Active |
| C-002 | Reading & extraction engine | Module | Open/parse `.docx/.pdf/.html/.md/.txt/.rtf`; chapter detection | `book_reader.py` (`_extract_*`) | Shannon | Active |
| C-003 | Read-aloud (TTS) subsystem | Module | Piper neural / pyttsx3 / PowerShell SAPI; word highlight | `book_reader.py` (`read_aloud`, `_speak_*`) | Shannon | Active |
| C-004 | Dictation (mic) subsystem | Module | Speech-to-text into notes | `book_reader.py` (`_start_mic`) | Shannon | Active |
| C-005 | Study database layer | Data store | SQLite store for highlights, topics, bookmarks, glossary, journal, day-blocks | `book_reader.py` (`_init_study_db`, `study.db`) | Shannon | Active |
| C-006 | Three-Zone Library | Module | Scan/organize saved excerpts by GREEN/YELLOW/RED zone | `book_reader.py` (`open_library`, `_scan_library`) | Shannon | Active |
| C-007 | Matrix Calendar / Pomodoro planner | UI / Module | Day-planner, Do-Now panel, schedule blocks, Pomodoro timer | `book_reader.py` (`_build_tab_eisenhower`, `_start_timer`) | Shannon | Active |
| C-008 | Session wizards & handoff | Module | Start/End session wizards; write `HANDOFF_STATE.json` | `book_reader.py` (`open_session_*_wizard`) | Shannon | Active |
| C-009 | Build spec | Package config | PyInstaller one-folder build definition | `Sentinel-Forge.spec` | Shannon | Active |
| C-010 | Launchers | Script | No-console / debug launch of the app | `run_book_reader.bat`, `run_book_reader_debug.bat` | Shannon | Active |
| C-011 | Build & install scripts | Script | Build `.exe`, install TTS, install Desktop shortcut, make icon | `scripts/` (`build_exe.ps1`, `install_tts.ps1`, `install_book_reader_shortcut.ps1`, `make_sentinel_icon.py`) | Shannon | Active |
| C-012 | TTS assets | Data store | Bundled Piper binary + `en_US` voice model | `tts/` | Shannon | Active |

## Notes
- One row per meaningful buildable or maintained unit.
- Subsystems C-002–C-008 all live inside the single `book_reader.py` file.
