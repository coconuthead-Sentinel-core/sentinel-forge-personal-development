"""Pomodoro wall-clock kernel — remaining time from a DEADLINE, never
from tick counting.

Owner QA (2026-07-22, diagnosed from the pomo breadcrumbs): a
"20-minute" work block ran 61 wall-clock minutes on 2026-07-21. The
old countdown subtracted one second per Tk `after(1000)` tick, so
laptop sleep and event-loop load stretched every counted "second" —
the timer trusted its own ticks instead of the clock. The law here:
a timer's truth is `deadline - now`; ticks only decide how often the
DISPLAY refreshes. Pure and testable: `now` is always passed in.
"""


def deadline_for(duration_min: int, now: float) -> float:
    """Absolute wall-clock deadline for a block starting at ``now``."""
    return now + int(duration_min) * 60


def remaining_seconds(deadline: float, now: float) -> int:
    """Whole seconds left before ``deadline`` — clamped at zero.

    Immune to tick drift by construction: however late or often it is
    called, the answer comes from the clock, not from call-counting.
    """
    return max(0, int(round(deadline - now)))
