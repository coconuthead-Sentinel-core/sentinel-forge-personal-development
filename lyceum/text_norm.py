"""Text normalization for speech — the read-aloud "front end".

Pure, UI-free string→string helpers that expand numbers, currency, percents,
ordinals, and common abbreviations into their spoken form BEFORE text is sent
to the TTS engine (Piper). This is the one front-end idea worth taking from
text-to-speech theory (the "text analysis" stage of a TTS pipeline): a voice
engine pronounces "$32" or "Dr." poorly, so we spell them out first.

Design rules that keep this safe to drop into the live read-aloud:
  * Pure: no Tkinter, no I/O — unit-testable in isolation.
  * Defensive: normalize_for_speech() never raises; on any error it returns the
    original text unchanged, so it can never break a reading session.
  * Boundary-only: callers apply it to the *chunk of text handed to the engine*,
    not to the on-screen text, so follow-along highlighting stays in sync.
"""
from __future__ import annotations

import re

_ONES = ["zero", "one", "two", "three", "four", "five", "six", "seven",
         "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
         "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
         "eighty", "ninety"]

# Common abbreviations with an unambiguous spoken form. Deliberately small —
# only ones that are nearly always read the same way.
_ABBREV = {
    "Mr.": "Mister", "Mrs.": "Missus", "Ms.": "Miss", "Dr.": "Doctor",
    "Prof.": "Professor", "Jr.": "Junior", "Sr.": "Senior", "St.": "Saint",
    "vs.": "versus", "etc.": "et cetera", "e.g.": "for example",
    "i.e.": "that is", "approx.": "approximately",
}

# Irregular ordinal stems.
_ORDINAL_IRREGULAR = {
    "one": "first", "two": "second", "three": "third", "five": "fifth",
    "eight": "eighth", "nine": "ninth", "twelve": "twelfth",
}


def _int_to_words(n: int) -> str:
    """Whole number -> English words (handles up to the billions)."""
    if n < 0:
        return "negative " + _int_to_words(-n)
    if n < 20:
        return _ONES[n]
    if n < 100:
        word = _TENS[n // 10]
        return word + ("-" + _ONES[n % 10] if n % 10 else "")
    parts = []
    for value, name in ((1_000_000_000, "billion"),
                        (1_000_000, "million"),
                        (1_000, "thousand")):
        if n >= value:
            parts.append(_int_to_words(n // value) + " " + name)
            n %= value
    if n >= 100:
        parts.append(_ONES[n // 100] + " hundred")
        n %= 100
    if n:
        parts.append(_int_to_words(n))
    return " ".join(parts)


def _ordinalize(words: str) -> str:
    """Turn a number's word form into its ordinal ("twenty" -> "twentieth")."""
    head, _, last = words.rpartition("-")        # split a hyphenated tail
    if not last:
        head, last = "", words
    if last in _ORDINAL_IRREGULAR:
        last = _ORDINAL_IRREGULAR[last]
    elif last.endswith("y"):
        last = last[:-1] + "ieth"
    else:
        last = last + "th"
    return (head + "-" + last) if head else last


def _decimal_to_words(token: str) -> str:
    """'3.14' -> 'three point one four'; '12' -> 'twelve'."""
    token = token.replace(",", "")
    if "." in token:
        whole, frac = token.split(".", 1)
        whole_words = _int_to_words(int(whole)) if whole else "zero"
        digits = " ".join(_ONES[int(d)] for d in frac if d.isdigit())
        return f"{whole_words} point {digits}".strip()
    return _int_to_words(int(token))


def _money(match: re.Match) -> str:
    whole = int(match.group(1).replace(",", ""))
    cents_str = match.group(2)
    dollars = f"{_int_to_words(whole)} {'dollar' if whole == 1 else 'dollars'}"
    if cents_str:
        c = int(round(float("0" + cents_str) * 100))
        if c:
            return f"{dollars} and {_int_to_words(c)} {'cent' if c == 1 else 'cents'}"
    return dollars


def normalize_for_speech(text: str) -> str:
    """Expand numbers/currency/percents/ordinals/abbreviations for TTS.

    Returns a speakable version of ``text``. Never raises: any unexpected input
    yields the original string so a reading session is never interrupted.
    """
    try:
        if not text:
            return text or ""
        s = text
        for abbr, full in _ABBREV.items():
            s = s.replace(abbr, full)
        # $1,234.50  ->  dollars (and cents).  Do money before bare numbers.
        s = re.sub(r"\$(\d[\d,]*)(\.\d{1,2})?", _money, s)
        # 50%  ->  fifty percent
        s = re.sub(r"(\d[\d,]*(?:\.\d+)?)\s*%",
                   lambda m: _decimal_to_words(m.group(1)) + " percent", s)
        # 1st / 2nd / 21st  ->  ordinals
        s = re.sub(r"\b(\d+)(?:st|nd|rd|th)\b",
                   lambda m: _ordinalize(_int_to_words(int(m.group(1)))), s)
        # remaining bare numbers / decimals
        s = re.sub(r"\b\d[\d,]*(?:\.\d+)?\b",
                   lambda m: _decimal_to_words(m.group(0)), s)
        return s
    except Exception:
        return text
