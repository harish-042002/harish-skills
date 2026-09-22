#!/usr/bin/env python3
"""Daily out-of-band Plat release checker.

Runs from an OS scheduler installed by Plat's installer. It never runs inside
normal engineering prompts, so update discovery adds no model/tool overhead.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import platform
import plistlib
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.request

REPO = "harish-042002/harish-skills"
LATEST_RELEASE_API = f"https://api.github.com/repos/{REPO}/releases/latest"
PLAT_HOME = Path.home() / ".plat"
BIN_DIR = PLAT_HOME / "bin"
LOG_DIR = PLAT_HOME / "logs"
REGISTRY = PLAT_HOME / "installations.json"
STATUS = PLAT_HOME / "update-status.json"
PERSISTED_SCRIPT = BIN_DIR / "update_check.py"
LABEL = "com.plat.daily-update-check"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp_name, path)
    finally:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass


def parse_version(value: str):
    m = re.match(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$", value.strip())
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def read_installed_version(skill_dir: Path) -> str | None:
    try:
        value = (skill_dir / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value if parse_version(value) else None


def fetch_latest_release() -> tuple[str, str]:
    req = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "plat-daily-update-check",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        payload = json.load(response)
    version = str(payload.get("tag_name", "")).strip()
    if not parse_version(version):
        raise RuntimeError(f"Invalid release tag returned by GitHub: {version!r}")
    return version.lstrip("v"), str(payload.get("html_url", ""))


def persist_self() -> None:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    src = Path(__file__).resolve()
    dst = PERSISTED_SCRIPT.resolve() if PERSISTED_SCRIPT.exists() else PERSISTED_SCRIPT
    if src != dst:
        shutil.copy2(src, PERSISTED_SCRIPT)
    try:
        PERSISTED_SCRIPT.chmod(0o755)
    except OSError:
        pass


def register_install(skill_dir: Path, agent: str, scope: str) -> None:
    skill_dir = skill_dir.expanduser().resolve()
    data = load_json(REGISTRY, {"version": 1, "installations": []})
    items = data.get("installations", [])
    items = [x for x in items if x.get("path") != str(skill_dir)]
    items.append(
        {
            "path": str(skill_dir),
            "agent": agent,
            "scope": scope,
            "registered_at": now_iso(),
        }
    )
    data["version"] = 1
    data["installations"] = items
    write_json(REGISTRY, data)


def notify(title: str, message: str) -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            script = (
                'display notification '
                + json.dumps(message)
                + ' with title '
                + json.dumps(title)
            )
            subprocess.run(
                ["osascript", "-e", script],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Linux" and shutil.which("notify-send"):
            subprocess.run(
                ["notify-send", title, message],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Windows":
            subprocess.run(
                ["msg", "*", f"{title}: {message}"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except OSError:
        pass


def check_updates() -> int:
    previous = load_json(STATUS, {})
    registry = load_json(REGISTRY, {"installations": []})
    active = []
    for item in registry.get("installations", []):
        skill_dir = Path(str(item.get("path", ""))).expanduser()
        version = read_installed_version(skill_dir)
        if version:
            active.append({**item, "installed_version": version})

    # Prune paths that no longer contain an installed Plat skill.
    registry["installations"] = [
        {k: v for k, v in item.items() if k != "installed_version"} for item in active
    ]
    write_json(REGISTRY, registry)

    state = {
        "checked_at": now_iso(),
        "update_available": False,
        "installations": active,
        "last_notified_version": previous.get("last_notified_version"),
    }

    try:
        latest, release_url = fetch_latest_release()
        state["latest_version"] = latest
        state["release_url"] = release_url
        latest_tuple = parse_version(latest)
        outdated = [
            item
            for item in active
            if latest_tuple
            and parse_version(item["installed_version"])
            and parse_version(item["installed_version"]) < latest_tuple
        ]
        state["update_available"] = bool(outdated)
        state["outdated_installations"] = outdated

        if outdated and previous.get("last_notified_version") != latest:
            notify(
                "Plat update available",
                f"Plat v{latest} is available. Re-run the Plat installer to update.",
            )
            state["last_notified_version"] = latest
    except Exception as exc:
        state["last_error"] = f"{type(exc).__name__}: {exc}"
        # A failed background check must never affect engineering work.
        write_json(STATUS, state)
        return 1

    write_json(STATUS, state)
    return 0


def install_macos_scheduler() -> str:
    launch_agents = Path.home() / "Library" / "LaunchAgents"
    launch_agents.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    plist_path = launch_agents / f"{LABEL}.plist"
    payload = {
        "Label": LABEL,
        "ProgramArguments": [sys.executable, str(PERSISTED_SCRIPT), "--run"],
        "StartInterval": 86400,
        "StandardOutPath": str(LOG_DIR / "update-check.log"),
        "StandardErrorPath": str(LOG_DIR / "update-check.err.log"),
        "ProcessType": "Background",
    }
    with plist_path.open("wb") as fh:
        plistlib.dump(payload, fh)

    uid = os.getuid()
    subprocess.run(
        ["launchctl", "bootout", f"gui/{uid}/{LABEL}"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    result = subprocess.run(
        ["launchctl", "bootstrap", f"gui/{uid}", str(plist_path)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if result.returncode != 0:
        # Compatibility fallback for older macOS launchctl behavior.
        result = subprocess.run(
            ["launchctl", "load", "-w", str(plist_path)],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if result.returncode != 0:
        raise RuntimeError(f"Could not register LaunchAgent: {plist_path}")
    return f"LaunchAgent {plist_path}"


def install_linux_scheduler() -> str:
    python = shlex.quote(sys.executable)
    script = shlex.quote(str(PERSISTED_SCRIPT))
    systemctl = shutil.which("systemctl")
    if systemctl:
        user_dir = Path.home() / ".config" / "systemd" / "user"
        user_dir.mkdir(parents=True, exist_ok=True)
        service = user_dir / "plat-update-check.service"
        timer = user_dir / "plat-update-check.timer"
        service.write_text(
            "[Unit]\nDescription=Plat daily update check\n\n"
            "[Service]\nType=oneshot\n"
            f"ExecStart={sys.executable} {PERSISTED_SCRIPT} --run\n",
            encoding="utf-8",
        )
        timer.write_text(
            "[Unit]\nDescription=Run Plat update check daily\n\n"
            "[Timer]\nOnBootSec=5m\nOnUnitActiveSec=24h\nPersistent=true\n\n"
            "[Install]\nWantedBy=timers.target\n",
            encoding="utf-8",
        )
        subprocess.run([systemctl, "--user", "daemon-reload"], check=True)
        subprocess.run(
            [systemctl, "--user", "enable", "--now", "plat-update-check.timer"],
            check=True,
        )
        return "systemd user timer"

    crontab = shutil.which("crontab")
    if not crontab:
        raise RuntimeError("Neither systemd user timers nor crontab are available")
    existing = subprocess.run(
        [crontab, "-l"], check=False, capture_output=True, text=True
    ).stdout
    marker = "# plat-daily-update-check"
    line = f"@daily {python} {script} --run >/dev/null 2>&1 {marker}"
    lines = [x for x in existing.splitlines() if marker not in x]
    lines.append(line)
    subprocess.run([crontab, "-"], input="\n".join(lines) + "\n", text=True, check=True)
    return "user crontab"


def install_windows_scheduler() -> str:
    when = (dt.datetime.now() + dt.timedelta(minutes=2)).strftime("%H:%M")
    task_cmd = f'"{sys.executable}" "{PERSISTED_SCRIPT}" --run'
    subprocess.run(
        [
            "schtasks",
            "/Create",
            "/SC",
            "DAILY",
            "/TN",
            "PlatDailyUpdateCheck",
            "/TR",
            task_cmd,
            "/ST",
            when,
            "/F",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return "Windows scheduled task"


def install_scheduler() -> str:
    system = platform.system()
    if system == "Darwin":
        return install_macos_scheduler()
    if system == "Linux":
        return install_linux_scheduler()
    if system == "Windows":
        return install_windows_scheduler()
    raise RuntimeError(f"Unsupported scheduler platform: {system}")


def print_status() -> None:
    state = load_json(STATUS, {})
    if not state:
        print("No Plat update check has run yet.")
        return
    print(json.dumps(state, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Plat daily release checker")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true", help="Run one background check")
    group.add_argument("--status", action="store_true", help="Print cached status; no network")
    group.add_argument("--register", metavar="SKILL_DIR", help="Register an installed Plat path")
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--scope", choices=["global", "project"], default="global")
    args = parser.parse_args()

    if args.status:
        print_status()
        return 0
    if args.run:
        return check_updates()

    persist_self()
    register_install(Path(args.register), args.agent, args.scope)
    try:
        scheduler = install_scheduler()
        print(f"✓ Daily Plat update check enabled: {scheduler}")
    except Exception as exc:
        print(f"Warning: daily Plat update scheduler was not installed: {exc}", file=sys.stderr)
        print(
            f"You can still check manually with: {sys.executable} {PERSISTED_SCRIPT} --run",
            file=sys.stderr,
        )
    # Populate the local status cache immediately; failures are non-fatal to install.
    check_updates()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
