"""Unit tests for lyceum/password_strength.py — the Shannon-entropy
strength estimator.

Mirrors the three proofs that gated the build (entropy math exact,
weak-vs-strong discrimination, determinism/edges/safety). Pure,
headless, deterministic — no storage, no network, so nothing to mock.
"""
import math
import unittest

from lyceum.password_strength import (band_for, charset_size,
                                      search_space_bits, shannon_bits,
                                      strength)


class EntropyMathTest(unittest.TestCase):
    def test_search_space_exact(self):
        # 8 random lowercase chars = 8 * log2(26)
        self.assertAlmostEqual(search_space_bits("abcdefgh"),
                               8 * math.log2(26), places=6)

    def test_charset_size_classes(self):
        self.assertEqual(charset_size("abc"), 26)
        self.assertEqual(charset_size("Abc123"), 62)
        self.assertEqual(charset_size("Abc123!"), 94)
        self.assertEqual(charset_size(""), 0)

    def test_shannon_closed_form(self):
        self.assertEqual(shannon_bits("aaaa"), 0.0)          # one symbol
        self.assertAlmostEqual(shannon_bits("ab"), 2.0, places=9)
        self.assertAlmostEqual(shannon_bits("abcd"), 8.0, places=9)

    def test_bands(self):
        self.assertEqual(band_for(10), "Very weak")
        self.assertEqual(band_for(30), "Weak")
        self.assertEqual(band_for(50), "Reasonable")
        self.assertEqual(band_for(80), "Strong")
        self.assertEqual(band_for(200), "Very strong")


class DiscriminationTest(unittest.TestCase):
    def test_repeated_chars_weak(self):
        r = strength("aaaaaaaa")
        self.assertIn(r["band"], ("Very weak", "Weak"))

    def test_short_is_weak(self):
        self.assertLess(strength("Ab1!")["bits"], 36)

    def test_long_mixed_is_strong(self):
        r = strength("Tr0ub4dor&3xplore!Now")
        self.assertIn(r["band"], ("Strong", "Very strong"))

    def test_common_password_flagged(self):
        r = strength("password")
        self.assertTrue(r["common"])
        self.assertLessEqual(r["bits"], 8.0)

    def test_strong_beats_weak(self):
        self.assertGreater(strength("Tr0ub4dor&3xplore!Now")["bits"],
                           strength("aaaaaaaa")["bits"])


class SafetyAndEdgeTest(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(strength("Hello123!"), strength("Hello123!"))

    def test_empty_safe(self):
        r = strength("")
        self.assertEqual(r["bits"], 0.0)
        self.assertEqual(r["band"], "Very weak")
        self.assertEqual(len(r["tips"]), 1)

    def test_bits_non_negative(self):
        for p in ("", "a", "Ab1!", "x" * 40, "correct horse battery"):
            self.assertGreaterEqual(strength(p)["bits"], 0.0)

    def test_longer_random_more_bits(self):
        self.assertGreaterEqual(strength("a" * 20 + "B7$k")["bits"],
                                strength("aB7$")["bits"])

    def test_tips_actionable(self):
        self.assertTrue(any("12 characters" in t
                            for t in strength("Ab1!")["tips"]))

    def test_returns_plain_dict_no_side_effects(self):
        # pure: same input twice, identical output, nothing external
        before = strength("MyPa55!")
        after = strength("MyPa55!")
        self.assertEqual(before, after)
        self.assertIsInstance(before, dict)


if __name__ == "__main__":
    unittest.main()
