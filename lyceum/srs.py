"""lyceum/srs.py — FSRS-backed spaced-repetition service (functional core).

No Tkinter. No wall-clock reads without an injectable ``now``.
Scheduling delegated to py-fsrs (MIT); storage in study_db SQLite.

Implements RELAY-SRS-001 §4. Design notes:
- ``fsrs_card_json`` is the single source of truth for scheduler state
  (the full py-fsrs ``Card.to_dict()``); ``due``/``state``/``lapses``/
  ``reps`` are denormalized copies maintained here so plain SQL can
  answer "what's due" fast. If they disagree, JSON wins — ``resync()``
  rebuilds the columns.
- py-fsrs has no explicit 'new' state: a card that has never been
  reviewed (``last_review is None``) is stored as ``'new'``; after that
  the py-fsrs State enum name (learning/review/relearning) is stored.
- Every mutating call wraps ALL of its writes in one
  ``study_db.transaction()`` block, so a crash partway leaves nothing
  half-written (the same ACID discipline as the rest of the app).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

try:
    import fsrs  # py-fsrs
    SRS_AVAILABLE = True
except ImportError:
    fsrs = None
    SRS_AVAILABLE = False


class DuplicateCardError(Exception):
    """A card with this (source_kind, source_ref) already exists."""


class SRSUnavailableError(RuntimeError):
    """py-fsrs is not installed — the SRS feature is disabled."""


# ── Value objects (plain dataclasses; UI-agnostic) ──────────────────


@dataclass(frozen=True)
class CardView:
    """Read-only snapshot handed to callers (UI shell, tests)."""
    card_id: int
    deck_id: int
    deck_name: str
    front: str
    back: str
    media_path: str | None
    due: datetime            # UTC
    state: str               # 'new' | 'learning' | 'review' | 'relearning'
    zone: str
    cognitive_load: int | None
    tags: list[str]
    reps: int
    lapses: int


@dataclass(frozen=True)
class ReviewOutcome:
    card_id: int
    rating: int              # 1..4
    next_due: datetime       # UTC
    new_state: str
    interval_days: float


@dataclass(frozen=True)
class SRSStats:
    """Feed for the 🏆 Scoreboard / Never-Miss-Twice calendar."""
    due_now: int
    due_today: int
    reviewed_today: int
    total_cards: int
    current_streak_days: int
    retention_estimate: float | None   # None until enough history


# ── Internal helpers (pure) ─────────────────────────────────────────

_VALID_ZONES = ("GREEN", "YELLOW", "RED")
_MIN_HISTORY_FOR_RETENTION = 20


def _utc_now(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("`now` must be timezone-aware (UTC)")
    return now.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def _parse_iso(s: str) -> datetime:
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _card_state_str(card) -> str:
    """py-fsrs Card → our four-state string ('new' when never reviewed)."""
    if getattr(card, "last_review", None) is None:
        return "new"
    return fsrs.State(card.state).name.lower()


# ── Service ─────────────────────────────────────────────────────────


class SRSService:
    """All entry points are safe to call headless. Every mutating call
    wraps its writes in study_db.transaction().

    ``db`` is the lyceum.db.study_db module (or a compatible object
    exposing ``db_query`` and ``transaction``) — the same handle style
    every other study_db consumer uses.
    """

    def __init__(self, db):
        if not SRS_AVAILABLE:
            raise SRSUnavailableError(
                "py-fsrs is not installed — run: pip install fsrs")
        self._db = db
        # enable_fuzzing=False: py-fsrs randomizes intervals slightly by
        # default (an anti-clumping trick for big shared decks). This
        # module promises DETERMINISTIC scheduling (RELAY-SRS-001 §1.5 /
        # test §5.8) — same card, same ratings, same clock, same due.
        self._scheduler = fsrs.Scheduler(enable_fuzzing=False)

    # -- deck management ------------------------------------------------
    def create_deck(self, name: str, deck_type: str = "basic",
                    *, now: datetime | None = None) -> int:
        name = (name or "").strip()
        if not name:
            raise ValueError("deck name must not be empty")
        now_dt = _utc_now(now)
        with self._db.transaction() as con:
            existing = con.execute(
                "SELECT deck_id FROM memory_decks WHERE name=?",
                (name,)).fetchone()
            if existing:
                raise ValueError(f"deck '{name}' already exists")
            cur = con.execute(
                "INSERT INTO memory_decks (name, deck_type, created_at) "
                "VALUES (?,?,?)", (name, deck_type, _iso(now_dt)))
            return cur.lastrowid

    def list_decks(self, include_archived: bool = False) -> list[dict]:
        sql = ("SELECT deck_id, name, deck_type, created_at, archived "
               "FROM memory_decks")
        if not include_archived:
            sql += " WHERE archived=0"
        sql += " ORDER BY name"
        return [
            {"deck_id": r[0], "name": r[1], "deck_type": r[2],
             "created_at": r[3], "archived": bool(r[4])}
            for r in self._db.db_query(sql)
        ]

    # -- card lifecycle --------------------------------------------------
    def add_card(self, deck_id: int, front: str, back: str, *,
                 media_path: str | None = None,
                 source_kind: str = "manual", source_ref: str | None = None,
                 zone: str = "GREEN", cognitive_load: int | None = None,
                 tags: list[str] | None = None,
                 now: datetime | None = None) -> int:
        """Creates a new py-fsrs Card, serializes to fsrs_card_json,
        denormalizes due/state. Raises DuplicateCardError if
        (source_kind, source_ref) already exists."""
        if zone not in _VALID_ZONES:
            raise ValueError(f"zone must be one of {_VALID_ZONES}")
        now_dt = _utc_now(now)
        card = fsrs.Card()
        # A fresh card is due immediately — pin its due to the injected
        # clock so scheduling is deterministic under test.
        card.due = now_dt
        payload = json.dumps(card.to_dict())
        with self._db.transaction() as con:
            if source_ref is not None:
                dup = con.execute(
                    "SELECT card_id FROM memory_cards "
                    "WHERE source_kind=? AND source_ref=?",
                    (source_kind, source_ref)).fetchone()
                if dup:
                    raise DuplicateCardError(
                        f"card for ({source_kind}, {source_ref}) already "
                        f"exists (card_id={dup[0]})")
            cur = con.execute(
                "INSERT INTO memory_cards "
                "(deck_id, front, back, media_path, source_kind, source_ref,"
                " zone, cognitive_load, tags, fsrs_card_json, due, state,"
                " created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (deck_id, front, back, media_path, source_kind, source_ref,
                 zone, cognitive_load, json.dumps(list(tags or [])),
                 payload, _iso(now_dt), _card_state_str(card),
                 _iso(now_dt)))
            return cur.lastrowid

    def suspend_card(self, card_id: int, suspended: bool = True) -> None:
        with self._db.transaction() as con:
            con.execute("UPDATE memory_cards SET suspended=? WHERE card_id=?",
                        (1 if suspended else 0, card_id))

    def get_card(self, card_id: int) -> CardView:
        rows = self._db.db_query(
            "SELECT c.card_id, c.deck_id, d.name, c.front, c.back,"
            "       c.media_path, c.due, c.state, c.zone, c.cognitive_load,"
            "       c.tags, c.reps, c.lapses "
            "FROM memory_cards c JOIN memory_decks d USING (deck_id) "
            "WHERE c.card_id=?", (card_id,))
        if not rows:
            raise ValueError(f"no card with card_id={card_id}")
        return self._row_to_view(rows[0])

    @staticmethod
    def _row_to_view(r) -> CardView:
        return CardView(
            card_id=r[0], deck_id=r[1], deck_name=r[2], front=r[3],
            back=r[4], media_path=r[5], due=_parse_iso(r[6]), state=r[7],
            zone=r[8], cognitive_load=r[9],
            tags=list(json.loads(r[10] or "[]")), reps=r[11], lapses=r[12])

    # -- the core loop -----------------------------------------------------
    def get_due_cards(self, *, deck_id: int | None = None, limit: int = 20,
                      now: datetime | None = None) -> list[CardView]:
        """Cards with due <= now, unsuspended, oldest-due first.
        `limit` defaults low on purpose — two-minute-rule friendly."""
        now_dt = _utc_now(now)
        sql = ("SELECT c.card_id, c.deck_id, d.name, c.front, c.back,"
               "       c.media_path, c.due, c.state, c.zone,"
               "       c.cognitive_load, c.tags, c.reps, c.lapses "
               "FROM memory_cards c JOIN memory_decks d USING (deck_id) "
               "WHERE c.suspended=0 AND c.due <= ?")
        params: list = [_iso(now_dt)]
        if deck_id is not None:
            sql += " AND c.deck_id=?"
            params.append(deck_id)
        sql += " ORDER BY c.due ASC LIMIT ?"
        params.append(int(limit))
        return [self._row_to_view(r)
                for r in self._db.db_query(sql, tuple(params))]

    def review_card(self, card_id: int, rating: int, *,
                    review_duration_ms: int | None = None,
                    session_load: int | None = None,
                    now: datetime | None = None) -> ReviewOutcome:
        """The atomic heart of the module. In ONE transaction:
        1. Load + deserialize fsrs_card_json.
        2. scheduler.review_card(card, Rating(rating), now).
        3. Persist updated JSON + denormalized columns.
        4. INSERT append-only memory_review_log row.
        Raises ValueError on rating outside 1..4."""
        if not isinstance(rating, int) or not 1 <= rating <= 4:
            raise ValueError("rating must be an integer 1..4 "
                             "(1=Again 2=Hard 3=Good 4=Easy)")
        now_dt = _utc_now(now)
        with self._db.transaction() as con:
            row = con.execute(
                "SELECT fsrs_card_json, reps, lapses FROM memory_cards "
                "WHERE card_id=?", (card_id,)).fetchone()
            if row is None:
                raise ValueError(f"no card with card_id={card_id}")
            card = fsrs.Card.from_dict(json.loads(row[0]))
            state_before = _card_state_str(card)
            card, _log = self._scheduler.review_card(
                card, fsrs.Rating(rating), now_dt)
            state_after = _card_state_str(card)
            next_due = card.due.astimezone(timezone.utc)
            interval_days = (next_due - now_dt).total_seconds() / 86400.0
            reps = row[1] + 1
            lapses = row[2] + (1 if rating == 1 else 0)
            con.execute(
                "UPDATE memory_cards SET fsrs_card_json=?, due=?, state=?,"
                " reps=?, lapses=? WHERE card_id=?",
                (json.dumps(card.to_dict()), _iso(next_due), state_after,
                 reps, lapses, card_id))
            self._insert_review_log(
                con, card_id, rating, now_dt, review_duration_ms,
                interval_days, state_before, state_after, session_load)
        return ReviewOutcome(card_id=card_id, rating=rating,
                             next_due=next_due, new_state=state_after,
                             interval_days=interval_days)

    def _insert_review_log(self, con, card_id, rating, now_dt, duration_ms,
                           scheduled_days, state_before, state_after,
                           session_load) -> None:
        """Separated so tests can prove review_card's atomicity by
        forcing a failure between the card UPDATE and this INSERT."""
        con.execute(
            "INSERT INTO memory_review_log "
            "(card_id, rating, reviewed_at, review_duration_ms,"
            " scheduled_days, state_before, state_after, session_load) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (card_id, rating, _iso(now_dt), duration_ms, scheduled_days,
             state_before, state_after, session_load))

    # -- card sources ------------------------------------------------------
    def sync_from_glossary(self, glossary_rows: list[tuple[str, str]], *,
                           deck_name: str = "Glossary",
                           now: datetime | None = None) -> dict:
        """Idempotent import: (term, definition) pairs → cards with
        source_kind='glossary', source_ref=term. Existing terms are
        skipped (unique index enforces). Returns
        {'added': int, 'skipped': int, 'deck_id': int}.
        Takes plain rows, not a Glossary object — the caller (shell)
        does the query; keeps srs.py decoupled from the glossary table."""
        now_dt = _utc_now(now)
        deck_id = None
        for d in self.list_decks(include_archived=True):
            if d["name"] == deck_name:
                deck_id = d["deck_id"]
                break
        if deck_id is None:
            deck_id = self.create_deck(deck_name, "glossary", now=now_dt)
        added = skipped = 0
        for term, definition in glossary_rows:
            term = (term or "").strip()
            definition = (definition or "").strip()
            if not term or not definition:
                skipped += 1
                continue
            try:
                self.add_card(deck_id, term, definition,
                              source_kind="glossary", source_ref=term,
                              tags=["glossary"], now=now_dt)
                added += 1
            except DuplicateCardError:
                skipped += 1
        return {"added": added, "skipped": skipped, "deck_id": deck_id}

    # -- dashboard feed ------------------------------------------------------
    def stats(self, *, now: datetime | None = None) -> SRSStats:
        now_dt = _utc_now(now)
        today = now_dt.date().isoformat()
        end_of_today = _iso(datetime.combine(
            now_dt.date(), datetime.max.time(), tzinfo=timezone.utc))
        q = self._db.db_query
        due_now = q("SELECT COUNT(*) FROM memory_cards "
                    "WHERE suspended=0 AND due <= ?",
                    (_iso(now_dt),))[0][0]
        due_today = q("SELECT COUNT(*) FROM memory_cards "
                      "WHERE suspended=0 AND due <= ?",
                      (end_of_today,))[0][0]
        reviewed_today = q(
            "SELECT COUNT(*) FROM memory_review_log "
            "WHERE substr(reviewed_at, 1, 10) = ?", (today,))[0][0]
        total_cards = q("SELECT COUNT(*) FROM memory_cards")[0][0]
        # Streak: consecutive days with >= 1 review, ending today (or
        # yesterday, so an unfinished today doesn't zero the streak).
        days_with = {r[0] for r in q(
            "SELECT DISTINCT substr(reviewed_at, 1, 10) "
            "FROM memory_review_log")}
        d = now_dt.date()
        if d.isoformat() not in days_with:
            d = d - timedelta(days=1)
        streak = 0
        while d.isoformat() in days_with:
            streak += 1
            d -= timedelta(days=1)
        # Retention estimate: share of reviews NOT rated Again, once
        # there is enough history to mean anything.
        hist = q("SELECT COUNT(*), SUM(CASE WHEN rating > 1 THEN 1 ELSE 0 "
                 "END) FROM memory_review_log")[0]
        retention = (hist[1] / hist[0]
                     if hist[0] and hist[0] >= _MIN_HISTORY_FOR_RETENTION
                     else None)
        return SRSStats(due_now=due_now, due_today=due_today,
                        reviewed_today=reviewed_today,
                        total_cards=total_cards,
                        current_streak_days=streak,
                        retention_estimate=retention)

    def reviews_by_day(self, days: int = 30, *,
                       now: datetime | None = None) -> dict[str, int]:
        """ISO date → review count for the trailing window. Feeds the
        Never-Miss-Twice green/red dots and the Scoreboard lead measure.
        Days with zero reviews are simply absent."""
        now_dt = _utc_now(now)
        since = (now_dt.date() - timedelta(days=max(0, days - 1))).isoformat()
        rows = self._db.db_query(
            "SELECT substr(reviewed_at, 1, 10) AS day, COUNT(*) "
            "FROM memory_review_log WHERE substr(reviewed_at, 1, 10) >= ? "
            "GROUP BY day ORDER BY day", (since,))
        return {r[0]: r[1] for r in rows}

    # -- maintenance ----------------------------------------------------------
    def resync(self) -> int:
        """Rebuild denormalized due/state from fsrs_card_json for every
        card. Returns the number of rows corrected. (Disaster-recovery /
        post-FSRS-upgrade tool. reps/lapses are OUR counters — they live
        only in the columns and are not part of the py-fsrs Card, so
        they are left untouched.)"""
        corrected = 0
        with self._db.transaction() as con:
            rows = con.execute(
                "SELECT card_id, fsrs_card_json, due, state "
                "FROM memory_cards").fetchall()
            for card_id, payload, due_col, state_col in rows:
                card = fsrs.Card.from_dict(json.loads(payload))
                true_due = _iso(card.due.astimezone(timezone.utc))
                true_state = _card_state_str(card)
                if due_col != true_due or state_col != true_state:
                    con.execute(
                        "UPDATE memory_cards SET due=?, state=? "
                        "WHERE card_id=?", (true_due, true_state, card_id))
                    corrected += 1
        return corrected
