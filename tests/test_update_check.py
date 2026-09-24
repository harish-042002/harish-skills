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

    def make_install(self, name: str, version: str = "2.0.1") -> Path:
        path = Path(self.tmp.name) / name
        path.mkdir(parents=True, exist_ok=True)
        (path / "VERSION").write_text(version + "\n", encoding="utf-8")
        (path / "SKILL.md").write_text("---\nname: plat\ndescription: test\n---\n", encoding="utf-8")
        return path

    def read_status(self):
        return json.loads(self.mod.STATUS.read_text(encoding="utf-8"))

    def test_check_interval_is_two_hours(self):
        self.assertEqual(self.mod.CHECK_INTERVAL_SECONDS, 7200)

    def test_version_parser(self):
        self.assertEqual(self.mod.parse_version("v2.0.2"), (2, 0, 2))
        self.assertEqual(self.mod.parse_version("2.0.2-beta.1"), (2, 0, 2))
        self.assertIsNone(self.mod.parse_version("latest"))

    def test_register_install_is_idempotent_and_schema_v3(self):
        project = Path(self.tmp.name) / "project"
        path = project / ".agents" / "skills" / "plat"
        path.mkdir(parents=True, exist_ok=True)
        (path / "VERSION").write_text("2.0.1\n", encoding="utf-8")
        self.mod.register_install(path, "kiro-cli", "project", project, agents=["Kiro CLI"])
        self.mod.register_install(path, "kiro-cli", "project", project, agents=["Kiro CLI"])
        data = json.loads(self.mod.REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 3)
        self.assertEqual(len(data["installations"]), 1)
        self.assertEqual(data["installations"][0]["agents"], ["Kiro CLI"])
        self.assertEqual(data["installations"][0]["project_root"], str(project.resolve()))

    def test_run_skills_list_uses_json_and_scope(self):
        payload = json.dumps([{
            "name": "plat",
            "path": "/tmp/plat",
            "scope": "global",
            "agents": ["Codex", "Kiro CLI"],
        }])
        completed = mock.Mock(returncode=0, stdout=payload, stderr="")
        with mock.patch.object(self.mod.shutil, "which", return_value="/usr/bin/npx"), \
             mock.patch.object(self.mod.subprocess, "run", return_value=completed) as run:
            rows = self.mod.run_skills_list(scope="global")

        self.assertEqual(rows[0]["agents"], ["Codex", "Kiro CLI"])
        command = run.call_args.args[0]
        self.assertIn("list", command)
        self.assertIn("--json", command)
        self.assertIn("-g", command)

    def test_register_scope_accepts_any_upstream_agent_group(self):
        path = self.make_install("plat-any", "2.0.1")
        rows = [{
            "name": "plat",
            "path": str(path),
            "scope": "global",
            "agents": ["Antigravity", "Cline", "OpenCode", "Qwen Code"],
        }]
        with mock.patch.object(self.mod, "run_skills_list", return_value=rows):
            registered = self.mod.register_scope("global", "*")

        self.assertEqual(len(registered), 1)
        registry = json.loads(self.mod.REGISTRY.read_text(encoding="utf-8"))
        item = registry["installations"][0]
        self.assertEqual(item["agent"], "*")
        self.assertEqual(item["agents"], ["Antigravity", "Cline", "OpenCode", "Qwen Code"])

    def test_display_installation_uses_agent_group_not_hardcoded_selector(self):
        item = {"agent": "*", "agents": ["A", "B", "C", "D", "E"]}
        self.assertEqual(self.mod.display_installation(item), "A, B, C, D +1 more")

    def test_outdated_install_notifies_once_for_unchanged_set(self):
        path = self.make_install("codex", "2.0.1")
        self.mod.register_install(path, "codex", "global", agents=["Codex"])

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.2", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify") as notify:
            self.assertEqual(self.mod.check_updates(), 0)
            self.assertEqual(self.mod.check_updates(), 0)

        state = self.read_status()
        self.assertTrue(state["update_available"])
        self.assertEqual(state["latest_version"], "2.0.2")
        self.assertEqual(state["check_interval_seconds"], 7200)
        self.assertEqual(notify.call_count, 1)

    def test_same_release_notifies_again_when_outdated_set_changes(self):
        codex = self.make_install("codex", "2.0.1")
        cursor = self.make_install("cursor", "2.0.1")
        self.mod.register_install(codex, "codex", "global", agents=["Codex"])
        self.mod.register_install(cursor, "cursor", "global", agents=["Cursor"])

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.2", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify") as notify:
            self.assertEqual(self.mod.check_updates(), 0)
            (codex / "VERSION").write_text("2.0.2\n", encoding="utf-8")
            self.assertEqual(self.mod.check_updates(), 0)

        self.assertEqual(notify.call_count, 2)
        state = self.read_status()
        self.assertEqual(len(state["outdated_installations"]), 1)
        self.assertEqual(state["outdated_installations"][0]["agent"], "cursor")

    def test_current_install_does_not_notify(self):
        path = self.make_install("claude", "2.0.2")
        self.mod.register_install(path, "claude-code", "global", agents=["Claude Code"])

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.2", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify") as notify:
            self.assertEqual(self.mod.check_updates(), 0)

        self.assertFalse(self.read_status()["update_available"])
        notify.assert_not_called()

    def test_missing_install_is_pruned_and_registry_migrates_to_v3(self):
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

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.2", "https://example.test/release")), \
             mock.patch.object(self.mod, "notify"):
            self.assertEqual(self.mod.check_updates(), 0)

        registry = json.loads(self.mod.REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["version"], 3)
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

    def test_fallback_reinstall_accepts_arbitrary_agent_id(self):
        fake = mock.Mock(returncode=0)
        item = {"agent": "antigravity", "scope": "global", "path": "/tmp/plat"}
        with mock.patch.object(self.mod.shutil, "which", return_value="/usr/bin/npx"), \
             mock.patch.object(self.mod.subprocess, "run", return_value=fake) as run:
            self.mod.fallback_reinstall(item)
        command = run.call_args.args[0]
        idx = command.index("-a")
        self.assertEqual(command[idx + 1], "antigravity")

    def test_fallback_reinstall_wildcard_installs_all_supported_agents(self):
        fake = mock.Mock(returncode=0)
        item = {"agent": "*", "scope": "global", "path": "/tmp/plat"}
        with mock.patch.object(self.mod.shutil, "which", return_value="/usr/bin/npx"), \
             mock.patch.object(self.mod.subprocess, "run", return_value=fake) as run:
            self.mod.fallback_reinstall(item)
        command = run.call_args.args[0]
        idx = command.index("-a")
        self.assertEqual(command[idx + 1], "*")

    def test_update_all_verifies_and_falls_back_per_group(self):
        group = self.make_install("all-agents", "2.0.1")
        self.mod.register_install(group, "*", "global", agents=["Codex", "Kiro CLI", "OpenCode"])

        def fallback(item):
            Path(item["path"]).joinpath("VERSION").write_text("2.0.2\n", encoding="utf-8")
            return mock.Mock(returncode=0)

        with mock.patch.object(self.mod, "fetch_latest_release", return_value=("2.0.2", "https://example.test/release")), \
             mock.patch.object(self.mod, "run_skills_update", return_value=mock.Mock(returncode=0)), \
             mock.patch.object(self.mod, "fallback_reinstall", side_effect=fallback) as fallback_mock, \
             mock.patch.object(self.mod, "notify"):
            self.assertEqual(self.mod.update_all_registered(), 0)

        self.assertEqual(fallback_mock.call_count, 1)
        self.assertEqual((group / "VERSION").read_text().strip(), "2.0.2")

    def test_network_failure_is_nonfatal_to_installed_skill_state(self):
        path = self.make_install("codex", "2.0.1")
        self.mod.register_install(path, "codex", "global", agents=["Codex"])

        with mock.patch.object(self.mod, "fetch_latest_release", side_effect=OSError("offline")):
            self.assertEqual(self.mod.check_updates(), 1)

        state = self.read_status()
        self.assertFalse(state["update_available"])
        self.assertIn("OSError", state["last_error"])
        self.assertTrue((path / "VERSION").exists())


if __name__ == "__main__":
    unittest.main()
