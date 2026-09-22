# Planning and System Design

Use for multi-file work, architecture, migrations, unclear requirements, or meaningful failure/compatibility risk.

## Match plan depth to risk

- Tiny: direct implementation; no written plan needed.
- Medium: short ordered steps plus proof for each.
- Large/high-risk: explicit contracts, dependencies, rollout/rollback, failure modes, and validation.

Do not create a large plan to avoid doing obvious work. Normal feature work does **not** require a formal spec.

## Planning sequence

1. Define observable success and acceptance cases.
2. Separate known requirements from assumptions. Resolve from repository evidence first; ask the developer only when an unresolved choice materially changes behavior, scope, compatibility, risk, or a hard-to-reverse action.
3. Record only hard constraints that change implementation: compatibility, latency, throughput, cost, security, platform/framework, migration, rollout.
4. Map current ownership boundaries and source of truth.
5. Choose the smallest viable change before designing a larger target architecture.
6. Define interfaces/data flow before internal implementation detail when boundaries actually change.
7. Identify state, concurrency, failure, retry, and recovery behavior where relevant.
8. Plan coexistence for old/new schemas, APIs, workers, clients, or services when deployments can overlap.
9. Break work into independently verifiable slices with real dependencies.
10. Attach proof to each material slice.
11. Define rollback, disable, or forward-fix when production impact is meaningful.

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

Stop the affected path and update direction when:

- The developer corrects intent in a way that invalidates the current approach.
- Repository/test/runtime evidence contradicts a core assumption.
- A required public/data contract change was not anticipated.
- The intended slice cannot be verified independently.
- Repeated implementation friction reveals the chosen boundary is wrong.
- The change grows materially beyond accepted scope.

Distinguish a **correction** (the earlier interpretation was wrong) from a **new requirement** (scope genuinely changed). Do not preserve a stale plan for consistency or respond with agreement alone.

### Lightweight course-correction anchor

Only when a material correction/evidence change risks continued drift, write or update at most 1-3 lines:

```text
Current outcome: ...
Changed assumption: ...
Next valid slice: ...
```

Then act. Do not create a full specification, restate stable requirements, or run periodic reflection without new evidence. Preserve valid work and rework only what depended on the invalid assumption.

## Task graph and delegation

Express actual dependencies. Shared contracts, schemas, migrations, and primitives usually precede consumers. Parallelize only independent tasks. Read `subagents.md` when delegation reduces wall time or context pollution enough to justify coordination cost.

## Decision record

Persist only decisions that are non-obvious, costly to reverse, or likely to be revisited:

```text
Decision: ...
Reason: ...
Trigger to revisit: ...
```
