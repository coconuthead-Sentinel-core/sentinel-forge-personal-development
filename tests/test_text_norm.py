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


if __name__ == "__main__":
    unittest.main()
