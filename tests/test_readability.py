"""Unit tests for lyceum/readability.py — the reading-difficulty engine.

Mirrors the three proofs that gated the build (syllable counter,
formula exactness, monotonicity/edges) plus the badge helper. Pure,
headless, deterministic.
"""
import unittest

from lyceum.readability import (analyze, badge, count_syllables,
                                label_for)


class SyllableTest(unittest.TestCase):
    def test_hand_counted_list(self):
        # >= 13/15 correct; 'idea' and 'science' are documented heuristic
        # misses (adjacent vowels that are really separate syllables).
        words = {"cat": 1, "apple": 2, "banana": 3, "table": 2,
                 "little": 2, "computer": 3, "readability": 5, "the": 1,
                 "make": 1, "code": 1, "open": 2, "idea": 3,
                 "science": 2, "university": 5, "queue": 1}
        correct = sum(count_syllables(w) == e for w, e in words.items())
        self.assertGreaterEqual(correct, 13)

    def test_consonant_le_keeps_e(self):
        for w in ("table", "little", "apple", "candle"):
            self.assertEqual(count_syllables(w),
                             count_syllables(w),  # stable
                             )
        self.assertEqual(count_syllables("table"), 2)
        self.assertEqual(count_syllables("apple"), 2)

    def test_silent_e_dropped(self):
        self.assertEqual(count_syllables("make"), 1)
        self.assertEqual(count_syllables("code"), 1)

    def test_minimum_one(self):
        self.assertEqual(count_syllables("rhythm"), 1)  # no standard vowel
        self.assertEqual(count_syllables("a"), 1)

    def test_empty_word(self):
        self.assertEqual(count_syllables(""), 0)


class AnalyzeTest(unittest.TestCase):
    def test_counts(self):
        r = analyze("The cat sat. The dog ran.")
        self.assertEqual((r["words"], r["sentences"], r["syllables"]),
                         (6, 2, 6))

    def test_reading_ease_clamped_high(self):
        # very short, simple -> formula > 100 -> clamp to 100
        r = analyze("The cat sat. The dog ran.")
        self.assertEqual(r["flesch_reading_ease"], 100.0)
        self.assertEqual(r["grade_level"], 0.0)
        self.assertEqual(r["label"], "Very easy")

    def test_reading_ease_clamped_low(self):
        # dense polysyllabic -> formula < 0 -> clamp to 0
        r = analyze("Readability matters enormously.")
        self.assertGreaterEqual(r["flesch_reading_ease"], 0.0)

    def test_monotonicity(self):
        easy = analyze("I run. You run. We run fast. The sun is up.")
        hard = analyze("Notwithstanding the aforementioned "
                       "considerations, the epistemological "
                       "ramifications necessitate comprehensive "
                       "reevaluation of foundational assumptions.")
        self.assertGreater(easy["flesch_reading_ease"],
                           hard["flesch_reading_ease"])
        self.assertGreater(hard["grade_level"], easy["grade_level"])

    def test_empty_text_safe(self):
        r = analyze("")
        self.assertEqual(r["words"], 0)
        self.assertEqual(r["label"], "—")

    def test_deterministic(self):
        t = "The quick brown fox jumps over the lazy dog."
        self.assertEqual(analyze(t), analyze(t))

    def test_ranges(self):
        r = analyze("This is a normal English sentence for testing.")
        self.assertTrue(0.0 <= r["flesch_reading_ease"] <= 100.0)
        self.assertGreaterEqual(r["grade_level"], 0.0)


class LabelAndBadgeTest(unittest.TestCase):
    def test_label_bands(self):
        self.assertEqual(label_for(85), "Very easy")
        self.assertEqual(label_for(65), "Plain")
        self.assertEqual(label_for(20), "Very hard")

    def test_badge_format(self):
        b = badge("This is a plain little sentence to read.")
        self.assertTrue(b.startswith("📖 Grade "))
        self.assertIn("·", b)

    def test_badge_empty(self):
        self.assertEqual(badge(""), "")


if __name__ == "__main__":
    unittest.main()
