# Deployment & Release Inventory — Sentinel Forge

- Project name: Sentinel Forge — Personal Development
- Build name: Full reconstruction (disaster-recovery rebuild)
- Owner: Shannon Brian Kelley (architect/QA) + AI coding assistant (implementer)
- Date: 2026-07-11
- Status: approved (standing paperwork; refresh on each release)

## Release channels
| Channel | Mechanism | Consumer |
| --- | --- | --- |
| Source (primary) | GitHub main → `git pull` in BOTH clones | the owner's two OneDrive-synced checkouts |
| Desktop shortcut | `run_sentinel.bat` in `Desktop\Sentinel-Forge` | daily use — ALWAYS pull here after push |
| Standalone .exe | `scripts/build_exe.ps1` (PyInstaller one-folder) | demo/distribution |

## Release procedure (pseudocode)
```pseudocode
per work block:
    branch work from origin/main (worktree)
    implement core+tests -> window -> full suite green
    commit (honest message) -> push work:main
    pull OneDrive clone; pull Desktop\Sentinel-Forge
    delete work branch                # single-branch law
    verify: rev-parse HEAD identical x3
version stamp (v1.0 etc.): README badge + roadmap + tag on GitHub
```

## Rollback
`git revert` on main (never force-push); DB is decoupled from code —
additive-only schema means old code runs against a newer DB.
