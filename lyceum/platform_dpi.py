"""High-DPI awareness for Windows — call BEFORE the Tk root is created.

Tkinter never declares DPI awareness, so on a scaled display Windows renders the
app at the legacy 96-DPI standard and then bitmap-stretches the result, producing
blurry text and fuzzy borders. Declaring awareness makes Windows hand the app the
true physical pixel grid so text renders crisply — which directly serves this
app's neurodivergent-first legibility goal.

CRITICAL ORDERING: this must run before ``tk.Tk()``. Once the window manager has
bound the process to the desktop, the awareness context is locked for the session
and later calls are ignored.

Defensive by design: non-Windows platforms and any missing/locked API are handled
silently; the function returns a short status string and never raises.

NOTE for maintainers: enabling awareness means Tk geometry requests are now in
TRUE physical pixels. Window sizing in this app is overwhelmingly expressed as a
fraction of ``winfo_screenwidth/height`` (DPI-independent), so it scales safely;
any remaining FIXED-pixel widget sizes may appear smaller on a scaled display and
should be spot-checked during visual QA.
"""
from __future__ import annotations

import sys


def enable_high_dpi_awareness() -> str:
    """Declare DPI awareness to Windows. Returns a short status string.

    Tries, strongest first: Per-Monitor-v2 → Per-Monitor → System-DPI, so it
    works across Windows 8.1 through 11. No-op (and safe) on other platforms.
    """
    if not sys.platform.startswith("win"):
        return "skipped: non-windows"
    try:
        import ctypes
    except Exception:
        return "unavailable: no ctypes"

    # 1) Per-Monitor v2 (Windows 10 1703+): best — re-scales when moved between
    #    monitors of differing density. DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4.
    try:
        if ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)):
            return "per-monitor-v2"
    except Exception:
        pass
    # 2) Per-Monitor aware (Windows 8.1+).
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        return "per-monitor"
    except Exception:
        pass
    # 3) System-DPI aware (legacy fallback).
    try:
        ctypes.windll.user32.SetProcessDPIAware()
        return "system"
    except Exception:
        return "unavailable"
