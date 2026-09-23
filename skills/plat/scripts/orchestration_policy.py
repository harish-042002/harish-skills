#!/usr/bin/env python3
"""Deterministic guardrails for Plat orchestration.

This is a CI/diagnostic helper, not part of the normal Quick/Standard runtime.
It tests delegation caps and circuit breakers from already-classified facts.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict

VALID_DEPTHS = {"Quick", "Standard", "Deep", "Research"}


@dataclass(frozen=True)
class Decision:
    action: str
    lead_control: str
    initial_specialists: int
    max_specialists: int
    parallel_limit: int
    external_skill: bool
    handoff: bool
    recursive_delegation: bool
    reason_codes: tuple[str, ...]


def decide(
    *,
    depth: str,
    unresolved: int = 0,
    independent: int = 0,
    built_in_sufficient: bool = True,
    external_match: bool = False,
    mutating: bool = False,
    shared_state: bool = False,
    same_question_rounds: int = 0,
    host_handoff: bool = False,
    specialist_should_own_turn: bool = False,
    research_oriented: bool = False,
    wall_time_critical: bool = False,
) -> Decision:
    if depth not in VALID_DEPTHS:
        raise ValueError(f"invalid depth: {depth}")
    if min(unresolved, independent, same_question_rounds) < 0:
        raise ValueError("counts must be >= 0")

    reasons: list[str] = []

    # Circuit breaker wins over adding another specialist.
    if same_question_rounds >= 2:
        return Decision(
            action="reroute",
            lead_control="manager",
            initial_specialists=0,
            max_specialists=0,
            parallel_limit=0,
            external_skill=False,
            handoff=False,
            recursive_delegation=False,
            reason_codes=("same-question-circuit-breaker",),
        )

    if depth == "Quick" or unresolved == 0:
        reasons.append("lead-can-finish")
        return Decision(
            action="lead",
            lead_control="manager",
            initial_specialists=0,
            max_specialists=0,
            parallel_limit=0,
            external_skill=False,
            handoff=False,
            recursive_delegation=False,
            reason_codes=tuple(reasons),
        )

    if depth == "Research" and not research_oriented:
        return Decision(
            action="lead",
            lead_control="manager",
            initial_specialists=0,
            max_specialists=0,
            parallel_limit=0,
            external_skill=False,
            handoff=False,
            recursive_delegation=False,
            reason_codes=("research-orient-first",),
        )

    if depth == "Standard":
        if built_in_sufficient:
            reasons.append("standard-built-in-sufficient")
            return Decision(
                action="lead",
                lead_control="manager",
                initial_specialists=0,
                max_specialists=0,
                parallel_limit=0,
                external_skill=False,
                handoff=False,
                recursive_delegation=False,
                reason_codes=tuple(reasons),
            )
        reasons.append("standard-capability-gap")
        use_external = bool(external_match)
        if use_external:
            reasons.append("matching-external-specialist")
        handoff = bool(
            host_handoff
            and specialist_should_own_turn
            and not mutating
            and not shared_state
        )
        if handoff:
            reasons.append("explicit-handoff-fit")
        return Decision(
            action="consult",
            lead_control="handoff" if handoff else "manager",
            initial_specialists=1,
            max_specialists=1,
            parallel_limit=1,
            external_skill=use_external,
            handoff=handoff,
            recursive_delegation=False,
            reason_codes=tuple(reasons),
        )

    # Deep/Research add specialists only after the lead has localized the work.
    cap = min(3, max(1, unresolved))
    parallel = 1
    if independent >= 2 and not mutating and not shared_state:
        default_parallel_cap = 2 if depth == "Research" and not wall_time_critical else 3
        parallel = min(default_parallel_cap, independent, cap)
        reasons.append("independent-readonly-parallel")
        if depth == "Research" and parallel == 2 and independent >= 3 and not wall_time_critical:
            reasons.append("research-cost-cap-two")
        if depth == "Research" and wall_time_critical and parallel >= 3:
            reasons.append("research-wall-time-override")
    elif independent >= 2:
        reasons.append("shared-mutation-sequential")

    if depth == "Research":
        reasons.append("research-specialist")
    else:
        reasons.append("deep-specialist")

    use_external = bool((not built_in_sufficient) and external_match)
    if use_external:
        reasons.append("matching-external-specialist")
    elif not built_in_sufficient:
        reasons.append("no-external-match")

    handoff = bool(
        host_handoff
        and specialist_should_own_turn
        and cap == 1
        and not mutating
        and not shared_state
    )
    if handoff:
        reasons.append("explicit-handoff-fit")

    return Decision(
        action="consult",
        lead_control="manager" if not handoff else "handoff",
        initial_specialists=1,
        max_specialists=cap,
        parallel_limit=parallel,
        external_skill=use_external,
        handoff=handoff,
        recursive_delegation=False,
        reason_codes=tuple(reasons),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Plat orchestration guardrails.")
    parser.add_argument("--json", help="JSON object with already-classified orchestration facts.")
    args = parser.parse_args()

    if args.json:
        payload = json.loads(args.json)
    else:
        payload = json.load(__import__("sys").stdin)

    result = decide(**payload)
    print(json.dumps(asdict(result), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
