"""lyceum/automation.py — an Event-Condition-Action (ECA) rule engine.

Reviewed from the *Power Automate Cookbook* / *Deep Dive into Power
Automate*, and proven in pseudocode before this module was written
(3 proofs / 22 checks — see docs/wiki/Review-PowerAutomate.md).

A Power Automate "flow" is exactly the ECA pattern: a TRIGGER (event), a
CONDITION (if this), ACTIONS (do that). ECA is a canonical, worldwide-
taught computer-science construct — active-database triggers (database
systems), production rule systems (AI), event-driven / workflow
architecture (software engineering). Every workflow product (Power
Automate, IFTTT, Zapier) is an ECA engine underneath.

CRITICAL SAFETY PROPERTY: this is a PURE decision engine. Given an
``event`` name and a ``facts`` dict it returns *which actions should
fire* and performs NO side effects. The imperative shell decides
whether/how to run them (human-in-the-loop), so the engine can never
break, delete, or alter anything. Malformed rules (unknown operator,
missing fact, wrong shape) are SKIPPED, never raised.

Rule shape (a plain dict, JSON-serializable for storage):
    {
        "name": "mark studied",
        "trigger": "focus_completed",
        "conditions": [("minutes", ">=", 25)],     # (fact, op, value)
        "actions": ["scoreboard:studied"],          # opaque to the engine
        "enabled": True,                            # optional, default True
    }

Public API:
    evaluate(event, facts, rules) -> list[actions]
    condition_passes(fact_key, op, value, facts) -> bool
    explain(rule, event, facts) -> str
    OPERATORS  (the supported comparison/membership operators)
"""

from __future__ import annotations


# ── condition operators (pure, total — never raise) ──────────────────

def _op_eq(a, b):
    return a == b


def _op_ne(a, b):
    return a != b


def _op_lt(a, b):
    return a is not None and a < b


def _op_gt(a, b):
    return a is not None and a > b


def _op_le(a, b):
    return a is not None and a <= b


def _op_ge(a, b):
    return a is not None and a >= b


def _op_contains(a, b):
    try:
        return b in a
    except TypeError:
        return False


def _op_in(a, b):
    try:
        return a in b
    except TypeError:
        return False


OPERATORS = {
    "==": _op_eq, "!=": _op_ne, "<": _op_lt, ">": _op_gt,
    "<=": _op_le, ">=": _op_ge, "contains": _op_contains, "in": _op_in,
}

_MISSING = object()


def condition_passes(fact_key, op, value, facts) -> bool:
    """True iff ``facts[fact_key]`` ``op`` ``value``. An unknown operator
    or a missing fact returns False — the engine is total, never raises."""
    fn = OPERATORS.get(op)
    if fn is None:
        return False
    actual = (facts or {}).get(fact_key, _MISSING)
    if actual is _MISSING:
        return False
    try:
        return bool(fn(actual, value))
    except Exception:
        return False


def _rule_matches(rule, event, facts) -> bool:
    if not isinstance(rule, dict):
        return False
    if rule.get("trigger") != event:
        return False
    for cond in rule.get("conditions", []):
        try:
            fact_key, op, value = cond
        except (TypeError, ValueError):
            return False                     # malformed condition -> skip rule
        if not condition_passes(fact_key, op, value, facts):
            return False
    return True


def evaluate(event, facts, rules) -> list:
    """Return the flat list of actions for every enabled rule whose
    trigger matches ``event`` and whose conditions all pass against
    ``facts``. Definition order preserved. Pure: no side effects."""
    facts = facts or {}
    fired: list = []
    for rule in rules or []:
        if not isinstance(rule, dict):
            continue
        if rule.get("enabled", True) is False:
            continue
        if _rule_matches(rule, event, facts):
            actions = rule.get("actions", [])
            if isinstance(actions, list):
                fired.extend(actions)
            elif actions:
                fired.append(actions)
    return fired


def explain(rule, event, facts) -> str:
    """Human-readable reason a rule did or did not fire — for a future
    rules UI and for debugging. Never raises."""
    if not isinstance(rule, dict):
        return "not a rule"
    if rule.get("enabled", True) is False:
        return "rule is disabled"
    if rule.get("trigger") != event:
        return f"trigger {rule.get('trigger')!r} != event {event!r}"
    for cond in rule.get("conditions", []):
        try:
            k, op, v = cond
        except (TypeError, ValueError):
            return f"malformed condition {cond!r}"
        if not condition_passes(k, op, v, (facts or {})):
            actual = (facts or {}).get(k, "(missing)")
            return f"condition failed: {k} {op} {v} (actual={actual!r})"
    return "fires: all conditions pass"
