# SRS Module — spaced-repetition core (`lyceum/srs.py`)

**What it is.** The Sprint 1 foundation from RELAY-SRS-001: an FSRS-backed
spaced-repetition service as a pure-logic module. Scheduling is delegated to
**py-fsrs** (MIT, from PyPI — the only new dependency); storage lives in three
additive SQLite tables (`memory_decks`, `memory_cards`, `memory_review_log`)
created idempotently by `lyceum/db/study_db.py`. No UI in this sprint; the
module is fully unit-testable headless (15 tests in `tests/test_srs.py`).

**How the shell will call it (Sprint 2).**

```python
from lyceum import srs
from lyceum.db import study_db

svc = srs.SRSService(study_db)          # raises SRSUnavailableError if
                                        # py-fsrs isn't installed
svc.sync_from_glossary(rows)            # rows = [(term, definition), ...]
for card in svc.get_due_cards(limit=20):
    ...show card.front, reveal card.back...
    svc.review_card(card.card_id, rating)   # 1=Again 2=Hard 3=Good 4=Easy
svc.stats()            # feeds the 🏆 Scoreboard / Never-Miss-Twice calendar
svc.reviews_by_day(30) # green/red dots
```

**Design notes.**
- `fsrs_card_json` is the single source of truth; `due`/`state`/`reps`/
  `lapses` are denormalized copies for fast SQL. `resync()` repairs the
  columns from JSON if they ever disagree.
- Every mutating call runs inside `study_db.transaction()`; `review_card`
  is proven atomic by test (card update + log insert land together or not
  at all). `memory_review_log` is append-only — it is the future FSRS
  parameter-optimizer's training data.
- Deterministic time: every "now"-touching function accepts an injectable
  UTC `now`; the scheduler is constructed with `enable_fuzzing=False` so
  identical inputs always produce identical due dates.
- Graceful degradation: `SRS_AVAILABLE = False` when py-fsrs is missing;
  the module still imports and the rest of the app is unaffected.

**License note.** py-fsrs is MIT — compatible with this repo's MIT license.
No source code from Anki, Mnemosyne (AGPL-3.0), or Brain Workshop (GPL-2.0)
is present or was consulted.

**Handoff (RELAY-SRS-001 §6).** SRS core complete, awaiting Shannon review —
Sprint 2 = Glossary review window (Tk) + Scoreboard lead-measure wiring.
