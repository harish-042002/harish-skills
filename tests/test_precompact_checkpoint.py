from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "precompact_checkpoint.py"


def load_module():
    script_dir = str(SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("plat_precompact", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PrecompactCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_checkpoint_uses_repo_relative_state_and_keeps_small_truth(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".plat").mkdir()
            (root / ".plat/session.json").write_text(
                json.dumps(
                    {
                        "goal": "finish feature",
                        "must": ["preserve API"],
                        "must_not": ["no migration"],
                        "current_slice": "service",
                        "owner": ["src/service.py"],
                        "proof": ["targeted test"],
                        "next": "run proof",
                        "health": {"status": "GREEN"},
                    }
                ),
                encoding="utf-8",
            )
            (root / ".plat/context.json").write_text(
                json.dumps({"health": {"status": "RED"}}),
                encoding="utf-8",
            )
            output = Path(".plat/checkpoints/precompact-latest.json")
            with mock.patch.object(
                self.mod.host_context,
                "discover",
                return_value={
                    "available": True,
                    "host": "test-agent",
                    "source": "test",
                    "cache_read_tokens": 123,
                },
            ), mock.patch.object(
                self.mod,
                "_run_git",
                side_effect=["abc123", "main", " M src/service.py", "1 file changed"],
            ):
                checkpoint = self.mod.create_checkpoint(
                    root=root,
                    session_path=Path(".plat/session.json"),
                    context_path=Path(".plat/context.json"),
                    output=output,
                    host="test-agent",
                )

            written = root / output
            self.assertTrue(written.exists())
            self.assertEqual(checkpoint["task"]["goal"], "finish feature")
            self.assertEqual(checkpoint["health"]["context"]["status"], "RED")
            self.assertEqual(checkpoint["repo"]["head"], "abc123")
            self.assertNotIn("accepted_evidence", checkpoint["task"])


if __name__ == "__main__":
    unittest.main()
