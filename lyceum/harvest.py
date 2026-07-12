"""lyceum/harvest.py — the Knowledge Harvester (functional core).

Mines term/definition pairs out of book text so the shell can turn any
Library book into Glossary entries — which the 🧠 Memory Review deck
then picks up as FSRS flashcards. Read → harvest → remember.

Pure logic: no Tkinter, no file or database access, deterministic.
The filter set was tuned ("practiced") against a real 1.9M-character
corpus (two captured Office Step-by-Step textbooks) until junk hits —
author names, sentence fragments, marketing copy, comma-splice
run-ons — were eliminated. Precision beats volume: a flashcard deck
would rather miss a term than memorize garbage.
"""

from __future__ import annotations

import re

# Terms that start with these words are fragments, not concepts
# ("Whether you…", "This means…", "Understanding your…").
_STOP_STARTS = {
    "this", "that", "there", "these", "those", "it", "he", "she", "we",
    "they", "you", "i", "one", "each", "here", "which", "what", "when",
    "if", "another", "understanding", "using", "creating", "the", "a",
    "an", "all", "some", "any", "most", "many", "both", "such", "so",
    "then", "now", "first", "second", "next", "chapter", "note", "tip",
    "important", "see", "click", "select", "choose", "type", "press",
    "figure", "table", "step", "practice", "caution", "troubleshooting",
    "whether", "where", "why", "how", "today", "tomorrow", "yesterday",
}

_BAD_DEF_STARTS = ("way to ", "way of ", "bit ", "lot ", "few ", "kind of")

# A definition worth memorizing names a THING. Gate: one of these nouns
# must appear in the first three words after the article. This is the
# filter that turned raw pattern-matching into flashcard-grade output.
_DEF_NOUNS = {
    "process", "tool", "collection", "document", "worksheet", "feature",
    "program", "application", "set", "group", "list", "area", "pane",
    "view", "file", "database", "object", "command", "tab", "window",
    "template", "report", "account", "statement", "method", "means",
    "record", "form", "button", "gallery", "field", "folder", "page",
    "task", "item", "chart", "formula", "function", "table", "workbook",
    "presentation", "message", "contact", "calendar", "place", "storage",
    "location", "name", "series", "sequence", "rule", "option", "setting",
    "control", "wizard", "dialog", "summary", "entry", "entries",
    "transaction", "balance", "ledger", "journal", "asset", "liability",
    "expense", "income", "invoice", "receipt", "companies", "individuals",
    "documents", "objects", "accounts", "items", "records", "version",
    "copy", "snapshot", "container", "unit", "measure", "value",
}

_PERSON_HINTS = ("author", "coauthor", "president", "founder", "writer")
_HYPE_WORDS = {"powerful", "nifty", "great", "good", "easy", "useful",
               "simple", "popular", "robust", "big", "wonderful"}
_GENERIC_TERMS = {"result", "results", "example", "answer", "difference",
                  "purpose", "goal", "reason", "problem", "benefit"}

_DEF_PATTERN = re.compile(
    r"(?<![a-z,;])"                                   # sentence-ish start
    r"([A-Z][A-Za-z0-9&\-/ ]{2,48}?)\s+"              # the Term
    r"(?:is|are)\s+(a|an|the)\s+"
    r"([a-z][^.;:\n]{15,180}[.])"                     # one-sentence definition
)

# Comma-splice run-ons captured by the pattern get cut back to their
# clean first clause ("a design template, the publication is…").
_SPLICES = (", the ", ", you ", ", it ", ", this ")


def _clean_term(raw: str) -> str:
    t = re.sub(r"\s+", " ", raw).strip(" -–—")
    t = re.sub(r"^(The|A|An)\s+", "", t)
    return t.strip()


def _quality_gate(term: str, defn: str) -> bool:
    """True when (term, defn) is flashcard-grade. Every rule here exists
    because a real junk hit demanded it — see the module docstring."""
    words = term.split()
    if not 1 <= len(words) <= 4:
        return False
    if words[0].lower() in _STOP_STARTS:
        return False
    if words[-1].lower() in ("you", "your", "the", "a", "an", "of", "to"):
        return False                        # truncated phrases
    if any(w.lower() in ("is", "are", "means", "shows", "lets")
           for w in words):
        return False
    if term.lower() in _GENERIC_TERMS:
        return False
    low = defn.lower()
    if low.startswith(_BAD_DEF_STARTS):
        return False
    if len(defn) < 25 or len(defn.split()) < 6:
        return False
    if any(h in low for h in _PERSON_HINTS):
        return False                        # people, not concepts
    head = [w.strip(",.").lower() for w in defn.split()[1:4]]
    if not any(w in _DEF_NOUNS for w in head):
        return False                        # must name a THING
    if head and head[0] in _HYPE_WORDS:
        return False                        # marketing copy
    return True


def harvest(text: str, max_terms: int = 40) -> list[tuple[str, str, int]]:
    """Mine (term, definition, score) triples from book text, best first.

    Pure and deterministic: same text in, same cards out. Score blends
    how often the book mentions the term (importance) with shape
    bonuses; duplicates keep their best-scoring definition.
    """
    if not text:
        return []
    found: dict[str, tuple[str, str, int]] = {}
    lowered = text.lower()
    for m in _DEF_PATTERN.finditer(text):
        term = _clean_term(m.group(1))
        defn = (m.group(2) + " " + m.group(3)).strip()
        for splice in _SPLICES:
            i = defn.find(splice)
            if i > 12:
                defn = defn[:i].rstrip() + "."
                break
        defn = defn[0].upper() + defn[1:]
        if not _quality_gate(term, defn):
            continue
        occurrences = lowered.count(term.lower())
        score = min(occurrences, 12)
        score += 2 if len(term.split()) <= 2 else 0
        score += 1 if term[0].isupper() and not term.isupper() else 0
        key = term.casefold()
        if key not in found or score > found[key][2]:
            found[key] = (term, defn, score)
    ranked = sorted(found.values(), key=lambda x: -x[2])
    return ranked[:max_terms]
