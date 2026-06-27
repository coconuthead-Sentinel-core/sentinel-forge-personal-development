"""Headless Tk test harness — a withdrawn root for GUI-dependent tests.

Instantiating ``tk.Tk()`` maps a blank window to the display; in a test we don't
want that flash, and on a runner with no display server ``tk.Tk()`` raises
``TclError``. ``GuiTestCase`` creates ONE *withdrawn* (hidden, not destroyed)
root for the whole test case via the ``withdraw()`` lifecycle method — keeping a
live interpreter for widget-logic assertions — and SKIPS the case entirely when
no display is available, so the suite stays green on a headless runner instead of
crashing.

This file is named ``gui_base.py`` (not ``test_*.py``) so unittest discovery does
not run it directly; import ``GuiTestCase`` from your own ``test_*.py``.
"""
from __future__ import annotations

import unittest

try:
    import tkinter as tk
    _TK_IMPORT_ERROR = None
except Exception as e:                # pragma: no cover - platform dependent
    tk = None
    _TK_IMPORT_ERROR = e


class GuiTestCase(unittest.TestCase):
    """Base class providing ``self.root`` — a withdrawn Tk root, or a skip."""

    root = None

    @classmethod
    def setUpClass(cls):
        if tk is None:
            raise unittest.SkipTest(f"tkinter unavailable: {_TK_IMPORT_ERROR}")
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()       # hide from screen/taskbar; keep interpreter
        except tk.TclError as e:      # pragma: no cover - headless runner
            raise unittest.SkipTest(f"no display for Tk: {e}")

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.root is not None:
                cls.root.destroy()    # full teardown: only at the very end
        except Exception:
            pass
