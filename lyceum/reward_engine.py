"""lyceum/reward_engine.py — variable-ratio reward engine (functional core).

No Tkinter. No wall-clock reads without an injectable ``now``; no
randomness without an injectable ``rng`` (tests stay deterministic).
Storage in study_db SQLite; lyceum/reward_engine.py is the sole writer
of reward_pool / reward_log.

Implements the Reward-Draw board (session 2026-07-16). Design notes:
- Variable-ratio schedule: tier weights default 70 / 25 / 5 for
  STANDARD / UNCOMMON / RARE. Variable-ratio reinforcement producing
  high, steady response rates is the classic operant-conditioning
  result (Ferster & Skinner, 1957, *Schedules of Reinforcement*) —
  labeled honestly: the mechanism is anticipation of an unpredictable
  reward, nothing more mysterious than that.
- Pity guarantee: once ``pity_limit - 1`` consecutive non-RARE draws
  have accumulated since the last RARE, the next draw is forced RARE,
  so a drought can never exceed ``pity_limit`` draws. Pure slot-machine
  math allows cruel droughts; this engine does not.
- Honesty gate: every pool payload carries a named source (a book from
  the owner's library, or the app itself for plain flourishes). Blank
  sources are refused at write time — no fabricated quotes, ever.
- reward_log is append-only: it is the pity counter's memory across
  sessions and the audit trail. Never UPDATE or DELETE.
- No reward without work: ``draw()`` refuses a blank event.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone

TIERS = ("STANDARD", "UNCOMMON", "RARE")
DEFAULT_WEIGHTS = {"STANDARD": 70, "UNCOMMON": 25, "RARE": 5}
PITY_LIMIT = 12


class EmptyPoolError(RuntimeError):
    """A tier's reward pool has no active entries — seed the pool first."""


@dataclass(frozen=True)
class Reward:
    """Read-only draw result handed to callers (UI shell, tests)."""
    tier: str
    payload: str
    source: str


# ── Pure kernel ──────────────────────────────────────────────────────


def choose_tier(drought: int, rng: random.Random,
                weights: dict | None = None,
                pity_limit: int = PITY_LIMIT) -> str:
    """Pick a tier on the weighted schedule, honoring the pity guarantee.

    ``drought`` is the count of consecutive non-RARE draws since the
    last RARE. When it reaches ``pity_limit - 1`` the next draw is RARE
    by fiat — the guarantee that makes the schedule kind.
    """
    if drought >= pity_limit - 1:
        return "RARE"
    w = weights or DEFAULT_WEIGHTS
    return rng.choices(TIERS, weights=[w[t] for t in TIERS])[0]


