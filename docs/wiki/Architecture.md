# Architecture

*Reviewed 2026-06-27 against `aea48c8`.*

## 1. The one-sentence model

Sentinel Forge is built as a **functional core / imperative shell** (Gary
Bernhardt's term): a thin, hard-to-test GUI shell wrapping a growing set of
pure, easily-tested logic modules.

```
┌─────────────────────────────────────────────────────────────┐
│  IMPERATIVE SHELL  —  sentinel_personal_development.py        │
│  class BookReader  (~590 methods, ~23.6k LOC)                │
│  • owns the Tk root, every window, widget, and event binding │
│  • does all I/O: file open, subprocess (TTS/STT), DB calls   │
│  • orchestrates worker threads and marshals results to the UI│
└───────────────┬─────────────────────────────────────────────┘
                │ calls (one-way, downward)
                ▼
┌─────────────────────────────────────────────────────────────┐
│  FUNCTIONAL CORE  —  lyceum/  (pure, UI-free, unit-tested)   │
│  • metrics.py            progress math (no Tk, no DB)         │
│  • text_norm.py          TTS text normalization (string→str) │
│  • dictation_commands.py spoken-punctuation parser (str→str) │
│  • db/study_db.py        SQLite schema + atomic transaction()│
│  • reminders.py          Windows scheduled-task reminders    │
└─────────────────────────────────────────────────────────────┘
```

**Why this split matters (the textbook reason):** GUI code is notoriously hard
to test — you cannot easily assert on pixels, and a withdrawn Tk root still
needs a display. By pushing *decision logic* down into pure functions
(`input → output`, no side effects), that logic becomes unit-testable **without
launching the GUI or touching the database**. The shell shrinks to "fetch data,
call core, render result," which is the part you verify by eye.

## 2. The honest caveat: `BookReader` is a God Object

The shell is **one class with ~590 methods**. Measured this cycle with Python's
`ast` module:

- **1 class · 953 functions · ~23.6k LOC**; `BookReader` holds **590 methods**.
- This is the **God Object** anti-pattern — it violates the **Single
  Responsibility Principle** (a class should have one reason to change; this one
  changes for *every* feature: reading, TTS, finance, habits, planning…).
- **McCabe cyclomatic complexity** (decision-point count per function):
  - 831 functions are *simple* (≤10),
  - 81 *moderate* (11–20),
  - 38 *complex* (21–50),
  - **3 are effectively untestable (>50):** `_build_goals_panel` (66),
    `open_idea_warehouse` (60), `_ftb_read_toggle` (58).

**Direction of travel:** the project is **not** doing a big-bang rewrite (which
Fowler warns against). It is applying **incremental Extract-Module refactoring** —
pulling pure logic out of the class *as it is touched*, each extraction landing
with tests. `lyceum/metrics`, `lyceum/text_norm`, `lyceum/dictation_commands`,
and `lyceum/db` are the pieces extracted so far. Full UI-level decomposition of
the three CC>50 builders is deferred to visual QA (you cannot screenshot a
`pythonw` GUI headlessly to verify a refactor).

## 3. The concurrency / threading model

Tkinter, like most GUI toolkits, is **single-threaded**: only the thread that
owns the event loop (`mainloop`) may touch widgets. Long jobs — running the
Piper TTS subprocess, Whisper transcription, an Ollama call, a web search —
**must not** run on that thread or the whole window freezes.

The pattern used throughout:

```python
def _worker():
    result = do_slow_blocking_thing()          # on a background thread
    self.root.after(0, lambda: render(result)) # marshal back to the UI thread
threading.Thread(target=_worker, daemon=True).start()
```

- **Rule:** background threads compute; **`root.after(...)`** is the only way
  they are allowed to mutate the UI. This is *thread confinement* — UI state is
  confined to the UI thread, and cross-thread hand-offs go through the event
  queue.
- Breaking this rule caused a real shipped bug — a stale worker clearing fresh
  highlights — see [Former Bugs](Former-Bugs-and-Regressions.md#1-thread-safety-race-the-vanishing-highlights).

## 4. Graceful degradation (optional-dependency policy)

Every non-stdlib capability is imported defensively:

```python
try:
    import pypdf
    _HAVE_PDF = True
except ImportError:
    _HAVE_PDF = False
```

If the package is absent, the matching feature is disabled and the rest of the
app runs. The **only hard dependency is Tkinter** (bundled with the official
Python installer). This keeps the app robust on a fresh machine and is why the
core can run on "~5 MB without TTS."

| Optional dependency | Capability it unlocks | If missing |
| --- | --- | --- |
| `faster-whisper`, `sounddevice`, `numpy`, `noisereduce` | Offline voice dictation | Dictation disabled |
| `python-docx` / `pypdf` / `beautifulsoup4` | `.docx` / `.pdf` / `.html` books | That format won't open; others still do |
| `ollama` (+ a pulled model) | Onboard AI assistant (`ai_brain.py`) | AI buttons return nothing; app unaffected |
| `tkinterdnd2` | Drag-and-drop into Library | Use the file picker instead |
| `send2trash` | Recoverable Library deletes | Falls back to permanent delete |
| `pyspellchecker` | Voice Memory spelling helper | Spelling suggestions off |

## 5. Process & data boundaries

- **TTS / STT run as child processes**, not in-process. All `subprocess` calls
  use **list-arguments (never `shell=True`)** and **`CREATE_NO_WINDOW`** so no
  console flashes on Windows 11. Long text is passed via a **temp file**, not the
  command line, to dodge the OS command-length limit (see
  [Former Bugs](Former-Bugs-and-Regressions.md#5-command-line-length-limit-argmax)).
- **Two persistence stores:**
  1. **`study.db`** (SQLite) at `~\OneDrive\Documents\BookReader\study.db` — all
     structured app state (37 tables). See [Database Schema](Database-Schema.md).
  2. **Markdown excerpts** with YAML front-matter under `…\Desktop\Books\` — the
     saved-passage vault (zone, cognitive load, source, timestamp), each with a
     sidecar `*.md.meta.json` for fast scanning.
- **UTF-8 everywhere** for file I/O — avoids the Windows `cp1252` mojibake trap.

## 6. Architectural risks on the radar

| Risk | Why it matters | Status |
| --- | --- | --- |
| God Object (`BookReader`) | Hard to test, change-coupled | Mitigating via Extract-Module |
| 3 functions with CC > 50 | Untestable branches; defect-prone | Logic extracted where possible; UI builders deferred |
| `study.db` under OneDrive | Live SQLite + cloud sync ⇒ possible conflict copies | Acceptable for single-user; flagged |
| No High-DPI declaration | Blurry text on scaled displays | Open (see [SDLC](SDLC-and-Process.md)) |

See [SDLC & Process](SDLC-and-Process.md) for the full conformance checklist and
exit criteria.
