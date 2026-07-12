"""lyceum/formula.py — a spreadsheet formula engine (functional core).

Reviewed from the *Excel 365 Bible*, Part II (Ch 9 Formulas & Functions,
Ch 11 Math, Ch 13 Conditional Analysis, Ch 14 Matching & Lookups) and
proven in pseudocode before this module was written (20/20 checks — see
docs/wiki/Review-Excel365Bible.md).

The classic three-stage pipeline taught in every parsing course and
built at every company that ships a spreadsheet, query planner, or
rules engine:

    tokenize(str)   -> tokens
    Parser(tokens)  -> AST      (precedence climbing:
                                 ^ right-assoc > * / % > + - > compare)
    evaluate(ast, grid) -> float | bool

Pure logic: no Tkinter, no I/O, deterministic. ``grid`` is a plain
``dict`` mapping A1-style addresses to numbers, supplied by the caller —
so formulas evaluate with no Excel and no openpyxl required.

Public API:
    excel(formula, grid=None) -> float | bool     # evaluate a formula
    FormulaError                                    # raised on bad input
    col_to_num / num_to_col / cells_in_range        # A1 address helpers
"""

from __future__ import annotations

import math
import re


class FormulaError(ValueError):
    """Any tokenize/parse/evaluate failure (bad syntax, unknown
    function, division by zero, etc.)."""


# ── A1 <-> (row, col): Excel columns are bijective base-26 ────────────

def col_to_num(letters: str) -> int:
    """'A' -> 1, 'Z' -> 26, 'AA' -> 27 …"""
    n = 0
    for ch in letters:
        if not ch.isalpha():
            raise FormulaError(f"bad column letter: {letters!r}")
        n = n * 26 + (ord(ch.upper()) - ord("A") + 1)
    return n


def num_to_col(n: int) -> str:
    """1 -> 'A', 27 -> 'AA' …"""
    if n < 1:
        raise FormulaError(f"column number must be >= 1: {n}")
    s = ""
    while n:
        n, rem = divmod(n - 1, 26)
        s = chr(ord("A") + rem) + s
    return s


_CELL = re.compile(r"^([A-Za-z]+)(\d+)$")


def _split_cell(addr: str) -> tuple[int, int]:
    m = _CELL.match(addr)
    if not m:
        raise FormulaError(f"bad cell reference: {addr!r}")
    return col_to_num(m.group(1)), int(m.group(2))


def cells_in_range(a: str, b: str) -> list[str]:
    """Enumerate 'A1:B2' -> ['A1','B1','A2','B2'] (row-major, the order
    a reader scans a block)."""
    c1, r1 = _split_cell(a)
    c2, r2 = _split_cell(b)
    out = []
    for r in range(min(r1, r2), max(r1, r2) + 1):
        for c in range(min(c1, c2), max(c1, c2) + 1):
            out.append(f"{num_to_col(c)}{r}")
    return out


# ── tokenizer ─────────────────────────────────────────────────────────

_TOKEN = re.compile(r"""
    (?P<NUMBER>\d+\.?\d*|\.\d+)
  | (?P<CELL>[A-Za-z]+\d+)
  | (?P<FUNC>[A-Za-z][A-Za-z0-9_.]*(?=\())
  | (?P<OP><=|>=|<>|[-+*/^%<>=])
  | (?P<LP>\()
  | (?P<RP>\))
  | (?P<COMMA>,)
  | (?P<COLON>:)
  | (?P<WS>\s+)
""", re.VERBOSE)


def tokenize(s: str) -> list[tuple[str, str]]:
    """String -> [(kind, text), …, ('END','')]. Raises FormulaError on
    an unrecognized character."""
    if s is None:
        raise FormulaError("empty formula")
    s = s.strip()
    if s.startswith("="):
        s = s[1:]
    toks: list[tuple[str, str]] = []
    i = 0
    while i < len(s):
        m = _TOKEN.match(s, i)
        if not m:
            raise FormulaError(f"unexpected character at {i}: {s[i]!r}")
        i = m.end()
        if m.lastgroup != "WS":
            toks.append((m.lastgroup, m.group()))
    toks.append(("END", ""))
    return toks


# ── recursive-descent parser (precedence climbing) ────────────────────
# AST nodes are tuples, tagged by their first element:
#   ('num', float) ('cell', 'A1') ('range', 'A1', 'B2')
#   ('neg', node)  ('bin', op, l, r)  ('cmp', op, l, r)
#   ('func', NAME, [args])

