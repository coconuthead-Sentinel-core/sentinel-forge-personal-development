"""Library document indexer — make the user's whole Books tree searchable.

The Library holds hundreds of source books as .docx/.pdf, which the RAG can't read
without extraction. Extracting them on every question would be far too slow, so we
build a CACHED index: each file's text is extracted once and stored keyed by path
+ modification time; subsequent runs reuse the cache and only re-extract changed
files. The app builds this in a background thread at startup.

All extractors are optional-dependency-guarded (python-docx / pypdf / bs4 are
already app dependencies); a missing one simply means that format contributes
nothing. Nothing here raises — failures degrade to empty text.
"""
from __future__ import annotations

import glob
import json
import os
import re

try:
    import docx as _docx            # python-docx
except Exception:
    _docx = None
try:
    import pypdf as _pypdf
except Exception:
    _pypdf = None
try:
    from bs4 import BeautifulSoup as _BS
except Exception:
    _BS = None

SUPPORTED = (".md", ".txt", ".docx", ".pdf", ".html", ".htm")


def extract_text(path: str) -> str:
    """Best-effort plain text from a file. "" on any failure / unsupported type."""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in (".md", ".txt"):
            with open(path, encoding="utf-8", errors="replace") as f:
                return f.read()
        if ext == ".docx" and _docx is not None:
            return "\n".join(p.text for p in _docx.Document(path).paragraphs)
        if ext == ".pdf" and _pypdf is not None:
            reader = _pypdf.PdfReader(path)
            return "\n".join((pg.extract_text() or "") for pg in reader.pages)
        if ext in (".html", ".htm"):
            with open(path, encoding="utf-8", errors="replace") as f:
                raw = f.read()
            return _BS(raw, "html.parser").get_text(" ") if _BS \
                else re.sub(r"<[^>]+>", " ", raw)
    except Exception:
        return ""
    return ""


def cache_path() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    return os.path.join(base, "SentinelForge", "library_index.json")


def build_index(books_dir: str, path: str | None = None, max_files: int = 4000):
    """Return [(filename, text), ...] for every supported file under books_dir,
    extracting via a path+mtime cache so unchanged files are never re-read.

    Persists the cache to ``path`` (default: %LOCALAPPDATA%). Safe/defensive.
    """
    path = path or cache_path()
    try:
        with open(path, encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        cache = {}

    files = []
    for ext in SUPPORTED:
        files.extend(glob.glob(os.path.join(books_dir or "", "**", "*" + ext),
                               recursive=True))

    out, new_cache, changed = [], {}, False
    for fp in files[:max_files]:
        try:
            mtime = os.path.getmtime(fp)
        except OSError:
            continue
        ent = cache.get(fp)
        if ent and ent.get("mtime") == mtime and "text" in ent:
            text = ent["text"]                      # cache hit
        else:
            text = extract_text(fp) or ""           # extract + remember
            changed = True
        new_cache[fp] = {"mtime": mtime, "text": text}
        if text.strip():
            out.append((os.path.basename(fp), text))

    if changed or len(new_cache) != len(cache):
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(new_cache, f)
        except OSError:
            pass
    return out
