"""Pure read-aloud chunking, extracted from the CC-58 _ftb_read_toggle engine.

Given the text and a unit (Word / Sentence / Paragraph), compute the character
spans to speak. This is the ONE genuinely pure, testable piece of the read engine
— and the area where the historical "stops after one chunk" bugs lived, so making
it unit-testable is the high-value part. The widget index-mapping, threading, and
audio playback stay in the GUI (they can't be unit-tested headlessly).
"""
from __future__ import annotations

import re

_WORD = re.compile(r"\S+")
_PARAGRAPH = re.compile(r"[^\n]+(?:\n[^\n]+)*")
# A sentence: run up to terminal . ! ? (with optional closing quote/bracket)
# followed by whitespace/end, or up to a newline, or end of text.
_SENTENCE = re.compile(r"\S[^\n]*?(?:[.!?]+[\"')\]]?(?=\s|$)|(?=\n)|$)", re.MULTILINE)


def read_spans(text, unit):
    """Return [(start, end), ...] character spans to read.

    ``unit`` is 'Word' or 'Sentence'; anything else is treated as 'Paragraph'
    (mirrors the GUI, which only ever passes those three). Empty/whitespace-only
    spans are dropped. Pure — no widget, deterministic, unit-testable.
    """
    if not text:
        return []
    if unit == "Word":
        pattern = _WORD
    elif unit == "Sentence":
        pattern = _SENTENCE
    else:
        pattern = _PARAGRAPH
    spans = []
    for m in pattern.finditer(text):
        s, e = m.span()
        if text[s:e].strip():
            spans.append((s, e))
    return spans
