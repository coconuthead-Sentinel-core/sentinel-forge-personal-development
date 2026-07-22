"""Tests for lyceum/pomo_clock.py — deadline-based Pomodoro truth.

Owner QA find (2026-07-22, from the pomo breadcrumb log): tick-counted
countdown stretched a 20-minute block to 61 wall-clock minutes across
a laptop sleep. These tests pin the deadline contract: remaining time
comes from the clock, and NO pattern of late, missing, or extra ticks
can change it.
"""
import unittest

from lyceum.pomo_clock import deadline_for, remaining_seconds


class DeadlineTest(unittest.TestCase):
    def test_deadline_is_start_plus_duration(self):
        self.assertEqual(deadline_for(20, 1000.0), 1000.0 + 1200)

    def test_zero_minutes_is_immediate(self):
        self.assertEqual(remaining_seconds(deadline_for(0, 50.0), 50.0), 0)


class RemainingTest(unittest.TestCase):
    def test_counts_down_with_the_clock(self):
        d = deadline_for(1, 0.0)              # 60s block
        self.assertEqual(remaining_seconds(d, 0.0), 60)
        self.assertEqual(remaining_seconds(d, 30.0), 30)
        self.assertEqual(remaining_seconds(d, 60.0), 0)

    def test_clamps_at_zero_after_deadline(self):
        d = deadline_for(1, 0.0)
        self.assertEqual(remaining_seconds(d, 3600.0), 0)

    def test_immune_to_tick_drift(self):
        # The 61-minute bug: however LATE the ticks arrive, the answer
        # tracks the wall clock. Simulate ticks at sloppy intervals.
        d = deadline_for(20, 0.0)             # 1200s block
        for now, want in [(0.0, 1200), (1.7, 1198), (300.0, 900),
                          (1199.4, 1), (1200.0, 0)]:
            self.assertEqual(remaining_seconds(d, now), want)

    def test_sleep_jump_lands_on_zero_not_negative(self):
        # Laptop sleeps mid-block; on wake the block is simply over.
        d = deadline_for(20, 0.0)
        self.assertEqual(remaining_seconds(d, 5000.0), 0)

    def test_extra_calls_change_nothing(self):
        # Calling many times at the same instant must not "count down".
        d = deadline_for(5, 100.0)
        for _ in range(50):
            self.assertEqual(remaining_seconds(d, 130.0), 270)


if __name__ == "__main__":
    unittest.main()
