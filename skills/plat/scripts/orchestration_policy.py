#!/usr/bin/env python3
"""Deterministic Plat runtime escalation, Brain, and context-isolation policy."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

VALID_PATHS = {"DIRECT", "STANDARD", "ESCALATED"}
LEGACY_DEPTH_MAP = {
    "Quick": "DIRECT",
    "Standard": "STANDARD",
    "Deep": "ESCALATED",
    "Research": "ESCALATED",
}
VALID_HEALTH = {"GREEN", "YELLOW", "RED", "BLOCKED"}
VALID_CONTEXT_HEALTH = {"GREEN", "YELLOW", "RED"}
MAX_BRAIN_REVIEWS = 2
MAX_FRESH_CONTEXT_WORKERS = 1


@dataclass(frozen=True)
class Decision:
    action: str
    execution_path: str
    initial_specialists: int
    max_specialists: int
    parallel_limit: int
    external_skill: bool
    brain_review: bool
    fresh_context_worker: bool
    worker_tier: str
    brain_tier: str
    recursive_delegation: bool
    reason_codes: tuple[str, ...]


def decide(
    *,
    execution_path: str | None = None,
    depth: str | None = None,
    unresolved: int = 0,
    independent: int = 0,
    built_in_sufficient: bool = True,
    external_match: bool = False,
    capability_gap: bool = False,
    second_boundary_earned: bool = False,
    mutating: bool = False,
    shared_state: bool = False,
    same_question_rounds: int = 0,
    research_task: bool = False,
    research_oriented: bool = False,
    wall_time_critical: bool = False,
    health: str = "GREEN",
    context_health: str = "GREEN",
    host_isolated_context: bool = False,
    fresh_context_workers: int = 0,
    brain_preflight: bool = False,
    brain_reviews: int = 0,
    failed_hypotheses: int = 0,
    reroutes: int = 0,
    scope_drift: bool = False,
    **_legacy: object,
) -> Decision:
    if execution_path is None:
        if depth is None:
            execution_path = "STANDARD"
        elif depth in LEGACY_DEPTH_MAP:
            execution_path = LEGACY_DEPTH_MAP[depth]
            research_task = research_task or depth == "Research"
        else:
            raise ValueError(f"invalid legacy depth: {depth}")

    execution_path = execution_path.upper()
    if execution_path not in VALID_PATHS:
        raise ValueError(f"invalid execution_path: {execution_path}")
    if health not in VALID_HEALTH:
        raise ValueError(f"invalid health: {health}")
    if context_health not in VALID_CONTEXT_HEALTH:
        raise ValueError(f"invalid context_health: {context_health}")
    if min(
        unresolved,
        independent,
        same_question_rounds,
        brain_reviews,
        failed_hypotheses,
        reroutes,
        fresh_context_workers,
    ) < 0:
        raise ValueError("counts must be >= 0")

    reasons: list[str] = []
    worker_tier = "cost-efficient-latest"
    brain_tier = "one-tier-stronger-cost-effective"

    unhealthy = bool(
        health == "RED"
        or failed_hypotheses >= 2
        or reroutes >= 2
        or scope_drift
    )
    brain_review = bool(
        brain_reviews < MAX_BRAIN_REVIEWS
        and (brain_preflight or unhealthy)
    )

    if brain_review:
        reasons.append("brain-course-correction")
    elif unhealthy and brain_reviews >= MAX_BRAIN_REVIEWS:
        reasons.append("brain-budget-exhausted")

    if context_health == "YELLOW":
        reasons.append("context-yellow-use-pointers")
    elif context_health == "RED":
        reasons.append("context-red-isolate")

    if health == "BLOCKED":
        return Decision(
            "surface-blocker",
            execution_path,
            0,
            0,
            0,
            False,
            False,
            False,
            worker_tier,
            brain_tier,
            False,
            tuple(reasons + ["blocked-authority"]),
        )

    if same_question_rounds >= 2:
        return Decision(
            "reroute",
            execution_path,
            0,
            0,
            0,
            False,
            brain_review,
            False,
            worker_tier,
            brain_tier,
            False,
            tuple(reasons + ["same-question-circuit-breaker"]),
        )

    # Context pressure is not itself a reasoning failure. On STANDARD/ESCALATED
    # work, isolate exactly one execution worker when the host can provide a
    # fresh context. This is an economics exception, not specialist fan-out.
    if (
        context_health == "RED"
        and execution_path != "DIRECT"
        and not unhealthy
    ):
        if (
            host_isolated_context
            and fresh_context_workers < MAX_FRESH_CONTEXT_WORKERS
        ):
            return Decision(
                "fresh-context-worker",
                execution_path,
                0,
                0,
                0,
                False,
                False,
                True,
                worker_tier,
                brain_tier,
                False,
                tuple(reasons + ["single-fresh-context-worker"]),
            )
        return Decision(
            "checkpoint-compact",
            execution_path,
            0,
            0,
            0,
            False,
            False,
            False,
            worker_tier,
            brain_tier,
            False,
            tuple(reasons + ["fresh-context-unavailable-or-used"]),
        )

    if execution_path == "DIRECT":
        return Decision(
            "reroute" if unhealthy else "lead",
            execution_path,
            0,
            0,
            0,
            False,
            False,
            False,
            worker_tier,
            brain_tier,
            False,
            tuple(reasons + ["direct-fast-path"]),
        )

    if execution_path == "STANDARD":
        return Decision(
            "brain-review" if brain_review else "lead",
            execution_path,
            0,
            0,
            0,
            False,
            brain_review,
            False,
            worker_tier,
            brain_tier,
            False,
            tuple(reasons + ["standard-single-agent"]),
        )

    if research_task and not research_oriented:
        return Decision(
            "lead",
            execution_path,
            0,
            0,
            0,
            False,
            brain_review,
            False,
            worker_tier,
            brain_tier,
            False,
            tuple(reasons + ["research-orient-first"]),
        )

    if unresolved == 0 and not capability_gap:
        return Decision(
            "brain-review" if brain_review else "lead",
            execution_path,
            0,
            0,
            0,
            False,
            brain_review,
            False,
            worker_tier,
            brain_tier,
            False,
            tuple(reasons + ["no-unresolved-boundary"]),
        )

    max_specialists = 1
    if second_boundary_earned and unresolved >= 2:
        max_specialists = 2
        reasons.append("second-boundary-earned")

    parallel_limit = 1
    if (
        max_specialists == 2
        and independent >= 2
        and not mutating
        and not shared_state
        and wall_time_critical
    ):
        parallel_limit = 2
        reasons.append("independent-readonly-parallel")

    use_external = bool(
        capability_gap and not built_in_sufficient and external_match
    )
    if use_external:
        reasons.append("bounded-external-specialist")

    action = "brain-review" if brain_review else "consult"
    return Decision(
        action,
        execution_path,
        1,
        max_specialists,
        parallel_limit,
        use_external,
        brain_review,
        False,
        worker_tier,
        brain_tier,
        False,
        tuple(reasons + ["escalated-one-first"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Plat runtime guardrails.")
    parser.add_argument("--json", help="JSON object with already-classified facts.")
    args = parser.parse_args()
    payload = (
        json.loads(args.json)
        if args.json
        else json.load(__import__("sys").stdin)
    )
    print(json.dumps(asdict(decide(**payload)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
