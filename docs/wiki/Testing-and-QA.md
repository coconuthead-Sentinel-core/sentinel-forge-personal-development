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

## Current state: 172 automated tests, all passing (July 2026)

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


## July 2026 update — 172 tests

The suite grew from 34 to **172** across the July feature track. New
test files, all still headless (no Tkinter, throwaway temp DBs):

| File | Covers |
| --- | --- |
| `test_srs.py` | FSRS spaced-repetition core: schema idempotency, card round-trip, **proven review atomicity** (forced failure between card UPDATE and log INSERT rolls back both), deterministic scheduling (fuzzing disabled), idempotent glossary sync, resync repair |
| `test_doc_writer.py` | model text → real .docx/.xlsx: tolerant table parsing, live =SUM() formulas, illegal sheet-title sanitizing (a `Budget: July` tab name aborted the write — caught end-to-end), refusal detection, safe filenames |
| `test_doc_index.py` (extended) | broad-folder indexer: repo-dir exclusion (.git, node_modules…), relative-path labels, mtime cache reuse, Excel/CSV extraction |
| plus | integration tests, GUI harness, finance kernel, voice modules (from the earlier hardening track) |

Verification practice for UI work: **headless smoke scripts** driving
the real app under a genuine `mainloop()` (worker threads deliver via
`after()`, which silently fails without one — a lesson learned twice).

## The breadcrumb method (standing QA practice — formalized 2026-07-16)

When the proprietor road-tests on the real screen and something
"doesn't work," the first move is a **log read, not a guess**. Every
QA-sensitive seam writes one timestamped line to an append-only local
log the moment it fires, so a field report can be answered with
evidence: did the handler run, with what values, and what did it decide?

| Log (all `*.log`, git-ignored, live next to the app) | What it proves |
| --- | --- |
| `voice_debug.log` | every voice change, read-aloud, TTS subprocess, and normalization change (before → after) |
| `%LOCALAPPDATA%\SentinelForge\fontsize_debug.log` | every A−/A+ click with old → new pt (the log that solved the "dead plugs" report) |
| `qa_debug.log` | **the QA trail**: floating-toolbar dispatch — which panel CLAIMED Add/Save/Delete, or that the click fell through; every dock move (requested target → resolved window); every reward draw (event → tier, drought counter); ambience start/stop/unavailable |

Rules of the method:
1. **One line per real event**, timestamped, `pid`-stamped — appended,
   never rewritten.
2. **Logging never raises** — every write is wrapped; a broken log must
   never break the app.
3. **Log decisions, not chatter** — the line records what was decided
   and the values that decided it (e.g. `ftb-review: DELETE claimed,
   day=2026-07-01, cleared=False (past day refused, archive law)`).
4. New feature → new breadcrumbs at its QA seams **in the same sprint**,
   so the proprietor's first road test is diagnosable from day one.

Field-report workflow: proprietor reports what he clicked and what he
saw → engineer reads the tail of the relevant log → the report resolves
to "never fired" (wiring defect), "fired with wrong values" (logic
defect), or "fired correctly but invisibly" (feedback defect) — three
different fixes, one log read apart.

---

## Field QA session sheet — 2026-07-20 (owner-led UAT, stabilization phase)

