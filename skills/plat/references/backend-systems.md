# Deep Backend and Distributed Systems

Use for concurrency, distributed state, queues/events, idempotency, multi-step workflows, overload, leases, service boundaries, and backend reliability where the ordinary backend reference is insufficient.

## Contents

1. Objective
2. Ownership and invariants
3. Idempotency and retries
4. Messaging and event delivery
5. Transactions and workflows
6. Concurrency control
7. Caching and freshness
8. Backpressure and overload
9. Leases, locks, and leadership
10. Service decomposition
11. Failure isolation
12. Operability
13. Multi-tenancy
14. Edge cases

## Objective

Preserve durable invariants despite retries, concurrency, partial failure, version overlap, and load. Prefer the simplest mechanism that works at the authoritative boundary.

## Ownership and invariants

For each protected transition identify:

- authoritative owner;
- unique operation/entity identity;
- allowed state transitions;
- transaction boundary;
- external side effects;
- consumers that assume the result.

Do not split one invariant across several services unless coordination semantics are explicit.

## Idempotency and retries

Retries are normal in distributed systems. Design commands so a repeated attempt cannot silently create duplicate protected side effects.

Consider:

- stable idempotency key/operation ID;
- uniqueness constraint or durable operation record;
- in-flight duplicate semantics;
- completed duplicate response semantics;
- TTL/retention of dedupe state;
- safe replay after crash/timeouts.

Retry only failures that may succeed later. Bound count/time/concurrency and use backoff/jitter when appropriate. Never retry validation/auth/conflict errors by default.

## Messaging and event delivery

Assume duplicates and possible reordering unless the transport contract proves stronger guarantees.

Define:

- event/message identity;
- ordering scope/partition key;
- producer commit semantics;
- consumer idempotency;
- ack point;
- retry/DLQ policy;
- poison-message handling;
- replay behavior;
- schema evolution.

Do not claim exactly-once without an end-to-end state proof.

## Transactions and workflows

Prefer one local transaction when the invariant fits one data authority.

For cross-boundary workflows choose deliberately among:

- transactional outbox/inbox;
- durable workflow/orchestrator;
- saga with compensating actions;
- CDC/event propagation;
- periodic reconciliation;
- explicit manual recovery.

Compensation is a business action, not automatic rollback. State what cannot truly be undone.

## Concurrency control

Choose the narrowest mechanism that protects the invariant:

1. atomic DB operation/constraint;
2. compare-and-set/version check;
3. row/advisory lock;
4. transaction isolation/serializable;
5. distributed lease/lock only when ownership crosses the authoritative store/process.

Watch for check-then-write races, lost updates, write skew, duplicate workers, stale owners, and deadlocks.

## Caching and freshness

A cache is another consistency system.

Define:

- owner/source of truth;
- key and tenant scope;
- freshness/TTL;
- invalidation/update path;
- stampede prevention;
- stale fallback semantics;
- memory/storage bounds;
- behavior when cache is unavailable.

Do not use cache to hide a correctness issue or unbounded database query.

## Backpressure and overload

Bound growth:

- request concurrency;
- queue backlog;
- worker fan-out;
- DB/HTTP pools;
- batch size;
- per-tenant/global quotas;
- in-memory buffers;
- retry traffic.

When saturated, decide which work to reject, defer, degrade, or shed. An unbounded queue merely moves failure into memory/latency.

## Leases, locks, and leadership

For distributed ownership:

- define lease duration/renewal;
- handle pause/network partition/renewal failure;
- account for stale holders after expiry;
- use fencing/version tokens or authoritative compare at mutation when stale owners could still write;
- avoid assuming clocks are perfectly synchronized.

## Service decomposition

A service boundary should have a concrete reason such as:

- distinct business ownership;
- independent deployment/scaling;
- security/data boundary;
- fault isolation;
- technology/runtime requirement.

Large code size alone is not enough. Prefer a modular monolith when distribution would only add network/failure/versioning cost.

## Failure isolation

Use patterns only when evidence justifies them:

- timeout/deadline propagation;
- bulkhead/resource partitioning;
- circuit breaker for persistent dependency failure with meaningful open/half-open semantics;
- fallback only when degraded data/behavior is actually acceptable;
- rate limits/admission control;
- dead-letter/reconciliation workflows.

Each pattern adds state and operational behavior. Do not stack resilience patterns by reflex.

## Operability

Important workflows should expose enough safe telemetry to answer:

- operation/message/request ID;
- current state/attempt;
- dependency latency/status;
- queue age/depth;
- version/config/feature flag;
- reconciliation/replay status.

Use correlation across components. Avoid logging secrets or unnecessary payloads.

## Multi-tenancy

Treat tenant identity as untrusted input until authoritative authorization binds it.

Check:

- data partition/RLS predicates;
- cache keys;
- queue/event attributes;
- object storage paths;
- scheduled/background work;
- admin/support tools;
- rate/cost isolation.

One missing tenant boundary can invalidate all higher-level authorization.

## Edge cases

- **Timeout after commit:** caller may retry even though side effect succeeded; idempotency must handle this.
- **Old/new workers coexist:** event/schema behavior must be compatible during deployment overlap.
- **Retry storm:** a dependency recovery can be overwhelmed by synchronized retries; use bounds/backoff/jitter/admission control.
- **DLQ is not resolution:** define replay/repair ownership and safety.
- **Distributed lock acquired:** still verify protected state/version at the authoritative write when stale-holder risk exists.
