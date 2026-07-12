"""Unit tests for the design-law linter (lyceum.lint_designlaws).

Pure static analysis — no GUI. Verifies the linter catches the two recurring
UI traps and, as a regression gate, that the live app file stays free of the
constructor-tuple-pad crash that was swept project-wide.

Run from the repo root:   python -m unittest discover -s tests
"""
import os
import unittest

from lyceum import lint_designlaws as lint

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_APP = os.path.join(_REPO, "sentinel_personal_development.py")


class RuleDetectionTest(unittest.TestCase):
    def test_flags_tuple_pady_in_constructor(self):
        src = "import tkinter as tk\ntk.Label(root, text='x', pady=(12, 2))\n"
        self.assertIn("A", [f.rule for f in lint.scan_source(src)])

    def test_flags_tuple_padx_in_constructor(self):
        src = "import tkinter as tk\ntk.Frame(root, padx=(8, 0))\n"
        self.assertIn("A", [f.rule for f in lint.scan_source(src)])

    def test_allows_tuple_pady_in_pack(self):
        self.assertEqual(lint.scan_source("lbl.pack(fill='x', pady=(12, 2))\n"), [])

    def test_allows_scalar_pady_in_constructor(self):
        src = "import tkinter as tk\ntk.Label(root, pady=6)\n"
        self.assertEqual(lint.scan_source(src), [])

    def test_flags_hardcoded_geometry(self):
        self.assertIn("B", [f.rule for f in lint.scan_source("root.geometry('800x600')\n")])

    def test_allows_computed_geometry(self):
        self.assertEqual(lint.scan_source("root.geometry(f'{w}x{h}')\n"), [])


class LiveSourceRegressionTest(unittest.TestCase):
    """The real app file must stay free of Rule A — the constructor-tuple-pad
    crash was fixed project-wide and must never regress."""

    def test_app_has_no_constructor_tuple_pad(self):
        if not os.path.exists(_APP):
            self.skipTest("app file not found")
        offenders = [f for f in lint.scan_file(_APP) if f.rule == "A"]
        self.assertEqual(
            offenders, [],
            "constructor-tuple pad regressed:\n" +
            "\n".join(f"  line {f.line}: {f.message}" for f in offenders))


if __name__ == "__main__":
    unittest.main()
