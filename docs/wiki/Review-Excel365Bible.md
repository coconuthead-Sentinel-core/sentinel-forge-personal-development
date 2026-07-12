# Clinical Review — *Excel 365 Bible* → Sentinel Forge integration

> Top-down, chapter-by-chapter review of the full *Microsoft Excel 365
> Bible* (10 source files on disk, 4 duplicates + 2 stubs discarded;
> ~2.87M chars of unique content, ~44 chapters across 6 parts) against
> one question: **what here is real computer science that can be woven
> into Sentinel Forge additively, without destroying working code?**
> Gate honored: no feature code is written until a proven pseudocode
> prototype exists. Reviewed 2026-07-12.

## Method

Every part mapped to a fit verdict: **BUILD** (real CS, additive, high
value), **PARTIAL** (a slice is worth taking), or **SKIP** (belongs to
Excel-the-application, not to a local Python/Tk study app). Verdicts
are judged the way a senior review at any AI/CS shop would judge them —
does it fit the architecture, is it testable, does it earn its risk.

## Part-by-part verdict

| Part | Chapters | Topic | Verdict | Why |
| --- | --- | --- | --- | --- |
| I | 1–8 | UI, data entry, ranges, formatting, files, printing, ribbon customization | **SKIP** | These are how to drive the Excel *application*. Sentinel already reads/writes .xlsx via openpyxl; re-implementing Excel's UI is out of scope and would be a teardown risk. |
| **II** | **9–16** | **Formulas & functions: arithmetic, arrays, math/dates, text, conditional, lookups, error-handling** | **BUILD** | A formula engine is a classic CS artifact (tokenizer → recursive-descent parser → evaluator). Pure logic, unit-testable, additive as `lyceum/formula.py`. **This is the pick.** |
| III | 17–20 | Charts, sparklines, custom number formats/shapes | **PARTIAL** | Sentinel's money tools already draw gauges/bars in Tk. Worth taking: **custom number-format strings** (Ch 20) applied to generated .xlsx cells in `doc_writer` (currency/percent formatting) — a small, safe upgrade. |
| IV | 21–37 | Import/clean data, Power Query, PivotTables, Power Pivot, what-if | **PARTIAL** | Full Power Query is out of scope. Worth taking: a **group-by + aggregate ("pivot") pure function** — Sentinel's expense ledger already groups by category; a general version would enrich reporting. Deferred behind Part II. |
| V | 38+ | VBA / macros | **SKIP** | A scripting host for Excel automation. No place in a local-first study app; would also be a security surface. Correctly out of scope. |
| VI | appendices | function reference, shortcuts | **REFERENCE** | Useful as harvest fodder for the Glossary/flashcards (the existing 🧠 Knowledge Harvester already covers this path — read the book, harvest terms). No new code. |

## The recommended BUILD: `lyceum/formula.py` — a spreadsheet formula engine

**What it is (the CS).** A three-stage pipeline, the textbook shape:

```pseudocode
tokenize(str)   -> [NUMBER | CELLREF | RANGE | OP | FUNC | ( ) , :]
parse(tokens)   -> AST     (precedence climbing:
                            ^ (right-assoc)  >  * / %  >  + -  >  compare)
eval(ast, grid) -> number/bool
    CELLREF  A1     -> grid["A1"]  (blank = 0)
    RANGE    A1:B3  -> flat cell list for SUM/AVERAGE/MIN/MAX/COUNT
    FUNC           -> apply over evaluated args (IF is short-circuit)
grid: dict "A1" -> number, supplied by the caller (no Excel needed)
```

Supported now: `+ - * / % ^`, unary minus, parentheses, comparisons
(`< > <= >= = <>`), A1 cells, `A1:B3` ranges, and functions
`SUM AVERAGE MIN MAX COUNT PRODUCT ROUND ABS SQRT IF`.

**Why it fits, judged like a real review:**
- **Architecture** — pure logic, no Tkinter, deterministic → drops
  straight into `lyceum/` beside `metrics.py` and `srs.py`.
- **Additive** — a NEW file. Zero edits to existing code to exist. No
  teardown risk (the standing rule from the "don't rebuild what works"
  decision).
- **Testable** — every stage unit-tests headlessly; see the proof below.
- **Real, not made-up** — a Pratt/recursive-descent expression evaluator
  is the canonical parsing lab taught worldwide (US, EU, India, Japan,
  Korea, Taiwan, Australia, UAE) and built at every company that ships a
  spreadsheet, query planner, or rules engine.
- **Genuinely useful here** — (a) the assistant's `doc_writer` could
  *evaluate* the formulas it writes to preview results; (b) a future
  "formula cell" in the money tools (type `=SUM(B2:B7)*1.05`); (c)
  validating generated spreadsheets.

## Proof (pseudocode tested BEFORE any real coding — the gate)

Prototype: `scratchpad/formula_engine_proto.py`. Three proofs, **20/20
checks pass**:

1. **Arithmetic & precedence (Ch 9):** `2+3*4=14`, `(2+3)*4=20`,
   `2^3^2=512` (right-assoc), unary minus, `%`.
2. **Functions over ranges (Ch 11/13/14):** `SUM/AVERAGE/MIN/MAX/COUNT`
   over `A1:B2`, `IF(A1>5,100,200)`, `ROUND(10/3,2)=3.33`, and nested
   `IF(SUM(A1:A3)>50, MAX(A1:A3), 0)`.
3. **Cross-check vs real Excel semantics:** our A1 column math equals
   `openpyxl.column_index_from_string` for `A..ZZ`; range enumeration
   and `SUM` match an independent computation.

## Recommendation & scope

- **Phase 1 (ready to build):** port the proven prototype to
  `lyceum/formula.py` + a `tests/test_formula.py` suite, wired first
  into `doc_writer` as an optional "compute preview" — smallest safe
  surface.
- **Phase 2 (deferred):** number-format strings on generated .xlsx
  cells (Part III slice).
- **Phase 3 (deferred):** group-by/pivot pure function (Part IV slice).
- **Explicitly out of scope:** Excel UI, Power Query, VBA (Parts I, V,
  and most of IV) — taking them would be the teardown the "stay the
  course" decision rejected.

Gate satisfied: review complete, pseudocode proven. Awaiting the
Architect's go to begin Phase 1 real coding.
