"""Spoken-dictation punctuation guard — collision & duplicate resolution.

Modern ASR (Whisper) AUTO-punctuates from acoustic pauses. A user who ALSO
speaks punctuation ("...stable period") therefore creates collisions: the
recognizer's own '.' plus the spoken-command '.', e.g. "stable . period" or
"stable period period" → duplicated marks. This module is the post-processing
guard that converts any still-spoken punctuation words into marks AND removes the
resulting duplicate / conflicting marks, keeping the strongest terminal.

Two entry points:
  * ``process(text)``           — full pass: convert spoken punctuation words to
                                  marks, then dedup. Standalone / tested transform.
  * ``dedup_punctuation(text)`` — tidy-only: collapse adjacent or duplicated marks
                                  in a string that already contains symbols. This
                                  is what the live Whisper path calls AFTER
                                  ``dictation_commands.apply_dictation_commands``,
                                  to clean up collisions.

Pure and defensive: no GUI, never raises (returns input unchanged on any error).
Complements ``dictation_commands`` (which inserts marks); this one *resolves* the
marks. Newlines are treated as hard boundaries so paragraph breaks are preserved.
"""
from __future__ import annotations

import re

# Spoken multi-word forms that become a line/paragraph break.
_TWO_BREAK = {
    ("new", "paragraph"): "\n\n",
    ("new", "line"): "\n",
}
# Spoken multi-word forms that become a punctuation mark.
_TWO_MARK = {
    ("question", "mark"): "?",
    ("exclamation", "mark"): "!",
    ("exclamation", "point"): "!",
    ("full", "stop"): ".",
}
# Spoken single-word forms that become a punctuation mark.
_ONE_MARK = {
    "period": ".", "comma": ",", "colon": ":", "semicolon": ";",
}

_MARKS = ".,!?;:"
# Strongest first: terminals outrank clause marks; '!' / '?' outrank '.'.
_PRECEDENCE = "!?.;:,"


def _strongest(marks: str) -> str:
    for m in _PRECEDENCE:
        if m in marks:
            return m
    return marks[0] if marks else ""


def dedup_punctuation(text: str) -> str:
    """Collapse adjacent/duplicate punctuation to the single strongest mark and
    tidy the spacing. Preserves numbers (3.14, 1,234) and newlines."""
    try:
        if not text:
            return text or ""
        s = text
        # 1) Collapse a run of marks (optionally separated by spaces/tabs, never
        #    newlines) down to the single strongest mark.
        s = re.sub(
            r"[.,!?;:]+(?:[ \t]*[.,!?;:]+)*",
            lambda m: _strongest("".join(c for c in m.group(0) if c in _MARKS)),
            s,
        )
        # 2) Drop a space sitting before a mark ("word ." -> "word.").
        s = re.sub(r"[ \t]+([.,!?;:])", r"\1", s)
        # 3) Ensure exactly one space after a mark when a word follows — but NOT
        #    between digits, so decimals/thousands (3.14, 1,234) survive.
        s = re.sub(r"(?<!\d)([.,!?;:])[ \t]*(?=[^\s\d.,!?;:])", r"\1 ", s)
        return s
    except Exception:
        return text


def process(text: str) -> str:
    """Convert spoken punctuation words to marks, then dedup collisions.

    Ordinary prose passes through; only recognized command words are converted.
    Returns the input untouched on any unexpected error.
    """
    try:
        if not text:
            return text or ""
        words = text.split()
        out: list[str] = []
        need_space = False
        i, n = 0, len(words)
        while i < n:
            lw = words[i].lower()
            two = (lw, words[i + 1].lower()) if i + 1 < n else None
            if two in _TWO_BREAK:
                out.append(_TWO_BREAK[two]); need_space = False; i += 2; continue
            if two in _TWO_MARK:
                out.append(_TWO_MARK[two]); need_space = True; i += 2; continue
            if lw in _ONE_MARK:
                out.append(_ONE_MARK[lw]); need_space = True; i += 1; continue
            w = words[i]
            if len(w) == 1 and w in _MARKS:        # a literal mark from the recognizer
                out.append(w); need_space = True; i += 1; continue
            if need_space and out:
                out.append(" ")
            out.append(w); need_space = True; i += 1
        return dedup_punctuation("".join(out))
    except Exception:
        return text
