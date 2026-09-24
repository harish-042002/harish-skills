#!/usr/bin/env python3
"""Out-of-band Plat release checker and multi-install updater.

The checker is installed by Plat's installer and runs from the OS scheduler.
It never runs inside normal engineering prompts, so update discovery adds no
model/tool overhead.
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
LABEL = "com.plat.daily-update-check"  # Keep label stable for existing installs.
CHECK_INTERVAL_SECONDS = 2 * 60 * 60


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
            "User-Agent": "plat-update-check",
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


def infer_project_root(skill_dir: Path, agent: str) -> Path | None:
    skill_dir = skill_dir.expanduser().resolve()
    parts = list(skill_dir.parents)
    if agent == "claude-code":
        for parent in parts:
            if parent.name == ".claude":
                return parent.parent
    for parent in parts:
        if parent.name == ".agents":
            return parent.parent
    return None


def register_install(
    skill_dir: Path,
    agent: str,
    scope: str,
    project_root: Path | None = None,
) -> None:
    skill_dir = skill_dir.expanduser().resolve()
    root = project_root.expanduser().resolve() if project_root else None
    if scope == "project" and root is None:
        root = infer_project_root(skill_dir, agent)

    data = load_json(REGISTRY, {"version": 2, "installations": []})
    items = data.get("installations", [])
    items = [x for x in items if x.get("path") != str(skill_dir)]
    item = {
        "path": str(skill_dir),
        "agent": agent,
        "scope": scope,
        "registered_at": now_iso(),
    }
    if root is not None:
        item["project_root"] = str(root)
    items.append(item)
    data["version"] = 2
    data["installations"] = items
    write_json(REGISTRY, data)


def active_installations() -> list[dict]:
    registry = load_json(REGISTRY, {"version": 2, "installations": []})
    active = []
    for raw in registry.get("installations", []):
        item = dict(raw)
        skill_dir = Path(str(item.get("path", ""))).expanduser()
        version = read_installed_version(skill_dir)
        if not version:
            continue
        item["installed_version"] = version
        if item.get("scope") == "project" and not item.get("project_root"):
            inferred = infer_project_root(skill_dir, str(item.get("agent", "")))
            if inferred:
                item["project_root"] = str(inferred)
        active.append(item)

    registry["version"] = 2
    registry["installations"] = [
        {k: v for k, v in item.items() if k != "installed_version"} for item in active
    ]
    write_json(REGISTRY, registry)
    return active


def display_agent(agent: str) -> str:
    return {
        "codex": "Codex",
        "claude-code": "Claude Code",
        "cursor": "Cursor",
    }.get(agent, agent or "unknown")


def notification_signature(latest: str, outdated: list[dict]) -> str:
    parts = [
        f"{item.get('path')}@{item.get('installed_version')}"
        for item in sorted(outdated, key=lambda x: str(x.get("path", "")))
    ]
    return latest + "|" + "|".join(parts)


def notify(title: str, message: str) -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            script = (
                "display notification "
                + json.dumps(message)
                + " with title "
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


def get_outdated(active: list[dict], latest: str) -> list[dict]:
    latest_tuple = parse_version(latest)
    if latest_tuple is None:
        return []
    return [
        item
        for item in active
        if parse_version(str(item.get("installed_version", "")))
        and parse_version(str(item["installed_version"])) < latest_tuple
    ]


def check_updates() -> int:
    previous = load_json(STATUS, {})
    active = active_installations()
    state = {
        "checked_at": now_iso(),
        "check_interval_seconds": CHECK_INTERVAL_SECONDS,
        "update_available": False,
        "installations": active,
        "last_notified_signature": previous.get("last_notified_signature"),
    }

    try:
        latest, release_url = fetch_latest_release()
        outdated = get_outdated(active, latest)
        state["latest_version"] = latest
        state["release_url"] = release_url
        state["update_available"] = bool(outdated)
        state["outdated_installations"] = outdated

        signature = notification_signature(latest, outdated) if outdated else None
        if outdated and previous.get("last_notified_signature") != signature:
            agents = ", ".join(sorted({display_agent(str(x.get("agent", ""))) for x in outdated}))
            notify(
                "Plat update available",
                f"Plat v{latest} is available for {agents}. Run the Plat updater once to sync all registered agents.",
            )
            state["last_notified_signature"] = signature
            state["last_notified_version"] = latest
        elif not outdated:
            state["last_notified_signature"] = None
    except Exception as exc:
        state["last_error"] = f"{type(exc).__name__}: {exc}"
        write_json(STATUS, state)
        return 1

    write_json(STATUS, state)
    return 0


def run_skills_update(*, global_scope: bool, project_root: Path | None = None) -> subprocess.CompletedProcess:
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required to update Plat installations")
    command = [npx, "-y", "skills@latest", "update", "plat", "-y"]
    command.append("-g" if global_scope else "-p")
    cwd = None if global_scope else str(project_root) if project_root else None
    if not global_scope and not cwd:
        raise RuntimeError("project update requires a project root")
    return subprocess.run(command, cwd=cwd, check=False, text=True)


def fallback_reinstall(item: dict) -> subprocess.CompletedProcess:
    npx = shutil.which("npx")
    if not npx:
        raise RuntimeError("npx is required to update Plat installations")
    agent = str(item.get("agent", ""))
    scope = str(item.get("scope", ""))
    if agent not in {"codex", "claude-code", "cursor"}:
        raise RuntimeError(f"unsupported registered agent: {agent}")

    command = [
        npx,
        "-y",
        "skills@latest",
        "add",
        REPO,
        "--skill",
        "plat",
        "-a",
        agent,
        "--copy",
        "-y",
    ]
    cwd = None
    if scope == "global":
        command.append("-g")
    else:
        root = item.get("project_root")
        if not root:
            raise RuntimeError(f"missing project root for {item.get('path')}")
        cwd = str(root)
    return subprocess.run(command, cwd=cwd, check=False, text=True)


def update_all_registered() -> int:
    active = active_installations()
    if not active:
        print("No registered Plat installations found.")
        return 0

    try:
        latest, _release_url = fetch_latest_release()
    except Exception as exc:
        print(f"Could not determine latest Plat release: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    outdated = get_outdated(active, latest)
    if not outdated:
        print(f"All registered Plat installations are already on v{latest}.")
        check_updates()
        return 0

    global_outdated = [x for x in outdated if x.get("scope") == "global"]
    project_groups: dict[str, list[dict]] = {}
    for item in outdated:
        if item.get("scope") != "project":
            continue
        root = str(item.get("project_root", ""))
        if root:
            project_groups.setdefault(root, []).append(item)

    if global_outdated:
        try:
            run_skills_update(global_scope=True)
        except Exception as exc:
            print(f"Global native update failed: {type(exc).__name__}: {exc}", file=sys.stderr)

    for root in sorted(project_groups):
        try:
            run_skills_update(global_scope=False, project_root=Path(root))
        except Exception as exc:
            print(f"Project native update failed for {root}: {type(exc).__name__}: {exc}", file=sys.stderr)

    # Verify every registered copy. If the native scoped updater did not refresh
    # a copy (for example an older install without usable lock metadata), fall
    # back to a targeted reinstall for that registered agent.
    remaining = []
    latest_tuple = parse_version(latest)
    for item in outdated:
        version = read_installed_version(Path(str(item["path"])))
        if version and latest_tuple and parse_version(version) and parse_version(version) >= latest_tuple:
            continue
        remaining.append(item)

    for item in remaining:
        try:
            result = fallback_reinstall(item)
            if result.returncode != 0:
                print(f"Fallback update failed for {item.get('agent')} at {item.get('path')}", file=sys.stderr)
        except Exception as exc:
            print(f"Fallback update failed for {item.get('path')}: {type(exc).__name__}: {exc}", file=sys.stderr)

    final_active = active_installations()
    final_outdated = get_outdated(final_active, latest)
    check_updates()

    if final_outdated:
        print("Plat update incomplete for:")
        for item in final_outdated:
            print(f"- {display_agent(str(item.get('agent', '')))}: {item.get('path')} (v{item.get('installed_version')})")
        return 1

    print(f"✓ Updated all registered Plat installations to v{latest}.")
    for item in final_active:
        print(f"- {display_agent(str(item.get('agent', '')))}: {item.get('path')}")
    return 0


def install_macos_scheduler() -> str:
    launch_agents = Path.home() / "Library" / "LaunchAgents"
    launch_agents.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    plist_path = launch_agents / f"{LABEL}.plist"
    payload = {
        "Label": LABEL,
        "ProgramArguments": [sys.executable, str(PERSISTED_SCRIPT), "--run"],
        "StartInterval": CHECK_INTERVAL_SECONDS,
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
            "[Unit]\nDescription=Plat update check\n\n"
            "[Service]\nType=oneshot\n"
            f"ExecStart={sys.executable} {PERSISTED_SCRIPT} --run\n",
            encoding="utf-8",
        )
        timer.write_text(
            "[Unit]\nDescription=Run Plat update check every two hours\n\n"
            "[Timer]\nOnBootSec=5m\nOnUnitActiveSec=2h\nPersistent=true\n\n"
            "[Install]\nWantedBy=timers.target\n",
            encoding="utf-8",
        )
        subprocess.run([systemctl, "--user", "daemon-reload"], check=True)
        subprocess.run([systemctl, "--user", "enable", "--now", "plat-update-check.timer"], check=True)
        return "systemd user timer"

    crontab = shutil.which("crontab")
    if not crontab:
        raise RuntimeError("Neither systemd user timers nor crontab are available")
    existing = subprocess.run([crontab, "-l"], check=False, capture_output=True, text=True).stdout
    marker = "# plat-update-check"
    line = f"0 */2 * * * {python} {script} --run >/dev/null 2>&1 {marker}"
    lines = [x for x in existing.splitlines() if "plat-daily-update-check" not in x and marker not in x]
    lines.append(line)
    subprocess.run([crontab, "-"], input="\n".join(lines) + "\n", text=True, check=True)
    return "user crontab"


def install_windows_scheduler() -> str:
    subprocess.run(
        [
            "schtasks",
            "/Create",
            "/SC",
            "HOURLY",
            "/MO",
            "2",
            "/TN",
            "PlatUpdateCheck",
            "/TR",
            f'"{sys.executable}" "{PERSISTED_SCRIPT}" --run',
            "/F",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Remove the old daily task name if it exists.
    subprocess.run(
        ["schtasks", "/Delete", "/TN", "PlatDailyUpdateCheck", "/F"],
        check=False,
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
    parser = argparse.ArgumentParser(description="Plat release checker and multi-install updater")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--run", action="store_true", help="Run one background update check")
    group.add_argument("--status", action="store_true", help="Print cached status; no network")
    group.add_argument("--update-all", action="store_true", help="Update every registered Plat installation")
    group.add_argument("--register", metavar="SKILL_DIR", help="Register an installed Plat path")
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--scope", choices=["global", "project"], default="global")
    parser.add_argument("--project-root")
    args = parser.parse_args()

    if args.status:
        print_status()
        return 0
    if args.run:
        return check_updates()
    if args.update_all:
        return update_all_registered()

    persist_self()
    register_install(
        Path(args.register),
        args.agent,
        args.scope,
        Path(args.project_root) if args.project_root else None,
    )
    try:
        scheduler = install_scheduler()
        print(f"✓ Plat update check enabled every 2 hours: {scheduler}")
    except Exception as exc:
        print(f"Warning: Plat update scheduler was not installed: {exc}", file=sys.stderr)
        print(f"You can still check manually with: {sys.executable} {PERSISTED_SCRIPT} --run", file=sys.stderr)
    check_updates()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
