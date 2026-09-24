from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "task_state.py"

def load_module():
    spec = importlib.util.spec_from_file_location("plat_task_state", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class TaskStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_new_state_defaults_to_generic_model_tiers(self):
        state = self.mod.new_state("Fix the thing", started_at="2026-09-24T10:00:00+00:00")
        self.assertEqual(state["execution"]["worker_tier"], "cost-efficient-latest")
        self.assertEqual(state["execution"]["brain_tier"], "one-tier-stronger-cost-effective")
        self.assertEqual(state["health"]["status"], "GREEN")

    def test_checkpoint_is_cheap_before_five_minutes(self):
        state = self.mod.new_state("x", started_at="2026-09-24T10:00:00+00:00")
        result = self.mod.evaluate_checkpoint(state, at="2026-09-24T10:04:59+00:00")
        self.assertFalse(result["due"])

    def test_progress_resets_health(self):
        state = self.mod.new_state("x", started_at="2026-09-24T10:00:00+00:00")
        result = self.mod.evaluate_checkpoint(state, at="2026-09-24T10:10:00+00:00", meaningful_progress=True)
        self.assertEqual(result["state"]["health"]["status"], "GREEN")
        self.assertEqual(result["since_progress"], 0)

    def test_ten_minutes_without_progress_is_yellow(self):
        state = self.mod.new_state("x", started_at="2026-09-24T10:00:00+00:00")
        result = self.mod.evaluate_checkpoint(state, at="2026-09-24T10:10:00+00:00")
        self.assertEqual(result["state"]["health"]["status"], "YELLOW")
        self.assertEqual(result["state"]["health"]["action"], "self-correct")

    def test_twenty_minutes_without_progress_requests_brain(self):
        state = self.mod.new_state("x", started_at="2026-09-24T10:00:00+00:00")
        result = self.mod.evaluate_checkpoint(state, at="2026-09-24T10:20:00+00:00")
        self.assertEqual(result["state"]["health"]["status"], "RED")
        self.assertEqual(result["state"]["health"]["action"], "brain-review")

    def test_brain_budget_caps_at_two(self):
        state = self.mod.new_state("x", started_at="2026-09-24T10:00:00+00:00")
        self.mod.record_brain_review(state)
        self.mod.record_brain_review(state)
        self.mod.record_brain_review(state)
        self.assertEqual(state["execution"]["brain_reviews"], 2)
        self.assertEqual(state["health"]["action"], "reroute-or-surface-blocker")

if __name__ == "__main__":
    unittest.main()
