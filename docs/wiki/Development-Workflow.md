# Development Workflow

*Reviewed 2026-06-27 against `aea48c8`. This is the operating manual for changing
the code safely and keeping all copies in sync.*

## 1. The three copies and the golden rule

Because the Desktop lives **inside OneDrive**, there are effectively three
representations of the project:

```
   ┌──────────────────────────────┐
   │  LIVE INSTALL (= laptop copy) │   C:\Users\sbrya\OneDrive\Desktop\Sentinel-Forge
   │  also the OneDrive-synced copy│   (laptop and OneDrive are the SAME files)
   └───────────────┬──────────────┘
                   │ commit + push
                   ▼
   ┌──────────────────────────────┐
   │  GitHub  main  (source of     │   github.com/coconuthead-Sentinel-core/
   │  truth)                       │   sentinel-forge-personal-development
   └──────────────────────────────┘
```

**Golden rule (the project's standing workflow):**
**edit the live install → commit → push to GitHub `main`.** GitHub `main` is the
single source of truth. Never let a feature exist only in an unpushed local copy
— that is how the project once ended up with **7 divergent copies** of the app
file, with the GitHub copy *older* than the running one. *Compare before you
destroy; sync before you walk away.*

## 2. Branching policy

| Change type | Policy |
| --- | --- |
| **Docs** (README, wiki, `docs/`) | May go **straight to `main`**. |
| **Risky code** changes | **Branch → pull request → merge.** |
| **Small, safe code** | Commit to `main` with a clear message + a green `unittest`/`py_compile`. |

History shows real PRs (e.g. the dockable-toolbar `feat/dockable-toolbar`
branch). Temporary worktrees (`dashboard-work`) are merged and **removed** when
done — don't leave dangling worktrees (a stale `sentinel-dashboard` worktree
pointer was a known fetch nuisance; prune with `git worktree prune`).

## 3. Commit message style

Observed convention in the log — keep it:

- **Imperative, typed subject:** `feat:`, `fix:`, `docs:`, `chore:`, or a plain
  descriptive line (`DB: add transaction() primitive…`).
- **Body explains the *why* and the failure mode** for bug fixes (see
  [`d92afb3`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/d92afb3)
  as the model: symptom → fix → tests → "py_compile clean").
- Co-authored commits append the `Co-Authored-By:` trailer.

## 4. Pre-commit smoke checks (do these every time)

```powershell
# 1. It must at least parse
python -m py_compile sentinel_personal_development.py ai_brain.py

# 2. The core logic must stay green
python -m unittest discover -s tests

# 3. Then commit + push
git add -A
git commit -m "fix: <what and why>"
git push origin main
```

`py_compile` is the **floor** (a syntax error must never reach `main` — see
[bug #7](Former-Bugs-and-Regressions.md#7-syntax-error-in-a-forelse-construct));
a green `unittest` run is the **ceiling**.

## 5. Running the app

```powershell
py -3 -m pip install -r requirements.txt      # optional deps
py -3 sentinel_personal_development.py          # or double-click run_sentinel.bat
```

`run_sentinel.bat` launches with **no console window**; `run_sentinel_debug.bat`
keeps a console for tracebacks. The app also writes `voice_debug.log` for the
TTS/STT path.

## 6. Building a standalone `.exe`

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1        # full
powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1 -NoTTS # smaller, SAPI5 fallback
```

- Output: `dist\Sentinel-Forge\Sentinel-Forge.exe` + `_internal\` runtime.
- **One-folder build on purpose:** fast cold-start, and the ~60 MB Piper voice
  model isn't re-extracted to `%TEMP%` on every launch. Ship the whole
  `dist\Sentinel-Forge\` folder.
- Spec file: `Sentinel-Forge.spec`.

## 7. GitHub repository hygiene (2026 classroom expectations)

A reviewer in 2026 expects a public repo to have these. Current status:

| Item | Status | Action |
| --- | --- | --- |
| README with build + architecture | ✅ | Present |
| Engineering/SDLC doc | ✅ | `docs/SDLC_STATUS.md` |
| **Wiki / knowledge base** | ✅ (this) | Keep updated as session notes |
| MIT `LICENSE` | ✅ | Present |
| `.gitignore` / `.gitattributes` | ✅ | Present |
| **Version tag** (`v0.9-rc1`) | ❌ | Tag the release candidate |
| **`CHANGELOG.md`** | ❌ | Start one (Keep a Changelog format) |
| **CI** (GitHub Actions running `unittest`) | ❌ | Add a workflow: `py_compile` + `unittest` on push/PR |
| Issue/PR templates | ❌ | Optional but expected for collaboration |
| Branch protection on `main` | ❌ | Optional for a solo repo; expected on teams |

**Recommended next process steps:** tag `v0.9-rc1`, add `CHANGELOG.md`, and add a
minimal GitHub Actions workflow so every push proves the suite is green. These
three close most of the "2026 classroom" gaps.
