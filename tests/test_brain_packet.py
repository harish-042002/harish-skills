from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "brain_packet.py"


def load_module():
    spec = importlib.util.spec_from_file_location("plat_brain_packet", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class BrainPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_packet_is_hard_capped(self):
        state = {
            "goal": "g" * 5000,
            "must": ["m" * 1200 for _ in range(10)],
            "must_not": ["n" * 1200 for _ in range(10)],
            "current_slice": "slice" * 1000,
            "owner": ["owner" * 500 for _ in range(8)],
            "proof": ["proof" * 500 for _ in range(8)],
            "next": "next" * 1000,
            "health": {"status": "RED", "reason": "r" * 2000},
            "execution": {
                "failed_hypotheses": 2,
                "reroutes": 2,
                "brain_reviews": 1,
            },
            "accepted_evidence": ["SHOULD_NOT_BE_COPIED" * 1000],
        }
        packet = self.mod.build_packet(
            state,
            question="q" * 5000,
            evidence=["e" * 2000 for _ in range(10)],
            max_bytes=4096,
        )
        rendered = json.dumps(packet, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self.assertLessEqual(len(rendered), 4096)
        self.assertNotIn("SHOULD_NOT_BE_COPIED", rendered.decode("utf-8"))

    def test_packet_keeps_core_course_correction_fields(self):
        state = {
            "goal": "Fix regression",
            "must": ["keep API stable"],
            "must_not": ["no schema change"],
            "current_slice": "tap handling",
            "owner": ["notification_service.dart"],
            "proof": ["tap test"],
            "next": "rerun selector suite",
            "health": {"status": "RED", "reason": "two failed hypotheses"},
            "execution": {"failed_hypotheses": 2, "reroutes": 1, "brain_reviews": 0},
        }
        packet = self.mod.build_packet(
            state,
            question="What is the smallest corrective direction?",
            evidence=["log:.plat/logs/evidence-1.log#L20-L35"],
        )
        self.assertEqual(packet["goal"], "Fix regression")
        self.assertEqual(packet["trajectory"]["failed_hypotheses"], 2)
        self.assertEqual(packet["evidence"][0], "log:.plat/logs/evidence-1.log#L20-L35")


if __name__ == "__main__":
    unittest.main()
