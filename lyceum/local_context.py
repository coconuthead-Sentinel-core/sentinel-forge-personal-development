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


def _iter_library(books_dir: str):
    """Yield (filename, body) for every Library .md excerpt. I/O, isolated."""
    for path in glob.glob(os.path.join(books_dir or "", "*.md")):
        try:
            with open(path, encoding="utf-8") as f:
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
