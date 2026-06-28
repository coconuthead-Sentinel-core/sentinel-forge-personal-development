"""Low-latency voice command-and-control (Vosk) — grammar + matcher + listener.

Whisper is great for free dictation but high-latency for short commands. Vosk
(Apache-2.0) supports a *fixed grammar*, so the recognizer only listens for the
app's own commands ("scratch that", "read selection") — fast and accurate.

This module separates the PURE, testable parts (grammar JSON + command matching)
from the I/O part (the microphone loop), per the functional-core/imperative-shell
split. ``listen`` is an OPTIONAL, guarded generator: it no-ops cleanly if vosk /
sounddevice aren't installed, so the app runs without them.
"""
from __future__ import annotations

import json

# Optional deps — the mic loop needs these; the pure helpers do not.
try:
    import vosk          # noqa: F401
    import sounddevice   # noqa: F401
    _HAVE_VOSK = True
except Exception:
    _HAVE_VOSK = False

UNKNOWN = "[unk]"        # Vosk's reject token for out-of-grammar speech


def build_grammar(commands) -> str:
    """JSON grammar string for vosk.KaldiRecognizer from command phrases.

    Includes the [unk] reject token so unknown speech is ignored rather than
    mis-mapped. Pure; lowercases and de-dupes while preserving order.
    """
    seen, phrases = set(), []
    for c in commands or ():
        p = (c or "").strip().lower()
        if p and p not in seen:
            seen.add(p)
            phrases.append(p)
    return json.dumps(phrases + [UNKNOWN])


def match_command(heard: str, commands):
    """Map a recognized phrase to its canonical command, or None.

    Exact (case-insensitive, whitespace-normalized) match. Pure and testable.
    """
    if not heard:
        return None
    h = " ".join(heard.strip().lower().split())
    for c in commands or ():
        if h == " ".join((c or "").strip().lower().split()):
            return c
    return None


def is_available() -> bool:
    """True if the optional Vosk + sounddevice stack is importable."""
    return _HAVE_VOSK


def listen(model_path: str, commands, samplerate: int = 16000):
    """Yield canonical commands as they are spoken. OPTIONAL / I/O.

    Requires vosk + sounddevice and a downloaded Vosk model at ``model_path``.
    Yields nothing if the stack is unavailable. (Imperative shell — not covered
    by unit tests; the pure grammar/matcher above are.)
    """
    if not _HAVE_VOSK:
        return
    import queue
    import vosk
    import sounddevice as sd

    grammar = build_grammar(commands)
    model = vosk.Model(model_path)
    rec = vosk.KaldiRecognizer(model, samplerate, grammar)
    q: "queue.Queue" = queue.Queue()

    def _cb(indata, frames, time, status):
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype="int16",
                           channels=1, callback=_cb):
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                text = json.loads(rec.Result()).get("text", "").strip()
                cmd = match_command(text, commands)
                if cmd:
                    yield cmd
