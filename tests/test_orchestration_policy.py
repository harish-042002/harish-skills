from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "skills" / "plat" / "scripts" / "orchestration_policy.py"
CASES_PATH = ROOT / "tests" / "orchestration-cases.json"


def load_policy():
    spec = importlib.util.spec_from_file_location("plat_orchestration_policy", POLICY_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class OrchestrationPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_policy()
        cls.cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))["cases"]

    def test_frozen_cases(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                decision = self.mod.decide(**case["input"])
                actual = decision.__dict__
                for key, expected in case["expect"].items():
                    self.assertEqual(actual[key], expected)

    def test_invalid_depth_rejected(self):
        with self.assertRaises(ValueError):
            self.mod.decide(depth="Maximum", unresolved=1)

    def test_negative_counts_rejected(self):
        with self.assertRaises(ValueError):
            self.mod.decide(depth="Deep", unresolved=-1)

    def test_manager_is_default(self):
        decision = self.mod.decide(
            depth="Deep",
            unresolved=2,
            independent=2,
            built_in_sufficient=False,
            external_match=True,
        )
        self.assertEqual(decision.lead_control, "manager")
        self.assertFalse(decision.handoff)
        self.assertFalse(decision.recursive_delegation)


if __name__ == "__main__":
    unittest.main()
