"""lyceum/ambience.py — background ambience: synthesis kernel + player.

Quiet, looping comfort sound to sit UNDER the read-aloud voice in the
Library: wind, rain, ocean, or a binaural tone. Synthesis is pure
(stdlib ``array`` + ``math`` + injectable ``random.Random``); playback
is the one piece of I/O this module owns, over the ``sounddevice``
dependency the app already ships for dictation — no new packages.

HONESTY LABELS (clinical-science gate, session 2026-07-16):
- All four beds are **comfort/preference features**, full stop. The
  evidence on background sound during verbal learning is mixed-to-
  negative, which is why every bed defaults QUIET and under the voice.
- **Binaural beats are NOT proven to improve learning.** The research
  record is heterogeneous — some small relaxation/anxiety effects,
  many null results for attention and memory; "brainwave entrainment
  for learning" claims outrun the data. The option ships as a
  relaxation preference with that label on its face, never as a study
  feature. It also needs headphones to produce a beat at all (one
  tone per ear).

Design: every synth returns one seamless loop — noise beds get a
crossfaded seam; the binaural loop is a whole number of cycles per
second for both ears, so the seam is mathematically silent.
"""

from __future__ import annotations

import array
import math
import random

RATE = 22050            # matches the app's TTS output rate
_AMP = 9000             # synth headroom; the player's volume scales DOWN


class AmbienceUnavailableError(RuntimeError):
    """sounddevice / numpy are missing — ambience is disabled, app is fine."""


# Honest metadata the shell renders verbatim — labels live WITH the code.
KINDS = {
    "wind": {
        "label": "🌬 Wind",
        "claim": "comfort sound — plays quietly under the voice",
        "stereo": False,
    },
    "rain": {
        "label": "🌧 Rain",
        "claim": "comfort sound — plays quietly under the voice",
        "stereo": False,
    },
    "ocean": {
        "label": "🌊 Ocean",
        "claim": "comfort sound — plays quietly under the voice",
        "stereo": False,
    },
    "binaural": {
        "label": "🎧 Binaural 10 Hz",
        "claim": ("relaxation preference — NOT proven to improve "
                  "learning; needs headphones"),
        "stereo": True,
    },
}


# ── Pure synthesis ───────────────────────────────────────────────────


