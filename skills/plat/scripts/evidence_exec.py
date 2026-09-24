#!/usr/bin/env python3
"""Run noisy commands without flooding the model context.

Complete stdout/stderr is persisted under .plat/logs. Stdout receives only a
small JSON evidence summary plus a bounded excerpt useful for next decisions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import subprocess
import sys
import time

import context_guard

DEFAULT_MAX_RETURN_BYTES = 6 * 1024
INTERESTING_MARKERS = (
    "error",
    "failed",
    "failure",
    "exception",
    "traceback",
    "assert",
    "fatal",
    "warning",
)


def _decode(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")


def _interesting_excerpt(text: str, max_bytes: int) -> str:
    lines = text.splitlines()
    selected: list[str] = []
    seen: set[str] = set()

    for line in lines:
        lowered = line.lower()
        if any(marker in lowered for marker in INTERESTING_MARKERS):
            if line not in seen:
                selected.append(line)
                seen.add(line)
        if len(selected) >= 24:
            break

    if not selected:
        selected = lines[-24:]

    excerpt = "\n".join(selected)
    data = excerpt.encode("utf-8")
    if len(data) <= max_bytes:
        return excerpt

    clipped = data[:max_bytes].decode("utf-8", errors="ignore")
    return clipped.rstrip() + "\n...[excerpt truncated]"


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    log_dir: Path = Path(".plat/logs"),
    max_return_bytes: int = DEFAULT_MAX_RETURN_BYTES,
    context_state: Path = Path(".plat/context.json"),
    kind: str = "command",
    broad_suite: bool = False,
) -> dict:
    if not command:
        raise ValueError("command is required")
    if max_return_bytes < 1024:
        raise ValueError("max_return_bytes must be >= 1024")

    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    log_path = log_dir / f"evidence-{stamp}.log"

    start = time.monotonic()
    proc = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    duration_ms = int((time.monotonic() - start) * 1000)

    stdout = proc.stdout or b""
    stderr = proc.stderr or b""
    combined = (
        b"===== STDOUT =====\n"
        + stdout
        + b"\n===== STDERR =====\n"
        + stderr
    )
    log_path.write_bytes(combined)

    excerpt = _interesting_excerpt(_decode(stdout + b"\n" + stderr), max_return_bytes)
    result = {
        "command": command,
        "exit_code": proc.returncode,
        "duration_ms": duration_ms,
        "stdout_bytes": len(stdout),
        "stderr_bytes": len(stderr),
        "total_output_bytes": len(stdout) + len(stderr),
        "log_path": str(log_path),
        "excerpt": excerpt,
    }

    rendered = json.dumps(result, sort_keys=True)
    rendered_bytes = len(rendered.encode("utf-8"))

    state = context_guard.load(context_state)
    state = context_guard.record(
        state,
        returned_bytes=rendered_bytes,
        kind="test" if kind == "test" else kind,
        key=" ".join(command[:4]),
        broad_suite=broad_suite,
    )
    context_guard.save(context_state, state)
    result["context_health"] = state["health"]
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a command with bounded model-visible output.")
    parser.add_argument("--cwd")
    parser.add_argument("--log-dir", default=".plat/logs")
    parser.add_argument("--context-state", default=".plat/context.json")
    parser.add_argument("--max-return-bytes", type=int, default=DEFAULT_MAX_RETURN_BYTES)
    parser.add_argument("--kind", choices=["command", "test", "diff"], default="command")
    parser.add_argument("--broad-suite", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("command required after --")

    result = run_command(
        command,
        cwd=Path(args.cwd) if args.cwd else None,
        log_dir=Path(args.log_dir),
        max_return_bytes=args.max_return_bytes,
        context_state=Path(args.context_state),
        kind=args.kind,
        broad_suite=args.broad_suite,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return int(result["exit_code"] != 0)


if __name__ == "__main__":
    raise SystemExit(main())
