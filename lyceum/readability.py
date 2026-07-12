"""lyceum/readability.py — reading-difficulty analysis (functional core).

Reviewed from *GO! With Microsoft Word 2010* (readability statistics —
Word reports exactly these two metrics) and proven in pseudocode before
this module was written (3 proofs — see docs/wiki/Review-Word2010Book.md).

This is the classic text-statistics algorithm: count words, sentences,
and — the genuinely algorithmic part — SYLLABLES (a vowel-group
heuristic with a silent-e / consonant-"le" adjustment), then apply two
published formulas:

    Flesch Reading Ease  = 206.835 - 1.015*(W/S) - 84.6*(Y/W)
    Flesch-Kincaid grade = 0.39*(W/S) + 11.8*(Y/W) - 15.59

where W = words, S = sentences, Y = syllables. Higher Reading Ease =
easier; higher grade = harder.

Why it lives here (the neurodivergent-first thesis): a dyslexic reader
benefits from a plain warning — "this passage reads at Grade 14 — Very
hard" — BEFORE spending attention on it. It gives an OBJECTIVE
difficulty score alongside the subjective cognitive_load / zone
metadata already stored with excerpts.

Pure logic: no Tkinter, no I/O, deterministic. Honest limit: the
syllable heuristic is ~85-90% accurate on ordinary English (adjacent
vowels that are actually separate syllables — "idea", "science" — are
the classic misses); the aggregate scores over a passage are stable and
useful, which is all the metric needs.
"""

from __future__ import annotations

import re

_VOWELS = "aeiouy"
_WORD = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_SENT = re.compile(r"[.!?]+")
_VOWEL_RUN = re.compile(r"[aeiouy]+")


def count_syllables(word: str) -> int:
    """Heuristic syllable count for one English word. Always >= 1."""
    w = word.lower().strip("'")
    if not w:
        return 0
    n = len(_VOWEL_RUN.findall(w))
    # Silent trailing 'e' ("make" -> 1) — BUT a consonant + "le" ending
    # ("table", "little", "apple") keeps that e: it forms the -le
    # syllable, so it is not silent.
    consonant_le = (w.endswith("le") and len(w) >= 3
                    and w[-3] not in _VOWELS)
    if w.endswith("e") and not consonant_le and n > 1:
        n -= 1
    return max(1, n)


def _count_sentences(text: str) -> int:
    parts = [p for p in _SENT.split(text) if p.strip()]
    return max(1, len(parts))


def label_for(reading_ease: float) -> str:
    """Plain-language band for a Reading Ease score (dyslexia-first:
    words, not just a number)."""
    if reading_ease >= 80:
        return "Very easy"
    if reading_ease >= 70:
        return "Easy"
    if reading_ease >= 60:
        return "Plain"
    if reading_ease >= 50:
        return "Fairly hard"
    if reading_ease >= 30:
        return "Hard"
    return "Very hard"


def analyze(text: str) -> dict:
    """Readability stats for a passage.

    Returns a dict:
        words, sentences, syllables        (ints)
        flesch_reading_ease   0..100        (higher = easier)
        grade_level           >= 0          (US school grade)
        label                 plain band    ("Plain", "Very hard", …)

    Empty text returns zeros with a neutral "—" label.
    """
    text = text or ""
    words = _WORD.findall(text)
    W = len(words)
    if W == 0:
        return {"words": 0, "sentences": 0, "syllables": 0,
                "flesch_reading_ease": 0.0, "grade_level": 0.0,
                "label": "—"}
    S = _count_sentences(text)
    Y = sum(count_syllables(w) for w in words)
    asl = W / S            # average sentence length
    asw = Y / W            # average syllables per word
    fre = 206.835 - 1.015 * asl - 84.6 * asw
    fkgl = 0.39 * asl + 11.8 * asw - 15.59
    fre = max(0.0, min(100.0, round(fre, 1)))
    fkgl = max(0.0, round(fkgl, 1))
    return {"words": W, "sentences": S, "syllables": Y,
            "flesch_reading_ease": fre, "grade_level": fkgl,
            "label": label_for(fre)}


def badge(text: str) -> str:
    """One-line badge for the reader/excerpt UI, e.g.
    "📖 Grade 8 · Plain". Empty text -> ""."""
    r = analyze(text)
    if r["words"] == 0:
        return ""
    grade = r["grade_level"]
    grade_str = f"{grade:.0f}" if grade == int(grade) else f"{grade:.1f}"
    return f"📖 Grade {grade_str} · {r['label']}"
