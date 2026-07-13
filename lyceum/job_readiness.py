"""Pure job-readiness audit logic — the "real world job" self-examination.

Six pillars a real hiring process actually checks, each scored 0-4 against a
plain-language rubric. Readiness is the share of the 24 rubric points earned;
the next move is always the rubric step above the LOWEST pillar (earlier
pillars are more foundational and win ties). No Tkinter, no I/O — the GUI maps
the returned semantic ``band`` to a colour, keeping presentation out of the
logic. Cold honesty beats a pretty number: the bands say where you actually
stand, not where it would be nice to be.
"""
from __future__ import annotations

import json

MAX_SCORE = 4

# (key, label, question) — order is foundational-first and breaks ties in
# next_moves(): no pitch means proof has nothing to hang from, and so on.
PILLARS = (
    ("story", "Story",
     "Can you say who you are and what job you want in 30 seconds?"),
    ("proof", "Proof",
     "Résumé plus tangible evidence — work samples, results, references?"),
    ("skills", "Skills",
     "Do your skills match the postings you actually want to win?"),
    ("people", "People",
     "Do real people know you are looking? Most jobs arrive through people."),
    ("pipeline", "Pipeline",
     "Are applications and follow-ups actually going out every week?"),
    ("interview", "Interview",
     "Have you practiced answers OUT LOUD recently — not just in your head?"),
)

PILLAR_KEYS = tuple(k for k, _l, _q in PILLARS)

# RUBRIC[key][score] — what each level looks like, in plain language.
RUBRIC = {
    "story": (
        "No pitch — the question makes me freeze",
        "Rough idea, but it rambles or apologizes",
        "Written pitch exists; not yet said out loud",
        "Said out loud; lands in under a minute",
        "30-second pitch on demand, tailored per listener",
    ),
    "proof": (
        "No current résumé, no evidence gathered",
        "Résumé draft exists but is stale or generic",
        "Résumé current; evidence (samples/results) scattered",
        "Résumé + one organized proof pack ready to send",
        "Tailored résumé per role + references who said yes",
    ),
    "skills": (
        "Haven't read real postings for the target job",
        "Read postings; gaps unknown or unwritten",
        "Gap list written — know what's missing",
        "Actively closing the top gap (course/practice/reps)",
        "Can do the top-listed skills and prove each one",
    ),
    "people": (
        "Nobody knows I'm looking",
        "Told household/friends only",
        "Told a few people in the field",
        "Asked specific people for intros or leads",
        "Warm intros happening; people send me postings",
    ),
    "pipeline": (
        "Zero applications out",
        "A few sent, ever; nothing tracked",
        "Applying sometimes; no weekly rhythm",
        "Weekly quota met and tracked",
        "Weekly quota + follow-ups + interviews booking",
    ),
    "interview": (
        "No practice at all",
        "Rehearsed silently in my head",
        "Answered common questions out loud, alone",
        "Mock interview with a real person done",
        "Multiple mocks + feedback folded back in",
    ),
}

# NEXT_STEP[key][score] — the one concrete action that moves score → score+1.
NEXT_STEP = {
    "story": (
        "Write 3 sentences: who I am, what I do, what job I want.",
        "Trim the pitch to 30 seconds — cut every apology.",
        "Say the pitch out loud 5 times today.",
        "Tailor the pitch to one real listener and try it on them.",
    ),
    "proof": (
        "Open a blank page and list every job, project, and result you have.",
        "Update the résumé to today — dates, latest work, one page.",
        "Put samples/results/numbers into ONE folder you can send.",
        "Ask two people to be references — get an actual yes.",
    ),
    "skills": (
        "Read 5 real postings for the target job; save them.",
        "Write the gap list: skills they ask for that you lack.",
        "Pick the ONE gap that appears most and start closing it.",
        "Build something small that proves the skill — keep it in the proof pack.",
    ),
    "people": (
        "Tell one person today that you are job hunting.",
        "Message 3 people who work in or near the field.",
        "Ask one specific person for one specific intro.",
        "Follow up with everyone who offered help — this week.",
    ),
    "pipeline": (
        "Send ONE application today — done beats perfect.",
        "Start a tracker: company, role, date, next step.",
        "Set a weekly quota you can keep (even 3) and meet it once.",
        "Add follow-ups: nudge every application older than a week.",
    ),
    "interview": (
        "Answer 'tell me about yourself' out loud, once, now.",
        "Answer the top 5 common questions out loud, alone.",
        "Book a mock interview with a real person.",
        "Do another mock; write down and fix what stung.",
    ),
}

# (floor_pct, band, badge) — highest floor ≤ pct wins. Honest names.
BANDS = (
    (0,   "cold_start",      "🔴 COLD START"),
    (20,  "foundations",     "🟠 FOUNDATIONS"),
    (40,  "warming_up",      "🟡 WARMING UP"),
    (60,  "in_the_hunt",     "🔵 IN THE HUNT"),
    (80,  "interview_ready", "🟢 INTERVIEW READY"),
    (100, "offer_ready",     "🏆 OFFER READY"),
)


def clamp(value):
    """Coerce any input to an int score in 0..MAX_SCORE (bad input → 0)."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(MAX_SCORE, v))


def readiness(scores):
    """Overall readiness for a ``{pillar_key: score}`` mapping.

    Returns ``(pct, band, badge)`` — pct is the share of the 24 rubric points
    earned (missing pillars count 0), band is a semantic level from BANDS for
    the GUI to colour, badge is the display string. Pure.
    """
    earned = sum(clamp(scores.get(k)) for k in PILLAR_KEYS)
    pct = round(100 * earned / (MAX_SCORE * len(PILLAR_KEYS)))
    band, badge = BANDS[0][1], BANDS[0][2]
    for floor, b, dg in BANDS:
        if pct >= floor:
            band, badge = b, dg
    return pct, band, badge


def next_moves(scores, k=3):
    """The ``k`` highest-impact actions, weakest pillar first.

    Returns a list of ``(key, label, score, action)`` for pillars below
    MAX_SCORE, ordered by score ascending with the foundational (PILLARS)
    order breaking ties. Empty list when every pillar is maxed. Pure.
    """
    ranked = sorted(
        ((clamp(scores.get(key)), idx, key, label)
         for idx, (key, label, _q) in enumerate(PILLARS)),
    )
    return [(key, label, s, NEXT_STEP[key][s])
            for s, _idx, key, label in ranked if s < MAX_SCORE][:k]


def compare(prev_scores, cur_scores):
    """Honest delta between two check-ins.

    Returns ``(delta_pct, improved, slipped)`` where improved/slipped are
    lists of ``(key, label, points)`` with points always positive. Pure.
    """
    delta = readiness(cur_scores)[0] - readiness(prev_scores)[0]
    improved, slipped = [], []
    for key, label, _q in PILLARS:
        d = clamp(cur_scores.get(key)) - clamp(prev_scores.get(key))
        if d > 0:
            improved.append((key, label, d))
        elif d < 0:
            slipped.append((key, label, -d))
    return delta, improved, slipped


def encode_scores(scores):
    """Serialize scores for storage — clamped, only known pillars, stable."""
    return json.dumps({k: clamp(scores.get(k)) for k in PILLAR_KEYS},
                      sort_keys=True)


def decode_scores(text):
    """Parse stored scores; tolerant of bad/missing data (→ zeros). Pure."""
    try:
        raw = json.loads(text or "{}")
    except (TypeError, ValueError):
        raw = {}
    if not isinstance(raw, dict):
        raw = {}
    return {k: clamp(raw.get(k)) for k in PILLAR_KEYS}
