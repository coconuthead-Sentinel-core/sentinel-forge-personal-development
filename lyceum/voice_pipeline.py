"""Duplex voice pipeline — stream the local LLM and speak it sentence-by-sentence.

The slow part of "talk to the assistant by voice" is waiting for the whole reply
before speech starts. This pipeline streams the model's reply (LocalBrain.stream)
and hands each COMPLETE SENTENCE to a speak() callback as soon as it finishes, so
audio begins almost immediately.

``iter_sentences`` is a PURE generator (unit-testable with no LLM/TTS): given an
iterable of text chunks it yields finished sentences and flushes the remainder.
``DuplexVoiceLoop`` wires that to any brain (with ``.stream``) and any ``speak``
callable, with a threading.Event so a spoken "stop" can interrupt mid-reply.
"""
from __future__ import annotations

import re
import threading

# A sentence ends at . ! or ? that is followed by whitespace. The lookahead for
# whitespace keeps decimals/IPs ("3.14") from being split mid-number.
_SENT_BOUNDARY = re.compile(r"[.!?](?=\s)")


def iter_sentences(chunks):
    """Yield complete sentences from a stream of text chunks; flush the tail.

    Pure: no I/O. ``chunks`` is any iterable of strings (e.g. LocalBrain.stream).
    """
    buf = ""
    for ch in chunks:
        if not ch:
            continue
        buf += ch
        while True:
            m = _SENT_BOUNDARY.search(buf)
            if not m:
                break
            end = m.end()
            sentence = buf[:end].strip()
            buf = buf[end:].lstrip()
            if sentence:
                yield sentence
    tail = buf.strip()
    if tail:
        yield tail


class DuplexVoiceLoop:
    """Orchestrate: stream the brain's reply and speak it as it arrives.

    ``brain`` must expose ``stream(prompt, context="") -> iterable[str]``.
    ``speak`` is any callable taking one string (e.g. NativeTTS.speak or a Piper
    wrapper). ``interrupt()`` halts speaking at the next sentence boundary.
    """

    def __init__(self, brain, speak):
        self._brain = brain
        self._speak = speak
        self._active = threading.Event()

    def ask_aloud(self, query: str, context: str = "") -> None:
        self._active.set()
        for sentence in iter_sentences(self._brain.stream(query, context=context)):
            if not self._active.is_set():
                break
            try:
                self._speak(sentence)
            except Exception:
                break

    def interrupt(self) -> None:
        """Stop the current reply (e.g. on a spoken 'scratch that')."""
        self._active.clear()

    @property
    def speaking(self) -> bool:
        return self._active.is_set()
