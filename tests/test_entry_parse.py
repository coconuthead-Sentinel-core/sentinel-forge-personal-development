"""Unit tests for lyceum/entry_parse.py — pasted-text parsing.

Proves the three paste shapes the owner will actually use (colon,
dash, tab), the multi-line block shape, and that definitions
containing a colon are not wrongly split. Pure/headless."""
import unittest

from lyceum.entry_parse import parse_glossary, split_title_body


class GlossaryColonTest(unittest.TestCase):
    def test_simple_colon_lines(self):
        text = "Entropy: a measure of disorder\nHeap: a tree-based structure"
        self.assertEqual(parse_glossary(text), [
            ("Entropy", "a measure of disorder"),
            ("Heap", "a tree-based structure"),
        ])

    def test_colon_no_space(self):
        self.assertEqual(parse_glossary("API:application interface"),
                         [("API", "application interface")])

    def test_colon_inside_definition_not_split(self):
        # The colon in "3:00" is past the term-length cutoff, so the
        # first ": " (after "Standup") is the split point.
        text = "Standup: the daily meeting happens at 3:00 sharp"
        self.assertEqual(parse_glossary(text),
                         [("Standup", "the daily meeting happens at 3:00 sharp")])


class GlossaryDashTabTest(unittest.TestCase):
    def test_hyphen_with_spaces(self):
        self.assertEqual(parse_glossary("Cache - fast local storage"),
                         [("Cache", "fast local storage")])

    def test_em_dash(self):
        self.assertEqual(parse_glossary("Cache — fast local storage"),
                         [("Cache", "fast local storage")])

    def test_hyphenated_term_not_split(self):
        # "context-aware" has no surrounding spaces, so the " - " sep
        # does not match there; the padded dash after "Term" wins.
        self.assertEqual(parse_glossary("context-aware - knows its setting"),
                         [("context-aware", "knows its setting")])

    def test_tab_separated(self):
        self.assertEqual(parse_glossary("Big-O\tgrowth-rate notation"),
                         [("Big-O", "growth-rate notation")])


class GlossaryBlockTest(unittest.TestCase):
    def test_bare_term_then_definition_line(self):
        text = "Recursion\nA function that calls itself."
        self.assertEqual(parse_glossary(text),
                         [("Recursion", "A function that calls itself.")])

    def test_multiline_definition_joined(self):
        # Wrapped continuation lines are indented (standard convention),
        # so they extend the definition rather than starting new terms.
        text = "Recursion: a function\n  that calls\n  itself"
        self.assertEqual(parse_glossary(text),
                         [("Recursion", "a function that calls itself")])

    def test_unindented_line_after_inline_is_new_term(self):
        # A fresh un-indented term after an inline pair is NOT swallowed.
        text = "Entropy: disorder\nHeap\na tree structure"
        self.assertEqual(parse_glossary(text), [
            ("Entropy", "disorder"),
            ("Heap", "a tree structure"),
        ])

    def test_blank_line_separates_blocks(self):
        text = "Stack\nLIFO structure\n\nQueue\nFIFO structure"
        self.assertEqual(parse_glossary(text), [
            ("Stack", "LIFO structure"),
            ("Queue", "FIFO structure"),
        ])

    def test_term_without_definition_dropped(self):
        self.assertEqual(parse_glossary("LonelyTerm"), [])

    def test_empty_and_whitespace(self):
        self.assertEqual(parse_glossary(""), [])
        self.assertEqual(parse_glossary("   \n  \n"), [])


class TitleBodyTest(unittest.TestCase):
    def test_first_line_title_rest_body(self):
        self.assertEqual(split_title_body("My Topic\nline one\nline two"),
                         ("My Topic", "line one\nline two"))

    def test_single_line_is_title_and_body(self):
        self.assertEqual(split_title_body("Just one line"),
                         ("Just one line", "Just one line"))

    def test_leading_blank_lines_skipped(self):
        self.assertEqual(split_title_body("\n\nTitle\nbody"),
                         ("Title", "body"))

    def test_empty(self):
        self.assertEqual(split_title_body(""), ("", ""))
        self.assertEqual(split_title_body("   "), ("", ""))

    def test_long_title_truncated(self):
        t, _ = split_title_body("x" * 200)
        self.assertLessEqual(len(t), 120)
        self.assertTrue(t.endswith("…"))


if __name__ == "__main__":
    unittest.main()
