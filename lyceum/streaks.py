"""Two-lapse streak protocol — the pure kernel behind "Never Miss Twice".

One missed day is a LAPSE, not a broken chain: the banner encourages
(self-compassion after a lapse predicts faster recovery — Neff, 2003,
*Self and Identity*). Only a SECOND consecutive miss escalates to a
fresh-start reset prompt (fresh-start effect — Dai, Milkman & Riis, 2014,
*Management Science*) that asks for an exact time, because specific
if-then plans beat vague intent (implementation intentions —
Gollwitzer & Sheeran, 2006, meta-analysis, d≈0.65).

Pure logic — no Tk, no I/O. The Never-Miss-Twice window feeds it three
booleans and paints whatever comes back.
"""
from __future__ import annotations

# Banner severity levels, mildest -> strongest.
GREEN = "GREEN"    # done today
OK = "OK"          # nothing due yet; neutral nudge
AMBER = "AMBER"    # one lapse; encouragement, never shame
RED = "RED"        # two consecutive lapses; fresh-start protocol


def classify_lapse(done_today: bool, missed_yesterday: bool,
                   missed_day_before: bool) -> str:
    """Classify the streak state. Precedence: today's completion wins,
    then a clean yesterday, then one lapse, then two."""
    if done_today:
        return "done_today"
    if not missed_yesterday:
        return "active"
    if not missed_day_before:
        return "first_miss"
    return "recovery"


def lapse_message(state: str, streak: int, best: int) -> tuple[str, str]:
    """(banner_text, level) for a streak state.

    first_miss is deliberately shame-free: a rest day framing with an
    immediate, doable action. recovery asks for an EXACT time — the
    implementation-intention form — not just "try harder".
    """
    if state == "done_today":
        return ("✅ Done today. The chain grows.", GREEN)
    if state == "active":
        return ("Keep the chain alive — green dot today.", OK)
    if state == "first_miss":
        return ("🟡 Yesterday was a rest day, not a broken chain. "
                "Do it today and the streak keeps going.", AMBER)
    # recovery — two consecutive misses
    return ("🔴 Fresh start today. Pick an exact time: "
            "“At ___ I will do this habit.” Two days off means the plan "
            "needs a time, not more willpower.", RED)
