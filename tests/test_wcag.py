"""Unit tests for the WCAG contrast kernel (lyceum.wcag).

Pure math — no GUI. Anchored to W3C-published values: black/white = 21.0,
the #767676-on-white AA boundary, symmetry, and the AA thresholds. Also
audits the app's PRIMARY reading pairs (they must pass AA); decorative /
accent pairs are audited by the findings probe, not hard-gated here —
a failing existing pair is a finding for the owner, never a silent recolor.

Run from the repo root:   python -m unittest discover -s tests
"""
import unittest

from lyceum import wcag


class FormulaTest(unittest.TestCase):
    def test_black_on_white_is_21(self):
        self.assertAlmostEqual(wcag.contrast_ratio("#000000", "#ffffff"),
                               21.0, places=2)

    def test_same_color_is_1(self):
        self.assertAlmostEqual(wcag.contrast_ratio("#123456", "#123456"),
                               1.0, places=6)

    def test_symmetry(self):
        a = wcag.contrast_ratio("#0f172a", "#f1f5f9")
        b = wcag.contrast_ratio("#f1f5f9", "#0f172a")
        self.assertAlmostEqual(a, b, places=9)

    def test_w3c_boundary_767676_on_white_passes(self):
        # #767676 on white ~= 4.54:1 — the canonical just-passes-AA gray.
        r = wcag.contrast_ratio("#767676", "#ffffff")
        self.assertGreaterEqual(r, 4.5)
        self.assertTrue(wcag.meets_aa(r))

    def test_777777_on_white_fails_normal(self):
        # #777777 on white ~= 4.48:1 — the canonical just-fails gray.
        r = wcag.contrast_ratio("#777777", "#ffffff")
        self.assertLess(r, 4.5)
        self.assertFalse(wcag.meets_aa(r))
        self.assertTrue(wcag.meets_aa(r, large=True))   # large text: 3.0

    def test_shorthand_hex(self):
        self.assertAlmostEqual(wcag.contrast_ratio("#000", "#fff"), 21.0,
                               places=2)

    def test_bad_hex_raises(self):
        with self.assertRaises(ValueError):
            wcag.relative_luminance("#12345")


class PrimaryReadingPairsTest(unittest.TestCase):
    """The pairs the user READS all day must pass AA (normal text)."""

    def test_body_text_on_all_backgrounds(self):
        for bg in ("#0f172a", "#1e293b", "#0b1220"):   # BG_DARK/PANEL/INPUT
            r = wcag.contrast_ratio("#f1f5f9", bg)      # FG_TEXT
            self.assertTrue(wcag.meets_aa(r),
                            f"FG_TEXT on {bg} = {r:.2f} — must pass AA")

    def test_audit_returns_findings_shape(self):
        rows = wcag.audit_pairs([("x", "#777777", "#ffffff", False)])
        self.assertEqual(len(rows), 1)
        self.assertFalse(rows[0]["passes_aa"])
        self.assertIn("ratio", rows[0])


if __name__ == "__main__":
    unittest.main()
