from __future__ import annotations
import importlib.util
import itertools
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "orchestration_policy.py"

def load_module():
    spec = importlib.util.spec_from_file_location("plat_orchestration_policy_props_v21", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class OrchestrationInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_module()

    def test_global_canonical_path_invariants(self):
        checked = 0
        for execution_path, unresolved, independent, health, gap, match, second in itertools.product(
            ["DIRECT", "STANDARD", "ESCALATED"], range(0, 4), range(0, 4),
            ["GREEN", "YELLOW", "RED"], [False, True], [False, True], [False, True]
        ):
            checked += 1
            d = self.policy.decide(
                execution_path=execution_path,
                unresolved=unresolved,
                independent=independent,
                health=health,
                capability_gap=gap,
                built_in_sufficient=not gap,
                external_match=match,
                second_boundary_earned=second,
            )
            self.assertFalse(d.recursive_delegation)
            self.assertLessEqual(d.max_specialists, 2)
            self.assertLessEqual(d.parallel_limit, d.max_specialists)
            if execution_path in {"DIRECT", "STANDARD"}:
                self.assertEqual(d.max_specialists, 0)
                self.assertFalse(d.external_skill)
            if d.external_skill:
                self.assertEqual(execution_path, "ESCALATED")
                self.assertTrue(gap)
                self.assertTrue(match)
        self.assertGreater(checked, 1000)

    def test_research_is_task_type_not_execution_path(self):
        d = self.policy.decide(
            execution_path="ESCALATED",
            research_task=True,
            unresolved=3,
            research_oriented=False,
        )
        self.assertEqual(d.execution_path, "ESCALATED")
        self.assertEqual(d.action, "lead")
        self.assertEqual(d.max_specialists, 0)

    def test_legacy_depth_mapping_remains_compatible(self):
        expected = {
            "Quick": "DIRECT",
            "Standard": "STANDARD",
            "Deep": "ESCALATED",
            "Research": "ESCALATED",
        }
        for depth, path in expected.items():
            d = self.policy.decide(depth=depth, unresolved=0)
            self.assertEqual(d.execution_path, path)

    def test_mutating_work_never_parallelizes_specialists(self):
        d = self.policy.decide(
            execution_path="ESCALATED",
            unresolved=2,
            independent=2,
            second_boundary_earned=True,
            wall_time_critical=True,
            mutating=True,
        )
        self.assertEqual(d.parallel_limit, 1)

if __name__ == "__main__":
    unittest.main()
