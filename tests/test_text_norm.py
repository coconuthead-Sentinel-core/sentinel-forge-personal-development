"""Unit tests for the read-aloud text normalizer (lyceum.text_norm).

Pure string→string; no TTS engine or GUI involved. This is what lets the
feature be verified without playing audio.
"""
import unittest

from lyceum.text_norm import normalize_for_speech


class NormalizeForSpeechTest(unittest.TestCase):
    def test_currency_plain(self):
        self.assertEqual(normalize_for_speech("$32"), "thirty-two dollars")

    def test_currency_singular_dollar(self):
        self.assertEqual(normalize_for_speech("$1"), "one dollar")

    def test_currency_with_cents(self):
        self.assertEqual(
            normalize_for_speech("$1,234.50"),
            "one thousand two hundred thirty-four dollars and fifty cents")

    def test_percent(self):
        self.assertEqual(normalize_for_speech("50%"), "fifty percent")

    def test_ordinals(self):
        self.assertEqual(normalize_for_speech("1st"), "first")
        self.assertEqual(normalize_for_speech("2nd"), "second")
        self.assertEqual(normalize_for_speech("3rd"), "third")
        self.assertEqual(normalize_for_speech("21st"), "twenty-first")

    def test_abbreviations(self):
        self.assertEqual(normalize_for_speech("Dr. Smith"), "Doctor Smith")

    def test_decimal(self):
        self.assertEqual(normalize_for_speech("3.5"), "three point five")

    def test_plain_sentence_unchanged(self):
        s = "The cat sat on the mat."
        self.assertEqual(normalize_for_speech(s), s)

    def test_empty_and_none_are_safe(self):
        self.assertEqual(normalize_for_speech(""), "")
        self.assertEqual(normalize_for_speech(None), "")


class YearReadingTest(unittest.TestCase):
    def test_1900s_year(self):
        self.assertEqual(normalize_for_speech("1999"), "nineteen ninety-nine")

    def test_two_thousands(self):
        self.assertEqual(normalize_for_speech("2007"), "two thousand seven")
        self.assertEqual(normalize_for_speech("2000"), "two thousand")

    def test_twenty_tens(self):
        self.assertEqual(normalize_for_speech("2015"), "twenty fifteen")

    def test_oh_years_and_centuries(self):
        self.assertEqual(normalize_for_speech("1905"), "nineteen oh five")
        self.assertEqual(normalize_for_speech("1900"), "nineteen hundred")

    def test_year_in_a_sentence(self):
        self.assertEqual(normalize_for_speech("Born in 1984."),
                         "Born in nineteen eighty-four.")

    def test_money_year_not_confused(self):
        # Currency is handled before the year rule, so $2000 stays dollars.
        self.assertEqual(normalize_for_speech("$2000"), "two thousand dollars")


class CodeSpanTest(unittest.TestCase):
    """Backtick code spans are atomic: exempt from English normalization,
    spoken with the minimal code-reading form (underscore/slash named)."""

    def test_number_inside_code_not_year_expanded(self):
        # Without protection, 1024 reads as the year "ten twenty-four".
        self.assertEqual(normalize_for_speech("`1024`"), "1024")

    def test_path_gets_separator_names_only(self):
        self.assertEqual(normalize_for_speech("`lyceum/text_norm.py`"),
                         "lyceum slash text underscore norm.py")

    def test_abbrev_not_expanded_inside_code(self):
        # 'St.' is an abbreviation in prose, a literal token in code.
        self.assertEqual(normalize_for_speech("`St.py`"), "St.py")

    def test_prose_around_code_still_normalizes(self):
        self.assertEqual(
            normalize_for_speech("Dr. Smith wrote `run_all()` in 1999."),
            "Doctor Smith wrote run underscore all() in nineteen "
            "ninety-nine.")

    def test_multiple_spans(self):
        self.assertEqual(normalize_for_speech("`a_b` and `c/d`"),
                         "a underscore b and c slash d")

    def test_unpaired_backtick_left_alone(self):
        # An odd backtick is not a span; prose rules apply as before.
        self.assertEqual(normalize_for_speech("a ` 2nd try"),
                         "a ` second try")


if __name__ == "__main__":
    unittest.main()
