#!/usr/bin/env python3
"""Run noisy commands without flooding the model context.

Complete stdout/stderr is persisted under .plat/logs. Stdout receives only a
small JSON evidence summary plus a bounded excerpt useful for next decisions.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import signal
import shutil
import tempfile
from pathlib import Path
import subprocess
import sys
import time

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import context_guard

DEFAULT_MAX_RETURN_BYTES = 6 * 1024
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_MAX_OUTPUT_BYTES = 16 * 1024 * 1024
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

    suffix = b"\n...[excerpt truncated]"
    keep = max(0, max_bytes - len(suffix))
    clipped = data[:keep].decode("utf-8", errors="ignore").rstrip()
    return clipped + suffix.decode("utf-8")


def _terminate(proc: subprocess.Popen) -> None:
    # Only the process group created for this command; never unrelated processes.
    if os.name == "posix":
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif os.name == "nt":
        try:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=5, check=False)
        except (OSError, subprocess.TimeoutExpired):
            pass  # Still terminate/reap the direct child; tree cleanup is best-effort.
    if proc.poll() is None:
        proc.kill()
    proc.wait(timeout=5)


def _sample(stream, size: int) -> bytes:
    stream.seek(0)
    if size <= 32768:
        return stream.read()
    head = stream.read(8192)
    stream.seek(max(0, size - 24576))
    return head + b"\n...[middle retained in log]\n" + stream.read(24576)


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    log_dir: Path = Path(".plat/logs"),
    max_return_bytes: int = DEFAULT_MAX_RETURN_BYTES,
    context_state: Path = Path(".plat/context.json"),
    kind: str = "command",
    broad_suite: bool = False,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> dict:
    if not command:
        raise ValueError("command is required")
    if max_return_bytes < 1024:
        raise ValueError("max_return_bytes must be >= 1024")

    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and > 0")
    if max_output_bytes < 1024:
        raise ValueError("max_output_bytes must be >= 1024")
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    log_path = log_dir / f"evidence-{stamp}.log"

    start = time.monotonic()
    timed_out = output_limited = False
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        proc = subprocess.Popen(
            command, cwd=str(cwd) if cwd else None, stdin=subprocess.DEVNULL,
            stdout=out, stderr=err, start_new_session=(os.name == "posix"),
        )
        try:
            while proc.poll() is None:
                total = os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size
                if time.monotonic() - start >= timeout_seconds:
                    timed_out = True
                    _terminate(proc)
                    break
                if total > max_output_bytes:
                    output_limited = True
                    _terminate(proc)
                    break
                time.sleep(0.02)
        finally:
            # Also stop descendants left behind by a command that already exited.
            if os.name == "posix" or proc.poll() is None:
                _terminate(proc)
        stdout_bytes = os.fstat(out.fileno()).st_size
        stderr_bytes = os.fstat(err.fileno()).st_size
        output_limited = output_limited or stdout_bytes + stderr_bytes > max_output_bytes
        stdout = _sample(out, stdout_bytes)
        stderr = _sample(err, stderr_bytes)
        with log_path.open("wb") as log:
            log.write(b"===== STDOUT =====\n")
            out.seek(0)
            shutil.copyfileobj(out, log, length=65536)
            log.write(b"\n===== STDERR =====\n")
            err.seek(0)
            shutil.copyfileobj(err, log, length=65536)
    duration_ms = int((time.monotonic() - start) * 1000)
    exit_code = 124 if timed_out else 125 if output_limited else proc.returncode

    command_display = " ".join(command)
    if len(command_display) > 512:
        command_display = command_display[:496].rstrip() + " ...[truncated]"

    excerpt_budget = max(0, max_return_bytes - 1536)
    excerpt = _interesting_excerpt(
        _decode(stdout + b"\n" + stderr),
        excerpt_budget,
    )
    result = {
        "command": command_display,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "output_limited": output_limited,
        "duration_ms": duration_ms,
        "stdout_bytes": stdout_bytes,
        "stderr_bytes": stderr_bytes,
        "total_output_bytes": stdout_bytes + stderr_bytes,
        "log_path": str(log_path),
        "excerpt": excerpt,
    }

    provisional_bytes = len(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8")
    )
    try:
        state = context_guard.load(context_state)
        state = context_guard.record(
            state, returned_bytes=min(provisional_bytes, max_return_bytes),
            kind="test" if kind == "test" else kind,
            key=command_display[:256], broad_suite=broad_suite,
        )
        context_guard.save(context_state, state)
        result["context_health"] = state["health"]
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        # A diagnostics failure must not hide the command's actual result and
        # tempt the caller to repeat a command that already changed something.
        result["context_health"] = {"status": "UNKNOWN"}
        result["telemetry_warning"] = f"{type(exc).__name__}: context state not updated"

    rendered = json.dumps(result, indent=2, sort_keys=True)
    rendered_bytes = len(rendered.encode("utf-8"))
    if rendered_bytes > max_return_bytes:
        overflow = rendered_bytes - max_return_bytes
        excerpt_bytes = result["excerpt"].encode("utf-8")
        keep = max(0, len(excerpt_bytes) - overflow - 64)
        result["excerpt"] = excerpt_bytes[:keep].decode(
            "utf-8", errors="ignore"
        ).rstrip()
        if keep < len(excerpt_bytes):
            suffix = "\n...[excerpt truncated]"
            suffix_bytes = suffix.encode("utf-8")
            while (
                len(
                    json.dumps(
                        {**result, "excerpt": result["excerpt"] + suffix},
                        indent=2,
                        sort_keys=True,
                    ).encode("utf-8")
                )
                > max_return_bytes
                and result["excerpt"]
            ):
                result["excerpt"] = result["excerpt"][:-16]
            result["excerpt"] = result["excerpt"].rstrip() + suffix

    final_bytes = len(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8")
    )
    if final_bytes > max_return_bytes:
        # Keep the authoritative outcome, not decorative metadata. Do not raise
        # after a command has executed just because its description is large.
        result.pop("command", None)
        result.pop("excerpt", None)
        result["context_health"] = {"status": result["context_health"]["status"]}
        result["summary_reduced"] = True
        if len(json.dumps(result, indent=2, sort_keys=True).encode("utf-8")) > max_return_bytes:
            result.pop("telemetry_warning", None)
            result.pop("context_health", None)
        if len(json.dumps(result, indent=2, sort_keys=True).encode("utf-8")) > max_return_bytes:
            # A pathological path cannot be returned in this budget. Say what
            # happened, retain the outcome, and avoid suggesting a command retry.
            result.pop("log_path", None)
            result["log_location"] = "configured log_dir; path exceeds return budget"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a command with bounded model-visible output.")
    parser.add_argument("--cwd")
    parser.add_argument("--log-dir", default=".plat/logs")
    parser.add_argument("--context-state", default=".plat/context.json")
    parser.add_argument("--max-return-bytes", type=int, default=DEFAULT_MAX_RETURN_BYTES)
    parser.add_argument("--kind", choices=["command", "test", "diff"], default="command")
    parser.add_argument("--broad-suite", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--max-output-bytes", type=int, default=DEFAULT_MAX_OUTPUT_BYTES)
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
        timeout_seconds=args.timeout_seconds,
        max_output_bytes=args.max_output_bytes,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    code = int(result["exit_code"])
    return code if code >= 0 else 128 - code


if __name__ == "__main__":
    raise SystemExit(main())
