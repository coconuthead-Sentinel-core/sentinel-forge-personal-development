"""Windows-native TTS via SAPI5 (COM) — a voice for the onboard assistant.

Lets the assistant speak through the OS's built-in voices with zero model
download, using the Windows Speech API directly over COM. Pure optional
dependency: if pywin32 isn't installed the wrapper is simply ``available=False``
and every method is a safe no-op, so the app runs unchanged.

NOTE: the app's reading feature uses Piper; this is specifically a lightweight
TTS path for the AI assistant (and a fallback). Async speech uses SAPI flag 1
(SVSFlagsAsync) so it never blocks the UI thread.
"""
from __future__ import annotations

# Optional dependency — guarded at the IMPORT (a missing pywin32 raises here,
# not at Dispatch; the reply that inspired this had that guard misplaced).
try:
    import win32com.client as _w32
    _IMPORT_ERROR = None
except Exception as e:                 # pragma: no cover - platform dependent
    _w32 = None
    _IMPORT_ERROR = str(e)

_SVSF_ASYNC = 1                        # SpeechVoiceSpeakFlags.SVSFlagsAsync


class NativeTTS:
    """Thin, defensive wrapper over SAPI.SpVoice."""

    def __init__(self):
        self.available = False
        self.engine = None
        self.last_error = _IMPORT_ERROR
        if _w32 is None:
            return
        try:
            self.engine = _w32.Dispatch("SAPI.SpVoice")
            self.available = True
        except Exception as e:         # com_error etc. — NOT ImportError
            self.last_error = f"{type(e).__name__}: {e}"

    def speak(self, text: str, rate: int = 0, async_mode: bool = True) -> bool:
        """Speak text. rate in [-10, 10]. Returns True if dispatched."""
        if not self.available or not text:
            return False
        try:
            self.engine.Rate = max(-10, min(10, int(rate)))
            self.engine.Speak(str(text), _SVSF_ASYNC if async_mode else 0)
            return True
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            return False

    def stop(self) -> None:
        """Cut off async speech (speak empty text with the purge flag)."""
        if not self.available:
            return
        try:
            self.engine.Speak("", 2)   # SVSFPurgeBeforeSpeak
        except Exception:
            pass

    def voices(self) -> list[str]:
        if not self.available:
            return []
        try:
            return [v.GetDescription() for v in self.engine.GetVoices()]
        except Exception:
            return []
