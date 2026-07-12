# Build Artifact Inventory — Sentinel Forge

- Project name: Sentinel Forge — Personal Development
- Build name: Full reconstruction (disaster-recovery rebuild)
- Owner: Shannon Brian Kelley (architect/QA) + AI coding assistant (implementer)
- Date: 2026-07-11
- Status: approved (standing paperwork; refresh on each release)

| Artifact ID | Artifact | Type | Produced by | Location | Notes |
| --- | --- | --- | --- | --- | --- |
| A-001 | `sentinel_personal_development.py` | Source (shell) | development | repo root | single-file Tk shell, ~24k lines |
| A-002 | `lyceum/` package | Source (core) | development | repo | ~20 modules, no Tkinter |
| A-003 | Test suite | Source | development | `tests/` | 172 headless tests |
| A-004 | `study.db` | Data store | first run (`init_study_db`) | %LOCALAPPDATA%\SentinelForge | additive migrations; OneDrive snapshot copy |
| A-005 | Books library + sidecars | User data | app usage | `Desktop\Books\` | .md + .meta.json; archive folder beside it |
| A-006 | `HANDOFF_STATE.json` | State | session end | app data | cross-session memory |
| A-007 | `Sentinel-Forge.exe` one-folder build | Executable | PyInstaller (`scripts/build_exe.ps1`) | `dist\Sentinel-Forge\` | ~30 MB, ~175 MB with TTS |
| A-008 | Piper TTS bundle | Vendored binaries | `scripts/install_tts.ps1` | `tts/` (gitignored) | ~159 MB; NOT in repo — reinstall by script |
| A-009 | Docs + wiki | Documentation | development | `docs/` | incl. this pack + blueprint |
