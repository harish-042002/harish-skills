# Backend Engineering

Use for services, APIs, workers, queues, jobs, business logic, server-side integrations, and distributed state.

## Authority

Keep durable protected invariants on authoritative backend/data boundaries. Clients may validate for UX, but server-side enforcement owns permissions, money, inventory, quotas, entitlements, and persisted state transitions.

## Command path

For state-changing operations, consider only the relevant steps:

```text
input contract
-> authentication
-> authorization
-> validation
-> business invariant
-> transaction/state transition
-> external side effect
-> durable result/event
-> response
```

Do not force every request through decorative layers; preserve the repository's established architecture.

## Failure model

For each remote/database/queue boundary ask:

- What can time out, disconnect, duplicate, reorder, be cancelled, or partially succeed?
- Are connect/read/overall deadlines bounded and propagated through downstream work where the stack supports cancellation?
- Is retry safe? What makes it idempotent?
- What bounds retry count/time and concurrency?
- What happens when the dependency stays unhealthy?
- Can backlog/pool/thread/task growth exhaust the service?

Use bounded retries for transient failures only, normally with backoff/jitter supported by the stack. Never turn permanent validation/auth/conflict errors into retry storms. Add a circuit breaker only when repeated dependency failure and recovery semantics justify another state machine; do not add one by reflex.

## Idempotency and delivery

For repeatable commands or at-least-once delivery:

- Define a stable operation/event identity.
- Make duplicate handling explicit.
- Prefer a durable uniqueness/operation record when duplicates can create money, inventory, notification, or job side effects.
- Acknowledge queue/event work only after the intended durable state is safe according to the broker's semantics.
- Define poison-message/dead-letter/replay handling for messages that cannot succeed after bounded retries.
- Design replay/recovery behavior before assuming "exactly once".

## Transactions and side effects

- Put related durable changes inside the narrowest valid transaction.
- Avoid slow remote calls while holding database locks/transactions unless the invariant truly requires it.
- Avoid uncoordinated dual writes to independent durable systems.
- When state change must publish a fact, prefer outbox/inbox, durable workflow, or explicit reconciliation according to project constraints.
- Define what happens after partial external success: retry, compensate, reconcile, or surface for operations.

## Service boundaries

Do not split services because a module is large. Distribution is justified by ownership, deployment independence, security/data boundary, scaling profile, fault isolation, or operational constraints strong enough to pay for network/failure complexity.

A well-bounded monolith is often simpler and more reliable.

## Resource safety

Bound work that can grow with traffic/data:

- Queue depth and consumer concurrency.
- DB/HTTP connection pools.
- Batch/page size.
- In-memory buffering/caches.
- Background task creation and fan-out.
- Per-tenant/user/global concurrency where one workload can starve others.
- Request/body/file size and expensive operations where abuse or accidents are possible.
- Under saturation, prefer bounded admission/backpressure/load shedding over unbounded queue or task growth; define which work may be rejected/deferred.

## Lifecycle

For long-running services/workers consider startup dependency readiness, graceful shutdown, cancellation, leases/heartbeats, in-flight work, poison messages, and restart/replay behavior.

For correctness-critical leases/leadership, account for expiry, renewal failure, clock assumptions, and stale owners. Use fencing/version tokens or an equivalent authoritative check when an expired holder could still mutate protected state.

## Operability

Important paths should make it possible to answer with safe identifiers:

- What request/job/entity failed?
- Where and why did it fail?
- Is it retrying/recovering?
- How often, for how long, and since which deployment/config change?

Use the existing stack's structured logs, metrics, traces, and error monitoring. Avoid secrets and unnecessarily sensitive payloads.

## Compatibility

Treat APIs, stored data, queue messages, events, and integration payloads as contracts. Plan coexistence when old/new producers, consumers, app versions, or workers may run simultaneously.
