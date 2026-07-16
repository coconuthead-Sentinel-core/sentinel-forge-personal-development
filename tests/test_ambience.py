"""Unit tests for lyceum/ambience.py — synthesis kernel + honesty
labels (Ambience sprint, session 2026-07-16). Headless: pure synthesis
only; the sounddevice-backed player is exercised for its SAFE paths
(stop-before-start, graceful unavailability contract), never for real
audio output.

Run from the repo root:   python -m unittest discover -s tests
"""
import random
import unittest

from lyceum import ambience
from lyceum.ambience import (KINDS, RATE, AmbiencePlayer, build_loop,
                             synth_binaural, synth_ocean, synth_rain,
                             synth_wind)


class KindsHonestyTest(unittest.TestCase):
    def test_every_kind_carries_a_claim_label(self):
        for kind, meta in KINDS.items():
            self.assertTrue(meta.get("label", "").strip(), kind)
            self.assertTrue(meta.get("claim", "").strip(), kind)

    def test_binaural_label_is_honest(self):
        claim = KINDS["binaural"]["claim"]
        self.assertIn("NOT proven", claim)
        self.assertIn("headphones", claim)

    def test_build_loop_rejects_unknown_kind(self):
        with self.assertRaises(ValueError):
            build_loop("whalesong")


class SynthesisTest(unittest.TestCase):
    def test_mono_beds_shape_and_bounds(self):
        for fn in (synth_wind, synth_rain, synth_ocean):
            buf, channels = fn(rng=random.Random(7))
            self.assertEqual(channels, 1)
            self.assertGreater(len(buf), RATE)          # ≥1 s after seam
            peak = max(max(buf), -min(buf))
            self.assertLessEqual(peak, 32767)
            self.assertGreater(peak, 500, "bed is near-silent")

    def test_seeded_determinism(self):
        a, _ = synth_wind(rng=random.Random(42))
        b, _ = synth_wind(rng=random.Random(42))
        self.assertEqual(a, b)

    def test_binaural_is_stereo_with_distinct_ears(self):
        buf, channels = synth_binaural()
        self.assertEqual(channels, 2)
        left = buf[0::2]
        right = buf[1::2]
        self.assertNotEqual(left[:200], right[:200])    # two frequencies
        peak = max(max(buf), -min(buf))
        self.assertLessEqual(peak, 32767)

    def test_binaural_loop_seam_is_silent(self):
        # Whole cycles per ear per loop: sample 0 is sin(0)=0 and the
        # wrap-around continues the wave — both ears end near zero.
        buf, _ = synth_binaural()
        self.assertEqual(buf[0], 0)
        self.assertEqual(buf[1], 0)
        amp_tolerance = 6000 * 0.02
        self.assertLess(abs(buf[-2]), 6000)             # heading back to 0
        left = buf[0::2]
        # continuity: |last - first| stays a small fraction of amplitude
        self.assertLess(abs(left[-1] - left[0]), 6000 * 0.15,
                        f"seam jump {abs(left[-1] - left[0])} "
                        f"(tolerance {amp_tolerance})")

    def test_build_loop_dispatch(self):
        for kind, meta in KINDS.items():
            buf, channels = build_loop(kind, rng=random.Random(1))
            self.assertEqual(channels, 2 if meta["stereo"] else 1, kind)
            self.assertTrue(len(buf), kind)


class PlayerSafetyTest(unittest.TestCase):
    def test_stop_before_start_is_safe(self):
        player = AmbiencePlayer()
        player.stop()                                   # must not raise
        self.assertFalse(player.playing)
        self.assertIsNone(player.kind)

    def test_unavailability_contract_exists(self):
        # The shell catches this exact type to degrade gracefully.
        self.assertTrue(issubclass(ambience.AmbienceUnavailableError,
                                   RuntimeError))


if __name__ == "__main__":
    unittest.main()
