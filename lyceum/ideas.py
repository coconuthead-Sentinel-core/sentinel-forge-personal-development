"""Pure Idea-Warehouse logic extracted from the CC-60 open_idea_warehouse builder.

Task ordering (open before scheduled, Big-Three first, ABCDE priority, then id)
and the banner counts. No Tkinter, no DB — unit-testable in isolation.
"""
from __future__ import annotations

# Row shape from the master_tasks query:
#   (id, text, priority, big_three, scheduled_day, status)


def order_tasks(rows, priority_rank):
    """Sort tasks: open before scheduled, Big-Three first, ABCDE priority
    (``priority_rank`` maps 'A'..'E' -> 0..n; untagged sorts last), then id.
    Pure; returns a new list."""
    return sorted(rows, key=lambda r: (
        0 if r[5] == "open" else 1,        # open before scheduled
        0 if r[3] else 1,                  # Big-Three first
        priority_rank.get(r[2], 9),        # A..E, untagged last
        r[0]))                             # stable by id


def banner_counts(rows):
    """(open_a, big_open): number of open 'A'-priority tasks and open Big-Three
    tasks — drives the 'do those first' banner."""
    open_a = sum(1 for r in rows if r[2] == "A" and r[5] == "open")
    big_open = sum(1 for r in rows if r[3] and r[5] == "open")
    return open_a, big_open
