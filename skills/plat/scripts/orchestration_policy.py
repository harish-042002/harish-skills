#!/usr/bin/env python3
"""Deterministic Plat v2 runtime/orchestration guardrails."""
from __future__ import annotations
import argparse, json
from dataclasses import asdict, dataclass

VALID_DEPTHS = {"Quick", "Standard", "Deep", "Research"}
VALID_HEALTH = {"GREEN", "YELLOW", "RED", "BLOCKED"}
MAX_BRAIN_REVIEWS = 2

@dataclass(frozen=True)
class Decision:
    action: str
    lead_control: str
    initial_specialists: int
    max_specialists: int
    parallel_limit: int
    external_skill: bool
    brain_review: bool
    worker_tier: str
    brain_tier: str
    recursive_delegation: bool
    reason_codes: tuple[str, ...]

def decide(*, depth: str, unresolved: int = 0, independent: int = 0, built_in_sufficient: bool = True,
           external_match: bool = False, capability_gap: bool = False, second_boundary_earned: bool = False,
           mutating: bool = False, shared_state: bool = False, same_question_rounds: int = 0,
           research_oriented: bool = False, wall_time_critical: bool = False, health: str = "GREEN",
           brain_preflight: bool = False, brain_reviews: int = 0, **_legacy: object) -> Decision:
    if depth not in VALID_DEPTHS:
        raise ValueError(f"invalid depth: {depth}")
    if health not in VALID_HEALTH:
        raise ValueError(f"invalid health: {health}")
    if min(unresolved, independent, same_question_rounds, brain_reviews) < 0:
        raise ValueError("counts must be >= 0")

    reasons: list[str] = []
    worker_tier = "cost-efficient-latest"
    brain_tier = "one-tier-stronger-cost-effective"
    brain_review = bool(brain_reviews < MAX_BRAIN_REVIEWS and (brain_preflight or health == "RED"))
    if brain_review:
        reasons.append("brain-course-correction")
    elif health == "RED" and brain_reviews >= MAX_BRAIN_REVIEWS:
        reasons.append("brain-budget-exhausted")

    if health == "BLOCKED":
        return Decision("surface-blocker", "manager", 0, 0, 0, False, False, worker_tier, brain_tier, False, tuple(reasons + ["blocked-authority"]))

    if same_question_rounds >= 2:
        return Decision("reroute", "manager", 0, 0, 0, False, brain_review, worker_tier, brain_tier, False, tuple(reasons + ["same-question-circuit-breaker"]))

    if depth in {"Quick", "Standard"} or unresolved == 0:
        reasons.append("single-agent-hot-path")
        return Decision("lead", "manager", 0, 0, 0, False, brain_review, worker_tier, brain_tier, False, tuple(reasons))

    if depth == "Research" and not research_oriented:
        return Decision("lead", "manager", 0, 0, 0, False, brain_review, worker_tier, brain_tier, False, tuple(reasons + ["research-orient-first"]))

    max_specialists = 1
    if second_boundary_earned and unresolved >= 2:
        max_specialists = 2
        reasons.append("second-boundary-earned")

    parallel_limit = 1
    if max_specialists == 2 and independent >= 2 and not mutating and not shared_state and (depth == "Deep" or wall_time_critical):
        parallel_limit = 2
        reasons.append("independent-readonly-parallel")

    use_external = bool(capability_gap and not built_in_sufficient and external_match)
    if use_external:
        reasons.append("bounded-external-specialist")
    elif capability_gap and not built_in_sufficient:
        reasons.append("capability-gap-no-external-match")

    reasons.append("escalated-one-first")
    return Decision("consult", "manager", 1, max_specialists, parallel_limit, use_external, brain_review, worker_tier, brain_tier, False, tuple(reasons))

def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Plat v2 runtime guardrails.")
    parser.add_argument("--json", help="JSON object with already-classified facts.")
    args = parser.parse_args()
    payload = json.loads(args.json) if args.json else json.load(__import__("sys").stdin)
    print(json.dumps(asdict(decide(**payload)), indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
