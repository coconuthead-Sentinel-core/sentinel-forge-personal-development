# Clinical Review — *GO! With Microsoft Word 2010* → Sentinel Forge

> Top-down review of the 8-file *GO! With Microsoft Word 2010,
> Comprehensive* textbook (~1.38M chars, ~98 hands-on objectives)
> against one question: **what here is real computer science that adds
> to Sentinel Forge — additively, no teardown, no disruption?** Gate
> honored: reviewed and proven in pseudocode before any feature code.
> Reviewed 2026-07-12.

## What the book is

A step-by-step tutorial for *driving Microsoft Word*: creating
documents, tables, Quick Styles, research papers (citations,
bibliography, footnotes), mail merge, building blocks / Quick Parts,
master documents, custom forms, web pages, track changes, and Office
integration. Like the Excel Bible's UI chapters, most of it teaches the
*application*, not transferable algorithms.

## Part-by-part verdict

| Area | Verdict | Why |
| --- | --- | --- |
| Create/edit docs, tables, formatting, pictures, SmartArt, printing | **SKIP** | Driving Word's UI. Sentinel already reads/writes .docx; re-implementing Word is out of scope + teardown risk. |
| Mail merge, master documents, custom forms, web-page export, PowerPoint/Excel integration | **SKIP** | Word-application workflows, not study-app features. |
| Building Blocks / Quick Parts (reusable snippets) | **SKIP** | Sentinel already has this shape — the Prompt Library. |
| Track changes / comments | **SKIP** | Multi-author review tooling; single-user study app. |
| Table of contents / outline (heading extraction) | **PARTIAL** | The Library reader already does chapter navigation; a doc-outline extractor is a possible small add, deferred. |
| Citations / bibliography (APA/MLA formatting) | **PARTIAL** | A bounded formatting algorithm, genuinely useful for Shannon's coursework papers — a good *future* candidate, deferred behind the pick below. |
| **Readability statistics (Flesch Reading Ease / Flesch-Kincaid grade)** | **BUILD** | Word reports exactly these. A real text-statistics algorithm (syllable counting + two published formulas) that lands squarely on this app's neurodivergent-first thesis. **This is the pick — and the extra mile.** |

## The BUILD: `lyceum/readability.py` — reading-difficulty analysis

**What it is (the CS).** Count words, sentences, and — the genuinely
algorithmic part — **syllables** (a vowel-group heuristic with a
silent-`e` / consonant-`le` adjustment), then apply two published
formulas:

```pseudocode
count_syllables(word):
    n = number of maximal vowel runs
    if word ends in silent 'e' (but NOT consonant+'le'): n -= 1
    return max(1, n)

analyze(text):
    W = words ; S = sentences (split on . ! ?) ; Y = sum syllables
    FRE  = 206.835 - 1.015*(W/S) - 84.6*(Y/W)     # Flesch Reading Ease
    FKGL = 0.39*(W/S) + 11.8*(Y/W) - 15.59         # grade level
    label = plain-language band from FRE
```

**Why it fits — and why it gets the professor's attention.**
- **On-thesis.** Sentinel Forge is *neurodivergent-first*. A dyslexic
  reader benefits from a plain warning — *"this passage reads at Grade
  14 — Very hard"* — BEFORE spending attention on it. It connects a
  metric from a Microsoft Word textbook to the app's accessibility
  mission. That is the extra-mile story: not "I copied a Word feature,"
  but "I took a readability algorithm and turned it into an
  accessibility guardrail for a specific disability." A reviewer
  notices the *why*, not just the *what*.
- **Ties to existing data.** It complements the excerpt `cognitive_load`
  / GREEN-YELLOW-RED zone metadata already in the app — an *objective*
  difficulty score beside the subjective one.
- **Architecture.** Pure logic, no Tkinter, deterministic → drops into
  `lyceum/` beside `metrics.py`, `srs.py`, `formula.py`. Additive: a
  NEW file, zero edits to existing behavior to exist.
- **Real, not made-up.** Flesch-Kincaid is the readability standard used
  by the U.S. government, education systems worldwide, and Word itself;
  the syllable heuristic is a classic NLP kernel.

## Proof (pseudocode tested BEFORE any real coding — the gate)

Prototype `scratchpad/readability_proto.py`, three proofs, **all pass**:
1. **Syllable counter** — 13/15 on a hand-counted word list (cat=1,
   apple=2, table=2, little=2, readability=5…); the two misses
   (*idea*, *science* — adjacent vowels that are actually separate
   syllables) are documented, expected limits of any lightweight
   heuristic.
2. **Formula exactness** — on hand-counted inputs the FRE/FKGL arithmetic
   matches the published formulas, including clamping (FRE 0–100, grade
   ≥ 0).
3. **Monotonicity + edges** — a simple passage scores easier (higher
   FRE, lower grade) than a dense academic one; empty text is safe;
   output is deterministic; label bands correct.

## Recommendation & scope

- **Phase 1 (ready to build):** `lyceum/readability.py` + a
  `tests/test_readability.py` suite, surfaced first as a **readability
  badge** on saved excerpts / the reader ("📖 Grade 8 · Plain") and in
  the assistant when it reports on a passage — the smallest, most
  on-thesis surface.
- **Phase 2 (deferred):** citation/bibliography formatter for coursework
  papers.
- **Phase 3 (deferred):** document-outline (heading) extractor.
- **Out of scope:** Word UI, mail merge, master docs, track changes,
  SmartArt — taking them would be the teardown the "stay the course"
  decision rejected.

Gate satisfied: review complete, pseudocode proven. Awaiting the
Architect's go to begin Phase 1.
