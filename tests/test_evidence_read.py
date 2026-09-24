from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "evidence_read.py"


def load_module():
    script_dir = str(SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("plat_evidence_read", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EvidenceReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_second_unchanged_read_is_masked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.py"
            source.write_text("a\nb\nc\n", encoding="utf-8")
            kwargs = {
                "index_path": root / "index.json",
                "context_state": root / "context.json",
                "max_return_bytes": 2048,
            }
            first = self.mod.read_evidence(source, **kwargs)
            second = self.mod.read_evidence(source, **kwargs)

        self.assertFalse(first["masked"])
        self.assertIn("content", first)
        self.assertTrue(second["masked"])
        self.assertNotIn("content", second)
        self.assertEqual(first["sha256"], second["sha256"])

    def test_changed_range_is_returned_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.py"
            source.write_text("old\n", encoding="utf-8")
            kwargs = {
                "index_path": root / "index.json",
                "context_state": root / "context.json",
                "max_return_bytes": 2048,
            }
            self.mod.read_evidence(source, **kwargs)
            source.write_text("new\n", encoding="utf-8")
            second = self.mod.read_evidence(source, **kwargs)

        self.assertFalse(second["masked"])
        self.assertIn("new", second["content"])

    def test_visible_read_response_is_hard_capped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "big.txt"
            source.write_text("x" * 30000, encoding="utf-8")
            result = self.mod.read_evidence(
                source,
                index_path=root / "index.json",
                context_state=root / "context.json",
                max_return_bytes=2048,
            )
            encoded = json.dumps(
                result,
                indent=2,
                sort_keys=True,
            ).encode("utf-8")

        self.assertLessEqual(len(encoded), 2048)


if __name__ == "__main__":
    unittest.main()
