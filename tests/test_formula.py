"""Unit tests for lyceum/formula.py — the spreadsheet formula engine.

Mirrors the three proofs that gated the build (arithmetic + precedence,
functions over A1 ranges, Excel-semantics cross-check) plus the error
paths a real evaluator must handle. Pure, headless, deterministic.
"""
import unittest

from lyceum.formula import (FormulaError, cells_in_range, col_to_num,
                            excel, num_to_col)


class AddressTest(unittest.TestCase):
    def test_col_round_trip(self):
        for n in (1, 26, 27, 52, 53, 702, 703):
            self.assertEqual(col_to_num(num_to_col(n)), n)

    def test_known_columns(self):
        self.assertEqual(col_to_num("A"), 1)
        self.assertEqual(col_to_num("Z"), 26)
        self.assertEqual(col_to_num("AA"), 27)
        self.assertEqual(num_to_col(28), "AB")

    def test_range_row_major(self):
        self.assertEqual(cells_in_range("A1", "B2"),
                         ["A1", "B1", "A2", "B2"])

    def test_range_is_orientation_independent(self):
        self.assertEqual(cells_in_range("B2", "A1"),
                         cells_in_range("A1", "B2"))


class ArithmeticTest(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(excel("2+3*4"), 14)
        self.assertEqual(excel("(2+3)*4"), 20)

    def test_power_right_associative(self):
        self.assertEqual(excel("2^3^2"), 512)     # 2^(3^2), not (2^3)^2

    def test_unary_minus_and_plus(self):
        self.assertEqual(excel("-3+10"), 7)
        self.assertEqual(excel("+5-2"), 3)

    def test_division_and_modulo(self):
        self.assertEqual(excel("10/4"), 2.5)
        self.assertEqual(excel("17%5"), 2)

    def test_leading_equals_optional(self):
        self.assertEqual(excel("=1+1"), excel("1+1"))


class FunctionTest(unittest.TestCase):
    def setUp(self):
        self.grid = {"A1": 10, "A2": 20, "A3": 30, "B1": 5, "B2": 15}

    def test_aggregates(self):
        g = self.grid
        self.assertEqual(excel("SUM(A1:A3)", g), 60)
        self.assertEqual(excel("AVERAGE(A1:A3)", g), 20)
        self.assertEqual(excel("MAX(A1:A3)", g), 30)
        self.assertEqual(excel("MIN(A1:B2)", g), 5)
        self.assertEqual(excel("COUNT(A1:A3)", g), 3)
        self.assertEqual(excel("PRODUCT(B1,B2)", g), 75)

    def test_mixed_range_and_scalar(self):
        self.assertEqual(excel("SUM(A1:A3)+B1*2", self.grid), 70)

    def test_if_branches(self):
        g = self.grid
        self.assertEqual(excel("IF(A1>5, 100, 200)", g), 100)
        self.assertEqual(excel("IF(A1>50, 100, 200)", g), 200)
        self.assertEqual(excel("IF(A1>50, 100)", g), 0.0)  # no else -> 0

    def test_round(self):
        self.assertEqual(excel("ROUND(10/3, 2)"), 3.33)
        self.assertEqual(excel("ROUND(2.5)"), 2)          # banker's? python round

    def test_nested_functions(self):
        self.assertEqual(
            excel("IF(SUM(A1:A3)>50, MAX(A1:A3), 0)", self.grid), 30)

    def test_blank_cells_are_zero(self):
        self.assertEqual(excel("SUM(A1:A3)", {"A1": 10}), 10)

    def test_math_functions(self):
        self.assertEqual(excel("ABS(-7)"), 7)
        self.assertEqual(excel("SQRT(144)"), 12)
        self.assertEqual(excel("INT(3.9)"), 3)


class ExcelCrossCheckTest(unittest.TestCase):
    def test_a1_math_matches_openpyxl(self):
        try:
            from openpyxl.utils import column_index_from_string
        except Exception:
            self.skipTest("openpyxl not installed")
        for letters in ("A", "B", "Z", "AA", "AB", "BA", "ZZ"):
            self.assertEqual(col_to_num(letters),
                             column_index_from_string(letters))


class ErrorTest(unittest.TestCase):
    def test_bad_character(self):
        with self.assertRaises(FormulaError):
            excel("1 + @")

    def test_unbalanced_parens(self):
        with self.assertRaises(FormulaError):
            excel("(1+2")

    def test_unknown_function(self):
        with self.assertRaises(FormulaError):
            excel("BOGUS(1,2)")

    def test_division_by_zero(self):
        with self.assertRaises(FormulaError):
            excel("1/0")

    def test_bare_range_outside_function(self):
        with self.assertRaises(FormulaError):
            excel("A1:B2", {"A1": 1})

    def test_determinism(self):
        f = "IF(SUM(A1:A3)>50, MAX(A1:A3)*1.05, 0)"
        g = {"A1": 10, "A2": 20, "A3": 30}
        self.assertEqual(excel(f, g), excel(f, g))


if __name__ == "__main__":
    unittest.main()
