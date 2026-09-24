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

    def make_install(self, name: str, version: str = "2.0.0") -> Path:
        path = Path(self.tmp.name) / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "VERSION").write_text(version + "\n", encoding="utf-8")
        return path

    def read_status(self):
        return json.loads(self.mod.STATUS.read_text(encoding="utf-8"))

    def test_check_interval_is_two_hours(self):
        self.assertEqual(self.mod.CHECK_INTERVAL_SECONDS, 7200)

    def test_version_parser(self):
        self.assertEqual(self.mod.parse_version("v2.0.1"), (2, 0, 1))
        self.assertEqual(self.mod.parse_version("2.0.1-beta.1"), (2, 0, 1))
        self.assertIsNone(self.mod.parse_version("latest"))

    def test_register_install_is_idempotent_and_records_project_root(self):
        project = Path(self.tmp.name) / "project"
        path = project / ".agents" / "skills" / "plat"
        path.mkdir(parents=True, exist_ok=True)
        (path / "VERSION").write_text("2.0.0\n", encoding="utf-8")
        self.mod.register_install(path, "codex", "project", project)
        self.mod.register_install(path, "codex", "project", project)
        data = json.loads(self.mod.REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 2)
        self.assertEqual(len(data["installations"]), 1)
        self.assertEqual(data["installations"][0]["project_root"], str(project.resolve()))

    def test_outdated_install_notifies_once_for_unchanged_set(self):
        path = self.make_install("codex", "2.0.0")
        self.mod.register_install(path, "codex", "global")

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.1", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify") as notify:
            self.assertEqual(self.mod.check_updates(), 0)
            self.assertEqual(self.mod.check_updates(), 0)

        state = self.read_status()
        self.assertTrue(state["update_available"])
        self.assertEqual(state["latest_version"], "2.0.1")
        self.assertEqual(state["check_interval_seconds"], 7200)
        self.assertEqual(notify.call_count, 1)

    def test_same_release_notifies_again_when_outdated_set_changes(self):
        codex = self.make_install("codex", "2.0.0")
        cursor = self.make_install("cursor", "2.0.0")
        self.mod.register_install(codex, "codex", "global")
        self.mod.register_install(cursor, "cursor", "global")

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.1", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify") as notify:
            self.assertEqual(self.mod.check_updates(), 0)
            (codex / "VERSION").write_text("2.0.1\n", encoding="utf-8")
            self.assertEqual(self.mod.check_updates(), 0)

        self.assertEqual(notify.call_count, 2)
        state = self.read_status()
        self.assertEqual(len(state["outdated_installations"]), 1)
        self.assertEqual(state["outdated_installations"][0]["agent"], "cursor")

    def test_current_install_does_not_notify(self):
        path = self.make_install("claude", "2.0.1")
        self.mod.register_install(path, "claude-code", "global")

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.1", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify") as notify:
            self.assertEqual(self.mod.check_updates(), 0)

        self.assertFalse(self.read_status()["update_available"])
        notify.assert_not_called()

    def test_missing_install_is_pruned(self):
        missing = Path(self.tmp.name) / "gone"
        self.mod.REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        self.mod.REGISTRY.write_text(
            json.dumps({
                "version": 2,
                "installations": [{
                    "path": str(missing),
                    "agent": "cursor",
                    "scope": "project",
                    "project_root": str(Path(self.tmp.name) / "project"),
                    "registered_at": "2026-01-01T00:00:00+00:00",
                }],
            }),
            encoding="utf-8",
        )

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.1", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify"):
            self.assertEqual(self.mod.check_updates(), 0)

        registry = json.loads(self.mod.REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["installations"], [])

    def test_native_scope_update_uses_skills_update(self):
        fake = mock.Mock(returncode=0)
        with mock.patch.object(self.mod.shutil, "which", return_value="/usr/bin/npx"), \
             mock.patch.object(self.mod.subprocess, "run", return_value=fake) as run:
            self.mod.run_skills_update(global_scope=True)
            command = run.call_args.args[0]
            self.assertEqual(command[:4], ["/usr/bin/npx", "-y", "skills@latest", "update"])
            self.assertIn("plat", command)
            self.assertIn("-g", command)

    def test_project_scope_update_uses_project_root(self):
        root = Path(self.tmp.name) / "project"
        root.mkdir()
        fake = mock.Mock(returncode=0)
        with mock.patch.object(self.mod.shutil, "which", return_value="/usr/bin/npx"), \
             mock.patch.object(self.mod.subprocess, "run", return_value=fake) as run:
            self.mod.run_skills_update(global_scope=False, project_root=root)
            self.assertEqual(run.call_args.kwargs["cwd"], str(root))
            self.assertIn("-p", run.call_args.args[0])

    def test_update_all_verifies_and_falls_back_per_install(self):
        codex = self.make_install("codex", "2.0.0")
        cursor = self.make_install("cursor", "2.0.0")
        self.mod.register_install(codex, "codex", "global")
        self.mod.register_install(cursor, "cursor", "global")

        def fallback(item):
            Path(item["path"]).joinpath("VERSION").write_text("2.0.1\n", encoding="utf-8")
            return mock.Mock(returncode=0)

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.1", "https://example.test/release")), \
             mock.patch.object(self.mod, "run_skills_update", return_value=mock.Mock(returncode=0)), \
             mock.patch.object(self.mod, "fallback_reinstall", side_effect=fallback) as fallback_mock, \
             mock.patch.object(self.mod, "notify"):
            self.assertEqual(self.mod.update_all_registered(), 0)

        self.assertEqual(fallback_mock.call_count, 2)
        self.assertEqual((codex / "VERSION").read_text().strip(), "2.0.1")
        self.assertEqual((cursor / "VERSION").read_text().strip(), "2.0.1")

    def test_network_failure_is_nonfatal_to_installed_skill_state(self):
        path = self.make_install("codex", "2.0.0")
        self.mod.register_install(path, "codex", "global")

        with mock.patch.object(self.mod, "fetch_latest_release", side_effect=OSError("offline")):
            self.assertEqual(self.mod.check_updates(), 1)

        state = self.read_status()
        self.assertFalse(state["update_available"])
        self.assertIn("OSError", state["last_error"])
        self.assertTrue((path / "VERSION").exists())


if __name__ == "__main__":
    unittest.main()
