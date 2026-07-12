# Environment & Toolchain Inventory — Sentinel Forge

- Project name: Sentinel Forge — Personal Development
- Build name: Full reconstruction (disaster-recovery rebuild)
- Owner: Shannon Brian Kelley (architect/QA) + AI coding assistant (implementer)
- Date: 2026-07-11
- Status: approved (standing paperwork; refresh on each release)

| Item | Value | Notes |
| --- | --- | --- |
| OS | Windows 11 Home (10.0.26200 tested) | Windows 10 supported |
| Display reality | ~1097×617 effective (DPI-scaled) | drives the window-fit law |
| Python | 3.13 via python.org installer + `py` launcher | Store-Python stub breaks `pythonw` launches — use launchers/vbs |
| Tk | bundled with python.org installer | ctk NOT used in this app |
| Git | git for Windows; `gh` CLI authed as coconuthead-Sentinel-core | |
| Package install | `py -3 -m pip install -r requirements.txt` | |
| Ollama | daemon on localhost; model `llama3.2:3b` pulled | 8 GB RAM machine → num_ctx=2048 law |
| Piper TTS | `scripts/install_tts.ps1` → `tts/` | verify audio ON HARDWARE (winsound, not pyaudio) |
| Whisper models | auto-download to HF cache on first 🎤 use | base/small/medium.en |
| Build tool | PyInstaller via `scripts/build_exe.ps1` | one-folder build |
| Test runner | `py -3 -m unittest discover -s tests` | headless; UI smokes need a real mainloop |
| Storage caution | C: SSD small; E: (1 TB) preferred for index caches | cache_dir() auto-prefers E: |
