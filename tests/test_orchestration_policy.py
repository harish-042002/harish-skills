from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "orchestration_policy.py"

def load_module():
    spec = importlib.util.spec_from_file_location("plat_orchestration_policy_v2", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class OrchestrationPolicyV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_module()

    def test_direct_and_standard_are_single_agent(self):
        for execution_path in ["DIRECT", "STANDARD"]:
            d = self.policy.decide(execution_path=execution_path, unresolved=5, capability_gap=True, built_in_sufficient=False, external_match=True)
            self.assertEqual(d.max_specialists, 0)
            self.assertFalse(d.external_skill)

    def test_deep_starts_with_one(self):
        d = self.policy.decide(execution_path="ESCALATED", unresolved=4, independent=4)
        self.assertEqual(d.initial_specialists, 1)
        self.assertEqual(d.max_specialists, 1)
        self.assertEqual(d.parallel_limit, 1)

    def test_second_specialist_requires_earned_boundary(self):
        d = self.policy.decide(execution_path="ESCALATED", unresolved=2, independent=2, second_boundary_earned=True, wall_time_critical=True)
        self.assertEqual(d.max_specialists, 2)
        self.assertEqual(d.parallel_limit, 2)

    def test_external_skill_requires_real_capability_gap(self):
        no_gap = self.policy.decide(execution_path="ESCALATED", unresolved=1, built_in_sufficient=False, external_match=True, capability_gap=False)
        self.assertFalse(no_gap.external_skill)
        gap = self.policy.decide(execution_path="ESCALATED", unresolved=1, built_in_sufficient=False, external_match=True, capability_gap=True)
        self.assertTrue(gap.external_skill)

    def test_research_orients_before_consulting(self):
        d = self.policy.decide(execution_path="ESCALATED", research_task=True, unresolved=3, research_oriented=False)
        self.assertEqual(d.action, "lead")
        self.assertEqual(d.max_specialists, 0)

    def test_red_health_triggers_brain_until_budget(self):
        d = self.policy.decide(execution_path="STANDARD", unresolved=1, health="RED", brain_reviews=1)
        self.assertTrue(d.brain_review)
        capped = self.policy.decide(execution_path="STANDARD", unresolved=1, health="RED", brain_reviews=2)
        self.assertFalse(capped.brain_review)
        self.assertIn("brain-budget-exhausted", capped.reason_codes)

    def test_model_policy_is_capability_based(self):
        d = self.policy.decide(execution_path="STANDARD")
        self.assertEqual(d.worker_tier, "cost-efficient-latest")
        self.assertEqual(d.brain_tier, "one-tier-stronger-cost-effective")

    def test_same_question_circuit_breaker(self):
        d = self.policy.decide(execution_path="ESCALATED", unresolved=2, same_question_rounds=2)
        self.assertEqual(d.action, "reroute")
        self.assertEqual(d.max_specialists, 0)

    def test_blocked_surfaces_without_delegation(self):
        d = self.policy.decide(execution_path="ESCALATED", unresolved=2, health="BLOCKED")
        self.assertEqual(d.action, "surface-blocker")
        self.assertEqual(d.max_specialists, 0)

if __name__ == "__main__":
    unittest.main()
