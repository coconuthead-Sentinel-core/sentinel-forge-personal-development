"""Tests for lyceum/handoff_view.py — the read-only handoff box kernel.

Owner QA find (2026-07-21): Session Start's "Last session" box was a
tk.Label — nothing on it could be selected or copied, so the handoff
could not be pasted to the coding assistant. These tests pin the
enable→replace→disable contract headless (fake widget), then prove the
real Tk behavior: a disabled Text still allows selection + <<Copy>>,
and ignores typing.
"""
import unittest

from gui_base import GuiTestCase
from lyceum.handoff_view import fill_readonly

try:
    import tkinter as tk
except Exception:                     # pragma: no cover
    tk = None


class _FakeText:
    """Duck-typed Text stand-in that enforces the disabled guard the way
    Tk does (silently ignoring edits while disabled would hide bugs, so
    the fake RAISES instead — stricter than Tk, on purpose)."""

    def __init__(self):
        self.state = "disabled"
        self.content = ""
        self.calls = []

    def configure(self, state):
        self.state = state
        self.calls.append(("configure", state))

    def delete(self, start, end):
        if self.state != "normal":
            raise AssertionError("delete while disabled")
        self.content = ""
        self.calls.append(("delete", start, end))

    def insert(self, index, text):
        if self.state != "normal":
            raise AssertionError("insert while disabled")
        self.content = text
        self.calls.append(("insert", index, text))


class FillContractTest(unittest.TestCase):
    def test_fill_replaces_and_relocks(self):
        w = _FakeText()
        fill_readonly(w, "Last session: A. Next task: B.")
        self.assertEqual(w.content, "Last session: A. Next task: B.")
        self.assertEqual(w.state, "disabled")

    def test_unlock_edit_relock_order(self):
        w = _FakeText()
        fill_readonly(w, "x")
        self.assertEqual(
            [c[0] for c in w.calls],
            ["configure", "delete", "insert", "configure"])
        self.assertEqual(w.calls[0], ("configure", "normal"))
        self.assertEqual(w.calls[-1], ("configure", "disabled"))

    def test_refill_overwrites_not_appends(self):
        w = _FakeText()
        fill_readonly(w, "first")
        fill_readonly(w, "second")
        self.assertEqual(w.content, "second")

    def test_relocks_even_when_insert_raises(self):
        class Exploding(_FakeText):
            def insert(self, index, text):
                super().insert(index, "")
                raise RuntimeError("boom")
        w = Exploding()
        with self.assertRaises(RuntimeError):
            fill_readonly(w, "x")
        self.assertEqual(w.state, "disabled")


class RealTkReadonlyBoxTest(GuiTestCase):
    """The live proofs: on a real (withdrawn) Tk root, the disabled box
    is copyable but not editable."""

    def _box(self, content):
        t = tk.Text(self.root, height=5, wrap="word")
        fill_readonly(t, content)
        return t

    def test_content_readable_after_fill(self):
        t = self._box("Last session: QA weekend.")
        self.assertEqual(t.get("1.0", "end-1c"), "Last session: QA weekend.")
        self.assertEqual(str(t.cget("state")), "disabled")

    def test_refill_replaces_live(self):
        t = self._box("old")
        fill_readonly(t, "new")
        self.assertEqual(t.get("1.0", "end-1c"), "new")

    def test_typing_is_ignored_while_disabled(self):
        t = self._box("locked")
        t.insert("1.0", "HACK")          # disabled Text ignores this
        self.assertEqual(t.get("1.0", "end-1c"), "locked")

    def test_selection_and_copy_work_while_disabled(self):
        t = self._box("copy me to the assistant")
        t.tag_add("sel", "1.0", "end-1c")     # select all
        self.root.clipboard_clear()
        t.event_generate("<<Copy>>")
        self.root.update()
        self.assertEqual(self.root.clipboard_get(),
                         "copy me to the assistant")


if __name__ == "__main__":
    unittest.main()
