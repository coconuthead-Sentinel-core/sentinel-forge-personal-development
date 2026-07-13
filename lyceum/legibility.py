"""lyceum/legibility.py — accessibility text-formatting kernel
(functional core).

Turns an accessibility *preset* + the reader's chosen base size into a
concrete formatting spec the Tk shell applies to the Study read-panes
(Topics / Commentary / Glossary) and their paste boxes. Proven in
pseudocode before wiring (3 proofs / 14 checks — see
scratchpad/prove_legibility.py, mirrored in tests/test_legibility.py).

Evidence base (the presets are not arbitrary):
  * Rello & Baeza-Yates, "Good Fonts for Dyslexia" (ACM ASSETS 2013):
    plain sans-serif faces at a larger size with increased spacing
    measurably improve dyslexic reading; OpenDyslexic is the owner's
    stated preference and is demoted-to-fallback only when absent.
    Later controlled studies found NO objective reading benefit for
    specialized dyslexia fonts over spacing-matched standard fonts —
    Wery & Diliberto (Annals of Dyslexia, 2017, OpenDyslexic) and
    Kuster et al. (Annals of Dyslexia, 2017, Dyslexie) — so the size
    and spacing levers below carry the evidence; the font choice is
    honored as personal comfort, which is its own valid outcome.
  * British Dyslexia Association *Dyslexia Style Guide* (2023): 12–14pt
    minimum, 1.5× line spacing, avoid dense blocks — encoded as
    line-leading (Tk ``spacing1``/``spacing3``) and ``wrap=word``.
  * ADHD reading guidance (CHADD; Nielsen Norman Group): reducing
    visual crowding via generous leading lowers re-read load.

PURE: no tkinter import, no I/O, no globals. It takes the set of
installed font families as an argument (the shell reads that from
``tkfont.families()`` once and passes it in), so the whole thing is
deterministic and headless-testable. The shell owns every ``configure``
call; this module only computes what to apply.

Public API:
    legibility_spec(preset, base_size, installed) -> spec dict
    clamp_size(n) -> int              # [MIN_SIZE, MAX_SIZE]
    step_size(n, direction) -> int    # A- / A+ helper
    preset_names() -> [str]           # dropdown order
    MIN_SIZE, MAX_SIZE
"""

from __future__ import annotations

# Text size bounds. 12pt is the BDA minimum; 32pt keeps a definition
# pane usable without a single word filling the widget.
MIN_SIZE = 12
MAX_SIZE = 32
SIZE_STEP = 2          # one A-/A+ press

# Universal fallback present on every Windows install — the last resort
# when none of a preset's preferred faces are installed.
_UNIVERSAL_FALLBACK = "Segoe UI"

# preset -> (family candidates in priority order, size delta, line-leading
# in points). ``lead`` becomes both spacing1 (above a line) and spacing3
# (below wrapped display lines), i.e. symmetric extra leading.
_PRESETS = {
    "Default":      {"families": ["Segoe UI"],                     "delta": 0, "lead": 2},
    "OpenDyslexic": {"families": ["OpenDyslexic", "OpenDyslexic3",
                                   "Comic Sans MS", "Verdana"],     "delta": 2, "lead": 6},
    "Dyslexia":     {"families": ["Verdana", "Tahoma", "Arial"],   "delta": 2, "lead": 6},
    "ADHD focus":   {"families": ["Verdana", "Segoe UI"],          "delta": 1, "lead": 8},
    "Dysgraphia":   {"families": ["Comic Sans MS", "Verdana"],     "delta": 3, "lead": 7},
}

_SPEC_KEYS = frozenset({"family", "size", "spacing1", "spacing3", "wrap"})


def clamp_size(n) -> int:
    """Clamp any number into the legible size window [MIN_SIZE, MAX_SIZE]."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = MIN_SIZE
    return max(MIN_SIZE, min(MAX_SIZE, n))


def step_size(n, direction) -> int:
    """A- / A+ helper: move ``n`` one step (``direction`` <0 shrinks,
    >0 grows) and clamp. Zero leaves it unchanged (but clamped)."""
    if direction < 0:
        n = int(n) - SIZE_STEP
    elif direction > 0:
        n = int(n) + SIZE_STEP
    return clamp_size(n)


def first_installed(candidates, installed) -> str:
    """First family in ``candidates`` that is in ``installed``; else the
    universal fallback."""
    for fam in candidates:
        if fam in installed:
            return fam
    return _UNIVERSAL_FALLBACK


def preset_names():
    """Preset labels in dropdown order (Default first)."""
    return list(_PRESETS.keys())


def legibility_spec(preset, base_size, installed) -> dict:
    """Pure: (preset name, base size, set-of-installed-families) -> spec.

    Returns ``{family, size, spacing1, spacing3, wrap}``. An unknown
    preset degrades to Default. ``size`` = clamp(base_size + delta). The
    family is the first installed candidate, else Segoe UI."""
    p = _PRESETS.get(preset, _PRESETS["Default"])
    size = clamp_size(int(base_size) + p["delta"])
    return {
        "family": first_installed(p["families"], installed),
        "size": size,
        "spacing1": p["lead"],
        "spacing3": p["lead"],
        "wrap": "word",
    }
