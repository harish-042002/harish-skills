#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 3
DEFAULT_CHECKPOINT_SECONDS = 300
YELLOW_AFTER_SECONDS = 300
RED_AFTER_SECONDS = 600
ORDINARY_BRAIN_AFTER_SECONDS = 1200
MAX_BRAIN_REVIEWS = 2
VALID_HEALTH = {"GREEN", "YELLOW", "RED", "BLOCKED"}
VALID_ROUTES = {"DIRECT", "STANDARD", "ESCALATED"}

def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()

def parse_time(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)

def elapsed_seconds(start: str, end: str) -> int:
    return max(0, int((parse_time(end) - parse_time(start)).total_seconds()))

def new_state(goal: str, *, started_at: str | None = None, route: str = "STANDARD", worker_tier: str = "cost-efficient-latest") -> dict[str, Any]:
    route = route.upper()
    if route not in VALID_ROUTES:
        raise ValueError(f"invalid route: {route}")
    stamp = started_at or now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "goal": goal.strip(),
        "must": [],
        "must_not": [],
        "preserve": [],
        "owner": [],
        "current_slice": "",
        "accepted_evidence": [],
        "proof": [],
        "next": "",
        "execution": {
            "route": route,
            "worker_tier": worker_tier,
            "brain_tier": "one-tier-stronger-cost-effective",
            "started_at": stamp,
            "last_checkpoint_at": stamp,
            "last_progress_at": stamp,
            "brain_reviews": 0,
            "reroutes": 0,
            "failed_hypotheses": 0,
        },
        "health": {"status": "GREEN", "reason": "task started", "action": "continue"},
    }

def evaluate_checkpoint(
    state: dict[str, Any],
    *,
    at: str | None = None,
    meaningful_progress: bool = False,
    blocked: bool = False,
    waiting: bool = False,
    reason: str = "",
    checkpoint_seconds: int = DEFAULT_CHECKPOINT_SECONDS,
) -> dict[str, Any]:
    stamp = at or now_iso()
    execution = state["execution"]
    since_checkpoint = elapsed_seconds(execution["last_checkpoint_at"], stamp)
    since_progress = elapsed_seconds(execution["last_progress_at"], stamp)
    elapsed = elapsed_seconds(execution["started_at"], stamp)

    if blocked:
        state["health"] = {"status": "BLOCKED", "reason": reason or "requires external authority or unavailable evidence", "action": "ask-or-unblock"}
        execution["last_checkpoint_at"] = stamp
        return {"due": True, "elapsed": elapsed, "since_progress": since_progress, "brain_recommended": False, "state": state}

    if since_checkpoint < checkpoint_seconds:
        return {"due": False, "elapsed": elapsed, "since_progress": since_progress, "brain_recommended": False, "state": state}

    execution["last_checkpoint_at"] = stamp

    if meaningful_progress:
        execution["last_progress_at"] = stamp
        state["health"] = {"status": "GREEN", "reason": reason or "meaningful progress observed", "action": "continue"}
        return {"due": True, "elapsed": elapsed, "since_progress": 0, "brain_recommended": False, "state": state}

    if waiting:
        state["health"] = {"status": "GREEN", "reason": reason or "waiting on known long-running operation", "action": "continue"}
        return {"due": True, "elapsed": elapsed, "since_progress": since_progress, "brain_recommended": False, "state": state}

    if since_progress >= RED_AFTER_SECONDS:
        status, action = "RED", "brain-review"
    elif since_progress >= YELLOW_AFTER_SECONDS:
        status, action = "YELLOW", "act-verify-reroute"
    else:
        status, action = "GREEN", "continue"

    brain_recommended = bool(
        execution.get("brain_reviews", 0) < MAX_BRAIN_REVIEWS
        and (
            status == "RED"
            or (elapsed >= ORDINARY_BRAIN_AFTER_SECONDS and since_progress >= YELLOW_AFTER_SECONDS)
            or execution.get("failed_hypotheses", 0) >= 2
            or execution.get("reroutes", 0) >= 2
        )
    )
    if status == "RED" and not brain_recommended:
        action = "reroute-or-surface-blocker"

    state["health"] = {"status": status, "reason": reason or f"no meaningful progress for {since_progress}s", "action": action}
    return {"due": True, "elapsed": elapsed, "since_progress": since_progress, "brain_recommended": brain_recommended, "state": state}

def record_event(state: dict[str, Any], event: str) -> dict[str, Any]:
    execution = state["execution"]
    if event == "brain-review":
        if int(execution.get("brain_reviews", 0)) >= MAX_BRAIN_REVIEWS:
            state["health"] = {"status": "RED", "reason": "brain review budget exhausted", "action": "reroute-or-surface-blocker"}
            return state
        execution["brain_reviews"] = int(execution.get("brain_reviews", 0)) + 1
    elif event == "reroute":
        execution["reroutes"] = int(execution.get("reroutes", 0)) + 1
    elif event == "failed-hypothesis":
        execution["failed_hypotheses"] = int(execution.get("failed_hypotheses", 0)) + 1
    else:
        raise ValueError(f"invalid event: {event}")
    return state

def record_brain_review(state: dict[str, Any]) -> dict[str, Any]:
    return record_event(state, "brain-review")

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def save(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description="Maintain Plat compact task runtime state.")
    parser.add_argument("--state", default=".plat/session.json")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start")
    start.add_argument("--goal", required=True)
    start.add_argument("--route", choices=sorted(VALID_ROUTES), default="STANDARD")
    start.add_argument("--worker-tier", default="cost-efficient-latest")
    check = sub.add_parser("checkpoint")
    check.add_argument("--progress", action="store_true")
    check.add_argument("--blocked", action="store_true")
    check.add_argument("--waiting", action="store_true")
    check.add_argument("--reason", default="")
    event = sub.add_parser("event")
    event.add_argument("--kind", choices=["brain-review", "reroute", "failed-hypothesis"], required=True)
    sub.add_parser("brain-review")
    sub.add_parser("show")
    args = parser.parse_args()
    path = Path(args.state)

    if args.command == "start":
        state = new_state(args.goal, route=args.route, worker_tier=args.worker_tier)
        save(path, state)
        print(json.dumps(state, indent=2, sort_keys=True))
        return 0

    state = load(path)
    if args.command == "checkpoint":
        result = evaluate_checkpoint(state, meaningful_progress=args.progress, blocked=args.blocked, waiting=args.waiting, reason=args.reason)
        save(path, result["state"])
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    if args.command == "brain-review":
        state = record_brain_review(state)
        save(path, state)
        print(json.dumps(state, indent=2, sort_keys=True))
        return 0
    if args.command == "event":
        state = record_event(state, args.kind)
        save(path, state)
        print(json.dumps(state, indent=2, sort_keys=True))
        return 0

    print(json.dumps(state, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
