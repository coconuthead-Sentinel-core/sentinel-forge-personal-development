"""Pure goal-accountability logic, extracted from the BookReader God Object (Q3).

The "cold honest status" decision tree for a goal, plus the list summary — no
Tkinter, no DB. Fully unit-testable across every branch (inject ``today`` for
determinism). The GUI maps the returned semantic ``level`` to a colour, keeping
presentation out of the logic.
"""
from __future__ import annotations

from datetime import date, datetime

LEVELS = ("done", "parked", "no_date", "overdue", "behind", "on_track")


def _parse_date(s):
    try:
        return datetime.strptime((s or "")[:10], "%Y-%m-%d").date()
    except Exception:
        return None


def accountability(created_at, target_date, progress, status, today=None):
    """Return (badge, level, is_behind) for a goal.

    Pace = actual progress vs the share of time elapsed toward the target date;
    falling >10 points behind that pace is BEHIND, a passed date is OVERDUE.
    ``level`` is one of LEVELS. Pure — pass a ``today`` date for deterministic
    tests; defaults to date.today().
    """
    today = today or date.today()
    prog = int(progress or 0)
    st = (status or "active").lower()
    if st == "done" or prog >= 100:
        return ("✅ DONE", "done", False)
    if st == "parked":
        return ("⏸ PARKED", "parked", False)
    tgt = _parse_date(target_date)
    started = _parse_date(created_at) or today
    if tgt is None:
        return ("• SET A DATE", "no_date", False)
    if tgt < today:
        return (f"⛔ OVERDUE {(today - tgt).days}d", "overdue", True)
    span = max(1, (tgt - started).days)
    elapsed = max(0, (today - started).days)
    expected = min(100, int(100 * elapsed / span))
    if prog < expected - 10:
        return (f"🔻 BEHIND {prog}/{expected}%", "behind", True)
    return (f"🟢 ON TRACK {(tgt - today).days}d", "on_track", False)


def summarize(rows, today=None):
    """Classify many goals at once.

    ``rows``: iterable of (created_at, target_date, progress, status). Returns
    (per, (n_behind, n_ok, n_done)) where per[i] = (badge, level, is_behind),
    aligned with the input order. Pure.
    """
    today = today or date.today()
    per = []
    n_bad = n_ok = n_done = 0
    for created, target, prog, status in rows:
        badge, level, behind = accountability(created, target, prog, status, today)
        per.append((badge, level, behind))
        if behind:
            n_bad += 1
        elif level == "done":
            n_done += 1
        else:
            n_ok += 1
    return per, (n_bad, n_ok, n_done)
