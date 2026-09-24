# Execution Path Selection

Read only when DIRECT vs STANDARD vs ESCALATED is genuinely uncertain.

## DIRECT

Choose DIRECT when all are true enough:

- ownership is obvious;
- requested delta is local and reversible;
- no protected contract/data/security boundary changes;
- direct proof is cheap.

Examples: copy/constant change, isolated styling, known-file correction, simple config update.

## STANDARD

Default for normal product engineering:

- one subsystem or understandable cross-file path;
- targeted repository discovery can localize ownership;
- no concrete high-risk boundary remains unresolved;
- one knowledge card is enough if guidance is needed.

Large prompt length or repository size alone does not change STANDARD to ESCALATED.

## ESCALATED

Choose only for a named hard question such as:

- concurrency, ordering, distributed state, retries/idempotency;
- production-only/intermittent failure;
- authentication/authorization/tenant isolation/money/destructive data;
- public API/schema/data migration/coexistence;
- major architecture boundary;
- measured performance/capacity requiring profiling/load evidence;
- complex RAG/agent/eval/memory/tool behavior;
- mobile lifecycle/offline/process death;
- two or more failed hypotheses/reroutes on the same unresolved question.

Escalation is an investment. Name the unresolved question before loading deeper guidance or another agent.

## Research is a task type, not a fourth depth

A research/audit request still uses STANDARD or ESCALATED execution. The lead first creates a task-scoped comparison model/evidence ledger, then may use one bounded scout if it materially saves wall time/context. Do not turn "research" into permission for unrestricted reading.

## De-escalate

Return to STANDARD/DIRECT when evidence localizes the problem. Do not stay ESCALATED because the task started there.

## Reference budget

- DIRECT: 0 extra references normally.
- STANDARD: 1 directly relevant knowledge card.
- ESCALATED: 1 relevant card plus at most 1 deep card for the named hard question.

No reference-to-reference exploration without a new named unresolved question.
