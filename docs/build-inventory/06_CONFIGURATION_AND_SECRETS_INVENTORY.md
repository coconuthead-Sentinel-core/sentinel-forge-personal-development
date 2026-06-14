# Configuration and Secrets Inventory — Sentinel Forge

## Document metadata
- **Project name:** Sentinel Forge
- **Owner:** Shannon Brian Kelley
- **Date:** 2026-05-28

## Configuration inventory
| Config ID | Config Item | Type | Used By | Required | Secret | Storage Location | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CFG-001 | `BOOK_READER_TTS` | Environment variable | TTS subsystem | No | No | OS environment | Forces engine: `piper` \| `powershell` \| `pyttsx3` |
| CFG-002 | `DEFAULT_BOOKS_DIR` | Code constant (path) | Library / save excerpts | Yes | No | `book_reader.py` (hardcoded to `…\OneDrive\Desktop\Books`) | Where saved excerpts land |
| CFG-003 | `STUDY_DIR` | Code constant (path) | Study DB + handoff | Yes | No | `book_reader.py` (`~\OneDrive\Documents\BookReader`) | Holds `study.db` + `HANDOFF_STATE.json` |
| CFG-004 | `STUDY_DB` | SQLite DB file | Study database layer | Yes | No | `STUDY_DIR\study.db` | Highlights, topics, day-blocks, etc. |
| CFG-005 | `HANDOFF_STATE_PATH` | JSON state file | Session wizards | No | No | `STUDY_DIR\HANDOFF_STATE.json` | Session continuity between launches |
| CFG-006 | `PLATFORM_ASK_URL` | Code constant (URL) | Ask Library integration | No | No | `book_reader.py` (`http://127.0.0.1:8000/...`) | Localhost only |
| CFG-007 | `COMMENTARIES_DIR` | Code constant (path) | Commentary feature | No | No | `DEFAULT_BOOKS_DIR\Commentaries` | Optional commentary files |

## Guidelines / findings
- **No secrets, API keys, tokens, or certificates exist in this project.** The
  app is offline-first and authenticates to nothing — there is nothing sensitive
  to store or rotate.
- Most configuration is currently **hardcoded constants** in `book_reader.py`
  rather than env vars. The one runtime override is `BOOK_READER_TTS`.
  *(Improvement opportunity: promote the directory paths to env vars for
  portability — the README references a `SENTINEL_FORGE_BOOKS_DIR` override that
  is not yet wired into the current code.)*
