# Glossary of CS Concepts

*Plain-language definitions of every computer-science concept this codebase
relies on, each anchored to **where it actually appears in Sentinel Forge**. This
is written for the project's owner, who is learning programming — so each term is
defined, then tied back to your own code.*

---

### ACID (Atomicity, Consistency, Isolation, Durability)
The four guarantees a database transaction should provide. **Atomicity** = a
multi-step operation happens *completely or not at all*. **In your code:**
`lyceum/db/study_db.py: transaction()` gives you Atomicity — deleting a paycheck
and its budget items either both happen or neither does. See
[Database Schema](Database-Schema.md#the-transaction-primitive--acid-atomicity).

### Anti-pattern
A common "solution" that looks reasonable but causes trouble later. **In your
code:** the **God Object** — one class doing everything.

### `ast` (Abstract Syntax Tree)
A structured, tree representation of source code that tools read to *measure* it
(count functions, compute complexity) without running it. **In your project:**
used to measure "953 functions, 590 methods, CC per function."

### Boundary / off-by-one error
A mistake at the edge of a range — counting one too many or one too few, or using
an index that's just past the valid data. **In your code:** the `tk.END` bug
(#2 in [Former Bugs](Former-Bugs-and-Regressions.md)) — `tk.END` pointed *past* the
text you just wrote, so the highlight missed it.

### Cyclomatic complexity (McCabe)
A number that counts the independent decision paths through a function (each
`if`/`for`/`and` adds one). Higher = more branches = harder to test and more
bug-prone. **Rule of thumb:** ≤10 fine, >50 effectively untestable. **In your
code:** `_build_goals_panel` (66), `open_idea_warehouse` (60),
`_ftb_read_toggle` (58) are the three to break up.

### Defensive programming
Writing code that survives bad input instead of crashing. **In your code:**
`normalize_for_speech` and `apply_dictation_commands` both `return text` on any
error — a weird passage can never break a read-aloud or dictation session.

### Functional core / imperative shell
A design where pure decision-logic (no I/O, easy to test) sits at the center and
the messy I/O/UI code wraps around it. **In your code:** `lyceum/` is the core;
`BookReader` is the shell. See [Architecture](Architecture.md).

### Graceful degradation
When an optional capability is missing, the program disables *just that feature*
and keeps running. **In your code:** every `try/except ImportError` — no `pypdf`?
PDFs won't open but everything else works.

### God Object
One class that knows and does too much — it becomes the place every change has to
touch. **In your code:** `BookReader` (590 methods). It works, but it's the #1
thing to gradually break apart. Opposite principle: **Single Responsibility**.

### Idempotent
An operation you can run repeatedly with the same result as running it once.
**In your code:** `init_study_db()` — `CREATE TABLE IF NOT EXISTS` means starting
the app 1,000 times doesn't duplicate or damage anything.

### Marshaling (to a thread)
Handing data or work from one thread to another safely. **In your code:**
`root.after(0, …)` marshals a background worker's result onto the UI thread —
the only thread allowed to touch widgets.

### Migration (database)
Changing a database's structure after it already has data in it. **In your
code:** the `ALTER TABLE goals ADD COLUMN baseline …` guarded by a
`PRAGMA table_info` check — adds new columns to an existing `study.db` without
losing rows.

### Race condition
A bug where the outcome depends on the unpredictable *timing* of two things
happening at once. **In your code:** the vanishing-highlights bug (#1) — a stale
worker cleared highlights a new worker had just painted. Fixed by serializing and
using a single highlight engine.

### Referential integrity / foreign key / CASCADE
Rules that keep related rows consistent — e.g. deleting a topic should delete its
entries, not leave "orphans." **In your code:** `topic_entries → topics ON DELETE
CASCADE`, and `PRAGMA foreign_keys = ON` on every connection (SQLite leaves FK
enforcement *off* by default — a classic trap you avoid).

### Regression test
A test added specifically so a bug that was fixed can never silently come back.
**In your code:** `test_transactions.py` is the regression test for the
atomicity bug.

### `shell=True` / command injection
Building a shell command by pasting text together lets that text *become* part of
the command — dangerous and fragile. **In your code:** you avoid it — every
`subprocess` call uses a **list of arguments**, never `shell=True`, and bulk text
goes through a temp file (bugs #4, #5).

### Single Responsibility Principle (SRP)
"A class should have one reason to change." The cure for a God Object. **In your
project:** the `lyceum/` extractions are SRP in action — each module has one job.

### Soundex / phonetic key
A way to index words by *how they sound* so misspellings still match. **In your
code:** `_phonetic_key` powers the spelling helper.

### Thread / thread confinement
A thread is an independent line of execution. **Confinement** = keeping certain
data on exactly one thread. **In your code:** UI state is confined to the UI
thread; workers do slow work off it and hand results back via `root.after`.

### TOCTOU (Time-Of-Check to Time-Of-Use)
A bug where something is valid when you check it but stale by the time you use it.
**In your code:** the `tk.END` bug is this flavor — the index was correct when
captured, wrong after more text was inserted.

### TTS text normalization
The "text analysis" front-end stage of a text-to-speech pipeline: rewrite `$32`,
`50%`, `Dr.`, `21st` into spoken words *before* the voice engine sees them. **In
your code:** `lyceum/text_norm.py`.

### UTF-8 vs. cp1252 (mojibake)
Two ways to encode text as bytes. Mixing them on Windows turns "café" into
"cafÃ©" (mojibake). **In your code:** you read/write **UTF-8 everywhere**, which
sidesteps the Windows default-`cp1252` trap.

### WIP limit (Kanban)
A cap on how many tasks are "in progress" at once, to force finishing over
starting. **In your process:** the recommended cure for the project's scope-creep
risk — see [SDLC & Process](SDLC-and-Process.md).
