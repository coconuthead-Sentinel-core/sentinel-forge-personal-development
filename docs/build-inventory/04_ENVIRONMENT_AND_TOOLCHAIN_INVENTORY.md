# Environment and Toolchain Inventory — Sentinel Forge

## Document metadata
- **Project name:** Sentinel Forge
- **Build identifier:** Sentinel-Forge
- **Owner:** Shannon Brian Kelley
- **Date:** 2026-05-28

## 1. Build environments
| Environment ID | Environment Name | OS / Platform | Purpose | Access Method | Status |
| --- | --- | --- | --- | --- | --- |
| E-001 | Local dev / build | Windows 11 (10/11 supported) | Write code, run, build `.exe` | Local workstation | Active |
| E-002 | Clean-machine test | Windows 10/11 | Verify one-folder bundle runs without Python installed | Copy `dist\Sentinel-Forge\` | Planned |

## 2. Toolchain inventory
| Tool Name | Version | Purpose | Required | Notes |
| --- | --- | --- | --- | --- |
| Python | 3.11+ (3.13 tested) | Language runtime / interpreter | Yes | `py` launcher recommended |
| pip | bundled with Python | Install dependencies | Yes | `py -3 -m pip install -r requirements.txt` |
| PyInstaller | latest | Build the one-folder `.exe` | For builds only | `pyinstaller Sentinel-Forge.spec --clean --noconfirm` |
| PowerShell | Windows built-in | Run `scripts\*.ps1` (build, install TTS, shortcut) | For scripts | `-ExecutionPolicy Bypass` |
| Git | any recent | Version control | Yes | source of truth on GitHub |
| GitHub CLI (`gh`) | 2.90.0 | Repo management / push | Optional | used for repo rename + workflow |

## 3. Runtime inventory
| Runtime | Version | Purpose | Required | Notes |
| --- | --- | --- | --- | --- |
| Python | 3.11+ | Runs the app (bundled into `.exe` for end users) | Yes | end users of the `.exe` need no separate install |
| Tcl/Tk | bundled with Python | GUI toolkit (Tkinter) | Yes | ships with python.org installer |
| Piper TTS | bundled binary + `en_US` voice | Neural read-aloud | Optional | ~100 MB; falls back to SAPI5 |
| Windows SAPI5 | OS-provided | Fallback read-aloud voice | Fallback | via `pyttsx3` / PowerShell |

## Notes
- Record exact versions when reproducibility matters; Python 3.13 is the tested target.
- Tk is part of the standard Python distribution — nothing extra to install.
