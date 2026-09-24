from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "context_guard.py"


def load_module():
    spec = importlib.util.spec_from_file_location("plat_context_guard", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ContextGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_new_state_is_green(self):
        state = self.mod.new_state()
        self.assertEqual(state["health"]["status"], "GREEN")
        self.assertEqual(state["returned_bytes"], 0)

    def test_yellow_on_returned_byte_pressure(self):
        state = self.mod.new_state()
        state = self.mod.record(
            state,
            returned_bytes=self.mod.YELLOW_RETURNED_BYTES,
            kind="command",
        )
        self.assertEqual(state["health"]["status"], "YELLOW")
        self.assertEqual(state["health"]["action"], "summarize-use-pointers")

    def test_red_recommends_one_fresh_context_worker(self):
        state = self.mod.new_state()
        state = self.mod.record(
            state,
            returned_bytes=self.mod.RED_RETURNED_BYTES,
            kind="command",
        )
        self.assertEqual(state["health"]["status"], "RED")
        self.assertEqual(state["health"]["action"], "fresh-context-worker")

        state = self.mod.record_fresh_context_worker(state)
        self.assertEqual(state["health"]["status"], "RED")
        self.assertEqual(state["health"]["action"], "checkpoint-compact")

    def test_repeated_reads_raise_pressure(self):
        state = self.mod.new_state()
        for _ in range(3):
            state = self.mod.record(
                state,
                returned_bytes=100,
                kind="read",
                key="src/service.py:1-200",
            )
        self.assertEqual(state["repeated_reads"], 2)
        self.assertEqual(state["health"]["status"], "YELLOW")

    def test_second_broad_suite_is_yellow(self):
        state = self.mod.new_state()
        state = self.mod.record(state, returned_bytes=100, kind="test", broad_suite=True)
        self.assertEqual(state["health"]["status"], "GREEN")
        state = self.mod.record(state, returned_bytes=100, kind="test", broad_suite=True)
        self.assertEqual(state["health"]["status"], "YELLOW")


if __name__ == "__main__":
    unittest.main()
