#!/usr/bin/env python3
"""Create a small, deterministic Plat Brain review packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_MAX_BYTES = 4096


def _clip(value: Any, limit: int) -> Any:
    if isinstance(value, str):
        if len(value) <= limit:
            return value
        return value[: max(0, limit - 16)].rstrip() + " ...[truncated]"
    if isinstance(value, list):
        return [_clip(x, limit) for x in value[:5]]
    if isinstance(value, dict):
        return {k: _clip(v, limit) for k, v in value.items()}
    return value


def build_packet(
    state: dict[str, Any],
    *,
    question: str,
    evidence: list[str] | None = None,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> dict[str, Any]:
    if max_bytes < 1024:
        raise ValueError("max_bytes must be >= 1024")

    execution = state.get("execution", {}) if isinstance(state.get("execution"), dict) else {}
    health = state.get("health", {}) if isinstance(state.get("health"), dict) else {}

    # These are binding instructions, not optional summary prose. Never clip them.
    packet: dict[str, Any] = {
        "goal": state.get("goal", ""),
        "must": state.get("must", []),
        "must_not": state.get("must_not", []),
        "preserve": state.get("preserve", []),
        "proof": state.get("proof", []),
        "question": question,
        "contract_complete": True,
        "current_slice": _clip(state.get("current_slice", ""), 320),
        "owner": _clip(state.get("owner", []), 220),
        "next": _clip(state.get("next", ""), 320),
        "health": {"status": health.get("status"), "reason": _clip(health.get("reason", ""), 220)},
        "trajectory": {key: execution.get(key, 0) for key in ("failed_hypotheses", "reroutes", "brain_reviews")},
        "evidence": _clip(evidence or [], 300),
        "optional_context_omitted": False,
    }
    def size():
        # Match CLI serialization, including escaped Unicode.
        return len(json.dumps(packet, indent=2, sort_keys=True).encode("utf-8"))
    while size() > max_bytes and packet["evidence"]:
        packet["evidence"].pop()
        packet["optional_context_omitted"] = True
    for field in ("next", "owner", "current_slice", "health"):
        if size() <= max_bytes:
            break
        packet.pop(field, None)
        packet["optional_context_omitted"] = True
    if size() > max_bytes:
        raise ValueError(
            "Complete binding contract exceeds packet budget. Do not delegate an incomplete brief; "
            "use a verified shared contract file, choose a genuinely independent slice, "
            "or explicitly increase --max-bytes."
        )
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a bounded Plat Brain review packet.")
    parser.add_argument("--state", default=".plat/session.json")
    parser.add_argument("--question", required=True)
    parser.add_argument("--evidence", action="append", default=[])
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--output")
    args = parser.parse_args()

    state = json.loads(Path(args.state).read_text(encoding="utf-8"))
    packet = build_packet(
        state,
        question=args.question,
        evidence=args.evidence,
        max_bytes=args.max_bytes,
    )
    rendered = json.dumps(packet, indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
