"""Small pure helpers extracted from the BookReader God Object (Q3 maintainability).

No Tkinter, no DB, no I/O — zone thresholds, time formatting, habit phrasing, and
date-window / back-scheduling math. Each is unit-testable in isolation, which is
the whole point of lifting it out of the 590-method GUI class.
"""
from __future__ import annotations

from datetime import date, timedelta


def zone_for_load(load) -> str:
    """Cognitive-load (1-10) -> GREEN/YELLOW/RED reading zone."""
    if load >= 7:
        return "GREEN"
    if load >= 4:
        return "YELLOW"
    return "RED"


def fmt_hm(minutes) -> str:
    """Minutes -> 'Hh Mm' (or 'Mm' under an hour). Clamps negatives to 0."""
    minutes = max(0, int(minutes))
    h, m = divmod(minutes, 60)
    return f"{h}h {m}m" if h else f"{m}m"


def habit_formula(cue, new) -> str:
    """James Clear habit stack: 'After I [cue], I will [new].' Empty -> ''."""
    cue = (cue or "").strip().rstrip(".")
    new = (new or "").strip().rstrip(".")
    if not cue and not new:
        return ""
    return f"After I {cue or '…'}, I will {new or '…'}."


def period_start(period, today):
    """Start date for a reporting window relative to ``today``."""
    if period == "This month":
        return today.replace(day=1)
    if period == "Last 30 days":
        return today - timedelta(days=30)
    if period == "This year":
        return today.replace(month=1, day=1)
    return date(1970, 1, 1)   # All time


def pert_schedule(target_date, steps):
    """Back-from-the-future PERT scheduling.

    ``steps``: list of (name, weeks) in chronological order (first..last).
    Schedules BACKWARD from ``target_date``; returns a chronological list of
    {name, weeks, start, end}. Pure.
    """
    end = target_date
    out = []
    for name, weeks in reversed(steps):
        try:
            wk = float(weeks)
        except (TypeError, ValueError):
            wk = 0.0
        start = end - timedelta(weeks=wk)
        out.append({"name": name, "weeks": wk, "start": start, "end": end})
        end = start
    out.reverse()
    return out
