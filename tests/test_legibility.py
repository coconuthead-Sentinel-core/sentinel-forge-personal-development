"""Unit tests for lyceum/legibility.py — the accessibility formatting
kernel. Mirrors the three proofs that gated the build (font resolution
+ safe fallback, size clamping/monotonicity, total determinism). Pure,
headless, deterministic."""
import unittest

from lyceum.legibility import (MAX_SIZE, MIN_SIZE, clamp_size,
                               first_installed, legibility_spec,
                               preset_names, step_size)

# Fonts verified installed on the target machine.
INSTALLED = {"OpenDyslexic", "Comic Sans MS", "Verdana", "Tahoma",
             "Arial", "Segoe UI"}


class FontResolutionTest(unittest.TestCase):
    def test_opendyslexic_selected_when_installed(self):
        self.assertEqual(
            legibility_spec("OpenDyslexic", 16, INSTALLED)["family"],
            "OpenDyslexic")

    def test_fallback_when_opendyslexic_absent(self):
        self.assertEqual(
            legibility_spec("OpenDyslexic", 16, {"Verdana", "Segoe UI"})["family"],
            "Verdana")

    def test_universal_fallback(self):
        self.assertEqual(
            legibility_spec("Dyslexia", 16, {"Segoe UI"})["family"],
            "Segoe UI")
        self.assertEqual(first_installed(["Nope", "Nada"], INSTALLED),
                         "Segoe UI")

    def test_dyslexia_presets_add_leading(self):
        self.assertGreaterEqual(
            legibility_spec("OpenDyslexic", 16, INSTALLED)["spacing1"], 6)
        self.assertGreaterEqual(
            legibility_spec("ADHD focus", 16, INSTALLED)["spacing3"], 8)

    def test_default_is_plain(self):
        self.assertEqual(
            legibility_spec("Default", 16, INSTALLED),
            {"family": "Segoe UI", "size": 16,
             "spacing1": 2, "spacing3": 2, "wrap": "word"})

    def test_unknown_preset_degrades_to_default(self):
        self.assertEqual(
            legibility_spec("bogus", 16, INSTALLED)["family"], "Segoe UI")


class SizeClampTest(unittest.TestCase):
    def test_clamp_floor_ceiling(self):
        self.assertEqual(clamp_size(4), MIN_SIZE)
        self.assertEqual(clamp_size(999), MAX_SIZE)
        self.assertEqual(clamp_size("bad"), MIN_SIZE)

    def test_step_up_down(self):
        self.assertEqual(step_size(16, +1), 18)
        self.assertEqual(step_size(16, -1), 14)
        self.assertEqual(step_size(16, 0), 16)

    def test_step_clamps_at_bounds(self):
        self.assertEqual(step_size(MAX_SIZE, +1), MAX_SIZE)
        self.assertEqual(step_size(MIN_SIZE, -1), MIN_SIZE)

    def test_size_monotonic(self):
        sizes = [legibility_spec("Default", b, INSTALLED)["size"]
                 for b in range(12, 33, 2)]
        self.assertTrue(all(a <= b for a, b in zip(sizes, sizes[1:])))

    def test_delta_still_clamped(self):
        self.assertEqual(
            legibility_spec("Dysgraphia", 31, INSTALLED)["size"], MAX_SIZE)
        self.assertEqual(
            legibility_spec("Default", 1, INSTALLED)["size"], MIN_SIZE)


class TotalityTest(unittest.TestCase):
    def test_every_preset_size_valid_spec(self):
        keys = {"family", "size", "spacing1", "spacing3", "wrap"}
        for name in preset_names():
            for b in (10, 16, 24, 40):
                spec = legibility_spec(name, b, INSTALLED)
                self.assertEqual(set(spec), keys)
                self.assertEqual(spec["wrap"], "word")
                self.assertTrue(MIN_SIZE <= spec["size"] <= MAX_SIZE)
                self.assertIn(spec["family"], INSTALLED)

    def test_deterministic(self):
        self.assertEqual(legibility_spec("ADHD focus", 18, INSTALLED),
                         legibility_spec("ADHD focus", 18, INSTALLED))

    def test_dropdown_order(self):
        names = preset_names()
        self.assertEqual(names[0], "Default")
        self.assertIn("OpenDyslexic", names)
        self.assertIn("ADHD focus", names)
        self.assertIn("Dysgraphia", names)


if __name__ == "__main__":
    unittest.main()
