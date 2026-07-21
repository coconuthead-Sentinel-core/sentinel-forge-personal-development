"""Read-only handoff view kernel — fill a Text-like widget with the
Last-session handoff, copy-enabled but edit-locked.

Owner QA find (2026-07-21): the Session Start "Last session" box was a
``tk.Label`` — no selection, no clipboard, no way to hand the handoff
back to the coding assistant at session start. Fifth instance of the
enrollment defect class (see Whitepaper-Notes, invisible-success).
The repair renders the handoff in a DISABLED ``tk.Text`` — selection
and Copy still work on a disabled Text; edits do not — and every
refresh must re-lock. This kernel pins that enable→replace→disable
contract. Pure: the widget is duck-typed; no tkinter import here.
"""


def fill_readonly(widget, content: str) -> None:
    """Replace ``widget``'s entire text with ``content``, locked after.

    Contract (tested headless with a fake, and live under Tk):
    1. unlock first (``state="normal"``) — a disabled Text silently
       ignores ``delete``/``insert``, so writing while locked would be
       an invisible failure, the exact defect class this repairs;
    2. delete everything, insert ``content`` at the top;
    3. re-lock (``state="disabled"``) ALWAYS — even if insert raises —
       so the box can never be left editable.
    """
    widget.configure(state="normal")
    try:
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
    finally:
        widget.configure(state="disabled")
