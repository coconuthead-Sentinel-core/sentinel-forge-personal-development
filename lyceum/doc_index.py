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
try:
    import openpyxl as _openpyxl
except Exception:
    _openpyxl = None

SUPPORTED = (".md", ".txt", ".docx", ".pdf", ".html", ".htm",
             ".xlsx", ".xlsm", ".csv")

# Spreadsheets can be enormous; the assistant needs the content, not a
# million empty rows. Per-sheet row cap keeps extraction fast and sane.
_XLSX_MAX_ROWS = 1500


def _extract_xlsx(path: str) -> str:
    """Spreadsheet → readable text: 'Sheet: <name>' header, then one line
    per row with cells joined by ' | '. data_only=True returns the last
    CALCULATED value for formula cells (what the user sees in Excel)."""
    wb = _openpyxl.load_workbook(path, read_only=True, data_only=True)
    parts = []
    try:
        for ws in wb.worksheets:
            lines = [f"Sheet: {ws.title}"]
            for i, row in enumerate(ws.iter_rows(values_only=True)):
                if i >= _XLSX_MAX_ROWS:
                    lines.append(f"... (first {_XLSX_MAX_ROWS} rows shown)")
                    break
                cells = [str(c).strip() for c in row
                         if c is not None and str(c).strip()]
                if cells:
                    lines.append(" | ".join(cells))
            if len(lines) > 1:
                parts.append("\n".join(lines))
    finally:
        try:
            wb.close()
        except Exception:
            pass
    return "\n\n".join(parts)


def extract_text(path: str) -> str:
    """Best-effort plain text from a file. "" on any failure / unsupported type."""
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext in (".md", ".txt", ".csv"):
            with open(path, encoding="utf-8", errors="replace") as f:
                return f.read()
        if ext in (".xlsx", ".xlsm") and _openpyxl is not None:
            return _extract_xlsx(path)
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


def cache_dir() -> str:
    """Where the library index cache lives. Resolution order:
      1. SENTINEL_FORGE_INDEX_DIR (explicit override),
      2. the roomy E: offload drive if present (keeps the small C: SSD clear),
      3. %LOCALAPPDATA% fallback.
    Because the 85 MB cache shouldn't sit on a near-full C:, it auto-moves to E:
    as soon as E: is connected.
    """
    override = os.environ.get("SENTINEL_FORGE_INDEX_DIR")
    if override:
        return override
    if os.path.isdir("E:\\"):
        return os.path.join("E:\\", "SentinelForge")
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
    return os.path.join(base, "SentinelForge")


def cache_path() -> str:
    return os.path.join(cache_dir(), "library_index.json")


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


# ---- Broad-folder indexing (☁ OneDrive) -----------------------------------
# Same cached-extraction idea as build_index, but walked with directory
# exclusions (a user folder tree contains git repos, caches, and vendored
# binaries that must never be indexed) and labeled with RELATIVE paths so
# the assistant can say WHERE it found something.

EXCLUDE_DIRS = {".git", "__pycache__", ".claude", "node_modules", "tts",
                "dist", "build", ".venv", "venv", "site-packages"}


def iter_supported_files(root: str, exclude_dirs=EXCLUDE_DIRS):
    """Yield supported files under ``root``, pruning excluded / dot dirs."""
    for dirpath, dirnames, filenames in os.walk(root or ""):
        dirnames[:] = [d for d in dirnames
                       if d.lower() not in exclude_dirs
                       and not d.startswith(".")]
        for fn in filenames:
            if fn.lower().endswith(SUPPORTED):
                yield os.path.join(dirpath, fn)


def build_index_over(root: str, cache_file: str, max_files: int = 4000,
                     exclude_dirs=EXCLUDE_DIRS):
    """Return [(relative_path, text), ...] for supported files under ``root``,
    using the same path+mtime extraction cache pattern as build_index but
    persisted to its own ``cache_file``. Safe/defensive: never raises."""
    try:
        with open(cache_file, encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        cache = {}

    files = []
    for fp in iter_supported_files(root, exclude_dirs):
        files.append(fp)
        if len(files) >= max_files:
            break

    out, new_cache, changed = [], {}, False
    for fp in files:
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
            try:
                label = os.path.relpath(fp, root)
            except ValueError:
                label = os.path.basename(fp)
            out.append((label, text))

    if changed or len(new_cache) != len(cache):
        try:
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(new_cache, f)
        except OSError:
            pass
    return out
