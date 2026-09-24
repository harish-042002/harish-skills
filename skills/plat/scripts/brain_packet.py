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

    packet: dict[str, Any] = {
        "goal": _clip(state.get("goal", ""), 700),
        "must": _clip(state.get("must", []), 320),
        "must_not": _clip(state.get("must_not", []), 320),
        "current_slice": _clip(state.get("current_slice", ""), 500),
        "owner": _clip(state.get("owner", []), 320),
        "proof": _clip(state.get("proof", []), 320),
        "next": _clip(state.get("next", ""), 500),
        "health": {
            "status": health.get("status"),
            "reason": _clip(health.get("reason", ""), 320),
        },
        "trajectory": {
            "failed_hypotheses": execution.get("failed_hypotheses", 0),
            "reroutes": execution.get("reroutes", 0),
            "brain_reviews": execution.get("brain_reviews", 0),
        },
        "evidence": _clip(evidence or [], 400),
        "question": _clip(question, 800),
    }

    def size() -> int:
        return len(json.dumps(packet, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))

    while size() > max_bytes and packet["evidence"]:
        packet["evidence"].pop()

    if size() > max_bytes:
        for field in ("proof", "owner", "must_not", "must"):
            values = packet.get(field)
            if isinstance(values, list) and len(values) > 2:
                packet[field] = values[:2]
            if size() <= max_bytes:
                break

    if size() > max_bytes:
        packet["question"] = _clip(str(packet["question"]), 300)
        packet["goal"] = _clip(str(packet["goal"]), 400)
        packet["current_slice"] = _clip(str(packet["current_slice"]), 250)
        packet["next"] = _clip(str(packet["next"]), 250)

    rendered_size = size()
    if rendered_size > max_bytes:
        raise ValueError(f"brain packet exceeds hard limit: {rendered_size} > {max_bytes}")

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
