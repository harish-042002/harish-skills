#!/usr/bin/env python3
"""Deterministic cross-agent context-pressure guard for Plat.

Current context occupancy and cumulative work are different signals. Proxies
warn about repetition; they never prove that an unknown context is full.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import uuid
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 3
TOOL_RESULT_TARGET_BYTES = 6 * 1024
LARGE_RESULT_BYTES = 8 * 1024

YELLOW_RETURNED_BYTES = 64 * 1024
RED_RETURNED_BYTES = 128 * 1024
YELLOW_LARGE_OUTPUTS = 3
RED_LARGE_OUTPUTS = 6
YELLOW_REPEATED_READS = 2
RED_REPEATED_READS = 4
YELLOW_FILE_READS = 12
RED_FILE_READS = 24

YELLOW_CONTEXT_UTILIZATION = 0.65
RED_CONTEXT_UTILIZATION = 0.80
YELLOW_CACHE_READ_DELTA = 8_000_000
RED_CACHE_READ_DELTA = 20_000_000

MAX_FRESH_CONTEXT_WORKERS = 1

_LEVEL = {"GREEN": 0, "YELLOW": 1, "RED": 2}


def new_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "context_epoch": uuid.uuid4().hex,
        "returned_bytes": 0,
        "large_outputs": 0,
        "repeated_reads": 0,
        "file_reads": 0,
        "broad_suite_runs": 0,
        "fresh_context_workers": 0,
        "seen_keys": {},
        "telemetry_baseline": {},
        "telemetry": {
            "available": False,
            "health": "GREEN",
            "reason": "host telemetry unavailable; proxy guard active",
        },
        "health": {
            "status": "GREEN",
            "reason": "context budget healthy",
            "action": "continue",
        },
    }


def _utilization(state: dict[str, Any]) -> float | None:
    telemetry = state.get("telemetry", {})
    if not telemetry.get("available") or telemetry.get("occupancy_fresh") is False:
        return None
    stamp = telemetry.get("observed_at")
    if stamp:
        try:
            observed = dt.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
            if observed.tzinfo is None:
                observed = observed.replace(tzinfo=dt.timezone.utc)
            age = (dt.datetime.now(dt.timezone.utc) - observed).total_seconds()
            if age > 300 or age < -60:
                return None
        except (TypeError, ValueError):
            return None
    value = telemetry.get("context_utilization")
    if isinstance(value, bool):
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) and 0 <= value <= 1 else None


def _telemetry_health(state: dict[str, Any]) -> tuple[str, str]:
    value = _utilization(state)
    if value is None:
        return "GREEN", "current context utilization unknown"
    status = ("RED" if value >= RED_CONTEXT_UTILIZATION else
              "YELLOW" if value >= YELLOW_CONTEXT_UTILIZATION else "GREEN")
    return status, f"measured current context={value:.0%}"


def evaluate(state: dict[str, Any]) -> dict[str, Any]:
    returned = int(state.get("returned_bytes", 0))
    repeated = int(state.get("repeated_reads", 0))
    reads = int(state.get("file_reads", 0))
    broad = int(state.get("broad_suite_runs", 0))
    replay = state.get("telemetry", {}).get("cache_read_delta", 0) or 0
    inefficient = (repeated >= YELLOW_REPEATED_READS or reads >= YELLOW_FILE_READS
                   or broad > 1 or replay >= YELLOW_CACHE_READ_DELTA)
    state["efficiency"] = {
        "status": "YELLOW" if inefficient else "GREEN",
        "reason": "repeated work/replay merits inspection; not proof of a full context"
                  if inefficient else "no repetition warning",
    }
    utilization = _utilization(state)
    if utilization is not None:
        status, reason = _telemetry_health(state)
    else:
        # Bytes/reads cannot estimate fullness without a context capacity.
        # In particular, 24 tiny reads must not create a new worker.
        status = "YELLOW" if returned >= YELLOW_RETURNED_BYTES or inefficient else "GREEN"
        reason = ("proxy warning; context utilization unknown; narrow outputs, do not auto-reset"
                  if status == "YELLOW" else "context utilization unknown; no proxy warning")
    if status == "RED":
        action = ("fresh-context-worker" if int(state.get("fresh_context_workers", 0))
                  < MAX_FRESH_CONTEXT_WORKERS else "checkpoint-compact")
    else:
        action = "summarize-use-pointers" if status == "YELLOW" else "continue"
    state["health"] = {"status": status, "reason": reason, "action": action}
    return state


def reset_context(state: dict[str, Any]) -> dict[str, Any]:
    """Call AFTER a confirmed context replacement; not from a PreCompact hook.

    Clear epoch-local proxies and read masking, retaining the task's worker cap.
    Use start for a genuinely new task (which also resets that cap).
    """
    fresh = new_state()
    fresh["fresh_context_workers"] = int(state.get("fresh_context_workers", 0))
    return fresh


def apply_telemetry(state: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict) or not snapshot.get("available"):
        state["telemetry"] = {
            "available": False,
            "health": "GREEN",
            "reason": "host telemetry unavailable; proxy guard active",
        }
        return evaluate(state)

    baseline = state.get("telemetry_baseline")
    if not isinstance(baseline, dict):
        baseline = {}

    if not baseline:
        baseline = {
            key: snapshot.get(key, 0)
            for key in (
                "input_tokens",
                "output_tokens",
                "cache_read_tokens",
                "cache_write_tokens",
                "cost_usd",
            )
        }
        state["telemetry_baseline"] = baseline

    def delta(key: str) -> float:
        try:
            return max(
                0.0,
                float(snapshot.get(key, 0) or 0)
                - float(baseline.get(key, 0) or 0),
            )
        except (TypeError, ValueError):
            return 0.0

    telemetry = {
        "available": True,
        "host": snapshot.get("host", "unknown"),
        "source": snapshot.get("source", "unknown"),
        "observed_at": snapshot.get("observed_at"),
        "context_utilization": snapshot.get("context_utilization"),
        "occupancy_fresh": snapshot.get("occupancy_fresh"),
        "input_delta": int(delta("input_tokens")),
        "output_delta": int(delta("output_tokens")),
        "cache_read_delta": int(delta("cache_read_tokens")),
        "cache_write_delta": int(delta("cache_write_tokens")),
        "cost_delta_usd": round(delta("cost_usd"), 6),
    }
    state["telemetry"] = telemetry
    health, reason = _telemetry_health({**state, "telemetry": telemetry})
    telemetry["health"] = health
    telemetry["reason"] = reason
    return evaluate(state)


def record(
    state: dict[str, Any],
    *,
    returned_bytes: int,
    kind: str,
    key: str | None = None,
    broad_suite: bool = False,
) -> dict[str, Any]:
    if returned_bytes < 0:
        raise ValueError("returned_bytes must be >= 0")

    state["returned_bytes"] = int(state.get("returned_bytes", 0)) + returned_bytes
    if returned_bytes > LARGE_RESULT_BYTES:
        state["large_outputs"] = int(state.get("large_outputs", 0)) + 1

    if broad_suite:
        state["broad_suite_runs"] = int(state.get("broad_suite_runs", 0)) + 1

    if kind == "read":
        state["file_reads"] = int(state.get("file_reads", 0)) + 1

    if key:
        seen = dict(state.get("seen_keys", {}))
        prior = int(seen.get(key, 0))
        if kind == "read" and prior > 0:
            state["repeated_reads"] = int(state.get("repeated_reads", 0)) + 1
        seen[key] = prior + 1
        if len(seen) > 50:
            seen = dict(list(seen.items())[-50:])
        state["seen_keys"] = seen

    return evaluate(state)


def record_fresh_context_worker(state: dict[str, Any]) -> dict[str, Any]:
    state["fresh_context_workers"] = int(state.get("fresh_context_workers", 0)) + 1
    return evaluate(state)


def load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("context state must be an object")
        defaults = new_state()
        for key, value in defaults.items():
            data.setdefault(key, value)
        data["schema_version"] = SCHEMA_VERSION
        return data
    except FileNotFoundError:
        return new_state()


def save(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Track Plat context pressure.")
    parser.add_argument("--state", default=".plat/context.json")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--telemetry")

    rec = sub.add_parser("record")
    rec.add_argument("--bytes", type=int, required=True, dest="returned_bytes")
    rec.add_argument("--kind", choices=["command", "read", "diff", "test", "brain"], default="command")
    rec.add_argument("--key")
    rec.add_argument("--broad-suite", action="store_true")

    tel = sub.add_parser("telemetry")
    tel.add_argument("--file", default=".plat/telemetry.json")

    sub.add_parser("fresh-context-worker")
    sub.add_parser("status")
    sub.add_parser("reset", help="After confirmed compaction/new context, reset epoch only")

    args = parser.parse_args()
    path = Path(args.state)

    if args.command == "start":
        state = new_state()
        if args.telemetry:
            snapshot = json.loads(Path(args.telemetry).read_text(encoding="utf-8"))
            state = apply_telemetry(state, snapshot)
        save(path, state)
        print(json.dumps(state, indent=2, sort_keys=True))
        return 0

    state = load(path)
    if args.command == "record":
        state = record(
            state,
            returned_bytes=args.returned_bytes,
            kind=args.kind,
            key=args.key,
            broad_suite=args.broad_suite,
        )
        save(path, state)
    elif args.command == "telemetry":
        snapshot = json.loads(Path(args.file).read_text(encoding="utf-8"))
        state = apply_telemetry(state, snapshot)
        save(path, state)
    elif args.command == "reset":
        state = reset_context(state)
        save(path, state)
    elif args.command == "fresh-context-worker":
        state = record_fresh_context_worker(state)
        save(path, state)
    else:
        state = evaluate(state)

    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
