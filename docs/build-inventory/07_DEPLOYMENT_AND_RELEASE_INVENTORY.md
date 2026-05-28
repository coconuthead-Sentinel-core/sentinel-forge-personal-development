# Deployment and Release Inventory — Sentinel Screen Reader

## Document metadata
- **Project name:** Sentinel Screen Reader
- **Release name:** Sentinel-Forge MVP
- **Owner:** Shannon Brian Kelley
- **Date:** 2026-05-28

## Release targets
| Target ID | Target Name | Target Type | Artifact Input | Deployment Method | Validation Method | Status |
| --- | --- | --- | --- | --- | --- | --- |
| T-001 | Standalone Windows app | Desktop app | `dist\Sentinel-Forge\` (one-folder build) | Copy the whole folder to the target machine; run `Sentinel-Forge.exe` | Launch, open a book, read aloud, save an excerpt | Planned |
| T-002 | Desktop shortcut | Desktop app | `Sentinel-Forge.exe` / `run_book_reader.bat` | `scripts\install_book_reader_shortcut.ps1` | Shortcut launches app with icon | Verified |
| T-003 | Source distribution | Package (repo) | Git `main` branch | `git clone` + `pip install -r requirements.txt` + `py -3 book_reader.py` | Runs from source on a dev machine | Verified |
| T-004 | GitHub release surface | Documentation / public repo | Repo contents + README | Push to `main` (public, MIT) | README renders; clone works | In use |

## Notes
- Intentionally a **one-folder** PyInstaller build (not one-file): faster cold
  start, and the ~60 MB Piper voice model is not extracted to `%TEMP%` on every
  launch. **Ship the entire `dist\Sentinel-Forge\` folder.**
- `scripts\build_exe.ps1 -NoTTS` produces a smaller bundle that falls back to
  Windows SAPI5.
- **Rollback:** revert to the previous Git commit / previously distributed
  folder; no server-side state to roll back (app is local-only).
