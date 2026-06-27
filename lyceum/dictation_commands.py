"""Spoken dictation commands — hands-free punctuation, formatting, and caps.

Pure, UI-free helper for the speech-to-text (Whisper) input path. A person who
cannot type dictates *everything*, including punctuation and line breaks — but a
raw transcript leaves the spoken word "period" as the literal word, not ".".
This converts the universal spoken-dictation conventions into the characters
they name, so the user can punctuate, start new lines, and capitalize entirely
by voice. That is a core accessibility capability for the app's audience.

These are long-established, general dictation conventions and the outputs are
plain characters — nothing here is taken from any product's manual. The function
is pure and defensive: it never raises (returns the input unchanged on any
error), so it can never break a dictation session. It is applied AFTER the Voice
Memory corrections, at the same seam in _append_dictation.

NOT handled here (on purpose):
  * "scratch that" / "select x" — stateful editing that needs the text widget,
    not a pure string transform; a separate, carefully-scoped task.
  * NATO/phonetic-alphabet spelling ("alpha bravo" -> "AB") — too ambiguous in
    free dictation (e.g. the name "Victor"); belongs in the Spelling Helper as
    an explicit mode, so it would not corrupt ordinary speech.
"""
from __future__ import annotations

# Two-word spoken forms -> (output, kind). `kind` controls spacing:
#   "close" attaches to the preceding word ("word."), "open" attaches to the
#   following word ("$5", '"hi'), "break" is a line/tab control character.
_TWO_WORD = {
    ("question", "mark"): ("?", "close"),
    ("exclamation", "mark"): ("!", "close"),
    ("exclamation", "point"): ("!", "close"),
    ("full", "stop"): (".", "close"),
    ("open", "quote"): ('"', "open"),
    ("close", "quote"): ('"', "close"),
    ("open", "paren"): ("(", "open"),
    ("close", "paren"): (")", "close"),
    ("open", "parenthesis"): ("(", "open"),
    ("close", "parenthesis"): (")", "close"),
    ("dollar", "sign"): ("$", "open"),
    ("percent", "sign"): ("%", "close"),
    ("new", "line"): ("\n", "break"),
    ("new", "paragraph"): ("\n\n", "break"),
    ("tab", "key"): ("\t", "break"),
}
_ONE_WORD = {
    "period": (".", "close"),
    "comma": (",", "close"),
    "colon": (":", "close"),
    "semicolon": (";", "close"),
    "ellipsis": ("…", "close"),
}


def apply_dictation_commands(text: str) -> str:
    """Turn spoken punctuation/formatting/capitalization words into characters.

    Ordinary prose passes through unchanged; only the recognized command words
    are converted. Returns the input untouched on any unexpected error.
    """
    try:
        if not text:
            return text or ""
        words = text.split()
        out: list = []
        need_space = False
        cap_next = False
        caps_mode = None                     # None | "title" | "upper"

        def space_before():
            nonlocal need_space
            if need_space and out:
                out.append(" ")
            need_space = False

        i, n = 0, len(words)
        while i < n:
            lw = words[i].lower()
            two = tuple(w.lower() for w in words[i:i + 2])
            three = [w.lower() for w in words[i:i + 3]]

            # --- capitalization modes ---
            if three == ["all", "caps", "on"]:
                caps_mode = "upper"; i += 3; continue
            if three == ["all", "caps", "off"]:
                caps_mode = None; i += 3; continue
            if two == ("caps", "on"):
                caps_mode = "title"; i += 2; continue
            if two == ("caps", "off"):
                caps_mode = None; i += 2; continue
            if lw == "cap":
                cap_next = True; i += 1; continue

            # --- punctuation / formatting ---
            spec = _TWO_WORD.get(two) if len(two) == 2 else None
            step = 2
            if spec is None:
                spec = _ONE_WORD.get(lw)
                step = 1
            if spec is not None:
                sym, kind = spec
                if kind == "open":
                    space_before(); out.append(sym); need_space = False
                elif kind == "break":
                    out.append(sym); need_space = False
                else:                        # "close"
                    out.append(sym); need_space = True
                i += step
                continue

            # --- an ordinary word ---
            w = words[i]
            if cap_next:
                w = w[:1].upper() + w[1:]
                cap_next = False
            elif caps_mode == "title":
                w = w[:1].upper() + w[1:]
            elif caps_mode == "upper":
                w = w.upper()
            space_before(); out.append(w); need_space = True
            i += 1
        return "".join(out)
    except Exception:
        return text