def _utc_now(now: datetime | None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("`now` must be timezone-aware (UTC)")
    return now.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


# ── Default pool (seeded once, only into an empty pool) ─────────────
# Every quote below is either a book title / signature phrase of an
# author on the owner's library shelf or a common proverb — nothing
# invented, every entry names where it lives. The owner curates from
# here: add_pool_entry() to grow it, retire_pool_entry() to shelve.

_DEFAULT_POOL = (
    ("STANDARD", "Green dot — block banked.", "Sentinel Forge (app)"),
    ("STANDARD", "Logged. One block closer.", "Sentinel Forge (app)"),
    ("STANDARD", "Done is done. Next.", "Sentinel Forge (app)"),
    ("UNCOMMON", "Discipline equals freedom.",
     "Jocko Willink — Discipline Equals Freedom (library)"),
    ("UNCOMMON", "Fall seven times, rise eight.",
     "Japanese proverb — Bushido shelf (library)"),
    ("UNCOMMON", "Eat that frog!",
     "Brian Tracy — Eat That Frog! (library)"),
    ("RARE", "Do it now! Do it now! Do it now!",
     "Brian Tracy — Eat That Frog! (library)"),
    ("RARE", "What stands in the way becomes the way.",
     "Marcus Aurelius — Meditations, bk. 5 (library)"),
)


# ── Service ─────────────────────────────────────────────────────────


class RewardService:
    """All entry points are safe to call headless. Every mutating call
    wraps its writes in study_db.transaction().

    ``db`` is the lyceum.db.study_db module (or a compatible object
    exposing ``db_query`` and ``transaction``) — the same handle style
    every other study_db consumer uses.
    """

    def __init__(self, db, *, rng: random.Random | None = None,
                 weights: dict | None = None,
                 pity_limit: int = PITY_LIMIT):
        self._db = db
        self._rng = rng or random.Random()
        self._weights = dict(weights or DEFAULT_WEIGHTS)
        self._pity_limit = pity_limit

    # -- pool curation ---------------------------------------------------
    def add_pool_entry(self, tier: str, payload: str, source: str, *,
                       now: datetime | None = None) -> int:
        if tier not in TIERS:
            raise ValueError(f"tier must be one of {TIERS}")
        payload = (payload or "").strip()
        source = (source or "").strip()
        if not payload:
            raise ValueError("payload must not be empty")
        if not source:
            raise ValueError(
                "payload without a named source refused (honesty gate)")
        with self._db.transaction() as con:
            cur = con.execute(
                "INSERT INTO reward_pool (tier, payload, source, created_at)"
                " VALUES (?,?,?,?)",
                (tier, payload, source, _iso(_utc_now(now))))
            return cur.lastrowid

    def retire_pool_entry(self, pool_id: int) -> None:
        """Soft-retire — entries are shelved, never deleted."""
        with self._db.transaction() as con:
            con.execute("UPDATE reward_pool SET retired=1 WHERE pool_id=?",
                        (pool_id,))

    def seed_default_pool(self, *, now: datetime | None = None) -> int:
        """Insert the starter pool, but only into a completely empty
        pool — never duplicates, never overwrites the owner's curation.
        Returns the number of rows inserted (0 if already seeded)."""
        existing = self._db.db_query("SELECT COUNT(*) FROM reward_pool")
        if existing and existing[0][0]:
            return 0
        stamp = _iso(_utc_now(now))
        with self._db.transaction() as con:
            con.executemany(
                "INSERT INTO reward_pool (tier, payload, source, created_at)"
                " VALUES (?,?,?,?)",
                [(t, p, s, stamp) for t, p, s in _DEFAULT_POOL])
        return len(_DEFAULT_POOL)

    def pool(self, tier: str | None = None,
             include_retired: bool = False) -> list[dict]:
        sql = ("SELECT pool_id, tier, payload, source, retired "
               "FROM reward_pool")
        clauses, params = [], []
        if not include_retired:
            clauses.append("retired=0")
        if tier is not None:
            clauses.append("tier=?")
            params.append(tier)
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY pool_id"
        return [
            {"pool_id": r[0], "tier": r[1], "payload": r[2],
             "source": r[3], "retired": bool(r[4])}
            for r in self._db.db_query(sql, tuple(params))
        ]

    # -- the draw ----------------------------------------------------------
    def drought(self) -> int:
        """Consecutive non-RARE draws since the last RARE — read from
        the append-only log, so the pity counter survives restarts."""
        rows = self._db.db_query(
            "SELECT COUNT(*) FROM reward_log WHERE reward_id > "
            "COALESCE((SELECT MAX(reward_id) FROM reward_log "
            "          WHERE tier='RARE'), 0)")
        return rows[0][0] if rows else 0

    def draw(self, event: str, *, now: datetime | None = None) -> Reward:
        """Draw a reward for a real completion. Raises ValueError on a
        blank event (no reward without work) and EmptyPoolError when the
        chosen tier has no active payloads."""
        event = (event or "").strip()
        if not event:
            raise ValueError("no reward without a completed event")
        tier = choose_tier(self.drought(), self._rng,
                           self._weights, self._pity_limit)
        candidates = self._db.db_query(
            "SELECT payload, source FROM reward_pool "
            "WHERE tier=? AND retired=0", (tier,))
        if not candidates:
            raise EmptyPoolError(
                f"reward pool for tier {tier} is empty — "
                f"seed_default_pool() first")
        payload, source = self._rng.choice(candidates)
        reward = Reward(tier, payload, source)
        with self._db.transaction() as con:
            con.execute(
                "INSERT INTO reward_log (event, tier, payload, source,"
                " created_at) VALUES (?,?,?,?,?)",
                (event, tier, payload, source, _iso(_utc_now(now))))
        return reward

    # -- history (read-only) ----------------------------------------------
    def history(self, limit: int = 50) -> list[dict]:
        return [
            {"reward_id": r[0], "event": r[1], "tier": r[2],
             "payload": r[3], "source": r[4], "created_at": r[5]}
            for r in self._db.db_query(
                "SELECT reward_id, event, tier, payload, source, created_at"
                " FROM reward_log ORDER BY reward_id DESC LIMIT ?",
                (int(limit),))
        ]
