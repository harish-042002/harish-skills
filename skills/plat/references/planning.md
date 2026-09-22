# Planning and System Design

Use for multi-file work, architecture, migrations, unclear requirements, or meaningful failure/compatibility risk.

## Match plan depth to risk

- Tiny: direct implementation; no written plan needed.
- Medium: short ordered steps plus proof for each.
- Large/high-risk: explicit contracts, dependencies, rollout/rollback, failure modes, and validation.

Do not create a large plan to avoid doing obvious work.

## Planning sequence

1. Define observable success and acceptance cases.
2. Separate known requirements from assumptions. Resolve from repository evidence first; ask the developer only when an unresolved choice materially changes behavior, scope, compatibility, risk, or a hard-to-reverse action.
3. Record hard constraints: compatibility, latency, throughput, cost, security, platform/framework, migration, rollout.
4. Map the current ownership boundaries and source of truth.
5. Choose the smallest viable change before designing a larger target architecture.
6. Define interfaces/data flow before internal implementation detail.
7. Identify state, concurrency, failure, retry, and recovery behavior where relevant.
8. Plan coexistence for old/new schemas, APIs, workers, clients, or services when deployments can overlap.
9. Break work into independently verifiable slices with real dependencies.
10. Attach proof to each slice.
11. Define rollback, disable, or forward-fix strategy when production impact is meaningful.

## Simplicity challenge

Before adding a service, queue, cache, database, framework, abstraction, dependency, or background worker, answer:

- What concrete requirement does it solve?
- Can the current system solve that safely?
- What failure/operational cost does the new component introduce?
- What measured or explicit threshold makes the simpler design inadequate?

Weak answers mean use the simpler design.

## Architecture checks

Consider only when applicable:

- Single source of truth and ownership.
- Transaction/consistency boundary.
- Idempotency and retries.
- Ordering and clock assumptions.
- Timeouts, cancellation, capacity, and backpressure.
- Schema/API/event evolution.
- Cache freshness/invalidation.
- Security/trust boundary.
- Observability and recovery.
- Deployment/migration coexistence.

## Re-plan triggers

Stop and update the plan when:

- Repository evidence contradicts a core assumption.
- A required public/data contract change was not anticipated.
- The intended slice cannot be verified independently.
- Repeated implementation friction reveals the chosen boundary is wrong.
- The change grows materially beyond the accepted scope.

Do not preserve a stale plan for consistency's sake.

## Task graph and delegation

Express actual dependencies. Shared contracts, schemas, migrations, and primitives usually precede consumers. Parallelize only independent tasks. Read `subagents.md` when delegation reduces wall time or context pollution enough to justify coordination cost.

## Decision record

Persist only decisions that are non-obvious, costly to reverse, or likely to be revisited:

```text
Decision: ...
Reason: ...
Rejected simpler option: ...
Trigger to revisit: ...
```
