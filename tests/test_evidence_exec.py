from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "evidence_exec.py"


def load_module():
    script_dir = str(SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("plat_evidence_exec", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvidenceExecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_large_output_is_saved_but_excerpt_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.mod.run_command(
                [sys.executable, "-c", "print('x' * 20000)"],
                log_dir=root / "logs",
                context_state=root / "context.json",
                max_return_bytes=4096,
            )
            self.assertEqual(result["exit_code"], 0)
            self.assertGreater(result["total_output_bytes"], 19000)
            self.assertLessEqual(len(result["excerpt"].encode("utf-8")), 4096)
            log_path = Path(result["log_path"])
            self.assertTrue(log_path.exists())
            self.assertGreater(log_path.stat().st_size, 19000)

            state = json.loads((root / "context.json").read_text(encoding="utf-8"))
            self.assertEqual(state["health"]["status"], "GREEN")

    def test_failure_excerpt_keeps_discriminating_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = self.mod.run_command(
                [
                    sys.executable,
                    "-c",
                    "import sys; print('noise'); print('ERROR sentinel', file=sys.stderr); sys.exit(3)",
                ],
                log_dir=root / "logs",
                context_state=root / "context.json",
            )
            self.assertEqual(result["exit_code"], 3)
            self.assertIn("ERROR sentinel", result["excerpt"])


if __name__ == "__main__":
    unittest.main()
