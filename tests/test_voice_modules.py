"""Tests for the optional voice modules: SAPI5 TTS, NVDA bridge, Vosk commands,
and LocalBrain.stream(). These exercise the GUARD paths and PURE logic so they
pass with or without the optional deps (pywin32 / NVDA / vosk / Ollama) present.
"""
import unittest

from lyceum import sapi_tts, accessibility_bridge, stt_command


class SapiTtsGuardTest(unittest.TestCase):
    """Whether or not pywin32 is installed, the wrapper must be safe."""
    def test_construct_and_methods_never_raise(self):
        tts = sapi_tts.NativeTTS()
        self.assertIsInstance(tts.available, bool)
        self.assertIsInstance(tts.voices(), list)
        # speak() returns a bool and never raises, even with no engine.
        self.assertIsInstance(tts.speak("hello"), bool)
        self.assertFalse(tts.speak(""))          # empty text -> False
        tts.stop()                                # no-op safe


class NvdaBridgeTest(unittest.TestCase):
    def test_safe_when_nvda_absent(self):
        # No NVDA on the test box -> announce returns False, never raises.
        self.assertFalse(accessibility_bridge.announce(""))
        self.assertIsInstance(accessibility_bridge.announce("hi"), bool)
        self.assertIsInstance(accessibility_bridge.is_available(), bool)


class SttCommandPureTest(unittest.TestCase):
    def test_build_grammar(self):
        import json
        g = json.loads(stt_command.build_grammar(["Scratch that", "scratch that", "Read"]))
        self.assertEqual(g, ["scratch that", "read", "[unk]"])   # deduped, lowercased

    def test_match_command(self):
        cmds = ["scratch that", "read selection"]
        self.assertEqual(stt_command.match_command("Scratch  That", cmds), "scratch that")
        self.assertEqual(stt_command.match_command("read selection", cmds), "read selection")
        self.assertIsNone(stt_command.match_command("open the pod bay doors", cmds))
        self.assertIsNone(stt_command.match_command("", cmds))

    def test_is_available_is_bool(self):
        self.assertIsInstance(stt_command.is_available(), bool)


class LocalBrainStreamTest(unittest.TestCase):
    def test_stream_contract(self):
        from ai_brain import get_brain
        brain = get_brain()
        if brain.available:
            chunks = list(brain.stream("Reply with one short word."))
            self.assertIsInstance("".join(chunks), str)   # streamed text joins to a str
        else:
            self.assertEqual(list(brain.stream("hi")), [])  # unavailable -> empty


if __name__ == "__main__":
    unittest.main()
