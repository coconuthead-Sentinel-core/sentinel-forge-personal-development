"""Local retrieval (RAG) — ground the onboard assistant in the user's OWN corpus.

The onboard LLM has a tiny context window, so it cannot "read all 300+ Library
files at once". Instead, for each question we rank the user's Library excerpts
(.md files) and study.db rows (notes, glossary, journal, topics) by relevance and
return only the top few as a context string, which the chat handler passes to
``LocalBrain.ask(query, context=...)`` — the same seam the web search uses.

Read-only and defensive: it never writes the user's files and returns an empty
string on any failure, so a retrieval hiccup can't break a chat. The ranking is a
pure function (``rank_snippets``) so it is unit-testable without files or a DB.
"""
from __future__ import annotations

import glob
import os
import re

from lyceum.db import study_db

_WORD = re.compile(r"[a-z0-9]+")


def _terms(query: str) -> list[str]:
    """Content words from the query (drop short stop-ish tokens)."""
    return [w for w in _WORD.findall((query or "").lower()) if len(w) > 2]


def score(text: str, terms: list[str]) -> int:
    """How many term occurrences appear in text. Pure."""
    if not terms:
        return 0
    t = (text or "").lower()
    return sum(t.count(w) for w in terms)


def rank_snippets(query, documents, limit: int = 5, max_chars: int = 1500):
    """Rank (source_label, text) documents against the query.

    Pure: returns the top ``limit`` matches as a list of (source_label, snippet),
    snippet truncated to ``max_chars``. Documents scoring 0 are dropped. This is
    the testable core — no file or database access here.
    """
    terms = _terms(query)
    if not terms:
        return []
    scored = []
    for src, text in documents:
        s = score(text, terms)
        if s > 0:
            scored.append((s, src, (text or "")[:max_chars]))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(src, snip) for _, src, snip in scored[:limit]]


def chunk_text(text: str, chunk_chars: int = 1200, overlap: int = 150):
    """Split text into overlapping chunks for retrieval. Pure.

    Overlap keeps a sentence that straddles a boundary from being lost. A short
    text returns a single chunk; empty/whitespace returns []. This is what lets a
    whole book be searched a passage at a time instead of truncated.
    """
    text = text or ""
    if not text.strip():
        return []
    if len(text) <= chunk_chars:
        return [text]
    step = max(1, chunk_chars - overlap)
    chunks = []
    for start in range(0, len(text), step):
        piece = text[start:start + chunk_chars]
        if piece.strip():
            chunks.append(piece)
        if start + chunk_chars >= len(text):
            break
    return chunks


def retrieve_from_text(query: str, text: str, limit: int = 4,
                       chunk_chars: int = 1200, overlap: int = 150,
                       max_context: int = 6000) -> str:
    """Chunk ONE document and return the passages most relevant to the query,
    joined and capped at ``max_context`` chars.

    This is the "chat with a whole book" core: instead of sending the first N
    characters, we send the few chunks that actually match the question. With no
    keyword hits (or a short doc) we fall back to the opening. Pure — testable
    without files. Used by the 📎 attach feature.
    """
    if not text:
        return ""
    chunks = chunk_text(text, chunk_chars, overlap)
    if not chunks:
        return ""
    ranked = rank_snippets(
        query,
        [(f"part {i + 1}", c) for i, c in enumerate(chunks)],
        limit=limit, max_chars=chunk_chars,
    )
    if not ranked:
        return text[:max_context]            # no match -> the opening
    out, total = [], 0
    for _src, snip in ranked:
        if total >= max_context:
            break
        if total + len(snip) > max_context:
            snip = snip[:max_context - total]
        out.append(snip)
        total += len(snip)
    return "\n…\n".join(out)


def _iter_library(books_dir: str):
    """Yield (filename, body) for Library text files, RECURSING subfolders.

    Covers .md excerpts and .txt notes anywhere under the Books tree (not just
    the top level). .docx/.pdf source books need extraction and are a follow-up.
    I/O, isolated.
    """
    if not books_dir:
        return
    for ext in ("*.md", "*.txt"):
        for path in glob.glob(os.path.join(books_dir, "**", ext), recursive=True):
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    yield (os.path.basename(path), f.read())
            except OSError:
                continue


def _iter_study_db():
    """Yield (tag, text) rows from the study database. I/O, isolated."""
    for sql, tag in (
        ("SELECT title, body FROM study_note_entries", "note"),
        ("SELECT term, definition FROM glossary", "glossary"),
        ("SELECT entry_date, body FROM journal", "journal"),
        ("SELECT title FROM topics", "topic"),
    ):
        try:
            for row in study_db.db_query(sql):
                text = " — ".join(str(c) for c in row if c)
                if text:
                    yield (tag, text)
        except Exception:
            continue


def retrieve_context(query: str, books_dir: str, limit: int = 5,
                     max_chars: int = 1500) -> str:
    """Search the Library + study.db and return a grounding context string.

    Read-only; returns "" on any failure or when nothing relevant is found.
    """
    try:
        docs = list(_iter_library(books_dir)) + list(_iter_study_db())
        top = rank_snippets(query, docs, limit=limit, max_chars=max_chars)
        if not top:
            return ""
        lines = ["Relevant excerpts from the user's own Library and study notes "
                 "(cite these when useful):"]
        for src, snip in top:
            lines.append(f"[{src}] {snip}")
        return "\n\n".join(lines)
    except Exception:
        return ""
