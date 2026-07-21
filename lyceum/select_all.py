"""Select-all kernel — full-content selection for BOTH box species.

Owner QA find (2026-07-21, with a screenshot): right-click → "Select
all" did nothing on the Session Start "One primary task" field. Root
cause: the old helper spoke only the multi-line Text API (``tag_add``);
on a single-line Entry it raised AttributeError inside the menu
callback — an invisible failure (the menu just closed), so Copy had an
empty selection and manual drag-highlighting was the owner's only path.
The menu is attached to 20+ Entries app-wide, so every one had a dead
"Select all" control — a defect by the functional-code law.

This kernel dispatches on what the widget can do (duck typing), not on
its class, so it needs no tkinter import and tests headless with fakes:
  - Text family  (has ``tag_add``):    tag 1.0 → end as the selection
  - Entry family (has ``select_range``): select_range(0, end)
The imperative shell (``_select_all_in``) wraps this in the Tk error
guard; the kernel itself stays pure.
"""


def select_all(widget) -> None:
    """Select the entire contents of a Text-like or Entry-like widget.

    Raises AttributeError for widgets that support neither API (e.g. a
    Label) — the shell catches it; silence here would recreate the very
    invisible-failure class this repairs.
    """
    if hasattr(widget, "tag_add"):            # multi-line Text family
        widget.tag_add("sel", "1.0", "end")
        widget.mark_set("insert", "1.0")
        widget.see("insert")
    else:                                     # single-line Entry family
        widget.select_range(0, "end")
        widget.icursor("end")
