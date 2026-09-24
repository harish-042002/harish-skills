from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "host_context.py"


def load_module():
    spec = importlib.util.spec_from_file_location("plat_host_context", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class HostContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_canonical_payload_normalizes_cross_provider_keys(self):
        snapshot = self.mod.normalize(
            {
                "prompt_tokens": 100,
                "completion_tokens": 25,
                "prompt_tokens_details": {"cached_tokens": 80},
                "context_used_tokens": 600,
                "context_limit_tokens": 1000,
            },
            host="any-agent",
            source="test",
        )
        self.assertTrue(snapshot["available"])
        self.assertEqual(snapshot["input_tokens"], 100)
        self.assertEqual(snapshot["output_tokens"], 25)
        self.assertEqual(snapshot["cache_read_tokens"], 80)
        self.assertAlmostEqual(snapshot["context_utilization"], 0.6)

    def test_capabilities_are_dynamic_not_host_hardcoded(self):
        with mock.patch.dict(
            os.environ,
            {
                self.mod.CAPABILITIES_ENV: json.dumps(
                    {
                        "isolated_context": True,
                        "precompact_hook": False,
                        "usage_telemetry": True,
                    }
                )
            },
            clear=False,
        ):
            snapshot = self.mod.normalize({}, host="future-agent", source="test")
        self.assertEqual(
            snapshot["capabilities"],
            {
                "isolated_context": True,
                "precompact_hook": False,
                "usage_telemetry": True,
            },
        )

    def test_transcript_jsonl_sums_unique_usage_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            rows = [
                {
                    "message": {
                        "id": "m1",
                        "usage": {
                            "input_tokens": 10,
                            "output_tokens": 2,
                            "cache_read_input_tokens": 100,
                        },
                    }
                },
                {
                    "message": {
                        "id": "m2",
                        "usage": {
                            "input_tokens": 12,
                            "output_tokens": 3,
                            "cache_creation_input_tokens": 7,
                        },
                    }
                },
                {
                    "message": {
                        "id": "m2",
                        "usage": {
                            "input_tokens": 12,
                            "output_tokens": 3,
                            "cache_creation_input_tokens": 7,
                        },
                    }
                },
            ]
            path.write_text(
                "\n".join(json.dumps(row) for row in rows) + "\n",
                encoding="utf-8",
            )
            parsed = self.mod.parse_jsonl(path)

        self.assertEqual(parsed["records"], 2)
        self.assertEqual(parsed["input_tokens"], 22)
        self.assertEqual(parsed["output_tokens"], 5)
        self.assertEqual(parsed["cache_read_tokens"], 100)
        self.assertEqual(parsed["cache_write_tokens"], 7)

    def test_no_telemetry_is_safe_fallback(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
            self.mod,
            "CANONICAL_FILE",
            Path(tmp) / "missing.json",
        ), mock.patch.dict(os.environ, {}, clear=True):
            snapshot = self.mod.discover(host="unknown-agent")
        self.assertFalse(snapshot["available"])
        self.assertEqual(snapshot["source"], "none")


if __name__ == "__main__":
    unittest.main()
