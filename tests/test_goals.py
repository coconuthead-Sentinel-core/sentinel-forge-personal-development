"""Unit tests for pure goal-accountability logic (lyceum.goals), extracted from
the CC-66 _build_goals_panel builder. Every branch is covered; `today` is
injected so the date math is deterministic."""
import unittest
from datetime import date

from lyceum import goals


T = date(2026, 6, 28)        # fixed "today" for all tests


class AccountabilityTest(unittest.TestCase):
    def test_done_by_status_or_progress(self):
        self.assertEqual(goals.accountability("", "", 0, "done", T)[:2], ("✅ DONE", "done"))
        self.assertEqual(goals.accountability("", "", 100, "active", T)[1], "done")

    def test_parked(self):
        b, lvl, behind = goals.accountability("", "2026-12-01", 10, "parked", T)
        self.assertEqual(lvl, "parked")
        self.assertFalse(behind)

    def test_no_target_date(self):
        self.assertEqual(goals.accountability("2026-01-01", "", 20, "active", T)[1], "no_date")

    def test_overdue(self):
        b, lvl, behind = goals.accountability("2026-01-01", "2026-06-01", 50, "active", T)
        self.assertEqual(lvl, "overdue")
        self.assertTrue(behind)
        self.assertIn("OVERDUE", b)

    def test_behind_pace(self):
        # started 2026-01-01, target 2026-12-31; ~half the year gone, expected ~49%,
        # progress 5 -> far behind.
        b, lvl, behind = goals.accountability("2026-01-01", "2026-12-31", 5, "active", T)
        self.assertEqual(lvl, "behind")
        self.assertTrue(behind)

    def test_on_track(self):
        b, lvl, behind = goals.accountability("2026-06-01", "2026-12-31", 90, "active", T)
        self.assertEqual(lvl, "on_track")
        self.assertFalse(behind)


class SummarizeTest(unittest.TestCase):
    def test_counts_match_classification(self):
        rows = [
            ("", "", 100, "active"),                       # done
            ("2026-01-01", "2026-06-01", 10, "active"),    # overdue -> behind count
            ("2026-06-01", "2026-12-31", 90, "active"),    # on track
            ("2026-01-01", "", 10, "active"),              # no_date -> ok
        ]
        per, (n_bad, n_ok, n_done) = goals.summarize(rows, today=T)
        self.assertEqual(len(per), 4)
        self.assertEqual((n_bad, n_ok, n_done), (1, 2, 1))


if __name__ == "__main__":
    unittest.main()
