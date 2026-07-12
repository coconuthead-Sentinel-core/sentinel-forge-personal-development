"""Unit tests for lyceum/automation.py — the ECA rule engine.

Mirrors the three proofs that gated the build (ECA core, operators,
robustness/safety) plus explain(). Pure, headless, deterministic. The
engine performs no side effects, so these tests need no DB or GUI.
"""
import unittest

from lyceum.automation import (OPERATORS, condition_passes, evaluate,
                               explain)


RULES = [
    {"name": "mark scoreboard", "trigger": "focus_completed",
     "conditions": [("minutes", ">=", 25)], "actions": ["mark:studied"]},
    {"name": "celebrate streak", "trigger": "habit_checked",
     "conditions": [("streak", "==", 7)], "actions": ["celebrate"]},
]


class ECACoreTest(unittest.TestCase):
    def test_fires_when_trigger_and_condition_match(self):
        self.assertEqual(
            evaluate("focus_completed", {"minutes": 30}, RULES),
            ["mark:studied"])

    def test_no_fire_when_condition_fails(self):
        self.assertEqual(
            evaluate("focus_completed", {"minutes": 10}, RULES), [])

    def test_no_fire_when_trigger_differs(self):
        self.assertEqual(
            evaluate("excerpt_saved", {"minutes": 30}, RULES), [])

    def test_other_rule_fires_on_its_trigger(self):
        self.assertEqual(
            evaluate("habit_checked", {"streak": 7}, RULES), ["celebrate"])


class OperatorTest(unittest.TestCase):
    def test_every_operator(self):
        self.assertTrue(condition_passes("x", "==", 5, {"x": 5}))
        self.assertTrue(condition_passes("x", "!=", 5, {"x": 4}))
        self.assertTrue(condition_passes("x", "<", 10, {"x": 3}))
        self.assertTrue(condition_passes("x", ">", 10, {"x": 30}))
        self.assertTrue(condition_passes("x", "<=", 5, {"x": 5}))
        self.assertTrue(condition_passes("x", ">=", 5, {"x": 9}))
        self.assertTrue(condition_passes(
            "tags", "contains", "cs", {"tags": ["cs", "math"]}))
        self.assertTrue(condition_passes(
            "zone", "in", ["GREEN", "YELLOW"], {"zone": "GREEN"}))

    def test_operator_false_when_unmet(self):
        self.assertFalse(condition_passes("x", ">", 10, {"x": 3}))
        self.assertFalse(condition_passes(
            "tags", "contains", "bio", {"tags": ["cs"]}))

    def test_all_operators_registered(self):
        for op in ("==", "!=", "<", ">", "<=", ">=", "contains", "in"):
            self.assertIn(op, OPERATORS)


class RobustnessTest(unittest.TestCase):
    def _multi(self):
        return [
            {"trigger": "e", "conditions": [], "actions": ["a1"]},
            {"trigger": "e", "conditions": [("n", ">", 0)],
             "actions": ["a2", "a3"]},
            {"trigger": "e", "enabled": False, "actions": ["never"]},
        ]

    def test_all_matching_rules_fire_in_order(self):
        self.assertEqual(evaluate("e", {"n": 5}, self._multi()),
                         ["a1", "a2", "a3"])

    def test_disabled_rule_skipped(self):
        self.assertNotIn("never", evaluate("e", {"n": 5}, self._multi()))

    def test_no_rules_returns_empty(self):
        self.assertEqual(evaluate("e", {}, []), [])
        self.assertEqual(evaluate("e", {}, None), [])

    def test_malformed_rules_skipped_no_crash(self):
        bad = [
            {"trigger": "e", "conditions": [("n", "BOGUS", 1)],
             "actions": ["x"]},                        # unknown op
            {"trigger": "e", "conditions": [("missing", "==", 1)],
             "actions": ["y"]},                        # missing fact
            "not a dict",                              # wrong type
            {"trigger": "e", "conditions": [("only", "two")],
             "actions": ["z"]},                        # malformed condition
        ]
        self.assertEqual(evaluate("e", {"n": 1}, bad), [])

    def test_missing_fact_and_unknown_op(self):
        self.assertFalse(condition_passes("nope", "==", 1, {}))
        self.assertFalse(condition_passes("x", "~~", 1, {"x": 1}))

    def test_deterministic(self):
        m = self._multi()
        self.assertEqual(evaluate("e", {"n": 5}, m),
                         evaluate("e", {"n": 5}, m))


class ExplainTest(unittest.TestCase):
    def test_reports_condition_failure(self):
        rule = {"trigger": "e", "conditions": [("n", ">", 0)],
                "actions": ["x"]}
        self.assertIn("condition failed", explain(rule, "e", {"n": -1}))

    def test_reports_trigger_mismatch(self):
        rule = {"trigger": "e", "actions": ["x"]}
        self.assertIn("!= event", explain(rule, "other", {}))

    def test_reports_fires(self):
        rule = {"trigger": "e", "conditions": [], "actions": ["x"]}
        self.assertTrue(explain(rule, "e", {}).startswith("fires"))

    def test_reports_disabled(self):
        rule = {"trigger": "e", "enabled": False, "actions": ["x"]}
        self.assertIn("disabled", explain(rule, "e", {}))


if __name__ == "__main__":
    unittest.main()
