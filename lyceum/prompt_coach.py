"""lyceum/prompt_coach.py — a prompt-quality analyzer (functional core).

Reviewed from *Microsoft 365 Copilot At Work*, Ch 3 "An Introduction to
Prompt Engineering", and proven in pseudocode before this module was
written (3 proofs / 15 checks — see docs/wiki/Review-CopilotAtWork.md).

Prompt engineering is a taught university AI/HCI subject. The classic
rubric: a strong prompt names a PERSONA/role, a clear TASK, CONTEXT, a
desired FORMAT, and is SPECIFIC rather than vague. This module is a
rubric-linting / heuristic text-analysis artifact — it scores a prompt
against that rubric (0-100) and returns prioritized, actionable
coaching. Nothing proprietary is copied: the rubric is public canon;
the detectors are original heuristics.

Why it lives here: the owner is *learning to work with AI*. A coach that
scores a prompt and teaches the missing component turns the AI Chat +
Prompt Library into a teaching tool. Pure logic: no Tkinter, no I/O,
deterministic, read-only — it can never break, delete, or alter
anything.

Public API:
    analyze(prompt) -> {score, band, components{...}, tips[...]}
    band_for(score) -> str
    improve(prompt) -> str        # apply the top tip as a template
"""

from __future__ import annotations

import re

# Detectors for each rubric component ---------------------------------

_ROLE_RE = re.compile(
    r"\b(act as|you are|as an? |pretend to be|imagine you|"
    r"in the role of|persona|role of|as my)\b", re.I)

_TASK_VERBS = (
    "write", "summarize", "summarise", "list", "explain", "compare",
    "draft", "translate", "rewrite", "outline", "analyze", "analyse",
    "generate", "create", "describe", "define", "classify", "extract",
    "brainstorm", "plan", "calculate", "convert", "review", "improve",
    "suggest", "recommend", "critique", "evaluate", "format", "sort")
_TASK_RE = re.compile(r"\b(" + "|".join(_TASK_VERBS) + r")\b", re.I)

_FORMAT_RE = re.compile(
    r"\b(bullet|bulleted|numbered list|as a list|table|paragraph|"
    r"steps|step-by-step|json|markdown|outline|headings|"
    r"in \d+ words|word limit|one sentence|short|concise|"
    r"format|columns?)\b", re.I)

_CONTEXT_RE = re.compile(
    r"\b(because|so that|for (a|an|my|our|the)|context|background|"
    r"given|based on|audience|reader|my (project|class|job|goal)|"
    r"the following|here is|here's)\b", re.I)

_SPECIFIC_RE = re.compile(r"[0-9]|\"[^\"]+\"|\b[A-Z][a-z]{2,}\b")


def _has_role(p: str) -> bool:
    return bool(_ROLE_RE.search(p))


def _has_task(p: str) -> bool:
    return bool(_TASK_RE.search(p))


def _has_format(p: str) -> bool:
    return bool(_FORMAT_RE.search(p))


def _has_context(p: str) -> bool:
    # an explicit context marker, OR simply enough detail to imply it
    return bool(_CONTEXT_RE.search(p)) or len(p.split()) >= 25


def _is_specific(p: str) -> bool:
    # not a vague one-liner: >= 8 words AND a concrete token
    return len(p.split()) >= 8 and bool(_SPECIFIC_RE.search(p))


# Rubric: (key, weight, human label, detector, tip-if-missing, template)
_RUBRIC = [
    ("task",     30, "a clear task verb", _has_task,
     'State the action clearly, e.g. "Summarize…" or "List…".',
     "Summarize the following: "),
    ("role",     20, "a role/persona", _has_role,
     'Give the assistant a role, e.g. "Act as a study tutor."',
     "Act as a knowledgeable tutor. "),
    ("context",  20, "context/background", _has_context,
     "Add context: who it's for, why, or the source material.",
     " — this is for my computer-science coursework."),
    ("format",   20, "a desired output format", _has_format,
     'Say the format, e.g. "as 5 bullet points" or "a table".',
     " Give the answer as 5 concise bullet points."),
    ("specific", 10, "concrete specifics", _is_specific,
     "Be specific — add numbers, names, or an exact goal.",
     ""),
]


def band_for(score: int) -> str:
    """Plain-language band for a rubric score."""
    if score >= 85:
        return "Excellent"
    if score >= 65:
        return "Good"
    if score >= 40:
        return "Fair"
    return "Needs work"


def analyze(prompt: str) -> dict:
    """Score a prompt (0-100) against the prompt-engineering rubric and
    return prioritized coaching. Deterministic; empty prompt -> score 0.

    Returns:
        score      int 0..100
        band       "Excellent" | "Good" | "Fair" | "Needs work"
        components {key: bool}   which rubric parts are present
        tips       [str]         suggestions for missing parts,
                                 biggest-win first
    """
    prompt = (prompt or "").strip()
    keys = [k for k, *_ in _RUBRIC]
    if not prompt:
        return {"score": 0, "band": "Needs work",
                "components": {k: False for k in keys},
                "tips": ["Type a prompt to get coaching."]}
    components: dict = {}
    score = 0
    missing = []
    for key, weight, _label, detector, tip, _tpl in _RUBRIC:
        ok = detector(prompt)
        components[key] = ok
        if ok:
            score += weight
        else:
            missing.append((weight, tip))
    missing.sort(key=lambda x: -x[0])          # biggest win first
    tips = [t for _w, t in missing] or ["Great prompt — all the key "
                                        "parts are here."]
    return {"score": score, "band": band_for(score),
            "components": components, "tips": tips}


def improve(prompt: str) -> str:
    """Return a stronger version of the prompt by grafting templates for
    the highest-weight MISSING components onto it. A gentle starting
    point the user then edits — not a rewrite of their intent."""
    prompt = (prompt or "").strip()
    if not prompt:
        return "Act as a knowledgeable tutor. Summarize the following: "
    result = prompt
    # role goes in front; task in front if absent; context/format append.
    if not _has_role(result):
        result = "Act as a knowledgeable tutor. " + result
    if not _has_task(result):
        result = re.sub(r"^(Act as[^.]*\.\s*)", r"\1Summarize: ", result) \
            if result.startswith("Act as") else "Summarize: " + result
    if not _has_format(result):
        result = result.rstrip() + " Give the answer as 5 concise " \
                                   "bullet points."
    if not _has_context(result):
        result = result.rstrip() + " (This is for my coursework.)"
    return result
