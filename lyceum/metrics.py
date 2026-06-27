"""Pure, UI-free progress metrics — the "functional core" (Bernhardt).

These functions contain NO Tkinter, no database, no I/O — only arithmetic on
plain values. That is deliberate: keeping the logic pure makes it unit-testable
in isolation (see tests/test_metrics.py) and reusable by any panel. The GUI
layer (the "imperative shell") fetches the data, calls these, and renders the
result.
"""
from __future__ import annotations


def wheel_progress(snapshot_avgs: list[float], target: int) -> dict:
    """Honest Wheel-of-Life progress, computed from snapshot averages.

    Args:
        snapshot_avgs: each element is one dated snapshot's roundness (the mean
            of its 7 spokes), ordered oldest -> newest. May be empty.
        target: the roundness you're aiming for; clamped to 1..10.

    Returns a dict with baseline (first snapshot), now (latest), target, pct
    (0..100), arrow ("▲"/"▼"/"■"), and n (snapshot count).

    Progress uses the same accountability formula as the Goals panel:
        pct = (now - baseline) / (target - baseline)
    clamped to [0, 100]. With no snapshots, baseline/now are None and pct is 0.
    Cold numbers by design: if you've slipped, `now < baseline` and pct is 0 —
    backsliding is exposed, not hidden.
    """
    t = max(1, min(10, int(target)))
    n = len(snapshot_avgs)
    if n == 0:
        return {"baseline": None, "now": None, "target": t,
                "pct": 0, "arrow": "", "n": 0}
    baseline = snapshot_avgs[0]
    now = snapshot_avgs[-1]
    if t > baseline:
        pct = max(0, min(100, round(100 * (now - baseline) / (t - baseline))))
    else:                                  # target at/below where you started
        pct = 100 if now >= t else 0
    arrow = "▲" if now > baseline else ("▼" if now < baseline else "■")
    return {"baseline": baseline, "now": now, "target": t,
            "pct": pct, "arrow": arrow, "n": n}
