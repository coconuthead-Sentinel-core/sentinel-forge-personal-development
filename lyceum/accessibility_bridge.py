"""Screen-reader announcement bridge — speak through the user's running NVDA.

For users who already run NVDA, this lets the app push dynamic text to their
screen reader. LICENSE-SAFE PATTERN: we do NOT bundle or ship NVDA's controller
DLL (it is GPL/copyleft). We only ``LoadLibrary`` it if it is ALREADY present on
the user's machine and NVDA is running — i.e. we talk to their installed reader
by IPC and ship zero copyleft code. Everywhere else this is a safe no-op.

Returns booleans, never raises. Verify NV Access's controller-client terms before
relying on this in a distributed build.
"""
from __future__ import annotations

import ctypes
import sys

# 64-bit first, then 32-bit; loaded only if present on the system PATH.
_DLL_CANDIDATES = ("nvdaControllerClient64.dll", "nvdaControllerClient32.dll")


def _load():
    for name in _DLL_CANDIDATES:
        try:
            dll = ctypes.windll.LoadLibrary(name)
            # const wchar_t* — declare so a Python str is passed as a wide string.
            dll.nvdaController_speakText.argtypes = [ctypes.c_wchar_p]
            return dll
        except (OSError, AttributeError):
            continue
    return None


def is_available() -> bool:
    """True only if the NVDA controller DLL loads AND NVDA is running."""
    if not sys.platform.startswith("win"):
        return False
    dll = _load()
    if dll is None:
        return False
    try:
        return dll.nvdaController_testIfRunning() == 0   # 0 == running
    except Exception:
        return False


def announce(text: str) -> bool:
    """Speak ``text`` through the user's running NVDA. Returns True on success,
    False (safely) if NVDA isn't installed/running or on any error."""
    if not text or not sys.platform.startswith("win"):
        return False
    dll = _load()
    if dll is None:
        return False
    try:
        if dll.nvdaController_testIfRunning() != 0:
            return False
        return dll.nvdaController_speakText(str(text)) == 0
    except Exception:
        return False
