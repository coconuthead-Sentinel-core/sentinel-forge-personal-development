# Build Artifact Inventory — Sentinel Forge

## Document metadata
- **Project name:** Sentinel Forge
- **Build identifier:** Sentinel-Forge (one-folder PyInstaller build)
- **Owner:** Shannon Brian Kelley
- **Date:** 2026-05-28

## Artifacts
| Artifact ID | Artifact Name | Type | Source Step | Output Path | Validation Method | Status |
| --- | --- | --- | --- | --- | --- | --- |
| A-001 | Sentinel-Forge.exe | Windows executable (launcher) | `pyinstaller Sentinel-Forge.spec` | `dist\Sentinel-Forge\Sentinel-Forge.exe` (~6 MB) | Launch app, open a book, read aloud | Planned |
| A-002 | `_internal\` runtime bundle | Python runtime + bundled libs | PyInstaller COLLECT step | `dist\Sentinel-Forge\_internal\` | App starts from packaged runtime | Planned |
| A-003 | One-folder distributable | Deployable bundle | Full PyInstaller build | `dist\Sentinel-Forge\` (~30 MB no-TTS · ~175 MB with Piper) | Copy folder to clean machine, run | Planned |
| A-004 | sentinel.ico | App icon (embedded) | Bundled via spec `datas` | embedded in `.exe` + `_internal` | Icon shows on taskbar/shortcut | Verified |
| A-005 | Source distribution | Git repository | `git push` to `main` | github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development | `git clone` + `pip install -r requirements.txt` + run | Verified |

## Notes
- Build artifacts are produced by `scripts\build_exe.ps1` (one command) or by
  hand with `py -3 -m PyInstaller Sentinel-Forge.spec --clean --noconfirm`.
- `-NoTTS` flag produces a smaller bundle that falls back to Windows SAPI5.
- Saved excerpts (`.md` + `.meta.json`) are **runtime user output**, not build
  artifacts — see `06` / `07` for where they land.
