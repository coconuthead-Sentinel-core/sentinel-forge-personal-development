"""Unit tests for pure helpers extracted from BookReader (lyceum.util)."""
import unittest
from datetime import date

from lyceum import util


class ZoneAndFormatTest(unittest.TestCase):
    def test_zone_for_load(self):
        self.assertEqual(util.zone_for_load(9), "GREEN")
        self.assertEqual(util.zone_for_load(7), "GREEN")
        self.assertEqual(util.zone_for_load(5), "YELLOW")
        self.assertEqual(util.zone_for_load(4), "YELLOW")
        self.assertEqual(util.zone_for_load(1), "RED")

    def test_fmt_hm(self):
        self.assertEqual(util.fmt_hm(0), "0m")
        self.assertEqual(util.fmt_hm(45), "45m")
        self.assertEqual(util.fmt_hm(60), "1h 0m")
        self.assertEqual(util.fmt_hm(125), "2h 5m")
        self.assertEqual(util.fmt_hm(-10), "0m")     # clamps

    def test_habit_formula(self):
        self.assertEqual(util.habit_formula("I pour coffee", "read one page"),
                         "After I I pour coffee, I will read one page.")
        self.assertEqual(util.habit_formula("", ""), "")
        self.assertEqual(util.habit_formula("wake up.", "stretch."),
                         "After I wake up, I will stretch.")   # trailing dot stripped


class DateWindowTest(unittest.TestCase):
    def test_period_start(self):
        today = date(2026, 6, 28)
        self.assertEqual(util.period_start("This month", today), date(2026, 6, 1))
        self.assertEqual(util.period_start("This year", today), date(2026, 1, 1))
        self.assertEqual(util.period_start("Last 30 days", today), date(2026, 5, 29))
        self.assertEqual(util.period_start("All time", today), date(1970, 1, 1))


class ParseClockTimeTest(unittest.TestCase):
    def test_various_formats(self):
        self.assertEqual(util.parse_clock_time("14:30"), "14:30")
        self.assertEqual(util.parse_clock_time("2:30 PM"), "14:30")
        self.assertEqual(util.parse_clock_time("2:30pm"), "14:30")
        self.assertEqual(util.parse_clock_time("2 PM"), "14:00")
        self.assertEqual(util.parse_clock_time("2pm"), "14:00")
        self.assertEqual(util.parse_clock_time("14"), "14:00")

    def test_invalid_returns_none(self):
        self.assertIsNone(util.parse_clock_time("not a time"))
        self.assertIsNone(util.parse_clock_time(""))
        self.assertIsNone(util.parse_clock_time(None))


class PertScheduleTest(unittest.TestCase):
    def test_schedules_backward(self):
        target = date(2026, 1, 29)            # 4 weeks out
        steps = [("plan", 1), ("build", 2), ("ship", 1)]   # 4 weeks total
        sched = util.pert_schedule(target, steps)
        self.assertEqual([s["name"] for s in sched], ["plan", "build", "ship"])
        self.assertEqual(sched[0]["start"], date(2026, 1, 1))   # 4 weeks before target
        self.assertEqual(sched[-1]["end"], target)
        # each step's end is the next step's start (contiguous)
        self.assertEqual(sched[0]["end"], sched[1]["start"])

    def test_bad_weeks_default_zero(self):
        sched = util.pert_schedule(date(2026, 1, 1), [("x", "oops")])
        self.assertEqual(sched[0]["weeks"], 0.0)


if __name__ == "__main__":
    unittest.main()
