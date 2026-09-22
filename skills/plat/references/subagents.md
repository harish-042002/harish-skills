# Subagents and Delegation

Use when bounded independent work, broad exploration, parallel verification, or fresh-context review materially improves speed or context quality.

## Default

Do not delegate by reflex. Coordination costs tokens and creates merge/consistency risk. If no subagent capability exists, execute the same dependency graph sequentially without ceremony.

Keep with the main agent: architecture/high-impact trade-offs, ambiguous scope, shared contracts/schemas, security/destructive decisions, integration, and final completion judgment.

Delegate when benefit exceeds coordination cost, for example:

- Two or more tasks are truly independent.
- Broad search can become a compact map.
- A bounded implementation has clear inputs/outputs and low integration ambiguity.
- Tests/docs/review can proceed independently.
- A fresh reviewer can challenge a non-obvious/high-risk artifact.
- A cheaper/faster model can handle bounded low-risk work without likely rework.

## Worker modes

### Scout

Inspect/search only; do not edit. Return relevant files/symbols/data flow/evidence/risks.

### Implementer

Change only defined scope and run specified proof. If correctness requires widening scope/shared contracts, stop and return the dependency instead of silently expanding.

### Reviewer

Receive artifact/diff + acceptance criteria + hard constraints. Prefer fresh context for high-risk review. Inspect evidence independently; do not inherit the author's rationale by default.

## Task contract

Send minimum sufficient context:

```text
GOAL
Observable result.

SCOPE
Allowed files/modules/data.

CONSTRAINTS
Contracts, patterns, risks, dependencies.

VERIFY
Exact evidence expected.

RETURN
Findings or changed files; verification; risks/blockers. No narration.
```

Reference existing artifacts by path instead of copying them.

## Parallel execution

1. Identify outputs and real dependencies.
2. Resolve shared contracts/schemas/primitives first.
3. Launch only unblocked tasks.
4. Avoid parallel edits to the same fragile files unless isolation/merge handling is explicit; use separate worktrees/branches/workspaces or strict file ownership when the runtime supports it.
5. Do not duplicate the same task across workers unless diversity is intentional and worth reconciliation cost.
6. Integrate and verify each wave before launching dependents.

Parallelism should shorten the critical path, not increase activity.

## Context and model economy

Do not send full chat/repository snapshots by default. Let workers inspect bounded scope. Compress results into durable findings rather than flooding main context.

When model selection exists, reserve stronger reasoning for architecture, subtle debugging, integration, or high-risk review; use economical models for bounded search/routine implementation/test execution when quality is adequate. Choose by capability/risk, not brand. A cheap worker that causes repair is not cheaper.

## Acceptance

A worker saying "done" is not proof. Inspect/reconcile the result and require fresh verification. The main agent owns the final completion claim.
