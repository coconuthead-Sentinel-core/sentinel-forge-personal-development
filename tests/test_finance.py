"""Unit tests for the finance kernel (lyceum.finance) — pure math extracted
from the BookReader God Object (Q3). No GUI, no DB."""
import unittest

from lyceum import finance as f


class FinanceKernelTest(unittest.TestCase):
    def test_run_rate_months(self):
        self.assertEqual(f.run_rate_months(3000, 1000), 3.0)
        self.assertIsNone(f.run_rate_months(3000, 0))
        self.assertIsNone(f.run_rate_months(3000, None))

    def test_time_cost_hours(self):
        self.assertEqual(f.time_cost_hours(100, 20, 0), 5.0)
        self.assertIsNone(f.time_cost_hours(100, 0, 0))   # no usable wage

    def test_wedge_split(self):
        r = f.wedge_split(20, 22, 40, 50)
        self.assertAlmostEqual(r["inc_hr"], 2.0)
        self.assertAlmostEqual(r["save_annual"], 2 * 40 * 52 * 0.5)   # 2080
        self.assertAlmostEqual(r["life_annual"], 2 * 40 * 52 * 0.5)

    def test_compound_series(self):
        self.assertEqual(f.compound_series(0, 0, 3, start=100),
                         [100.0, 100.0, 100.0, 100.0])
        self.assertAlmostEqual(f.compound_series(0, 10, 1, start=100)[1], 110.0)
        self.assertEqual(len(f.compound_series(10, 5, 5)), 6)   # years+1

    def test_expected_net_worth(self):
        self.assertEqual(f.expected_net_worth(40, 50000), 200000.0)

    def test_fee_future_value(self):
        v = f.fee_future_value(100, 0, 1, 12, 0)
        self.assertAlmostEqual(v, 100 * (1.01) ** 12, places=4)
        self.assertLess(f.fee_future_value(100, 0, 1, 12, 1), v)   # fee drags it

    def test_critical_mass(self):
        self.assertEqual(f.critical_mass(40000, 4), 1000000.0)
        self.assertIsNone(f.critical_mass(40000, 0))

    def test_years_until_depleted(self):
        self.assertEqual(f.years_until_depleted(100000, 100000, 0), 1)
        self.assertIsNone(f.years_until_depleted(1000000, 1000, 10))  # self-sustaining
        self.assertIsNone(f.years_until_depleted(100000, 0, 5))


if __name__ == "__main__":
    unittest.main()
