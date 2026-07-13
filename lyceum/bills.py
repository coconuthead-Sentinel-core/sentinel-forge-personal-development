"""Bill Sentinel — prospective-memory scaffolding for bills (pure kernel).

The evidence: automation and defaults beat remembering (Thaler & Benartzi,
2004, *Save More Tomorrow*, J. Political Economy — defaults/automation shift
behavior where willpower fails), and specific timed cues beat vague
intentions (implementation intentions — Gollwitzer & Sheeran, 2006). So the
goal state is EVERY bill on autopay (green, silent); the app tracks what is
automated and cues what is not. **This software cannot pay bills** — it is
external memory, like glasses are external focus.

Pure functions; `today` is always injected (no clock reads — testable).

Overdue semantics (reconciled design decision): a bill with NO payment
history is never called "overdue" — there is no evidence a cycle was
missed; it classifies by its NEXT due date. Once `last_paid` exists, the
current cycle is anchored: paid-before-the-most-recent-due-date means the
cycle was missed -> RED.
"""
from __future__ import annotations

import calendar
from datetime import date, timedelta

GREEN = "GREEN"    # autopay — automated, nothing to remember
OK = "OK"          # manual, due far out — quiet
AMBER = "AMBER"    # manual, due within 7 days (or today)
RED = "RED"        # manual, current cycle missed — overdue

SOON_DAYS = 7


def _clamped(year: int, month: int, due_day: int) -> date:
    """The due date in (year, month), clamping day 29-31 to the month end."""
    return date(year, month, min(due_day, calendar.monthrange(year, month)[1]))


def next_due(due_day: int, today: date) -> date:
    """First occurrence of `due_day` on or after `today` (month-end clamped)."""
    this_month = _clamped(today.year, today.month, due_day)
    if this_month >= today:
        return this_month
    y, m = (today.year + 1, 1) if today.month == 12 else (today.year,
                                                          today.month + 1)
    return _clamped(y, m, due_day)


def prev_due(due_day: int, today: date) -> date:
    """Most recent occurrence of `due_day` on or before `today`."""
    this_month = _clamped(today.year, today.month, due_day)
    if this_month <= today:
        return this_month
    y, m = (today.year - 1, 12) if today.month == 1 else (today.year,
                                                          today.month - 1)
    return _clamped(y, m, due_day)


def classify(bill: dict, today: date) -> dict:
    """Classify one bill for `today`.

    bill: {"name": str, "autopay": bool, "due_day": 1-31,
           "last_paid": date | None}
    returns {"level", "message", "days"} — days is to-next-due (or negative
    days-overdue for RED).
    """
    name = bill.get("name", "bill")
    if bill.get("autopay"):
        return {"level": GREEN, "days": None,
                "message": f"🟢 {name}: automated — nothing to remember."}
    due_day = int(bill["due_day"])
    last_paid = bill.get("last_paid")
    pd = prev_due(due_day, today)
    paid_current = last_paid is not None and last_paid >= pd
    if last_paid is not None and not paid_current:
        late = (today - pd).days
        if late == 0:
            return {"level": AMBER, "days": 0,
                    "message": f"🟡 {name}: due TODAY — pay it or set up autopay."}
        return {"level": RED, "days": -late,
                "message": f"🔴 {name}: overdue {late}d — pay today."}
    # No history yet, or current cycle already paid: look forward.
    if paid_current:
        nd = next_due(due_day, pd + timedelta(days=1))
        if nd <= today:                       # edge: clamp rolled us backward
            nd = next_due(due_day, today + timedelta(days=1))
    else:
        nd = next_due(due_day, today)
    days = (nd - today).days
    if days == 0:
        return {"level": AMBER, "days": 0,
                "message": f"🟡 {name}: due TODAY — pay it or set up autopay."}
    if days <= SOON_DAYS:
        return {"level": AMBER, "days": days,
                "message": f"🟡 {name}: due in {days}d — pay or set up autopay."}
    return {"level": OK, "days": days,
            "message": f"{name}: due in {days}d."}


def next_action(bills: list[dict], today: date) -> str:
    """THE one line: first red, else first amber, else the autopay nudge for
    the first manual bill, else all-clear."""
    results = [(b, classify(b, today)) for b in bills]
    for b, r in results:
        if r["level"] == RED:
            return r["message"]
    for b, r in results:
        if r["level"] == AMBER:
            return r["message"]
    for b, r in results:
        if not b.get("autopay"):
            return (f"⚙ Next move: set up autopay for {b.get('name','bill')} "
                    "— automated beats remembered.")
    if bills:
        return "🟢 Every bill is automated — nothing to remember."
    return "No bills tracked yet — add the first one."
