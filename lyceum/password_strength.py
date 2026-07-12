"""lyceum/password_strength.py — password/passphrase strength via
Shannon entropy (functional core).

Reviewed from *Microsoft 365 Certified: Fundamentals (MS-900)* — the
identity-and-security material — and proven in pseudocode before this
module was written (3 proofs / 20 checks — see
docs/wiki/Review-M365Certified.md).

The canonical CS foundation under "password strength" is SHANNON
ENTROPY (Claude Shannon, 1948): the number of BITS of information in a
string. It is the most universally-taught algorithm in the field —
strictly academic, recognized on every university campus. This module
computes two textbook entropy estimates and takes the attacker-
favorable minimum:

  1. Search-space bits  = len * log2(charset_size)   (brute-force view)
  2. Shannon bits       = ( -Σ p(c)*log2 p(c) ) * len   (information
     content — penalizes low-diversity strings like "aaaaaaaa")

PRIVACY / SAFETY (load-bearing): this is a PURE function. It performs NO
storage, NO network, NO logging. It analyzes a candidate string locally
and returns a score — it NEVER authenticates anywhere and NEVER persists
the input. That is the standard strength-meter design (e.g. zxcvbn) and
it matches this app's local-first, nothing-leaves-the-laptop ethos.

Public API:
    strength(s) -> {bits, band, crack_time, length, charset_size,
                    common, tips}
    charset_size / search_space_bits / shannon_bits / band_for
"""

from __future__ import annotations

import math
from collections import Counter

_LOWER = set("abcdefghijklmnopqrstuvwxyz")
_UPPER = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_DIGIT = set("0123456789")

# A small illustrative common-password set — membership => heavy
# penalty. A production build could ship a larger list; the point here
# is the algorithm, not the corpus.
_COMMON = {
    "password", "password1", "123456", "12345678", "123456789",
    "qwerty", "qwerty123", "letmein", "admin", "welcome", "monkey",
    "111111", "000000", "iloveyou", "abc123", "dragon", "sunshine",
    "princess", "football", "changeme", "passw0rd",
}


def charset_size(s: str) -> int:
    """Size of the brute-force alphabet implied by the character classes
    present in ``s`` (lower 26 + upper 26 + digit 10 + symbol ~32)."""
    chars = set(s)
    size = 0
    if chars & _LOWER:
        size += 26
    if chars & _UPPER:
        size += 26
    if chars & _DIGIT:
        size += 10
    if any(c not in _LOWER and c not in _UPPER and c not in _DIGIT
           for c in chars):
        size += 32
    return size


def search_space_bits(s: str) -> float:
    """Brute-force entropy: len * log2(charset_size). 0 for empty/one-class."""
    n = charset_size(s)
    if not s or n <= 1:
        return 0.0
    return len(s) * math.log2(n)


def shannon_bits(s: str) -> float:
    """Shannon entropy of the actual character distribution scaled by
    length: H = -Σ p(c)*log2 p(c); total = H * len. Zero for a single
    repeated character."""
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    h = -sum((c / n) * math.log2(c / n) for c in counts.values())
    return h * n


def band_for(bits: float) -> str:
    """Plain-language strength band for a bit-count."""
    if bits < 28:
        return "Very weak"
    if bits < 36:
        return "Weak"
    if bits < 60:
        return "Reasonable"
    if bits < 128:
        return "Strong"
    return "Very strong"


def _crack_time(bits: float) -> str:
    """Rough human label for offline guessing at ~1e10 guesses/second
    (expected = half the search space)."""
    if bits <= 0:
        return "instant"
    seconds = (2 ** min(bits, 200)) / 1e10 / 2
    if seconds < 1:
        return "instant"
    for name, step in (("seconds", 60), ("minutes", 60), ("hours", 24),
                       ("days", 365), ("years", 1000)):
        if seconds < step:
            return f"~{seconds:.0f} {name}"
        seconds /= step
    return "centuries+"


def strength(s: str) -> dict:
    """Estimate password/passphrase strength. Pure, local, no storage.

    Returns a dict:
        bits          float   information bits (attacker-favorable min)
        band          str     "Very weak" … "Very strong"
        crack_time    str     rough offline-guessing label
        length        int
        charset_size  int
        common        bool    is a well-known password
        tips          [str]   actionable guidance
    """
    s = s or ""
    if not s:
        return {"bits": 0.0, "band": "Very weak", "crack_time": "instant",
                "length": 0, "charset_size": 0, "common": False,
                "tips": ["Enter a password to analyze."]}
    bits = min(search_space_bits(s), shannon_bits(s))
    common = s.lower() in _COMMON
    if common:
        bits = min(bits, 8.0)          # a known password is effectively free
    tips = []
    if len(s) < 12:
        tips.append("Use at least 12 characters — length matters most.")
    if charset_size(s) < 62:
        tips.append("Mix upper- and lower-case, digits, and symbols.")
    if common:
        tips.append("This is a well-known password — choose something unique.")
    if len(set(s)) < max(1, len(s) // 2):
        tips.append("Avoid repeated characters.")
    if not tips:
        tips.append("Strong — a passphrase of several random words is "
                    "even better.")
    return {"bits": round(bits, 1) or 0.0, "band": band_for(bits),
            "crack_time": _crack_time(bits), "length": len(s),
            "charset_size": charset_size(s), "common": common,
            "tips": tips}
