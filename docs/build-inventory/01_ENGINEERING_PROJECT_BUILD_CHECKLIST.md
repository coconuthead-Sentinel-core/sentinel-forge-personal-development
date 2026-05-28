# Engineering Project Build Checklist — Sentinel Screen Reader

## Document metadata
- **Project name:** Sentinel Screen Reader
- **Build name:** Sentinel-Forge one-folder PyInstaller build
- **Owner:** Shannon Brian Kelley
- **Date:** 2026-05-28
- **Status:** review

## Build checklist
- [x] Project objective is defined.
- [x] Build scope is defined.
- [x] Required inputs are listed.
- [x] Owners are assigned.
- [x] Architecture documents are available. *(README.md + this pack; single-file app)*
- [x] Dependencies are identified. *(requirements.txt — all optional/try-except)*
- [x] Build environment is defined. *(Windows 10/11, Python 3.11+/3.13, PyInstaller)*
- [x] Risks are recorded.
- [x] Output artifacts are defined.
- [x] Validation steps are defined. *(manual smoke test + successful PyInstaller build; no automated test suite yet)*
- [x] Handoff path is known. *(GitHub `main` is the source of truth)*

## Build readiness notes
- **Objective:**
  - A native, offline Windows desktop reading app that opens `.docx`, `.pdf`,
    `.md`, `.txt`, `.rtf`, and `.html`, reads aloud with a neural voice, and
    saves zone-tagged excerpts — designed neurodivergent-first (ADHD, dyslexia,
    dysgraphia).
- **Scope:**
  - Package the single-file Tkinter app (`book_reader.py`) into a distributable
    one-folder Windows `.exe` via `Sentinel-Forge.spec` / `scripts/build_exe.ps1`.
    In scope: the desktop app, its launchers, and the PyInstaller bundle.
    Out of scope: the optional FastAPI platform and macOS/Linux ports.
- **Known blockers:**
  - None blocking. The Piper neural-voice bundle (~100 MB) is optional; the app
    falls back to Windows SAPI5 if it is absent.
- **Required approvals:**
  - Solo project — self-signoff by the owner.

## Signoff
- **Build coordinator:** Shannon Brian Kelley
- **Review status:** review
