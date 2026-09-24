#!/usr/bin/env python3
"""Create a small cross-agent checkpoint before compaction/reset/handoff."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import host_context


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def _run_git(args: list[str], cwd: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if proc.returncode != 0:
        return ""
    text = proc.stdout.strip()
    return text[:4096]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else None
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def create_checkpoint(
    *,
    root: Path,
    session_path: Path,
    context_path: Path,
    output: Path,
    host: str = "unknown",
    transcript: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    session = load_json(session_path)
    context = load_json(context_path)
    telemetry = host_context.discover(host=host, transcript=transcript)

    checkpoint = {
        "schema_version": 1,
        "created_at": now_iso(),
        "reason": "precompact-or-context-reset",
        "task": {
            "goal": (session or {}).get("goal", ""),
            "must": (session or {}).get("must", []),
            "must_not": (session or {}).get("must_not", []),
            "current_slice": (session or {}).get("current_slice", ""),
            "owner": (session or {}).get("owner", []),
            "proof": (session or {}).get("proof", []),
            "next": (session or {}).get("next", ""),
        },
        "health": {
            "task": (session or {}).get("health", {}),
            "context": (context or {}).get("health", {}),
        },
        "repo": {
            "head": _run_git(["rev-parse", "HEAD"], root),
            "branch": _run_git(["branch", "--show-current"], root),
            "status": _run_git(["status", "--short"], root),
            "diff_stat": _run_git(["diff", "--stat"], root),
        },
        "telemetry": telemetry if telemetry.get("available") else {
            "available": False,
            "host": telemetry.get("host", host),
            "source": telemetry.get("source", "none"),
        },
        "resume": [
            "read task capsule",
            "inspect branch/diff",
            "revalidate only stale facts",
            "resume next",
        ],
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return checkpoint


def main() -> int:
    parser = argparse.ArgumentParser(description="Checkpoint Plat state before compaction/reset.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--session", default=".plat/session.json")
    parser.add_argument("--context", default=".plat/context.json")
    parser.add_argument("--output", default=".plat/checkpoints/precompact-latest.json")
    parser.add_argument("--host", default="unknown")
    parser.add_argument("--transcript")
    args = parser.parse_args()

    root = Path(args.root)
    checkpoint = create_checkpoint(
        root=root,
        session_path=Path(args.session),
        context_path=Path(args.context),
        output=Path(args.output),
        host=args.host,
        transcript=Path(args.transcript).expanduser() if args.transcript else None,
    )
    print(json.dumps(checkpoint, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
