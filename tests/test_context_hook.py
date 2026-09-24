from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "context_hook.py"


def load_module():
    script_dir = str(SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("plat_context_hook", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ContextHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_precompact_alias_is_handled(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            self.mod.precompact_checkpoint,
            "create_checkpoint",
            return_value={"created_at": "2026-09-24T00:00:00+00:00"},
        ) as create:
            result = self.mod.handle(
                {"hook_event_name": "PreCompact"},
                root=Path(tmp),
                host="claude-code",
            )
        self.assertTrue(result["handled"])
        create.assert_called_once()

    def test_unknown_event_is_noop(self):
        result = self.mod.handle(
            {"event": "PostToolUse"},
            root=Path("."),
            host="future-agent",
        )
        self.assertFalse(result["handled"])


if __name__ == "__main__":
    unittest.main()
