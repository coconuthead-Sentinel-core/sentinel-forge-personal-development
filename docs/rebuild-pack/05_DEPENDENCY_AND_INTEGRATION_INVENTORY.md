# Dependency & Integration Inventory — Sentinel Forge

- Project name: Sentinel Forge — Personal Development
- Build name: Full reconstruction (disaster-recovery rebuild)
- Owner: Shannon Brian Kelley (architect/QA) + AI coding assistant (implementer)
- Date: 2026-07-11
- Status: approved (standing paperwork; refresh on each release)

## Python dependencies (all optional-guarded; app degrades gracefully)
| Dependency | Purpose | License note |
| --- | --- | --- |
| faster-whisper | on-device dictation | MIT |
| sounddevice / numpy / noisereduce | mic capture + cleanup | MIT/BSD |
| python-docx | .docx read + write | MIT |
| pypdf | .pdf read | BSD |
| beautifulsoup4 | .html read + web-result parsing | MIT |
| send2trash | recoverable deletes (legacy path) | BSD |
| tkinterdnd2 | drag-drop onto Library | MIT |
| openpyxl | .xlsx read/write (assistant) | MIT |
| fsrs (py-fsrs) | FSRS scheduler | MIT — NO Anki/AGPL/GPL code anywhere |
| pywin32 / vosk | optional assistant voice extras | PSF/Apache |

## External integrations (all local/loopback by design)
| Integration | Direction | Notes |
| --- | --- | --- |
| Ollama daemon | loopback HTTP | the ONLY standing network touch |
| DuckDuckGo lite | outbound HTTPS, user-invoked | 🌐 web search; stdlib urllib; no key |
| HuggingFace | outbound, first-use only | whisper model download |
| Windows Task Scheduler | local API | appointment reminders (no admin) |
| Windows hosts file | local file (admin) | Not-To-Do site blocker; always unblocks on exit |
| OneDrive | passive folder sync | repo clones + Books + DB snapshot |
| GitHub | git push/pull | source of truth, main only |
