"""Unit tests for the spoken-dictation command processor (accessibility).

Pure string→string; no microphone, no GUI. This is what lets the hands-free
dictation feature be verified without speaking.
"""
import unittest

from lyceum.dictation_commands import apply_dictation_commands as run


class DictationCommandsTest(unittest.TestCase):
    def test_spoken_period_and_comma(self):
        self.assertEqual(run("hello world period"), "hello world.")
        self.assertEqual(run("it works comma really"), "it works, really")

    def test_question_and_exclamation(self):
        self.assertEqual(run("really question mark"), "really?")
        self.assertEqual(run("wow exclamation point"), "wow!")

    def test_new_paragraph_then_cap(self):
        self.assertEqual(run("new paragraph cap hello"), "\n\nHello")

    def test_new_line(self):
        self.assertEqual(run("new line"), "\n")

    def test_caps_on_off_title(self):
        self.assertEqual(run("caps on the cat caps off sat"), "The Cat sat")

    def test_all_caps(self):
        self.assertEqual(run("all caps on abc all caps off"), "ABC")

    def test_currency_attaches(self):
        self.assertEqual(run("it costs dollar sign five"), "it costs $five")

    def test_quotes_attach(self):
        self.assertEqual(run("open quote hi close quote"), '"hi"')

    def test_plain_text_unchanged(self):
        s = "a plain sentence with no commands"
        self.assertEqual(run(s), s)

    def test_empty_and_none_safe(self):
        self.assertEqual(run(""), "")
        self.assertEqual(run(None), "")


if __name__ == "__main__":
    unittest.main()
