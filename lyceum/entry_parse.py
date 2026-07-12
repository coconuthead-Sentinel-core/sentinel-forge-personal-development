"""lyceum/entry_parse.py — parse pasted study text into structured
entries (functional core).

The Study workspace lets the owner paste raw notes into a "main entry
section" and click Save. Two shapes are needed:

  * Glossary — many *term → definition* pairs in one paste. Real pastes
    come in several shapes (``Term: definition``, ``Term - definition``,
    ``Term<TAB>definition``, or a bare term line followed by its
    definition on the next line(s)). ``parse_glossary`` normalises all
    of them into ``[(term, definition), ...]``.

  * Topics / Commentary — a single free-form entry whose first line is
    the title and the remainder the body. ``split_title_body`` handles
    that.

Both are PURE: no I/O, no globals, deterministic. The Tk shell owns all
persistence; this module only reshapes text. That keeps the parsing
logic headless-testable (see tests/test_entry_parse.py).
"""

from __future__ import annotations

# Separators that mark a "term SEP definition" line, in priority order.
# Tab first (spreadsheet paste), then dashes padded with spaces (so a
# hyphenated word like "context-aware" is never mistaken for a break),
# then a colon followed by a space.
_INLINE_SEPS = ("\t", " — ", " – ", " - ", ": ")

# A bare ":" only counts as a separator when it sits near the start of
# the line, so a colon inside a definition ("due at 3:00") does not
# split it. Term side must be within this many characters.
_COLON_TERM_MAX = 40


def _split_on_separator(line: str):
    """Return ``(term, definition)`` if *line* looks like a term/definition
    pair, else ``None``. Splits on the first separator found (priority
    order); a lone colon only counts when the term side is short."""
    best = None  # (index, sep_len)
    for sep in _INLINE_SEPS:
        i = line.find(sep)
        if i > 0 and (best is None or i < best[0]):
            best = (i, len(sep))
    if best is None:
        i = line.find(":")
        if 0 < i <= _COLON_TERM_MAX:
            best = (i, 1)
    if best is None:
        return None
    i, n = best
    term = line[:i].strip()
    definition = line[i + n:].strip()
    if not term:
        return None
    return term, definition


def parse_glossary(text: str):
    """Parse pasted glossary text into ``[(term, definition), ...]``.

    Predictable, dominant-format-first rules:

    * A line containing an inline separator (``Term: definition`` /
      ``Term - definition`` / ``Term<TAB>definition``) is a complete
      entry on its own — the common one-per-line paste.
    * A bare line (no separator) starts a *term* whose definition is on
      the following line(s), up to a blank line or the next entry —
      the common "glossary webpage" shape (term, then its definition
      below).
    * A definition that wraps across lines continues only when the
      continuation line is *indented* (leading space/tab), the standard
      wrapped-text convention. This is what keeps a fresh un-indented
      term from being swallowed into the previous definition.

    Terms with no definition are dropped. Order is preserved; nothing is
    deduplicated (the caller decides how to merge with existing rows)."""
    pairs = []
    cur_term = None
    cur_def = []
    awaiting = False   # a bare term is still waiting for its definition

    def flush():
        nonlocal cur_term, cur_def, awaiting
        if cur_term:
            definition = " ".join(p for p in cur_def if p).strip()
            if definition:
                pairs.append((cur_term, definition))
        cur_term = None
        cur_def = []
        awaiting = False

    for raw in (text or "").splitlines():
        if not raw.strip():
            flush()
            continue
        indented = raw[:1] in (" ", "\t")
        split = _split_on_separator(raw)
        if split is not None:
            flush()
            cur_term, definition = split[0], split[1]
            cur_def = [definition] if definition else []
            awaiting = not definition
        elif indented and cur_term is not None:
            cur_def.append(raw.strip())          # wrapped continuation
        elif awaiting:
            cur_def.append(raw.strip())          # definition of a bare term
            awaiting = False
        else:
            flush()
            cur_term = raw.strip()               # a new bare term
            cur_def = []
            awaiting = True
    flush()
    return pairs


def split_title_body(text: str):
    """Split a free-form entry into ``(title, body)``.

    First non-blank line is the title (trimmed to a sane length); the
    remainder is the body. If there is only one line, it is both the
    title and the body. Returns ``("", "")`` for empty input."""
    text = (text or "").strip()
    if not text:
        return "", ""
    lines = text.splitlines()
    # Find the first non-blank line as the title.
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    title = lines[idx].strip() if idx < len(lines) else ""
    if len(title) > 120:
        title = title[:117].rstrip() + "…"
    body = "\n".join(lines[idx + 1:]).strip()
    if not body:
        body = title
    return title, body
