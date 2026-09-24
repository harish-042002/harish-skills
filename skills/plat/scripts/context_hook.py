#!/usr/bin/env python3
"""Generic lifecycle hook bridge for coding-agent hosts.

Hosts with PreCompact/preCompact/beforeCompact-style lifecycle hooks can invoke
this script. Hosts without hooks lose nothing: Plat calls the same checkpoint
logic when context health reaches RED.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import precompact_checkpoint


PRECOMPACT_NAMES = {
    "precompact",
    "pre_compact",
    "beforecompact",
    "before_compact",
    "contextcompact",
    "context_compact",
}


def _event_name(payload: dict[str, Any], explicit: str | None) -> str:
    value = explicit
    if not value:
        for key in ("hook_event_name", "event", "event_name", "type"):
            candidate = payload.get(key)
            if isinstance(candidate, str) and candidate:
                value = candidate
                break
    return (value or "").replace("-", "_").lower()


def _transcript(payload: dict[str, Any]) -> Path | None:
    for key in ("transcript_path", "transcript", "conversation_path"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            path = Path(value).expanduser()
            if path.exists():
                return path
    return None


def handle(
    payload: dict[str, Any],
    *,
    event: str | None = None,
    root: Path = Path("."),
    host: str = "unknown",
) -> dict[str, Any]:
    name = _event_name(payload, event)
    compact_key = name.replace("_", "")
    if compact_key not in {x.replace("_", "") for x in PRECOMPACT_NAMES}:
        return {"handled": False, "event": name or "unknown"}

    checkpoint = precompact_checkpoint.create_checkpoint(
        root=root,
        session_path=root / ".plat/session.json",
        context_path=root / ".plat/context.json",
        output=root / ".plat/checkpoints/precompact-latest.json",
        host=host,
        transcript=_transcript(payload),
    )
    return {
        "handled": True,
        "event": name,
        "checkpoint": str(root / ".plat/checkpoints/precompact-latest.json"),
        "created_at": checkpoint["created_at"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Bridge host lifecycle hooks into Plat context checkpoints.")
    parser.add_argument("--event")
    parser.add_argument("--root", default=".")
    parser.add_argument("--host", default="unknown")
    parser.add_argument("--payload-file")
    args = parser.parse_args()

    if args.payload_file:
        payload = json.loads(Path(args.payload_file).read_text(encoding="utf-8"))
    else:
        raw = sys.stdin.read().strip()
        payload = json.loads(raw) if raw else {}
    if not isinstance(payload, dict):
        raise ValueError("hook payload must be a JSON object")

    result = handle(
        payload,
        event=args.event,
        root=Path(args.root),
        host=args.host,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