def _crossfade_loop(buf: array.array, n: int) -> array.array:
    """Blend the last ``n`` samples into the first ``n`` so the loop
    seam is inaudible. Pure; returns a new array of len(buf) - n."""
    n = min(n, len(buf) // 2)
    out = array.array("h", buf[:len(buf) - n])
    for i in range(n):
        w = i / n
        mixed = int(buf[len(buf) - n + i] * (1.0 - w) + buf[i] * w)
        out[i] = max(-32768, min(32767, mixed))
    return out


def _filtered_noise(samples: int, rng: random.Random, smooth: float,
                    amp: int) -> array.array:
    """One-pole low-passed white noise — the whoosh family. Higher
    ``smooth`` = deeper/windier; lower = hissier/rainier."""
    out = array.array("h", bytearray(2 * samples))
    y = 0.0
    gain = 1.0 + 3.0 * smooth          # make up the level the filter eats
    for i in range(samples):
        x = rng.uniform(-1.0, 1.0)
        y = smooth * y + (1.0 - smooth) * x
        out[i] = max(-32768, min(32767, int(y * amp * gain)))
    return out


def synth_wind(seconds: float = 4.0, rng: random.Random | None = None,
               amp: int = _AMP) -> tuple[array.array, int]:
    """Deep filtered noise. Returns (mono loop, channels=1)."""
    rng = rng or random.Random()
    buf = _filtered_noise(int(RATE * seconds), rng, smooth=0.97, amp=amp)
    return _crossfade_loop(buf, RATE // 4), 1


def synth_rain(seconds: float = 4.0, rng: random.Random | None = None,
               amp: int = _AMP) -> tuple[array.array, int]:
    """Light filtered noise — steady patter. (mono loop, 1)."""
    rng = rng or random.Random()
    buf = _filtered_noise(int(RATE * seconds), rng, smooth=0.55, amp=amp)
    return _crossfade_loop(buf, RATE // 4), 1


def synth_ocean(seconds: float = 8.0, rng: random.Random | None = None,
                amp: int = _AMP) -> tuple[array.array, int]:
    """Filtered noise under a slow whole-cycle swell envelope, so the
    loop's envelope seam is exact. (mono loop, 1)."""
    rng = rng or random.Random()
    samples = int(RATE * seconds)
    noise = _filtered_noise(samples, rng, smooth=0.92, amp=amp)
    out = array.array("h", bytearray(2 * samples))
    for i in range(samples):
        swell = 0.45 + 0.55 * (0.5 - 0.5 * math.cos(
            2.0 * math.pi * i / samples))       # one full swell per loop
        out[i] = int(noise[i] * swell)
    return _crossfade_loop(out, RATE // 4), 1


def synth_binaural(seconds: float = 1.0, base_hz: int = 200,
                   beat_hz: int = 10,
                   amp: int = 6000) -> tuple[array.array, int]:
    """Left ear ``base_hz``, right ear ``base_hz + beat_hz`` — whole
    cycles per loop for both ears, so the seam is silent. Interleaved
    stereo (L,R,L,R…). Returns (stereo loop, channels=2).

    Honest label lives in KINDS['binaural']: relaxation preference,
    NOT proven to improve learning."""
    samples = int(RATE * seconds)
    out = array.array("h", bytearray(2 * samples * 2))
    for i in range(samples):
        t = i / RATE
        out[2 * i] = int(amp * math.sin(2.0 * math.pi * base_hz * t))
        out[2 * i + 1] = int(
            amp * math.sin(2.0 * math.pi * (base_hz + beat_hz) * t))
    return out, 2


_SYNTHS = {
    "wind": synth_wind,
    "rain": synth_rain,
    "ocean": synth_ocean,
    "binaural": synth_binaural,
}


def build_loop(kind: str,
               rng: random.Random | None = None) -> tuple[array.array, int]:
    """One seamless loop for ``kind``. Raises ValueError on unknown kind."""
    if kind not in _SYNTHS:
        raise ValueError(f"unknown ambience kind {kind!r}; "
                         f"one of {sorted(_SYNTHS)}")
    if kind == "binaural":
        return synth_binaural()
    return _SYNTHS[kind](rng=rng)


# ── Player (the I/O this module owns) ───────────────────────────────


class AmbiencePlayer:
    """Loops one ambience bed on its own output stream, quietly, next
    to (never instead of) the TTS voice. Windows mixes the streams.
    Degrades gracefully: missing sounddevice/numpy raises
    AmbienceUnavailableError from start(); stop() is always safe."""

    def __init__(self):
        self._stream = None
        self.kind: str | None = None
        self.volume: float = 0.0

    @property
    def playing(self) -> bool:
        return self._stream is not None

    def start(self, kind: str, volume: float = 0.25,
              rng: random.Random | None = None) -> None:
        try:
            import numpy as np
            import sounddevice as sd
        except Exception as e:
            raise AmbienceUnavailableError(
                f"ambience needs sounddevice + numpy: {e}") from e
        self.stop()
        volume = max(0.0, min(1.0, float(volume)))
        buf, channels = build_loop(kind, rng=rng)
        data = (np.frombuffer(buf.tobytes(), dtype=np.int16)
                .astype(np.float32) / 32768.0) * volume
        frames_total = len(data) // channels
        data = data.reshape(frames_total, channels)
        pos = {"i": 0}

        def _callback(outdata, frames, _time, _status):
            i = pos["i"]
            take = 0
            while take < frames:
                n = min(frames - take, frames_total - i)
                outdata[take:take + n] = data[i:i + n]
                take += n
                i = (i + n) % frames_total
            pos["i"] = i

        self._stream = sd.OutputStream(
            samplerate=RATE, channels=channels, dtype="float32",
            callback=_callback)
        self._stream.start()
        self.kind = kind
        self.volume = volume

    def stop(self) -> None:
        stream, self._stream = self._stream, None
        self.kind = None
        self.volume = 0.0
        if stream is not None:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass
