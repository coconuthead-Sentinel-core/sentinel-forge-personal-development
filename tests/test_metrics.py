"""Unit tests for the pure metrics core (lyceum.metrics).

Run from the repo root:   python -m unittest discover -s tests
These import NO Tkinter and touch NO database — they exercise the logic in
isolation, which is the whole point of separating the functional core from the
GUI shell.
"""
import unittest

from lyceum.metrics import wheel_progress, progress_pct, goal_progress


class WheelProgressTest(unittest.TestCase):
    def test_no_snapshots(self):
        p = wheel_progress([], 8)
        self.assertEqual(p["n"], 0)
        self.assertEqual(p["pct"], 0)
        self.assertIsNone(p["baseline"])

    def test_real_data_backslide(self):
        # The user's 4 real snapshots: spoke-averages 4.71, 2.86, 3.00, 2.14.
        p = wheel_progress([4.714, 2.857, 3.0, 2.143], 8)
        self.assertEqual(p["arrow"], "▼")   # down vs baseline
        self.assertEqual(p["pct"], 0)            # no progress toward target
        self.assertEqual(p["n"], 4)

    def test_improvement_is_proportional(self):
        # 3 -> 6 toward target 8 == (6-3)/(8-3) == 60%.
        p = wheel_progress([3.0, 6.0], 8)
        self.assertEqual(p["arrow"], "▲")
        self.assertEqual(p["pct"], 60)

    def test_single_snapshot_is_flat(self):
        p = wheel_progress([5.0], 8)
        self.assertEqual(p["n"], 1)
        self.assertEqual(p["arrow"], "■")   # baseline == now
        self.assertEqual(p["pct"], 0)

    def test_reaching_target_is_100(self):
        p = wheel_progress([4.0, 8.0], 8)
        self.assertEqual(p["pct"], 100)

    def test_target_is_clamped(self):
        p = wheel_progress([5.0, 7.0], 99)       # out-of-range target
        self.assertEqual(p["target"], 10)


class ProgressPctTest(unittest.TestCase):
    def test_proportional(self):
        self.assertEqual(progress_pct(6, 3, 8), 60)   # (6-3)/(8-3)

    def test_backslide_is_zero(self):
        self.assertEqual(progress_pct(2, 5, 8), 0)

    def test_reaching_target_is_100(self):
        self.assertEqual(progress_pct(8, 4, 8), 100)

    def test_target_not_above_baseline(self):
        self.assertEqual(progress_pct(5, 5, 5), 100)  # already at/above target
        self.assertEqual(progress_pct(4, 5, 5), 0)


class GoalProgressTest(unittest.TestCase):
    def test_matches_wheel_formula(self):
        g = goal_progress(6, 3, 8)
        self.assertEqual(g["pct"], 60)
        self.assertEqual(g["arrow"], "▲")

    def test_backslide(self):
        g = goal_progress(2, 5, 8)
        self.assertEqual(g["pct"], 0)
        self.assertEqual(g["arrow"], "▼")

    def test_clamps_baseline_target(self):
        g = goal_progress(7, 0, 99)
        self.assertEqual(g["baseline"], 1)
        self.assertEqual(g["target"], 10)


if __name__ == "__main__":
    unittest.main()
