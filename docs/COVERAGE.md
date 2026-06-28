# Test Coverage Report

*Snapshot generated with `coverage.py` over the 135-test suite. Reproduce with
the commands at the bottom. Reviewed 2026-06-28.*

## Headline

- **Functional core: 85%** (the pure, logic-bearing modules — what a test suite
  is supposed to cover).
- **Pure-logic kernels: 90–100%** (`goals`, `ideas`, `util`, `metrics` 100%;
  `finance` 98%; `dictation_commands` 97%; `voice_pipeline` 95%; `text_norm` 91%;
  `local_context` 90%).
- **Full `lyceum` + `ai_brain`: 64%** — the lower figure is dragged down by
  GUI/OS-only modules (the scheduled-reminder window and Windows-API shims) that
  cannot be exercised headlessly. See "What isn't covered, and why" below.
- The 23k-line Tkinter shell (`sentinel_personal_development.py`) is **not** in
  these numbers by design — it's the imperative shell, verified by manual/visual
  QA. The whole point of the `lyceum/` extraction was to make the *logic*
  measurable in isolation.

## Functional-core breakdown (85%)

| Module | Cover | Notes |
| --- | --- | --- |
| `lyceum/goals.py` | 100% | accountability + summarize, all branches |
| `lyceum/ideas.py` | 100% | task ordering + banner counts |
| `lyceum/util.py` | 100% | zone/format/habit/dates/PERT/time-parse |
| `lyceum/metrics.py` | 100% | progress kernels |
| `lyceum/finance.py` | 98% | money/budget/retirement math |
| `lyceum/dictation_commands.py` | 97% | spoken-punctuation parser |
| `lyceum/voice_pipeline.py` | 95% | sentence chunker + duplex loop |
| `lyceum/text_norm.py` | 91% | TTS normalization incl. years |
| `lyceum/local_context.py` | 90% | RAG ranking + chunk retrieval |
| `lyceum/dictation_guard.py` | 86% | punctuation collision dedup |
| `lyceum/db/db_location.py` | 84% | DB relocation + snapshot |
| `lyceum/doc_index.py` | 78% | library extractor + cache |
| `lyceum/db/study_db.py` | 55% | schema + data layer (init/migrate paths have side effects, not unit-tested) |
| `ai_brain.py` | 59% | `stream()` covered live; `ask()`/`explain()` need Ollama |

## What isn't covered, and why (honest)

These are excluded from the 85% core figure because they require a display,
microphone, screen reader, or network that a headless CI runner doesn't have —
they're verified by manual QA, not unit tests:

| Module | Cover | Reason |
| --- | --- | --- |
| `lyceum/reminder_flash.py` | 0% | A Tkinter alert window — pure GUI |
| `lyceum/reminders.py` | 0% | Windows scheduled-task registration (OS side effects) |
| `lyceum/platform_dpi.py` | 50% | Windows DPI APIs; branch depends on OS version |
| `lyceum/sapi_tts.py` | 71% | SAPI5 needs pywin32 + speakers |
| `lyceum/accessibility_bridge.py` | 63% | needs a running NVDA |
| `lyceum/stt_command.py` | 55% | the mic loop is I/O; the pure grammar/matcher *is* tested |

## Reproduce

```powershell
py -3 -m pip install coverage
py -3 -m coverage run --source=lyceum,ai_brain -m unittest discover -s tests
py -3 -m coverage report
# functional-core only:
py -3 -m coverage report --omit="lyceum/reminder_flash.py,lyceum/reminders.py,lyceum/platform_dpi.py,lyceum/accessibility_bridge.py,lyceum/sapi_tts.py,lyceum/stt_command.py"
```
