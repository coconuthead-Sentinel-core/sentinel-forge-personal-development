"""Unit tests for lyceum/srs.py — the FSRS spaced-repetition core
(RELAY-SRS-001 §5). Headless: temp-file SQLite, injected clocks, no GUI.

Run from the repo root:   python -m unittest discover -s tests
"""
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from lyceum import srs
from lyceum.db import study_db

NOW = datetime(2026, 7, 7, 12, 0, 0, tzinfo=timezone.utc)


@unittest.skipIf(not srs.SRS_AVAILABLE, "py-fsrs not installed")
class SRSBase(unittest.TestCase):
    def setUp(self):
        self._orig_db = study_db.STUDY_DB
        fd, self._path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        study_db.STUDY_DB = self._path
        con = study_db.connect()
        con.executescript(study_db.STUDY_SCHEMA)
        con.commit()
        con.close()
        self.svc = srs.SRSService(study_db)

    def tearDown(self):
        study_db.STUDY_DB = self._orig_db
        try:
            os.remove(self._path)
        except OSError:
            pass

    def _deck(self):
        return self.svc.create_deck("Test Deck", now=NOW)


class SchemaTest(SRSBase):
    def test_tables_and_indexes_exist(self):
        names = {r[0] for r in study_db.db_query(
            "SELECT name FROM sqlite_master")}
        for t in ("memory_decks", "memory_cards", "memory_review_log",
                  "idx_memory_cards_due", "idx_memory_cards_source",
                  "idx_review_log_time"):
            self.assertIn(t, names)

    def test_migration_idempotent(self):
        # Re-running the whole schema on a populated DB is a no-op.
        deck = self._deck()
        cid = self.svc.add_card(deck, "front", "back", now=NOW)
        con = study_db.connect()
        con.executescript(study_db.STUDY_SCHEMA)
        con.commit()
        con.close()
        self.assertEqual(self.svc.get_card(cid).front, "front")


class AddCardTest(SRSBase):
    def test_round_trip(self):
        deck = self._deck()
        cid = self.svc.add_card(deck, "What is ACID?", "Atomicity…",
                                zone="YELLOW", cognitive_load=7,
                                tags=["db", "acid"], now=NOW)
        view = self.svc.get_card(cid)
        self.assertEqual(view.front, "What is ACID?")
        self.assertEqual(view.state, "new")
        self.assertEqual(view.tags, ["db", "acid"])
        # fsrs_card_json deserializes to a valid Card whose denormalized
        # copies match.
        raw = study_db.db_query(
            "SELECT fsrs_card_json, due, state FROM memory_cards "
            "WHERE card_id=?", (cid,))[0]
        import fsrs
        card = fsrs.Card.from_dict(json.loads(raw[0]))
        self.assertEqual(card.due.astimezone(timezone.utc).isoformat(),
                         raw[1])
        self.assertEqual(srs._card_state_str(card), raw[2])

    def test_new_card_is_due_immediately(self):
        deck = self._deck()
        self.svc.add_card(deck, "f", "b", now=NOW)
        self.assertEqual(len(self.svc.get_due_cards(now=NOW)), 1)


class ReviewTest(SRSBase):
    def test_happy_path_good(self):
        deck = self._deck()
        cid = self.svc.add_card(deck, "f", "b", now=NOW)
        out = self.svc.review_card(cid, 3, now=NOW)
        self.assertGreater(out.next_due, NOW)
        view = self.svc.get_card(cid)
        self.assertEqual(view.reps, 1)
        self.assertEqual(view.lapses, 0)
        log = study_db.db_query(
            "SELECT state_before, state_after, rating "
            "FROM memory_review_log WHERE card_id=?", (cid,))
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0][0], "new")
        self.assertEqual(log[0][2], 3)
        self.assertIn(log[0][1], ("learning", "review", "relearning"))

    def test_again_counts_a_lapse(self):
        deck = self._deck()
        cid = self.svc.add_card(deck, "f", "b", now=NOW)
        self.svc.review_card(cid, 1, now=NOW)
        self.assertEqual(self.svc.get_card(cid).lapses, 1)

    def test_atomicity_on_log_failure(self):
        """Forced failure between the card UPDATE and the log INSERT must
        roll back BOTH — card unchanged AND no log row."""
        deck = self._deck()
        cid = self.svc.add_card(deck, "f", "b", now=NOW)
        before = study_db.db_query(
            "SELECT fsrs_card_json, due, reps FROM memory_cards "
            "WHERE card_id=?", (cid,))[0]

        def boom(*_a, **_k):
            raise RuntimeError("forced failure after card UPDATE")

        orig = srs.SRSService._insert_review_log
        srs.SRSService._insert_review_log = boom
        try:
            with self.assertRaises(RuntimeError):
                self.svc.review_card(cid, 3, now=NOW)
        finally:
            srs.SRSService._insert_review_log = orig
        after = study_db.db_query(
            "SELECT fsrs_card_json, due, reps FROM memory_cards "
            "WHERE card_id=?", (cid,))[0]
        self.assertEqual(before, after)
        self.assertEqual(study_db.db_query(
            "SELECT COUNT(*) FROM memory_review_log")[0][0], 0)

    def test_rating_validation(self):
        deck = self._deck()
        cid = self.svc.add_card(deck, "f", "b", now=NOW)
        for bad in (0, 5, -1):
            with self.assertRaises(ValueError):
                self.svc.review_card(cid, bad, now=NOW)
        self.svc.review_card(cid, 2, now=NOW)   # 1..4 accepted

    def test_deterministic_scheduling(self):
        """Same card + same rating sequence + same clocks ⇒ identical due
        outputs across two independent runs."""
        def run():
            deck = self.svc.create_deck(
                f"D{study_db.db_query('SELECT COUNT(*) FROM memory_decks')[0][0]}",
                now=NOW)
            cid = self.svc.add_card(deck, "f", "b", now=NOW)
            dues = []
            t = NOW
            for rating in (3, 3, 4, 2):
                out = self.svc.review_card(cid, rating, now=t)
                dues.append(out.next_due.isoformat())
                t = out.next_due
            return dues
        self.assertEqual(run(), run())


