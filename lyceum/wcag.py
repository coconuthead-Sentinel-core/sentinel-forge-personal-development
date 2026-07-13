"""WCAG 2.x contrast kernel — the W3C relative-luminance and contrast-ratio
formulas, plus the AA thresholds.

Source of the math: W3C, *Web Content Accessibility Guidelines (WCAG) 2.1*,
"relative luminance" definition and Success Criterion 1.4.3 (Contrast,
Minimum): normal text >= 4.5:1, large text >= 3:1.

Pure functions — no Tk, no I/O. Used two ways:
  1. as a gate for any NEW color pair introduced in the UI, and
  2. by the palette audit, which reports failing existing pairs as
     FINDINGS for the owner (never a silent recolor of his app).
"""
from __future__ import annotations

AA_NORMAL = 4.5
AA_LARGE = 3.0


def _srgb_to_linear(channel_0_to_1: float) -> float:
    """One sRGB channel -> linear-light value (W3C piecewise formula)."""
    c = channel_0_to_1
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """Relative luminance of an sRGB hex color ('#rrggbb'), 0.0–1.0."""
    s = hex_color.strip().lstrip("#")
    if len(s) == 3:                      # allow #abc shorthand
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"not a hex color: {hex_color!r}")
    r = _srgb_to_linear(int(s[0:2], 16) / 255.0)
    g = _srgb_to_linear(int(s[2:4], 16) / 255.0)
    b = _srgb_to_linear(int(s[4:6], 16) / 255.0)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color_a: str, color_b: str) -> float:
    """WCAG contrast ratio between two colors, 1.0 (equal) to 21.0 (b/w).
    Symmetric: order does not matter."""
    la = relative_luminance(color_a)
    lb = relative_luminance(color_b)
    lighter, darker = max(la, lb), min(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def meets_aa(ratio: float, large: bool = False) -> bool:
    """WCAG 2.1 AA: >= 4.5:1 normal text, >= 3.0:1 large text."""
    return ratio >= (AA_LARGE if large else AA_NORMAL)


def audit_pairs(pairs: list[tuple[str, str, str, bool]]) -> list[dict]:
    """Audit (name, fg, bg, is_large) text pairs. Returns one dict per pair
    with the ratio and verdict — failures are FINDINGS for the owner."""
    out = []
    for name, fg, bg, large in pairs:
        ratio = contrast_ratio(fg, bg)
        out.append({"name": name, "fg": fg, "bg": bg, "large": large,
                    "ratio": round(ratio, 2),
                    "passes_aa": meets_aa(ratio, large)})
    return out
