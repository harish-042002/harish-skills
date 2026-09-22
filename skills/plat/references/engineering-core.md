# Engineering Core

Use for non-trivial implementation, refactoring, architecture, and code-quality decisions.

## Priority order

1. Correct observable behavior.
2. Clear contracts and invariants.
3. Reliability under expected failure modes.
4. Simplicity and human readability.
5. Security and compatibility.
6. Measured performance and scalability.
7. Convenience and cleverness.

Never improve a lower priority by silently damaging a higher one.

## Before coding

- Define the observable success condition and meaningful acceptance cases.
- Find the owning boundary: UI, application/service, domain, persistence, infrastructure, or external system.
- Search for existing implementation patterns before inventing another.
- Ask whether code is needed at all; configuration, deletion, a constraint, or platform feature may solve it better.
- Identify public/data compatibility constraints before changing shared behavior.
- For version-sensitive framework/library behavior, inspect the installed version and prefer current official/local documentation over model memory.

## Implementation rules

- Prefer explicit conventional control flow over clever compression. Fewer lines are not the goal; lower cognitive load is.
- Keep side effects visible and localized.
- Separate pure calculation from I/O when it materially improves reasoning or tests.
- Name by domain meaning, not accidental implementation detail.
- Model meaningful states explicitly when boolean combinations become ambiguous.
- Reject impossible states early with types, schemas, validation, or durable constraints when practical.
- Use data structures that match access patterns; simplicity does not mean avoiding maps, sets, queues, heaps, indexes, or graphs.
- Prefer one canonical path for the same job. Remove duplicate ways of doing the same thing when safely in scope.
- Extract abstractions around a repeated concept, not merely repeated syntax.
- Prefer composition over deep inheritance unless the framework strongly requires otherwise.
- Convert errors only at boundaries that have enough context to handle/map them meaningfully; never swallow them.
- Comments should preserve non-obvious intent, invariant, trade-off, or workaround context; do not narrate code that is already clear.

## Trajectory control
Earlier plans/code are provisional when new evidence appears. On a developer correction, failed proof, or repository contradiction:

1. Stop expanding the affected path and name the invalid assumption; do not merely agree.
2. Re-check only evidence needed to resolve the contradiction.
3. Update the working spec/plan/session state.
4. Keep valid work; undo/rework only the slice built on the invalid assumption.
5. Resume against the corrected outcome with fresh evidence.

Do not periodically second-guess a valid path without new evidence; course correction should reduce rework, not create a reflection loop.

## Thin-slice rule
For multi-step work, prefer the smallest vertical slice that can be verified end-to-end. Verify it before expanding the pattern. If a slice disproves an assumption, update the plan rather than scaling the wrong approach.

## Complexity rule

For code whose cost can grow materially, reason about the dominant term:

- CPU and memory complexity.
- Database round trips, locks, rows scanned, and result size.
- Network calls, payload size, and external rate/latency limits.
- Serialization/deserialization and disk I/O.

Do not complicate five-item code to improve an irrelevant Big-O term while ignoring a 500 ms remote call. Do fix algorithmic or query complexity when expected scale makes it material.

## Scope discipline

- Keep the patch aligned with the task.
- Refactor adjacent code only when needed for correctness, safe implementation, or substantial simplification.
- Separate broad cleanup from behavior changes when mixing them harms review or rollback.
- Avoid speculative extension points, wrapper-on-wrapper layers, one-use configuration systems, and future-proofing without a current requirement.
- Add an extension point when a real second use or near-certain requirement exists.
- Treat surface area as a budget: every new public symbol, file, layer, dependency, service, or indirection should pay for itself by removing more complexity or satisfying a concrete requirement. Architecture that only adds has failed the simplicity check.
- Delete dead or superseded paths when the migration/removal is safe and within scope; do not preserve obsolete code solely because an agent is afraid to remove it.
- When an important structural rule is repeatedly violated, prefer a small existing-tool automated guard/CI check over more prose; do not build a custom enforcement system for a one-off concern.

## Review in two stages

### 1. Requirement compliance

- Does the result satisfy the stated behavior and constraints?
- Did scope drift or an unstated assumption change the requirement?
- Are contracts/data migrations/backward compatibility correct?

Fix compliance issues before polishing implementation quality.

### 2. Engineering quality

Check only what is relevant. Rank findings by impact: correctness/security/data-loss/compatibility blockers first, structural simplifications next, style nits last and clearly optional. A few high-confidence findings beat a long list of low-value comments. After correctness is proven, ask whether a new team member would understand the result faster than the previous version:

- Edge/null/boundary behavior.
- Error, timeout, retry, and recovery behavior.
- Concurrency/ordering/shared state.
- Security/trust boundaries.
- Operability for important failures.
- Readability for a developer unfamiliar with the change.
- Dead code, duplication, wrappers, dependencies, or abstractions that can be removed.

## Delivery
Prefer atomic, reviewable, reversible changes. Do not create commits unless requested or required by repository workflow. Never infer production readiness from unit tests alone when runtime, integration, migration, concurrency, or deployment behavior is material.
