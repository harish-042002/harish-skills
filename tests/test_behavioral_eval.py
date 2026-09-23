from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks" / "behavioral-v1.8"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BehavioralEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = load_module("plat_behavioral_runner", BENCH / "run_behavioral_eval.py")
        cls.scorer = load_module("plat_behavioral_scorer", BENCH / "score_results.py")

    def test_case_pack_is_frozen_and_multi_turn(self):
        cases = self.runner.load_cases(BENCH / "cases.json")
        self.assertGreaterEqual(len(cases), 5)
        self.assertTrue(any(len(c["turns"]) >= 3 for c in cases))
        self.assertIn("aws-sqs-durable-idempotency", {c["id"] for c in cases})

    def test_trigger_pack_has_positive_negative_and_aws_cases(self):
        data = json.loads((BENCH / "trigger-cases.json").read_text(encoding="utf-8"))
        cases = data["cases"]
        self.assertGreaterEqual(len(cases), 20)
        self.assertTrue(any(c["expect_plat"] is False for c in cases))
        self.assertTrue(any(c["expect_aws_deep"] is True for c in cases))
        self.assertTrue(any(c["expect_depth"] == "Quick" and not c["expect_aws_deep"] for c in cases if c["expect_plat"]))

    def test_scope_allowlist_uses_globs(self):
        self.assertTrue(self.runner.allowed_path("src/app.py", ["src/*.py"]))
        self.assertFalse(self.runner.allowed_path("infra/app.tf", ["src/*.py"]))

    def test_score_summary_separates_conditions(self):
        rows = [
            {"condition":"plat","passed":True,"changed_files":["a.py"],"lines_added":2,"lines_deleted":1,"wall_seconds":3,"telemetry":{"tool_calls":4}},
            {"condition":"plat","passed":False,"changed_files":["a.py","b.py"],"lines_added":4,"lines_deleted":0,"wall_seconds":5,"telemetry":{"tool_calls":8}},
            {"condition":"no-plat","passed":True,"changed_files":["a.py"],"lines_added":1,"lines_deleted":1,"wall_seconds":2,"telemetry":{"tool_calls":2}},
        ]
        out = self.scorer.summarize(rows)
        self.assertEqual(out["plat"]["runs"], 2)
        self.assertEqual(out["plat"]["passed"], 1)
        self.assertEqual(out["plat"]["pass_rate"], 0.5)
        self.assertEqual(out["plat"]["mean_telemetry"]["tool_calls"], 6.0)
        self.assertEqual(out["no-plat"]["pass_rate"], 1.0)

    def test_plan_case_fixtures_have_verifiers(self):
        for case in self.runner.load_cases(BENCH / "cases.json"):
            fixture = BENCH / case["fixture"]
            self.assertTrue((fixture / "verify.py").exists())


if __name__ == "__main__":
    unittest.main()