**Standing order (proprietor, 2026-07-20): feature freeze holds. No new
development; test what exists, log what's found.** This sheet is the
session script. Mark each line ✅ pass / ❌ fail + one note; a ❌ becomes
a defect report (screenshot + what you expected vs. what happened —
the Prompt Library find is the model). Breadcrumbs are your witness —
two addresses (corrected 2026-07-21; the old line sent readers to the
wrong door for two of the three): `voice_debug.log` and `qa_debug.log`
live NEXT TO THE APP in `Desktop\Sentinel-Forge\`;
`fontsize_debug.log` lives in `%LOCALAPPDATA%\SentinelForge\`.

**Setup (dogfood on purpose):** open Session Start, pre-commit to
"Field QA session," and run the session inside a 🔥 Do Now 25-minute
block — the timer under test is also the timer timing the test.

**Prompt Library CLOSE-OUT gate (proprietor, 2026-07-21 — NOT clear
yet).** One 25-min Pomodoro, three checks, all on the real screen:
1. 🔡 **A+** → Title/Prompt/Response letters visibly grow
2. 🎤 toolbar mic → a dictated **Title** lands in the box
3. 🔴 red lamp archives an entry → `.md` file appears in
   `Desktop\Prompt Archive\`

Three checkmarks = section clear → move to the next field-sheet line.
(The three span §A line 4 and the two §B re-test lines below — bundled
here as one gate by the proprietor's order.)

### A. Today's ship — Prompt Library repair (step 7 still open)
- [ ] Open 🗒 Prompt Library → traffic-light toolbar is docked at the top on arrival
- [ ] Edit a selected entry → yellow **Save** → status shows "entry saved"
- [ ] Red **Delete** on a junk entry → dialog says ARCHIVE (not "can't be undone") → entry leaves the list
- [ ] The archived entry exists as a `.md` file in `Desktop\Prompt Archive\` and opens readable
- [ ] Right-click an entry → "🗃 Archive this entry" present and works
- [ ] Close the window → toolbar returns home to the dashboard

### B. Recently shipped, never verified on this laptop
- [ ] 🌧 Ambience: pick Rain, Quiet → **audible** under the reading voice, on the real speakers (this is the one the bench could not verify)
- [ ] 🎁 Reward-Draw: finish the 25-min Do Now block → a draw fires (dot, quote card, or gold) and `reward_log` gains a row
- [ ] 🪞 AAR window: toolbar docks there; Save commits today's reflection; Delete refuses past days
- [ ] ⏱ Time Check popup (fixed 2026-07-20, re-test): dock the bar via the dock menu → type or dictate a note → yellow Save or Enter files it → status reads "⏱ Logged: … · ✏ note saved"
- [ ] 🔡 A−/A+ in Prompt Library (fixed 2026-07-21, re-test): open Prompt Library → A+ twice → Title/Prompt/Response letters visibly grow; breadcrumb line shows prompt_lib=yes
- [ ] 🎤 Mic enrollment (fixed 2026-07-20, re-test): focus the Prompt Library Title box → toolbar mic → speak a session title → words land in the box (then Prompt, Response, and the Time Check note the same way)
- [x] 📋 Last-session handoff copy (fixed 2026-07-21) — ✅ **owner re-test PASSED 2026-07-21 ~04:00**: proprietor right-clicked, copied, and pasted the full handoff (summary + next task + blocker + notes) to the assistant — the previously-impossible action, done with the real mouse on the real screen. Coaching note filed: right-click → Select all → Copy grabs a whole box in one shot.
- [ ] 🖱 Select all on single-line fields (fixed 2026-07-21, re-test): click ONCE anywhere in the "One primary task" field → right-click → Select all → the whole line highlights (no dragging) → Copy → paste anywhere → the full line arrives. Same now works on every single-line box in the app.
- [ ] 🔊 Read on the Last-session box (fixed 2026-07-21, re-test): click anywhere in the "Last session" box → toolbar 🔊 Read → the handoff is spoken from the first word (the notes box already worked; now both sections read aloud).
- [ ] 🗒 Prompt Library fits its window (fixed 2026-07-21, re-test): open Prompt Library → A+ up to a big size → Title, Prompt, AND Response boxes all visible with the ➕ Add / + New / 📋 Paste buttons at the bottom; Prompt and Response split the space evenly; the left list scrolls to every entry (no 12-entry limit — it was the clipping).
- [x] 🧠 Harvest checkboxes visible (fixed 2026-07-22) — ✅ **owner re-test PASSED 2026-07-22**: proprietor ran Harvest, checked/unchecked visibly, approved, and confirmed the terms SAVED to the Glossary ("tool function performed adequately — harvested the key terms, seven and all, saved, confirmation").

### C. Timer sweep (first full pass on the record)
- [ ] 🔥 Do Now 25-min Pomodoro: counts down, ends visibly (used as the session frame above)
- [ ] 🎯 Focus Mode 60/90: starts, countdown visible, cancel works cleanly
- [ ] 🚀 5-4-3-2-1: beats once per second, lands in Focus Mode on the #1 task
- [ ] ⏱ Winner's Time Log at 5-min interval: chime fires, one-tap files it, pie chart updates
- [ ] 🌤 Vision Board 60-second slideshow: plays, countdown shown, pause/next work, WAV music if set
- [ ] ⏳ Wishlist: cooling item shows correct days remaining; "bought" stays disabled
- [ ] Morning/evening nudges (Daily 10, vision board, AAR): can't be forced on demand — observe over the coming week and log dates seen

### D. Imprint (documentation suite)
- [ ] Launches clean from its shortcut
- [ ] One document automation runs end-to-end and the output file opens in Word/Excel
- [ ] Assistant buttons (🌐 web, ☁ OneDrive, 📄 draft) each produce a visible result or an honest error

**Close-out:** write results below this sheet (date + ✅/❌ lines),
then the assistant reconciles: defects get triaged, the suite stays
green, results get committed and mirrored. Maintenance mode until the
sheet is clean.
