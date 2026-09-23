#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "skills" / "plat" / "scripts" / "update_check.py"


def load_module():
    spec = importlib.util.spec_from_file_location("plat_update_check", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class UpdateCheckTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.mod.PLAT_HOME = base / ".plat"
        self.mod.BIN_DIR = self.mod.PLAT_HOME / "bin"
        self.mod.LOG_DIR = self.mod.PLAT_HOME / "logs"
        self.mod.REGISTRY = self.mod.PLAT_HOME / "installations.json"
        self.mod.STATUS = self.mod.PLAT_HOME / "update-status.json"
        self.mod.PERSISTED_SCRIPT = self.mod.BIN_DIR / "update_check.py"

    def tearDown(self):
        self.tmp.cleanup()

    def make_install(self, version: str = "1.0.0") -> Path:
        path = Path(self.tmp.name) / "skill"
        path.mkdir(parents=True, exist_ok=True)
        (path / "VERSION").write_text(version + "\n", encoding="utf-8")
        return path

    def read_status(self):
        return json.loads(self.mod.STATUS.read_text(encoding="utf-8"))

    def test_version_parser(self):
        self.assertEqual(self.mod.parse_version("v1.2.3"), (1, 2, 3))
        self.assertEqual(self.mod.parse_version("1.2.3-beta.1"), (1, 2, 3))
        self.assertIsNone(self.mod.parse_version("latest"))

    def test_register_install_is_idempotent_for_same_path(self):
        path = self.make_install("1.3.2")
        self.mod.register_install(path, "codex", "project")
        self.mod.register_install(path, "codex", "project")
        data = json.loads(self.mod.REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(len(data["installations"]), 1)
        self.assertEqual(data["installations"][0]["path"], str(path.resolve()))

    def test_outdated_install_notifies_once_and_caches_status(self):
        path = self.make_install("1.3.2")
        self.mod.register_install(path, "codex", "project")

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("1.4.0", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify") as notify:
            self.assertEqual(self.mod.check_updates(), 0)
            self.assertEqual(self.mod.check_updates(), 0)

        state = self.read_status()
        self.assertTrue(state["update_available"])
        self.assertEqual(state["latest_version"], "1.4.0")
        self.assertEqual(state["last_notified_version"], "1.4.0")
        self.assertEqual(notify.call_count, 1)

    def test_current_install_does_not_notify(self):
        path = self.make_install("1.4.0")
        self.mod.register_install(path, "claude-code", "global")

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("1.4.0", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify") as notify:
            self.assertEqual(self.mod.check_updates(), 0)

        self.assertFalse(self.read_status()["update_available"])
        notify.assert_not_called()

    def test_missing_install_is_pruned(self):
        missing = Path(self.tmp.name) / "gone"
        self.mod.REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        self.mod.REGISTRY.write_text(
            json.dumps({
                "version": 1,
                "installations": [{
                    "path": str(missing),
                    "agent": "cursor",
                    "scope": "project",
                    "registered_at": "2026-01-01T00:00:00+00:00",
                }],
            }),
            encoding="utf-8",
        )

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("1.4.0", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify"):
            self.assertEqual(self.mod.check_updates(), 0)

        registry = json.loads(self.mod.REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["installations"], [])

    def test_network_failure_is_nonfatal_to_installed_skill_state(self):
        path = self.make_install("1.3.2")
        self.mod.register_install(path, "codex", "project")

        with mock.patch.object(self.mod, "fetch_latest_release", side_effect=OSError("offline")):
            self.assertEqual(self.mod.check_updates(), 1)

        state = self.read_status()
        self.assertFalse(state["update_available"])
        self.assertIn("OSError", state["last_error"])
        self.assertTrue((path / "VERSION").exists())


if __name__ == "__main__":
    unittest.main()
