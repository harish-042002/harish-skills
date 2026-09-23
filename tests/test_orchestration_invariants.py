from __future__ import annotations

import importlib.util
import itertools
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "skills" / "plat" / "scripts" / "orchestration_policy.py"


def load_policy():
    spec = importlib.util.spec_from_file_location("plat_orchestration_policy_props", POLICY_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class OrchestrationInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_policy()

    def all_decisions(self):
        depths = ["Quick", "Standard", "Deep", "Research"]
        for (
            depth,
            unresolved,
            independent,
            built_in_sufficient,
            external_match,
            mutating,
            shared_state,
            same_question_rounds,
            host_handoff,
            specialist_should_own_turn,
        ) in itertools.product(
            depths,
            range(0, 5),
            range(0, 5),
            [False, True],
            [False, True],
            [False, True],
            [False, True],
            range(0, 3),
            [False, True],
            [False, True],
        ):
            kwargs = dict(
                depth=depth,
                unresolved=unresolved,
                independent=independent,
                built_in_sufficient=built_in_sufficient,
                external_match=external_match,
                mutating=mutating,
                shared_state=shared_state,
                same_question_rounds=same_question_rounds,
                host_handoff=host_handoff,
                specialist_should_own_turn=specialist_should_own_turn,
            )
            yield kwargs, self.mod.decide(**kwargs)

    def test_global_invariants_across_state_space(self):
        checked = 0
        for kwargs, d in self.all_decisions():
            checked += 1

            self.assertFalse(d.recursive_delegation, kwargs)
            self.assertGreaterEqual(d.initial_specialists, 0, kwargs)
            self.assertGreaterEqual(d.max_specialists, d.initial_specialists, kwargs)
            self.assertLessEqual(d.max_specialists, 3, kwargs)
            self.assertGreaterEqual(d.parallel_limit, 0, kwargs)
            self.assertLessEqual(d.parallel_limit, d.max_specialists, kwargs)

            if kwargs["depth"] == "Quick":
                self.assertEqual(d.max_specialists, 0, kwargs)
                self.assertFalse(d.external_skill, kwargs)
                self.assertFalse(d.handoff, kwargs)

            if kwargs["depth"] == "Standard":
                self.assertLessEqual(d.max_specialists, 1, kwargs)
                self.assertLessEqual(d.parallel_limit, 1, kwargs)

            if kwargs["mutating"] or kwargs["shared_state"]:
                self.assertLessEqual(d.parallel_limit, 1, kwargs)

            if kwargs["same_question_rounds"] >= 2:
                self.assertEqual(d.action, "reroute", kwargs)
                self.assertEqual(d.max_specialists, 0, kwargs)
                self.assertFalse(d.external_skill, kwargs)
                self.assertFalse(d.handoff, kwargs)

            if d.external_skill:
                self.assertFalse(kwargs["built_in_sufficient"], kwargs)
                self.assertTrue(kwargs["external_match"], kwargs)
                self.assertEqual(d.action, "consult", kwargs)

            if d.handoff:
                self.assertTrue(kwargs["host_handoff"], kwargs)
                self.assertTrue(kwargs["specialist_should_own_turn"], kwargs)
                self.assertFalse(kwargs["mutating"], kwargs)
                self.assertFalse(kwargs["shared_state"], kwargs)
                self.assertEqual(d.max_specialists, 1, kwargs)
                self.assertEqual(d.lead_control, "handoff", kwargs)
            else:
                self.assertEqual(d.lead_control, "manager", kwargs)

        self.assertGreater(checked, 10000)

    def test_external_skill_is_never_used_only_because_it_exists(self):
        for depth in ["Quick", "Standard", "Deep", "Research"]:
            d = self.mod.decide(
                depth=depth,
                unresolved=1,
                built_in_sufficient=True,
                external_match=True,
            )
            self.assertFalse(d.external_skill, depth)

    def test_parallelism_requires_real_independence(self):
        for depth in ["Deep", "Research"]:
            d = self.mod.decide(
                depth=depth,
                unresolved=3,
                independent=1,
                built_in_sufficient=False,
                external_match=True,
                research_oriented=(depth == "Research"),
            )
            self.assertEqual(d.parallel_limit, 1, depth)


if __name__ == "__main__":
    unittest.main()
