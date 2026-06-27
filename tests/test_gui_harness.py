"""Smoke test proving the headless Tk harness works (tests/gui_base.py).

Demonstrates that GUI-dependent code can be exercised under CI without flashing a
window: the root is withdrawn, yet widgets build and their state is assertable.
This is the seam for future BookReader panel tests (closing the V&V gap, Q8).
"""
from gui_base import GuiTestCase

try:
    import tkinter as tk
except Exception:                     # pragma: no cover
    tk = None


class HarnessSmokeTest(GuiTestCase):
    def test_root_is_withdrawn(self):
        self.assertEqual(self.root.state(), "withdrawn")

    def test_widget_builds_and_reads_back(self):
        lbl = tk.Label(self.root, text="hello")
        self.assertEqual(lbl.cget("text"), "hello")
        var = tk.StringVar(self.root, value="x")
        self.assertEqual(var.get(), "x")
