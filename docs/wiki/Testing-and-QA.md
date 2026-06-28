# Testing & QA

*Reviewed 2026-06-27 against `aea48c8`.*

## How to run the suite

From the repository root:

```powershell
python -m unittest discover -s tests
```

All tests are **headless**: they import **no Tkinter** and touch **no real
database** (the transaction tests use a throwaway temp DB). That is the entire
payoff of the [functional-core / imperative-shell](Architecture.md) split — the
decision logic can be verified without a display or audio device.

## Current state: 34 unit tests, all passing

> The README states 24; the [SDLC status doc](SDLC-and-Process.md) and the latest
> dictation work bring it to **34** (24 + 10 dictation-command tests). Treat
> **34** as current and reconcile the README badge — tracked as a doc item.

| Test file | Count | What it locks in |
| --- | --- | --- |
| `tests/test_metrics.py` | ~12 | The shared **progress kernel** `progress_pct` and its wrappers `wheel_progress` / `goal_progress`. |
| `tests/test_transactions.py` | 2 | **ACID Atomicity**: commit persists all statements; mid-unit exception rolls back to zero rows. |
| `tests/test_text_norm.py` | ~10 | `normalize_for_speech` — currency, percents, ordinals, decimals, abbreviations, and *plain text unchanged*. |
| `tests/test_dictation_commands.py` | ~10 | `apply_dictation_commands` — spoken punctuation, new line/paragraph, caps modes, *plain text unchanged*. |

### What the tests demonstrate (the interesting ones)

- **Honest progress, including backsliding.** `test_real_data_backslide` feeds
  the user's *actual* four Wheel snapshots (averages 4.71 → 2.86 → 3.00 → 2.14)
  and asserts `pct == 0` with a `▼` arrow. The metric is designed so that being
  below your baseline reports **0%**, not a flattering number — *the math refuses
  to lie to the user.*
- **Proportional progress.** `progress_pct(6, 3, 8) == 60` — i.e.
  `(current − baseline) / (target − baseline)`, clamped to `[0, 100]`.
- **Atomicity proven directly.** `test_rollback_on_midunit_failure` inserts one
  row, raises `ValueError` mid-unit, and asserts the table is left with **zero**
  rows — the rollback undid the partial write.
- **Defensive purity.** Both string cores assert that `""` and `None` are safe
  and that ordinary prose passes through untouched — these functions sit on the
  live read-aloud / dictation path and must never raise.

## Test design principles in use

| Principle | Where it shows up |
| --- | --- |
| **Test the core, not the shell** | All four files target `lyceum/*`; the GUI is verified manually. |
| **Arrange-Act-Assert** | Each test sets inputs, calls one function, asserts one behavior. |
| **Test fixtures / isolation** | `test_transactions.py` uses `tempfile.mkstemp`, swaps `STUDY_DB`, restores it in `tearDown` — no shared state, no real data touched. |
| **Boundary & edge cases** | Empty input, `None`, out-of-range targets (clamped), singular vs plural ("$1" → "one dollar"). |
| **Regression tests** | Bug fixes that live in the core get a test (e.g. atomicity). See [Former Bugs](Former-Bugs-and-Regressions.md). |

## Verification & Validation status (IEEE 829 / SWEBOK V&V)

- **Unit testing:** ✅ established this cycle — first automated tests in the
  project's history.
- **Manual verification:** GUI panels are smoke-tested by launching the app and
  confirming each window builds and "blends with Windows 11."
- **Integration / system testing:** ⚠️ **no recorded suite.** Cross-subsystem
  flows (open book → highlight → save excerpt → Library zone filter) are checked
  by hand, not scripted.
- **Coverage:** narrow by design — high on the extracted core, ~nonexistent on
  the 590-method shell (which is the bulk of the LOC).

## Known gaps / the QA backlog

1. **Define a QA gate** ("Definition of Done" for a release): what must pass
   before cutting a build. Currently informal (manual window smoke test).
2. **Integration test record** for the marquee end-to-end reading flow.
3. **Coverage measurement** (`coverage.py`) so the untested surface is visible,
   not assumed.
4. **Reconcile the test count** (README says 24; actual 34).
5. **Extract more decision logic** out of the CC>50 builders so it becomes
   testable — every extraction is a chance to add tests (Fowler: refactor as you
   touch).

The guiding rule going forward: **`py_compile` is the floor; a green
`unittest` run is the ceiling — and any logic-bug fix in `lyceum/` ships with a
failing-then-passing test.**
