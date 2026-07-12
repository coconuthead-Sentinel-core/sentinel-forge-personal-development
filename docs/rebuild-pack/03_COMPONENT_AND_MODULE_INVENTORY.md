# Component & Module Inventory — Sentinel Forge

- Project name: Sentinel Forge — Personal Development
- Build name: Full reconstruction (disaster-recovery rebuild)
- Owner: Shannon Brian Kelley (architect/QA) + AI coding assistant (implementer)
- Date: 2026-07-11
- Status: approved (standing paperwork; refresh on each release)

| Component ID | Component Name | Type | Responsibility | Build Path | Status |
| --- | --- | --- | --- | --- | --- |
| C-001 | study_db | Library (core) | SQLite schema, queries, atomic `transaction()` | `lyceum/db/study_db.py` | built |
| C-002 | db_location | Library | live-DB placement + OneDrive snapshot | `lyceum/db/db_location.py` | built |
| C-003 | metrics | Library | pure progress math | `lyceum/metrics.py` | built |
| C-004 | text_norm | Library | speech normalization pre-TTS | `lyceum/text_norm.py` | built |
| C-005 | reminders + reminder_flash | Library + executable | Windows scheduled-task alerts | `lyceum/reminders.py`, `reminder_flash.py` | built |
| C-006 | srs | Library (core) | FSRS spaced repetition (decks/cards/append-only log) | `lyceum/srs.py` | built |
| C-007 | doc_writer | Library | model text → real .docx/.xlsx (live =SUM()) | `lyceum/doc_writer.py` | built |
| C-008 | doc_index | Library | cached file indexer (library + OneDrive; xlsx/csv) | `lyceum/doc_index.py` | built |
| C-009 | local_context | Library | pure retrieval ranking (RAG) | `lyceum/local_context.py` | built |
| C-010 | voice stack | Libraries | sapi_tts, voice_pipeline, stt_command, dictation_guard, accessibility_bridge | `lyceum/*.py` | built |
| C-011 | finance kernel | Library | money-tool math | `lyceum/finance.py` | built |
| C-012 | ai_brain | Library | LocalBrain over Ollama (ask/context seam) | `ai_brain.py` | built |
| C-013 | Reader room | UI | reading, highlighting, fonts | shell | built |
| C-014 | Library room | UI | scan/read/archive; study-hub buttons | shell | built |
| C-015 | Study workspace | UI | 8 tabs + 🧠 Review window | shell | built |
| C-016 | Dashboard | UI | MDP, Scoreboard, Focus, Not-To-Do, Session panel | shell | built |
| C-017 | Money wing | UI | ~15 education-only calculators | shell | built |
| C-018 | AI Chat room | UI | context sources + 📎 + 📄 drafting | shell | built |
| C-019 | Floating toolbar | UI | 🎤/🔊/speed/➕➖/❓tour, dockable | shell | built |

Rebuild order + acceptance gates: Rebuild-Blueprint §8.
