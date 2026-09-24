#!/usr/bin/env python3
"""Deterministic cross-agent context-pressure guard for Plat.

Every coding agent gets the same proxy signals. When a host exposes real usage
telemetry, Plat overlays it on the proxy health instead of requiring that
telemetry for correctness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 2
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


def _telemetry_health(state: dict[str, Any]) -> tuple[str, str]:
    telemetry = state.get("telemetry")
    if not isinstance(telemetry, dict) or not telemetry.get("available"):
        return "GREEN", "host telemetry unavailable"

    utilization = telemetry.get("context_utilization")
    cache_delta = telemetry.get("cache_read_delta", 0)
    try:
        utilization_value = float(utilization) if utilization is not None else 0.0
    except (TypeError, ValueError):
        utilization_value = 0.0
    try:
        cache_delta_value = int(cache_delta or 0)
    except (TypeError, ValueError):
        cache_delta_value = 0

    if (
        utilization_value >= RED_CONTEXT_UTILIZATION
        or cache_delta_value >= RED_CACHE_READ_DELTA
    ):
        return (
            "RED",
            f"real telemetry high: context={utilization_value:.0%}, "
            f"cache_read_delta={cache_delta_value}",
        )
    if (
        utilization_value >= YELLOW_CONTEXT_UTILIZATION
        or cache_delta_value >= YELLOW_CACHE_READ_DELTA
    ):
        return (
            "YELLOW",
            f"real telemetry rising: context={utilization_value:.0%}, "
            f"cache_read_delta={cache_delta_value}",
        )
    return (
        "GREEN",
        f"real telemetry healthy: context={utilization_value:.0%}, "
        f"cache_read_delta={cache_delta_value}",
    )


def evaluate(state: dict[str, Any]) -> dict[str, Any]:
    returned = int(state.get("returned_bytes", 0))
    large = int(state.get("large_outputs", 0))
    repeated = int(state.get("repeated_reads", 0))
    reads = int(state.get("file_reads", 0))
    broad = int(state.get("broad_suite_runs", 0))
    workers = int(state.get("fresh_context_workers", 0))

    proxy_red = (
        returned >= RED_RETURNED_BYTES
        or large >= RED_LARGE_OUTPUTS
        or repeated >= RED_REPEATED_READS
        or reads >= RED_FILE_READS
    )
    proxy_yellow = (
        returned >= YELLOW_RETURNED_BYTES
        or large >= YELLOW_LARGE_OUTPUTS
        or repeated >= YELLOW_REPEATED_READS
        or reads >= YELLOW_FILE_READS
        or broad > 1
    )
    proxy_status = "RED" if proxy_red else "YELLOW" if proxy_yellow else "GREEN"

    telemetry_status, telemetry_reason = _telemetry_health(state)
    status = max(
        (proxy_status, telemetry_status),
        key=lambda value: _LEVEL[value],
    )

    if status == "RED":
        action = (
            "fresh-context-worker"
            if workers < MAX_FRESH_CONTEXT_WORKERS
            else "checkpoint-compact"
        )
        reason = (
            f"context pressure high: returned={returned}B, large_outputs={large}, "
            f"repeated_reads={repeated}, file_reads={reads}; {telemetry_reason}"
        )
    elif status == "YELLOW":
        action = "summarize-use-pointers"
        reason = (
            f"context pressure rising: returned={returned}B, large_outputs={large}, "
            f"repeated_reads={repeated}, file_reads={reads}, broad_suites={broad}; "
            f"{telemetry_reason}"
        )
    else:
        action = "continue"
        reason = "context budget healthy"

    state["health"] = {"status": status, "reason": reason, "action": action}
    return state


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
    elif args.command == "fresh-context-worker":
        state = record_fresh_context_worker(state)
        save(path, state)
    else:
        state = evaluate(state)

    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
