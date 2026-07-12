# Configuration & Secrets Inventory — Sentinel Forge

- Project name: Sentinel Forge — Personal Development
- Build name: Full reconstruction (disaster-recovery rebuild)
- Owner: Shannon Brian Kelley (architect/QA) + AI coding assistant (implementer)
- Date: 2026-07-11
- Status: approved (standing paperwork; refresh on each release)

## Secrets
**None. By design.** No API keys, no accounts, no tokens, no telemetry.
This is a load-bearing product decision (local-first privacy) — any change
requires the owner's explicit approval and a README disclosure.

## Configuration knobs
| Knob | Default | Purpose |
| --- | --- | --- |
| `SENTINEL_FORGE_BOOKS_DIR` (env) | `Desktop\Books` | library location |
| `SENTINEL_FORGE_INDEX_DIR` (env) | E:\SentinelForge else %LOCALAPPDATA% | index cache |
| `SENTINEL_AI_MODEL` (env) | llama3.2:3b | assistant model |
| `SENTINEL_AI_NUM_CTX` (env) | 2048 | RAM ceiling law |
| `SENTINEL_AI_KEEP_ALIVE` (env) | 10m | model warm window |
| font family/size, read speed, toolbar dock, mode/zone | persisted | HANDOFF_STATE.json / study.db state table |
| Scoreboard measures, planner, goals, decks | user data | study.db |

## Pseudocode — configuration law
```pseudocode
read_config(name): env_var(name) else persisted_state(name) else default
NEVER a config file the user must hand-edit; NEVER a secret store.
```
