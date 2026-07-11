# Former Bugs & Regressions

*A documented history of notable defects that were found and fixed, each named
with the computer-science concept behind it and the guard now in place. This is
deliberately framed the way a professor would: a bug is only "fixed" when you can
**name the failure mode** and **show what prevents its return**.*

Commit hashes are clickable into the repo. Reviewed 2026-06-27 against `aea48c8`.

---

## 1. Thread-safety race: the vanishing highlights
**Commit [`99950c3`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/99950c3) — "Thread Safety Fix"**

- **Symptom:** when the AI assistant auto-read its reply aloud, the brand-new
  follow-along highlights were cleared *instantly*.
- **Concept — race condition / shared mutable state across threads.** Two
  asynchronous flows touched the same highlight tags: the new read-aloud worker
  painting highlights, and a *previous* worker's teardown still in flight,
  clearing them. Because GUI state was being mutated from more than one timeline,
  order of execution was non-deterministic — a classic data race.
- **Fix & guard:** serialize the hand-off so a stale clear cannot run after a
  fresh paint, and route all highlight mutation through the UI thread via
  `root.after(...)`. See the **threading model** in
  [Architecture §3](Architecture.md#3-the-concurrency--threading-model). Related:
  [`e7ba4ae`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/e7ba4ae)
  made the auto-reader reuse `_ftb_read_toggle` directly so there is **one**
  highlight engine, not two competing code paths.

## 2. Off-by-one / stale index: unhighlighted AI responses
**Commit [`bcdcfdf`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/bcdcfdf) — "Fix tk.END usage…"**

- **Symptom:** AI responses appeared but were never highlighted.
- **Concept — boundary error against a moving target.** In a Tk `Text` widget,
  `tk.END` resolves to the *current* end of the buffer **at evaluation time**.
  The code captured `tk.END` and then wrote more text, so the saved index now
  pointed *before* the newly inserted response — the highlight range covered
  empty space. This is the GUI cousin of an off-by-one / TOCTOU (the index was
  valid when read, stale when used).
- **Fix & guard:** compute the highlight bounds from the actual inserted span
  rather than a pre-captured `tk.END`. Anchor indices to the text you just wrote,
  not to a sentinel that drifts.

## 3. Unhandled exception in an iteration loop: TTS halts after one chunk
**Commit [`85906f5`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/85906f5) — "Fix continuous TTS reading halting after a single chunk…"**

- **Symptom:** continuous read-aloud spoke the first sentence, then stopped.
- **Concept — an exception escaping a loop body terminates the loop.** Computing
  the next chunk's text-widget indices could raise `tk.TclError` (out-of-bounds
  indexing) on certain inputs; the unhandled exception broke out of the
  read loop, so iteration died after chunk one.
- **Fix & guard:** bounds-check before indexing and handle `TclError` inside the
  loop so a single bad chunk is skipped, not fatal. **Robustness principle:** a
  long-running loop over user data must treat a single malformed item as
  recoverable.

## 4. Parser/encoding error: newlines break text-to-speech
**Commit [`d0917be`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/d0917be) — "Fix text-to-speech parser error with newlines"**

- **Symptom:** passages containing newlines failed to speak.
- **Concept — unescaped control characters crossing a process/quoting boundary.**
  Text handed to the speech subprocess was not safely quoted/escaped, so embedded
  newlines corrupted the command the TTS engine parsed.
- **Fix & guard:** sanitize and safely quote text before it crosses the
  subprocess boundary (`_ps_single_quote` and friends). This is the same class of
  problem as injection — **never build a command string by naive concatenation of
  untrusted text.** It also motivated fix #5.

## 5. Command-line length limit (ARG_MAX)
**Commit [`8dca41d`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/8dca41d) — "Bypass command-line length limits using a temp file…"**

- **Symptom:** reading a large selection aloud failed outright.
- **Concept — OS limit on total command-line length.** Every operating system
  caps the size of a process's argument vector (Windows `CreateProcess` ≈ 32 KB
  for the command line). Passing a whole chapter as a CLI argument blew past it.
- **Fix & guard:** write the text to a **temporary file** and pass the *path* to
  the TTS engine. **Lesson:** bulk data belongs in a file or stdin pipe, never in
  `argv`.

