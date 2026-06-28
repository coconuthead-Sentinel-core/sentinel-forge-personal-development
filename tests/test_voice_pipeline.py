"""Unit tests for the duplex voice pipeline (lyceum.voice_pipeline).

The sentence chunker and the loop are exercised with FAKE brain/speak objects —
no Ollama, no audio — so the orchestration logic is fully testable."""
import unittest

from lyceum.voice_pipeline import iter_sentences, DuplexVoiceLoop


class IterSentencesTest(unittest.TestCase):
    def test_splits_streamed_chunks(self):
        chunks = ["Hello world. ", "How are ", "you? I am fine."]
        self.assertEqual(list(iter_sentences(chunks)),
                         ["Hello world.", "How are you?", "I am fine."])

    def test_flushes_tail_without_terminal(self):
        self.assertEqual(list(iter_sentences(["no end here"])), ["no end here"])

    def test_decimal_not_split(self):
        # "3.14" must not break mid-number (boundary needs whitespace after).
        self.assertEqual(list(iter_sentences(["pi is 3.14 ", "roughly."])),
                         ["pi is 3.14 roughly."])

    def test_empty_stream(self):
        self.assertEqual(list(iter_sentences([])), [])
        self.assertEqual(list(iter_sentences(["", ""])), [])


class FakeBrain:
    def __init__(self, chunks):
        self._chunks = chunks

    def stream(self, prompt, context=""):
        for c in self._chunks:
            yield c


class DuplexLoopTest(unittest.TestCase):
    def test_speaks_each_sentence(self):
        spoken = []
        loop = DuplexVoiceLoop(FakeBrain(["Hi there. ", "Bye now."]), spoken.append)
        loop.ask_aloud("anything")
        self.assertEqual(spoken, ["Hi there.", "Bye now."])

    def test_interrupt_stops_speaking(self):
        spoken = []

        def speak(s):
            spoken.append(s)
            loop.interrupt()          # stop after the first sentence

        loop = DuplexVoiceLoop(FakeBrain(["One. ", "Two. ", "Three."]), speak)
        loop.ask_aloud("x")
        self.assertEqual(spoken, ["One."])
        self.assertFalse(loop.speaking)


if __name__ == "__main__":
    unittest.main()
