import unittest

from lyceum import dictation_guard as dg


class TestApply(unittest.TestCase):
    def test_basic_marks(self):
        self.assertEqual(dg.process("hello period"), "hello.")
        self.assertEqual(dg.process("wait comma then go"), "wait, then go")
        self.assertEqual(dg.process("really question mark"), "really?")

    def test_whole_word_only(self):
        # "period" inside another word must not be replaced.
        self.assertEqual(dg.process("a periodical here"), "a periodical here")


class TestCollision(unittest.TestCase):
    def test_whisper_already_punctuated_plus_spoken(self):
        # Whisper wrote the period AND user said "period".
        self.assertEqual(dg.process("done . period"), "done.")

    def test_double_period(self):
        self.assertEqual(dg.process("done period period"), "done.")

    def test_mixed_terminals_keep_strongest(self):
        self.assertEqual(dg.process("great exclamation mark period"), "great!")

    def test_terminal_then_comma(self):
        self.assertEqual(dg.process("stop period comma go"), "stop. go")

    def test_spacing_after_mark(self):
        self.assertEqual(dg.process("hi comma there period bye period"),
                         "hi, there. bye.")


class TestStructure(unittest.TestCase):
    def test_new_paragraph(self):
        self.assertEqual(dg.process("done period new paragraph next line"),
                         "done.\n\nnext line")

    def test_dedup_standalone(self):
        # When dictation_commands already produced marks, guard alone tidies.
        self.assertEqual(dg.dedup_punctuation("done .. , next"), "done. next")

    def test_idempotent(self):
        once = dg.process("first period new paragraph second period")
        self.assertEqual(dg.dedup_punctuation(once), once)


if __name__ == "__main__":
    unittest.main(verbosity=2)
