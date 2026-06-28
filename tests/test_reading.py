"""Unit tests for the pure read-aloud span computation (lyceum.reading),
extracted from the CC-58 _ftb_read_toggle engine. This is the piece where the
'stops after one chunk' bugs historically lived, so it gets explicit coverage."""
import unittest

from lyceum.reading import read_spans


def _texts(text, unit):
    return [text[s:e] for s, e in read_spans(text, unit)]


class ReadSpansTest(unittest.TestCase):
    def test_words(self):
        self.assertEqual(_texts("hello  world\tthere", "Word"),
                         ["hello", "world", "there"])

    def test_sentences(self):
        text = "First sentence. Second one! Third?"
        self.assertEqual(_texts(text, "Sentence"),
                         ["First sentence.", "Second one!", "Third?"])

    def test_sentence_with_quote(self):
        text = 'He said "stop." Then left.'
        out = _texts(text, "Sentence")
        self.assertEqual(len(out), 2)
        self.assertTrue(out[0].endswith('."'))

    def test_paragraphs(self):
        text = "Para one line.\nstill para one.\n\nPara two."
        out = read_spans(text, "Paragraph")
        self.assertEqual(len(out), 2)        # blank line splits paragraphs

    def test_multiple_sentences_not_truncated(self):
        # regression guard: every sentence is returned, not just the first
        text = "A. B. C. D. E."
        self.assertEqual(len(read_spans(text, "Sentence")), 5)

    def test_empty_and_whitespace(self):
        self.assertEqual(read_spans("", "Word"), [])
        self.assertEqual(read_spans("   \n  ", "Sentence"), [])


if __name__ == "__main__":
    unittest.main()
