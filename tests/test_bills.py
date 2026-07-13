"""Unit tests for the Bill Sentinel kernel (lyceum.bills) + schema round-trip.

Pure logic with injected dates — no GUI, no clock. Covers month-end
clamping, every classification level, next_action priority, and a
temp_study_db round-trip of the additive bills table.

Run from the repo root:   python -m unittest discover -s tests
"""
import sqlite3
import unittest
from datetime import date

from lyceum import bills
from lyceum.db import study_db


class NextDueTest(unittest.TestCase):
    def test_same_month_future(self):
        self.assertEqual(bills.next_due(20, date(2026, 7, 13)),
                         date(2026, 7, 20))

    def test_due_today_counts(self):
        self.assertEqual(bills.next_due(13, date(2026, 7, 13)),
                         date(2026, 7, 13))

    def test_rolls_to_next_month(self):
        self.assertEqual(bills.next_due(5, date(2026, 7, 13)),
                         date(2026, 8, 5))

    def test_month_end_clamp_february(self):
        # due_day 31 in February -> Feb 28 (2026 is not a leap year)
        self.assertEqual(bills.next_due(31, date(2026, 2, 10)),
                         date(2026, 2, 28))

    def test_december_rollover(self):
        self.assertEqual(bills.next_due(5, date(2026, 12, 20)),
                         date(2027, 1, 5))


class ClassifyTest(unittest.TestCase):
    TODAY = date(2026, 7, 13)

    def test_autopay_green_always(self):
        r = bills.classify({"name": "Rent", "autopay": True, "due_day": 1,
                            "last_paid": None}, self.TODAY)
        self.assertEqual(r["level"], bills.GREEN)
        self.assertIn("automated", r["message"])

    def test_manual_far_out_quiet(self):
        r = bills.classify({"name": "Water", "autopay": False, "due_day": 28,
                            "last_paid": date(2026, 6, 28)}, self.TODAY)
        self.assertEqual(r["level"], bills.OK)

    def test_manual_soon_amber(self):
        r = bills.classify({"name": "Power", "autopay": False, "due_day": 18,
                            "last_paid": date(2026, 6, 18)}, self.TODAY)
        self.assertEqual(r["level"], bills.AMBER)
        self.assertIn("due in 5d", r["message"])

    def test_manual_missed_cycle_red(self):
        # Due the 5th, last paid June 5 -> July 5 came and went unpaid.
        r = bills.classify({"name": "Net", "autopay": False, "due_day": 5,
                            "last_paid": date(2026, 6, 5)}, self.TODAY)
        self.assertEqual(r["level"], bills.RED)
        self.assertIn("overdue 8d", r["message"])

    def test_new_bill_never_overdue(self):
        # No payment history: no evidence a cycle was missed.
        r = bills.classify({"name": "New", "autopay": False, "due_day": 5,
                            "last_paid": None}, self.TODAY)
        self.assertNotEqual(r["level"], bills.RED)

    def test_due_today_amber(self):
        r = bills.classify({"name": "Gas", "autopay": False, "due_day": 13,
                            "last_paid": date(2026, 6, 13)}, self.TODAY)
        self.assertEqual(r["level"], bills.AMBER)
        self.assertIn("TODAY", r["message"])


class NextActionTest(unittest.TestCase):
    TODAY = date(2026, 7, 13)

    def test_red_beats_amber(self):
        bs = [{"name": "Soon", "autopay": False, "due_day": 15,
               "last_paid": date(2026, 6, 15)},
              {"name": "Late", "autopay": False, "due_day": 5,
               "last_paid": date(2026, 6, 5)}]
        self.assertIn("Late", bills.next_action(bs, self.TODAY))

    def test_amber_when_no_red(self):
        bs = [{"name": "Far", "autopay": False, "due_day": 28,
               "last_paid": date(2026, 6, 28)},
              {"name": "Soon", "autopay": False, "due_day": 15,
               "last_paid": date(2026, 6, 15)}]
        self.assertIn("Soon", bills.next_action(bs, self.TODAY))

    def test_autopay_nudge_when_all_quiet(self):
        bs = [{"name": "Rent", "autopay": True, "due_day": 1,
               "last_paid": None},
              {"name": "Water", "autopay": False, "due_day": 28,
               "last_paid": date(2026, 6, 28)}]
        msg = bills.next_action(bs, self.TODAY)
        self.assertIn("autopay", msg)
        self.assertIn("Water", msg)

    def test_all_green_goes_quiet(self):
        bs = [{"name": "Rent", "autopay": True, "due_day": 1,
               "last_paid": None}]
        self.assertIn("nothing to remember",
                      bills.next_action(bs, self.TODAY))

    def test_empty_prompts_first_add(self):
        self.assertIn("add", bills.next_action([], self.TODAY).lower())


class SchemaRoundTripTest(unittest.TestCase):
    def test_bills_table_roundtrip(self):
        with study_db.temp_study_db() as tmp:
            study_db.init_study_db()
            con = sqlite3.connect(tmp)
            con.execute("INSERT INTO bills (name, amount_cents, due_day, "
                        "autopay, created_at) VALUES ('Rent', 120000, 1, 1, 't')")
            con.commit()
            row = con.execute("SELECT name, amount_cents, due_day, autopay, "
                              "archived FROM bills").fetchone()
            self.assertEqual(row, ("Rent", 120000, 1, 1, 0))
            con.close()


if __name__ == "__main__":
    unittest.main()