class DueCardsTest(SRSBase):
    def test_ordering_and_exclusions(self):
        deck = self._deck()
        c_old = self.svc.add_card(deck, "old", "b", now=NOW - timedelta(days=2))
        c_new = self.svc.add_card(deck, "newer", "b", now=NOW - timedelta(days=1))
        c_future = self.svc.add_card(deck, "future", "b", now=NOW)
        self.svc.review_card(c_future, 4, now=NOW)      # pushes due ahead
        c_susp = self.svc.add_card(deck, "susp", "b", now=NOW - timedelta(days=3))
        self.svc.suspend_card(c_susp)
        due = self.svc.get_due_cards(now=NOW)
        fronts = [c.front for c in due]
        self.assertEqual(fronts, ["old", "newer"])       # oldest-due first
        self.assertNotIn("future", fronts)
        self.assertNotIn("susp", fronts)

    def test_limit_respected(self):
        deck = self._deck()
        for i in range(5):
            self.svc.add_card(deck, f"f{i}", "b",
                              now=NOW - timedelta(hours=i + 1))
        self.assertEqual(len(self.svc.get_due_cards(limit=3, now=NOW)), 3)


class GlossarySyncTest(SRSBase):
    def test_idempotent_import(self):
        rows = [("ACID", "Atomicity, Consistency, Isolation, Durability"),
                ("WAL", "Write-Ahead Logging")]
        r1 = self.svc.sync_from_glossary(rows, now=NOW)
        self.assertEqual((r1["added"], r1["skipped"]), (2, 0))
        r2 = self.svc.sync_from_glossary(rows, now=NOW)
        self.assertEqual((r2["added"], r2["skipped"]), (0, 2))
        self.assertEqual(r1["deck_id"], r2["deck_id"])
        self.assertEqual(study_db.db_query(
            "SELECT COUNT(*) FROM memory_cards")[0][0], 2)


class StatsTest(SRSBase):
    def test_stats_and_reviews_by_day(self):
        deck = self._deck()
        cid = self.svc.add_card(deck, "f", "b", now=NOW)
        self.svc.add_card(deck, "f2", "b2", now=NOW)
        self.svc.review_card(cid, 3, now=NOW)
        s = self.svc.stats(now=NOW)
        self.assertEqual(s.total_cards, 2)
        self.assertEqual(s.reviewed_today, 1)
        self.assertEqual(s.current_streak_days, 1)
        self.assertIsNone(s.retention_estimate)   # < 20 reviews
        by_day = self.svc.reviews_by_day(days=7, now=NOW)
        self.assertEqual(by_day.get(NOW.date().isoformat()), 1)


class ResyncTest(SRSBase):
    def test_repairs_corrupted_columns(self):
        deck = self._deck()
        cid = self.svc.add_card(deck, "f", "b", now=NOW)
        study_db.db_exec(
            "UPDATE memory_cards SET due='1999-01-01T00:00:00+00:00', "
            "state='review' WHERE card_id=?", (cid,))
        self.assertEqual(self.svc.resync(), 1)
        view = self.svc.get_card(cid)
        self.assertEqual(view.state, "new")
        self.assertEqual(view.due, NOW)
        self.assertEqual(self.svc.resync(), 0)   # second pass: nothing to fix


class UnavailableTest(unittest.TestCase):
    def test_construction_raises_cleanly_when_fsrs_missing(self):
        orig = srs.SRS_AVAILABLE
        srs.SRS_AVAILABLE = False
        try:
            with self.assertRaises(srs.SRSUnavailableError):
                srs.SRSService(study_db)
        finally:
            srs.SRS_AVAILABLE = orig


if __name__ == "__main__":
    unittest.main()
