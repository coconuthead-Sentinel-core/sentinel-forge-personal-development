"""Unit tests for the two-lapse streak protocol (lyceum.streaks).

Pure logic — no GUI. Verifies all four states, the precedence order, and
that a single lapse is AMBER and shame-free (the point of the protocol).

Run from the repo root:   python -m unittest discover -s tests
"""
import unittest

from lyceum import streaks


class ClassifyTest(unittest.TestCase):
    def test_done_today_wins_over_everything(self):
        self.assertEqual(streaks.classify_lapse(True, True, True), "done_today")

    def test_active_when_yesterday_done(self):
        self.assertEqual(streaks.classify_lapse(False, False, False), "active")

    def test_active_even_if_older_miss(self):
        # A miss two days ago with yesterday DONE is a recovered chain.
        self.assertEqual(streaks.classify_lapse(False, False, True), "active")

    def test_first_miss(self):
        self.assertEqual(streaks.classify_lapse(False, True, False), "first_miss")

    def test_recovery_after_two_misses(self):
        self.assertEqual(streaks.classify_lapse(False, True, True), "recovery")


class MessageTest(unittest.TestCase):
    def test_done_today_green(self):
        _, level = streaks.lapse_message("done_today", 5, 9)
        self.assertEqual(level, streaks.GREEN)

    def test_active_ok(self):
        _, level = streaks.lapse_message("active", 5, 9)
        self.assertEqual(level, streaks.OK)

    def test_first_miss_is_amber_and_shame_free(self):
        text, level = streaks.lapse_message("first_miss", 5, 9)
        self.assertEqual(level, streaks.AMBER)
        low = text.lower()
        self.assertIn("rest day", low)            # compassionate framing
        self.assertIn("not a broken chain", low)  # negation present, not blame
        for shame in ("fail", "never miss twice", "shame", "lost", "ruined"):
            self.assertNotIn(shame, low)

    def test_recovery_is_red_and_asks_exact_time(self):
        text, level = streaks.lapse_message("recovery", 0, 9)
        self.assertEqual(level, streaks.RED)
        self.assertIn("at ___", text.lower())     # implementation-intention form
        self.assertIn("fresh start", text.lower())


if __name__ == "__main__":
    unittest.main()
