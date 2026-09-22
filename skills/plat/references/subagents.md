# Subagents and Delegation

Use when independently bounded work, broad exploration, parallel verification, or fresh-context review materially improves speed or context quality.

## Default

Do not delegate by reflex. Coordination consumes tokens, introduces merge risk, and can duplicate work. If the runtime has no subagent capability, execute the same dependency graph sequentially without adding ceremony.

Keep with the main agent:

- Architecture and high-impact trade-offs.
- Ambiguous requirements and scope decisions.
- Shared contract/schema decisions.
- Security-sensitive/destructive choices.
- Cross-task integration.
- Final evidence review and completion judgment.

Delegate when the expected reduction in critical-path time or main-context pollution is larger than the coordination cost:

- At least two tasks are truly independent.
- Broad search can be turned into a compact map.
- A bounded implementation has clear inputs/outputs and low integration ambiguity.
- Tests/docs/review can proceed independently.
- A fresh reviewer can challenge a non-obvious/high-risk artifact.
- A cheaper/faster model can perform bounded low-risk work without causing rework.

## Choose worker mode explicitly

### Scout

Inspect/search only. Do not edit. Return relevant files/symbols/data flow/evidence/risks.

Use scouts when the main value is context compression or parallel repository discovery.

### Implementer

Change only the defined scope. Follow existing patterns. Run the specified proof. If correctness requires touching an excluded/shared contract or file, stop and return the dependency instead of silently widening scope. Return changed files, verification, and blockers.

### Reviewer

Receive the artifact/diff plus acceptance criteria and hard constraints. Prefer fresh context for high-risk decisions. Find requirement violations, correctness/security/compatibility gaps, and simpler alternatives. Do not inherit the author's rationale by default; independently inspect evidence so review is not anchored to the implementation story.

## Task contract

Send minimum sufficient context:

```text
GOAL
Observable result.

SCOPE
Files/modules/data the worker may inspect/change.

CONSTRAINTS
Contracts, patterns, risks, dependencies.

VERIFY
Exact evidence expected.

RETURN
Findings or changed files; verification; risks/blockers. No narration.
```

Reference existing artifacts by path instead of copying them into every worker prompt.

## Dependency graph

Before parallel edits:

1. Identify tasks and outputs.
2. Add only real dependencies.
3. Resolve shared schema/contracts/primitives first.
4. Launch only currently unblocked tasks.
5. Avoid parallel edits to the same fragile files unless isolation/merge handling is explicit.
6. Do not assign the same task to multiple workers unless independent diversity is intentional and the reconciliation cost is justified.
7. Integrate and verify each wave before launching dependent work.

Parallelism should shorten the critical path, not merely increase activity.

## Context isolation

Do not send full chat history or entire repository snapshots by default. Give a worker enough information to act correctly, then let it inspect its bounded scope.

Do not run multiple scouts over the same search unless diversity is intentional (for example independent security review).

Worker output should be compressed into durable findings; raw exploratory output should not flood main context.

## Model economy

When runtime supports model selection:

- Strong reasoning: architecture, subtle debugging, integration, high-risk review.
- Standard/fast/economical: bounded exploration, routine implementation, test generation/execution, formatting/docs.

Choose by capability/risk, not brand. If the runtime cannot select models, keep the same task decomposition without pretending model tiers exist.

A cheaper worker that triggers repeated repair is not cheaper.

## Acceptance

A worker saying "done" is not proof. Inspect the result, reconcile it with shared contracts, and require appropriate fresh verification before accepting it into the main task. The main agent owns the final completion claim.
