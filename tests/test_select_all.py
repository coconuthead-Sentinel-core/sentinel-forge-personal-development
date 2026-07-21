"""Tests for lyceum/select_all.py — Select-all works on BOTH box species.

Owner QA find (2026-07-21): right-click "Select all" was dead on every
single-line Entry (Text-only API crashed silently in the menu). These
tests pin the dispatch headless with fakes, then prove on real Tk that
select_all covers the full contents of an Entry AND a Text — and that
<<Copy>> after select_all puts the whole content on the clipboard (the
owner's actual workflow: click, Select all, Copy, paste).
"""
import unittest

from gui_base import GuiTestCase
from lyceum.select_all import select_all

try:
    import tkinter as tk
except Exception:                     # pragma: no cover
    tk = None


class _FakeText:
    def __init__(self):
        self.calls = []
    def tag_add(self, tag, start, end):
        self.calls.append(("tag_add", tag, start, end))
    def mark_set(self, mark, index):
        self.calls.append(("mark_set", mark, index))
    def see(self, index):
        self.calls.append(("see", index))


class _FakeEntry:
    def __init__(self):
        self.calls = []
    def select_range(self, start, end):
        self.calls.append(("select_range", start, end))
    def icursor(self, index):
        self.calls.append(("icursor", index))


class DispatchTest(unittest.TestCase):
    def test_text_family_selects_whole_range(self):
        w = _FakeText()
        select_all(w)
        self.assertIn(("tag_add", "sel", "1.0", "end"), w.calls)

    def test_entry_family_selects_whole_range(self):
        w = _FakeEntry()
        select_all(w)
        self.assertIn(("select_range", 0, "end"), w.calls)

    def test_unsupported_widget_raises_not_silence(self):
        # A Label supports neither API. The kernel must RAISE (the shell
        # catches it) — silent no-ops are the defect class this repairs.
        with self.assertRaises(AttributeError):
            select_all(object())


class RealTkSelectAllTest(GuiTestCase):
    def test_entry_fully_selected(self):
        e = tk.Entry(self.root)
        e.insert(0, "Prompt Library CLOSE-OUT - one 25-min Pomodoro")
        select_all(e)
        self.assertTrue(e.selection_present())
        self.assertEqual(e.index("sel.first"), 0)
        self.assertEqual(e.index("sel.last"), len(e.get()))

    def test_entry_select_all_then_copy_gets_everything(self):
        content = "the whole line, no dragging required"
        e = tk.Entry(self.root)
        e.insert(0, content)
        select_all(e)
        self.root.clipboard_clear()
        e.event_generate("<<Copy>>")
        self.root.update()
        self.assertEqual(self.root.clipboard_get(), content)

    def test_text_fully_selected(self):
        t = tk.Text(self.root)
        t.insert("1.0", "line one\nline two")
        select_all(t)
        self.assertEqual(t.get("sel.first", "sel.last"),
                         t.get("1.0", "end-1c") + "\n")

    def test_disabled_readonly_text_still_selects(self):
        # The Last-session handoff box is a DISABLED Text — Select all
        # must work there too (the whole point of the copy repair).
        t = tk.Text(self.root)
        t.insert("1.0", "handoff")
        t.configure(state="disabled")
        select_all(t)
        self.assertTrue(t.tag_ranges("sel"))


if __name__ == "__main__":
    unittest.main()
