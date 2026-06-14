# Dependency and Integration Inventory — Sentinel Forge

## Document metadata
- **Project name:** Sentinel Forge
- **Owner:** Shannon Brian Kelley
- **Date:** 2026-05-28

## 1. Dependency inventory
| Dependency ID | Dependency Name | Type | Version / Reference | Why Needed | Criticality | Status |
| --- | --- | --- | --- | --- | --- | --- |
| D-001 | python-docx | PyPI package | >=1.0.0 | Parse `.docx` files | Optional (graceful degrade) | In use |
| D-002 | pypdf | PyPI package | >=4.0.0 | Parse `.pdf` files | Optional (graceful degrade) | In use |
| D-003 | beautifulsoup4 | PyPI package | >=4.12.0 | Parse `.html` files | Optional (graceful degrade) | In use |
| D-004 | pyttsx3 | PyPI package | >=2.90 | Windows SAPI5 read-aloud fallback | Optional (Piper preferred) | In use |
| D-005 | send2trash | PyPI package | >=1.8.0 | Recoverable deletes from the Library | Optional | In use |
| D-006 | tkinterdnd2 | PyPI package | >=0.4.0 | Drag-and-drop files onto the Library | Optional | In use |
| D-007 | PyInstaller | PyPI package | latest | Build the standalone `.exe` | Build-time only | In use |
| D-008 | Tkinter / Tcl-Tk | Stdlib | bundled w/ Python | GUI toolkit | Critical | In use |
| D-009 | sqlite3 | Stdlib | bundled w/ Python | Study database | Critical | In use |
| D-010 | winsound | Stdlib | bundled w/ Python | Pomodoro chime | Low | In use |
| D-011 | Piper TTS | Bundled binary + voice model | `en_US` voice | High-quality offline neural read-aloud | Optional (bundled) | In use |

> Every third-party parser/voice dependency is imported with `try/except
> ImportError`; the app runs with any of them missing, disabling only the
> matching file type or voice.

## 2. Integration inventory
| Integration ID | System / Service | Interface Type | Direction | Owner | Risk | Status |
| --- | --- | --- | --- | --- | --- | --- |
| I-001 | Sentinel Forge platform ("Ask Library") | HTTP POST `http://127.0.0.1:8000/api/library/ask` | App → platform (outbound) | Shannon | Low — optional; app works offline if absent | Optional |
| I-002 | Windows SAPI5 speech engine | OS API (via pyttsx3 / PowerShell) | App → OS | Microsoft / OS | Low — fallback path | In use |
| I-003 | Local filesystem — Books vault | File read/write (`.md` + `.meta.json`) | Bidirectional | Shannon | Low | In use |
| I-004 | GitHub (origin remote) | Git over HTTPS | Bidirectional | Shannon | Low | In use |

## Notes
- The only network integration is the **optional** localhost platform (I-001);
  the app is otherwise fully offline with no internet calls.
