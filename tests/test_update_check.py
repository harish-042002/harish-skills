#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import plistlib
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "plat" / "scripts" / "update_check.py"

spec = importlib.util.spec_from_file_location("plat_update_check", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

assert module.parse_version("1.3.0") == (1, 3, 0)
assert module.parse_version("v2.0.1") == (2, 0, 1)
assert module.parse_version("invalid") is None

tmp = Path(tempfile.mkdtemp(prefix="plat-update-test-"))
module.PLAT_HOME = tmp / ".plat"
module.BIN_DIR = module.PLAT_HOME / "bin"
module.LOG_DIR = module.PLAT_HOME / "logs"
module.REGISTRY = module.PLAT_HOME / "installations.json"
module.STATUS = module.PLAT_HOME / "update-status.json"
module.PERSISTED_SCRIPT = module.BIN_DIR / "update_check.py"

skill = tmp / "skill"
skill.mkdir(parents=True)
(skill / "VERSION").write_text("1.3.0\n", encoding="utf-8")

module.register_install(skill, "codex", "project")
registry = json.loads(module.REGISTRY.read_text(encoding="utf-8"))
assert len(registry["installations"]) == 1
assert registry["installations"][0]["agent"] == "codex"

notifications = []
module.fetch_latest_release = lambda: ("1.3.1", "https://example.test/release")
module.notify = lambda title, message: notifications.append((title, message))

assert module.check_updates() == 0
status = json.loads(module.STATUS.read_text(encoding="utf-8"))
assert status["update_available"] is True
assert status["latest_version"] == "1.3.1"
assert len(notifications) == 1

# Same release should not notify repeatedly.
assert module.check_updates() == 0
assert len(notifications) == 1

# Once installed version catches up, cached status becomes current.
(skill / "VERSION").write_text("1.3.1\n", encoding="utf-8")
assert module.check_updates() == 0
status = json.loads(module.STATUS.read_text(encoding="utf-8"))
assert status["update_available"] is False

# macOS scheduler contract: one run every 86400 seconds, no prompt process involved.
class Result:
    returncode = 0

calls = []
def fake_run(args, **kwargs):
    calls.append(args)
    return Result()

module.PERSISTED_SCRIPT = tmp / ".plat" / "bin" / "update_check.py"
module.LOG_DIR = tmp / ".plat" / "logs"
with patch.object(module.Path, "home", return_value=tmp),      patch.object(module.os, "getuid", return_value=501),      patch.object(module.subprocess, "run", side_effect=fake_run):
    module.sys.executable = "/usr/bin/python3"
    module.install_macos_scheduler()

plist = tmp / "Library" / "LaunchAgents" / f"{module.LABEL}.plist"
payload = plistlib.loads(plist.read_bytes())
assert payload["StartInterval"] == 86400
assert payload["ProgramArguments"][-1] == "--run"

print("Plat update-check tests passed")
