"""lyceum/prompt_archive.py — Prompt Library archive rendering (functional core).

Owner QA find (2026-07-20): the Prompt Library's red lamp hard-deleted
entries ("This can't be undone") — a direct violation of the design law
*files archive, never delete*. The repair mirrors the Library's Books
Archive workflow: an archived entry is written out as a plain Markdown
file with YAML front-matter (the same shape saved excerpts use) into a
"Prompt Archive" folder that sits on the OneDrive-synced Desktop, so the
local file IS the cloud backup — same honesty as Bill Sentinel: the app
doesn't run a cloud service, OneDrive's own sync does the carrying.

This module is the pure part: given an entry's fields, produce the
Markdown text and a filesystem-safe filename. No Tkinter, no I/O,
deterministic — the shell decides where the file goes and writes it.
"""

from __future__ import annotations

import re

# Characters Windows forbids in filenames, plus control chars.
_UNSAFE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_DASH_RUNS = re.compile(r"-{2,}")


def safe_slug(title: str, max_len: int = 40) -> str:
    """A filesystem-safe slug of an entry title.

    Unsafe characters and whitespace become dashes, runs collapse, and
    the result is trimmed to ``max_len``. An empty or all-unsafe title
    falls back to ``"untitled"`` so the filename never goes blank.
    """
    slug = _UNSAFE.sub("-", (title or "").strip())
    slug = re.sub(r"\s+", "-", slug)
    slug = _DASH_RUNS.sub("-", slug).strip("-")
    slug = slug[:max_len].rstrip("-")
    return slug or "untitled"


def archive_filename(entry_id: int, title: str, archived_at: str) -> str:
    """The archive file's name: id + title slug + timestamp, .md.

    The id keeps names unique even for identical titles; the timestamp
    (colons made safe) records when it left the active list.
    """
    stamp = _UNSAFE.sub("-", (archived_at or "").strip()) or "unknown-time"
    return f"PROMPTLIB-{int(entry_id):04d}_{safe_slug(title)}_{stamp}.md"


def entry_to_markdown(entry: dict) -> str:
    """Render one Prompt Library row as Markdown with YAML front-matter.

    ``entry`` carries id, title, prompt, response, source, created_at,
    archived_at (missing keys degrade to empty strings — an archive
    must never refuse to write because a field is blank).
    """
    get = lambda k: str(entry.get(k) or "").strip()
    title = get("title") or "(untitled)"
    prompt = get("prompt")
    response = get("response")
    word_count = len(prompt.split()) + len(response.split())
    lines = [
        "---",
        f"doc_id:      PROMPTLIB-{int(entry.get('id') or 0):04d}",
        f"title:       {title!r}",
        f"source:      {get('source')!r}",
        f"created_at:  {get('created_at')}",
        f"archived_at: {get('archived_at')}",
        f"word_count:  {word_count}",
        "---",
        "",
        f"# {title}",
        "",
        "## Prompt (the owner's message)",
        "",
        prompt,
        "",
        "## Response (the reply)",
        "",
        response,
        "",
    ]
    return "\n".join(lines)
