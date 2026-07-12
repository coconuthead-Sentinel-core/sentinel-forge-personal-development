"""Unit tests for lyceum/prompt_coach.py — the prompt-quality analyzer.

Mirrors the three proofs that gated the build (rich-vs-vague
discrimination, per-detector accuracy, determinism/ordering/edges) plus
the improve() helper. Pure, headless, deterministic.
"""
import unittest

from lyceum.prompt_coach import analyze, band_for, improve


RICH = ("Act as a patient study tutor. Summarize the following chapter "
        "on photosynthesis for a 10th-grade student as 5 bullet points, "
        "each under 20 words, so it is easy to review before a quiz.")


class DiscriminationTest(unittest.TestCase):
    def test_rich_scores_excellent(self):
        r = analyze(RICH)
        self.assertGreaterEqual(r["score"], 85)
        self.assertEqual(r["band"], "Excellent")
        self.assertTrue(all(r["components"].values()))

    def test_vague_scores_low(self):
        r = analyze("tell me about stuff")
        self.assertLess(r["score"], 40)
        self.assertEqual(r["band"], "Needs work")

    def test_rich_beats_vague(self):
        self.assertGreater(analyze(RICH)["score"],
                           analyze("tell me about stuff")["score"])


class DetectorTest(unittest.TestCase):
    def test_role(self):
        self.assertTrue(analyze("Act as a lawyer and help")
                        ["components"]["role"])
        self.assertFalse(analyze("what is 2 plus 2")
                         ["components"]["role"])

    def test_task(self):
        self.assertTrue(analyze("Summarize this document")
                        ["components"]["task"])

    def test_format(self):
        self.assertTrue(analyze("Give it as a numbered list")
                        ["components"]["format"])
        self.assertFalse(analyze("Write a poem about cats")
                         ["components"]["format"])

    def test_context(self):
        self.assertTrue(analyze(
            "Explain this for my 8th grade class because they are new")
            ["components"]["context"])

    def test_specific(self):
        self.assertTrue(analyze(
            "List 5 causes of the French Revolution in detail")
            ["components"]["specific"])
        self.assertFalse(analyze("do it now")["components"]["specific"])


class OrderingAndEdgeTest(unittest.TestCase):
    def test_deterministic(self):
        p = "Write a summary of the notes"
        self.assertEqual(analyze(p), analyze(p))

    def test_tips_biggest_win_first(self):
        # has a role but no task -> the 30-pt task tip leads
        r = analyze("Act as an expert")
        self.assertIn("action", r["tips"][0].lower())

    def test_empty_safe(self):
        r = analyze("")
        self.assertEqual(r["score"], 0)
        self.assertEqual(len(r["tips"]), 1)

    def test_score_bounded(self):
        for p in ("", "x", RICH, "Summarize this now please quickly"):
            self.assertTrue(0 <= analyze(p)["score"] <= 100)

    def test_bands(self):
        self.assertEqual(band_for(90), "Excellent")
        self.assertEqual(band_for(70), "Good")
        self.assertEqual(band_for(45), "Fair")
        self.assertEqual(band_for(10), "Needs work")

    def test_perfect_prompt_positive_tip(self):
        self.assertTrue(analyze(RICH)["tips"][0].lower().startswith(
            "great prompt"))


class ImproveTest(unittest.TestCase):
    def test_improve_raises_score(self):
        weak = "cats"
        self.assertGreater(analyze(improve(weak))["score"],
                           analyze(weak)["score"])

    def test_improve_empty_gives_template(self):
        self.assertTrue(improve("").startswith("Act as"))

    def test_improve_adds_missing_role(self):
        self.assertIn("Act as", improve("Summarize this article"))

    def test_improve_is_deterministic(self):
        self.assertEqual(improve("write a poem"), improve("write a poem"))


if __name__ == "__main__":
    unittest.main()