class _Parser:
    def __init__(self, toks: list[tuple[str, str]]):
        self._t = toks
        self._i = 0

    def _peek(self):
        return self._t[self._i]

    def _eat(self, kind: str | None = None):
        k, v = self._t[self._i]
        if kind and k != kind:
            raise FormulaError(f"expected {kind}, got {k} {v!r}")
        self._i += 1
        return k, v

    def parse(self):
        node = self._expr()
        self._eat("END")
        return node

    def _expr(self):                      # comparison (lowest precedence)
        left = self._add()
        while self._peek()[0] == "OP" and self._peek()[1] in (
                "<", ">", "<=", ">=", "=", "<>"):
            op = self._eat()[1]
            left = ("cmp", op, left, self._add())
        return left

    def _add(self):
        left = self._mul()
        while self._peek()[0] == "OP" and self._peek()[1] in ("+", "-"):
            op = self._eat()[1]
            left = ("bin", op, left, self._mul())
        return left

    def _mul(self):
        left = self._power()
        while self._peek()[0] == "OP" and self._peek()[1] in ("*", "/", "%"):
            op = self._eat()[1]
            left = ("bin", op, left, self._power())
        return left

    def _power(self):
        left = self._unary()
        if self._peek()[0] == "OP" and self._peek()[1] == "^":
            self._eat()
            return ("bin", "^", left, self._power())   # right-assoc
        return left

    def _unary(self):
        if self._peek()[0] == "OP" and self._peek()[1] == "-":
            self._eat()
            return ("neg", self._unary())
        if self._peek()[0] == "OP" and self._peek()[1] == "+":
            self._eat()
            return self._unary()
        return self._atom()

    def _atom(self):
        k, v = self._peek()
        if k == "NUMBER":
            self._eat()
            return ("num", float(v))
        if k == "FUNC":
            self._eat()
            self._eat("LP")
            args = []
            if self._peek()[0] != "RP":
                args.append(self._arg())
                while self._peek()[0] == "COMMA":
                    self._eat()
                    args.append(self._arg())
            self._eat("RP")
            return ("func", v.upper(), args)
        if k == "CELL":
            self._eat()
            if self._peek()[0] == "COLON":
                self._eat()
                b = self._eat("CELL")[1]
                return ("range", v, b)
            return ("cell", v)
        if k == "LP":
            self._eat()
            node = self._expr()
            self._eat("RP")
            return node
        raise FormulaError(f"unexpected token {k} {v!r}")

    def _arg(self):
        """A function argument may be a bare range (A1:B3) or any expr."""
        if (self._peek()[0] == "CELL"
                and self._t[self._i + 1][0] == "COLON"):
            a = self._eat("CELL")[1]
            self._eat("COLON")
            b = self._eat("CELL")[1]
            return ("range", a, b)
        return self._expr()


# ── evaluator ─────────────────────────────────────────────────────────

def _num(x) -> float:
    if x is None or x == "":
        return 0.0
    try:
        return float(x)
    except (TypeError, ValueError):
        raise FormulaError(f"cell value is not a number: {x!r}")


def _flatten(node, grid) -> list[float]:
    """Function args: a range expands to its cells; anything else is a
    single evaluated value."""
    if node[0] == "range":
        return [_num(grid.get(c, 0)) for c in cells_in_range(node[1], node[2])]
    return [evaluate(node, grid)]


_FUNCS = {
    "SUM":     lambda xs: math.fsum(xs),
    "AVERAGE": lambda xs: (math.fsum(xs) / len(xs)) if xs else 0.0,
    "MIN":     lambda xs: min(xs) if xs else 0.0,
    "MAX":     lambda xs: max(xs) if xs else 0.0,
    "COUNT":   lambda xs: float(len(xs)),
    "PRODUCT": lambda xs: math.prod(xs) if xs else 0.0,
    "ABS":     lambda xs: abs(xs[0]),
    "SQRT":    lambda xs: math.sqrt(xs[0]),
    "INT":     lambda xs: float(math.floor(xs[0])),
}


def evaluate(node, grid: dict | None = None):
    """Walk the AST and return a float (or bool from a comparison)."""
    grid = grid or {}
    tag = node[0]
    if tag == "num":
        return node[1]
    if tag == "cell":
        return _num(grid.get(node[1].upper(), 0))
    if tag == "neg":
        return -evaluate(node[1], grid)
    if tag == "bin":
        a = evaluate(node[2], grid)
        b = evaluate(node[3], grid)
        op = node[1]
        if op in ("/", "%") and b == 0:
            raise FormulaError("division by zero")
        return {
            "+": lambda: a + b, "-": lambda: a - b, "*": lambda: a * b,
            "/": lambda: a / b, "%": lambda: a % b, "^": lambda: a ** b,
        }[op]()
    if tag == "cmp":
        a = evaluate(node[2], grid)
        b = evaluate(node[3], grid)
        op = node[1]
        return {
            "<": a < b, ">": a > b, "<=": a <= b, ">=": a >= b,
            "=": a == b, "<>": a != b,
        }[op]
    if tag == "range":
        raise FormulaError("a range (A1:B3) must be inside a function "
                           "like SUM()")
    if tag == "func":
        name, args = node[1], node[2]
        if name == "IF":
            if not 2 <= len(args) <= 3:
                raise FormulaError("IF takes 2 or 3 arguments")
            cond = evaluate(args[0], grid)
            if cond:
                return evaluate(args[1], grid)
            return evaluate(args[2], grid) if len(args) > 2 else 0.0
        if name == "ROUND":
            if not 1 <= len(args) <= 2:
                raise FormulaError("ROUND takes 1 or 2 arguments")
            val = evaluate(args[0], grid)
            digits = int(evaluate(args[1], grid)) if len(args) > 1 else 0
            return round(val, digits)
        if name not in _FUNCS:
            raise FormulaError(f"unknown function: {name}")
        xs: list[float] = []
        for a in args:
            xs.extend(_flatten(a, grid))
        return _FUNCS[name](xs)
    raise FormulaError(f"cannot evaluate node: {node!r}")


def excel(formula: str, grid: dict | None = None):
    """Evaluate an Excel-style formula string over an optional A1 grid.

    >>> excel("=SUM(A1:A3)+B1*2", {"A1": 10, "A2": 20, "A3": 30, "B1": 5})
    70.0
    """
    return evaluate(_Parser(tokenize(formula)).parse(), grid or {})
