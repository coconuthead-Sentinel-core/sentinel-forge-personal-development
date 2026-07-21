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


# ONE Tk interpreter for the whole test process, shared by every
# GuiTestCase subclass. History (2026-07-21): each class used to build
# and destroy its own root; once the suite grew to three GUI classes,
# the third re-initialization intermittently failed with Tcl's
# `invalid command name "tcl_findLibrary"` (a known Tcl re-init fault),
# silently turning 4 green tests into skips — a wobbling suite count.
# The process exit reclaims the interpreter; no explicit destroy.
_SHARED_ROOT = None


def _shared_root():
    global _SHARED_ROOT
    if _SHARED_ROOT is None:
        _SHARED_ROOT = tk.Tk()
        _SHARED_ROOT.withdraw()   # hide from screen/taskbar; keep interpreter
    return _SHARED_ROOT


class GuiTestCase(unittest.TestCase):
    """Base class providing ``self.root`` — a withdrawn Tk root, or a skip."""

    root = None

    @classmethod
    def setUpClass(cls):
        if tk is None:
            raise unittest.SkipTest(f"tkinter unavailable: {_TK_IMPORT_ERROR}")
        try:
            cls.root = _shared_root()
        except tk.TclError as e:      # pragma: no cover - headless runner
            raise unittest.SkipTest(f"no display for Tk: {e}")
