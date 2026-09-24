#!/usr/bin/env python3
"""Deterministic context-pressure guard for Plat.

Tracks only lightweight proxies that every coding host can provide:
returned bytes, repeated reads, large outputs, broad-suite runs, and
fresh-context worker usage. It never stores tool output itself.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
TOOL_RESULT_TARGET_BYTES = 6 * 1024
LARGE_RESULT_BYTES = 8 * 1024
YELLOW_RETURNED_BYTES = 64 * 1024
RED_RETURNED_BYTES = 128 * 1024
YELLOW_LARGE_OUTPUTS = 3
RED_LARGE_OUTPUTS = 6
YELLOW_REPEATED_READS = 2
RED_REPEATED_READS = 4
MAX_FRESH_CONTEXT_WORKERS = 1


def new_state() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "returned_bytes": 0,
        "large_outputs": 0,
        "repeated_reads": 0,
        "broad_suite_runs": 0,
        "fresh_context_workers": 0,
        "seen_keys": {},
        "health": {
            "status": "GREEN",
            "reason": "context budget healthy",
            "action": "continue",
        },
    }


def evaluate(state: dict[str, Any]) -> dict[str, Any]:
    returned = int(state.get("returned_bytes", 0))
    large = int(state.get("large_outputs", 0))
    repeated = int(state.get("repeated_reads", 0))
    broad = int(state.get("broad_suite_runs", 0))
    workers = int(state.get("fresh_context_workers", 0))

    red = (
        returned >= RED_RETURNED_BYTES
        or large >= RED_LARGE_OUTPUTS
        or repeated >= RED_REPEATED_READS
    )
    yellow = (
        returned >= YELLOW_RETURNED_BYTES
        or large >= YELLOW_LARGE_OUTPUTS
        or repeated >= YELLOW_REPEATED_READS
        or broad > 1
    )

    if red:
        action = (
            "fresh-context-worker"
            if workers < MAX_FRESH_CONTEXT_WORKERS
            else "checkpoint-compact"
        )
        status = "RED"
        reason = (
            f"context pressure high: returned={returned}B, "
            f"large_outputs={large}, repeated_reads={repeated}"
        )
    elif yellow:
        status = "YELLOW"
        action = "summarize-use-pointers"
        reason = (
            f"context pressure rising: returned={returned}B, "
            f"large_outputs={large}, repeated_reads={repeated}, broad_suites={broad}"
        )
    else:
        status = "GREEN"
        action = "continue"
        reason = "context budget healthy"

    state["health"] = {"status": status, "reason": reason, "action": action}
    return state


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

    sub.add_parser("start")

    rec = sub.add_parser("record")
    rec.add_argument("--bytes", type=int, required=True, dest="returned_bytes")
    rec.add_argument("--kind", choices=["command", "read", "diff", "test", "brain"], default="command")
    rec.add_argument("--key")
    rec.add_argument("--broad-suite", action="store_true")

    sub.add_parser("fresh-context-worker")
    sub.add_parser("status")

    args = parser.parse_args()
    path = Path(args.state)

    if args.command == "start":
        state = new_state()
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
    elif args.command == "fresh-context-worker":
        state = record_fresh_context_worker(state)
        save(path, state)
    else:
        state = evaluate(state)

    print(json.dumps(state, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
