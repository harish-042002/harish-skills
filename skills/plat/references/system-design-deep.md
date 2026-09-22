# Deep System Design and Architecture

Use for major architecture choices, service boundaries, new subsystems, large migrations, high-scale/reliability requirements, or decisions costly to reverse.

## Contents

1. Objective
2. Start from forces, not patterns
3. Requirements and scale
4. Ownership and boundaries
5. Data and consistency
6. Communication and workflows
7. Failure model
8. Capacity and performance
9. Security and tenancy
10. Evolution and migration
11. Operability
12. Build/buy/reuse
13. Decision comparison
14. Lightweight artifacts
15. Edge cases

## Objective

Choose the simplest architecture that satisfies current requirements and credible near-term constraints. Deep design exists to surface hidden costs before implementation, not to produce architecture theater.

## Start from forces, not patterns

Do not begin with "microservices", "event-driven", "CQRS", "serverless", or another named pattern.

Begin with:

- user/system outcome;
- ownership/deployment constraints;
- data consistency/invariants;
- latency/throughput/concurrency;
- failure/recovery expectations;
- security/tenancy/compliance;
- compatibility/migration constraints;
- team/operational reality;
- cost limits.

Patterns are candidate tools after forces are understood.

## Requirements and scale

Separate:

- hard requirements;
- current measured scale;
- expected near-term scale;
- speculative future scale.

Quantify only what changes design: requests/sec, writes/sec, dataset/cardinality, payload size, concurrency, retention, availability target, latency target, regions, tenants, cost ceiling.

Avoid designing for hypothetical 1000x scale without a credible requirement.

## Ownership and boundaries

Identify:

- authoritative owner of each invariant/data domain;
- transaction/consistency boundary;
- deployment boundary;
- team/security boundary where relevant;
- public/internal contracts;
- lifecycle owner for background work.

A service split should pay for network, deployment, observability, versioning, and failure complexity through a concrete benefit such as independent ownership/deployability, fault isolation, scaling profile, or security boundary.

Prefer a modular monolith when distribution has no clear payoff.

## Data and consistency

For each important state transition define:

- source of truth;
- required consistency level;
- transaction scope;
- uniqueness/idempotency identity;
- conflict/concurrency semantics;
- read freshness expectations;
- retention/audit requirements.

Avoid dual writes without coordination. When one durable change must publish another fact, evaluate transactional outbox/inbox, durable workflow, CDC, reconciliation, or a single authoritative transaction depending on stack and requirements.

## Communication and workflows

Choose sync vs async from semantics:

### Synchronous

Good when caller needs immediate result and dependency latency/availability coupling is acceptable.

### Asynchronous

Good for decoupled processing, buffering, fan-out, workflows, or work that need not complete in request latency.

Async adds delivery/order/retry/idempotency/observability complexity. Do not use a queue to make architecture look scalable.

For multi-step workflows define ownership of state and recovery. Use sagas/compensation/durable workflow only when cross-boundary partial failure actually exists.

## Failure model

Design for specific failures:

- dependency timeout/unavailability;
- duplicate/reordered messages;
- partial write/side effect;
- worker/process crash;
- overload/backlog;
- stale cache/replica;
- deployment overlap;
- region/service degradation;
- bad configuration;
- operator/user retry.

For each material failure define detection, bounded behavior, recovery, and data integrity.

## Capacity and performance

Model the dominant path:

```text
arrival rate
-> concurrency
-> service time / waits
-> pools/queues
-> downstream limits
-> storage/network/CPU cost
```

Identify likely saturation points and backpressure strategy. Do not solve theoretical scale by adding components that increase baseline latency/operational cost.

## Security and tenancy

Define trust boundaries and which system authorizes protected operations. For multi-tenant systems, state how tenant isolation is enforced at each authoritative data/action boundary.

Keep secrets/privileged actions out of untrusted clients and model abuse/cost-amplification paths for expensive endpoints/AI/tools.

## Evolution and migration

A target architecture without a transition plan is incomplete for an existing system.

Use expand/contract thinking:

1. introduce additive compatible capability;
2. allow old/new versions to coexist;
3. migrate/backfill/replay in bounded resumable steps;
4. switch reads/writes/traffic with evidence;
5. monitor and retain rollback/forward-fix path;
6. remove obsolete path after consumers are migrated.

Test the overlap window, not only final state.

## Operability

For important paths define how operators answer:

- is it healthy?
- what is slow/failing?
- which request/job/tenant/entity?
- how deep is backlog?
- which version/config is active?
- can work be replayed safely?
- what is the rollback/disable mechanism?

Prefer existing logs/metrics/traces/platform capabilities before adding observability products.

## Build/buy/reuse

Evaluate in order:

1. existing repository capability;
2. platform/framework/database native feature;
3. existing approved dependency/service;
4. new dependency/managed service;
5. custom subsystem.

Consider operational ownership, lock-in, migration, security, latency, cost, and failure modes. "Managed" does not mean zero operational work.

## Decision comparison

For genuinely expensive alternatives, compare a small number of viable options using the forces that matter:

```text
Option
Correctness/invariants
Complexity
Failure modes
Migration
Performance/capacity
Security
Operational cost
Reversibility
```

Do not create weighted scoring theater when one hard constraint already eliminates an option.

## Lightweight artifacts

Normal feature work still does not need a formal spec.

For a major/high-risk design, preserve only artifacts that save rework:

- short context/problem statement;
- hard constraints/assumptions;
- chosen boundary/data flow;
- rejected alternative only when likely to recur;
- rollout/rollback;
- verification plan;
- trigger to revisit.

Use a full formal specification only when project/team/process explicitly requires it.

## Edge cases

- **User asks for microservices:** validate the actual reason; do not refuse the request, but surface distribution cost and choose sensible boundaries.
- **Greenfield with unknown scale:** build a simple boundary that can evolve; avoid premature distributed infrastructure.
- **Legacy system with weak tests:** add characterization/contract proof around seams before migration.
- **Hard vendor constraint:** optimize within it rather than repeatedly proposing a forbidden replacement.
- **Regulated/high-risk system:** evidence/documentation requirements may legitimately increase design artifacts and verification depth.
