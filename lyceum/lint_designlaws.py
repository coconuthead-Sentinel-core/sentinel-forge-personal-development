"""Design-law linter — a static guard for this codebase's recurring UI traps.

Encodes rules from ``docs/wiki/Working-With-The-Architect.md`` §3 and the
Former-Bugs history as an AST check, so the traps that have bitten this
project before fail fast instead of shipping again:

  A  a tuple ``pady=``/``padx=`` inside a WIDGET CONSTRUCTOR — the codebase's
     oldest recurring crash (``bad screen distance``). Tuple padding belongs
     only in ``.pack()`` / ``.grid()``, never in a widget's constructor.
  B  a hardcoded ``.geometry("WxH")`` literal — windows must be sized from
     ``winfo_screenwidth/height``, never fixed pixels (a fixed size clips the
     bottom buttons on the owner's ~1097x617 effective display).

Pure and importable — no Tk, no I/O beyond reading a file the caller names.
Run headless from the repo root:  python -m unittest discover -s tests
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass

# Tk / ttk widget class names whose constructors must not carry tuple padding.
_WIDGETS = {
    "Label", "Button", "Frame", "LabelFrame", "Entry", "Text", "Canvas",
    "Listbox", "Scrollbar", "Toplevel", "Checkbutton", "Radiobutton",
    "Scale", "Spinbox", "Menu", "Menubutton", "PanedWindow", "Message",
    "OptionMenu", "Combobox", "Treeview", "Notebook", "Progressbar",
    "Separator", "Sizegrip", "ScrolledText",
}
_GEOMETRY_RE = re.compile(r"^\d+x\d+")


@dataclass(frozen=True)
class Finding:
    line: int
    rule: str
    message: str


def _func_tail(func: ast.AST) -> str:
    """Last name of a call target: ``tk.Label`` -> 'Label', ``x.pack`` -> 'pack'."""
    if isinstance(func, ast.Attribute):
        return func.attr
    if isinstance(func, ast.Name):
        return func.id
    return ""


def scan_source(src: str) -> list[Finding]:
    """Return the design-law violations in `src` (Python source text)."""
    findings: list[Finding] = []
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [Finding(e.lineno or 0, "parse", f"could not parse: {e.msg}")]
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        tail = _func_tail(node.func)
        # Rule A — tuple pad kwarg in a widget constructor
        if tail in _WIDGETS:
            for kw in node.keywords:
                if kw.arg in ("pady", "padx") and isinstance(kw.value, ast.Tuple):
                    findings.append(Finding(
                        node.lineno, "A",
                        f"{tail}(... {kw.arg}=(tuple) ...) — tuple padding in a "
                        f"constructor; move it to .pack()/.grid()"))
        # Rule B — hardcoded geometry literal
        if tail == "geometry" and node.args:
            a0 = node.args[0]
            if (isinstance(a0, ast.Constant) and isinstance(a0.value, str)
                    and _GEOMETRY_RE.match(a0.value)):
                findings.append(Finding(
                    node.lineno, "B",
                    f'geometry("{a0.value}") — hardcoded size; derive it from '
                    f'winfo_screenwidth/height'))
    return findings


def scan_file(path: str) -> list[Finding]:
    """Scan a Python file on disk. Returns [] for an unreadable file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return scan_source(f.read())
    except OSError:
        return []