## 6. Non-atomic deletes (ACID violation)
**Commit [`d92afb3`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/d92afb3) — "DB: add transaction() primitive; make parent/child deletes atomic"**

- **Symptom (latent):** several deletions ran as **two independently
  auto-committed statements**. A crash *between* them could orphan child rows or
  half-delete a record.
- **Concept — Atomicity, the 'A' in ACID.** A logical operation made of multiple
  statements must be **all-or-nothing**. Two separate auto-commits are two
  separate transactions, so the in-between state is observable and corruptible.
- **Fix & guard:** the `transaction()` context manager (commit on success,
  `ROLLBACK` on any exception) now wraps four parent/child delete units. Locked
  in by **`tests/test_transactions.py`**, which proves both halves: a clean unit
  persists *all* statements, and a mid-unit exception rolls back to **zero** rows.
  See [Database Schema](Database-Schema.md#the-transaction-primitive--acid-atomicity).

## 7. Syntax error in a `for…else` construct
**Commit [`d00ef47`](https://github.com/coconuthead-Sentinel-core/sentinel-forge-personal-development/commit/d00ef47) — "Fix syntax error in for-else loop"**

- **Concept — Python's `for…else` is widely misread.** The `else` runs when the
  loop completes **without `break`**, not "if the loop was empty." A
  misunderstanding here produced a syntax/logic error.
- **Guard:** the project now runs **`py_compile`** as a pre-commit smoke check so
  a syntax error can't reach `main` (the build paperwork records "py_compile
  clean" on the DB-atomicity commit).

---

## Cross-cutting lessons baked into the codebase

These recurring fixes hardened into standing rules — apply them to all new code:

1. **UI mutation only on the UI thread** (`root.after`); workers compute, they
   don't paint. *(bugs 1, 2)*
2. **Index against the text you actually wrote**, never a sentinel that moves.
   *(bug 2)*
3. **Loops over user data swallow per-item failures** and continue. *(bug 3)*
4. **Escape/quote everything crossing a process boundary**; bulk data goes in a
   file, not `argv`. *(bugs 4, 5)*
5. **Multi-statement DB work is atomic or it doesn't ship** — wrap it in
   `transaction()`. *(bug 6)*
6. **`py_compile` is the floor**; tests are the ceiling. *(bug 7)*

## How to add to this page

When you fix a bug, append an entry with: **symptom → named CS concept →
fix & guard → commit link**. If the bug was a logic error in the functional
core, add a **failing-then-passing unit test** and cite it here — that is what
turns "fixed" into "can't regress." See [Testing & QA](Testing-and-QA.md).


## July 2026 — the "silent sweep" regression batch

Three regression families traced to the post-v0.9 refactor commits
(`2f08bfb`..`8e70f8e`), all sharing one root pattern: **failures hidden
inside bare `except: pass`.**

1. **Save-widget sweep orphans.** A cleanup removed Save/Delete buttons
   project-wide but left the save functions with nothing calling them —
   7 dialogs (Scoreboard editor, V2MOM, Daily 10 Goals, Session-End
   handoff, Glossary editor, Goals worksheet, block dialogs) accepted
   typing and silently kept nothing. Fix: buttons restored; Daily 10
   also gained an in-window ✓ confirmation + auto-close (a save the
   user can't SEE reads as broken).
2. **Read-aloud silence.** Piper playback was swapped from stdlib
   `winsound` to `pyaudio` inside `except: pass`; PortAudio raises
   OSError -9999 on this hardware, so every read highlighted in
   silence. Fix: winsound restored (the stop paths still expected its
   `SND_PURGE`); playback errors now surface as error events.
3. **Constructor-tuple pady crashes.** Seven `tk.Label(..., pady=(12, 2))`
   constructor tuples (glossary editor, folder + time-block dialogs)
   raised `bad screen distance` and aborted those windows half-built —
   the codebase's oldest recurring trap, now swept project-wide.

**Standing lesson:** when the user says "X doesn't work," grep for a
swallowed exception near X first, and check `voice_debug.log` for
anything voice-related. And after any large pulled refactor, verify the
audio/UI paths **on the real hardware** before trusting them.
