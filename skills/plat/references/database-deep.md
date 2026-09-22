# Deep Database Engineering

Use for high-scale queries, transaction anomalies, concurrency, zero/low-downtime migrations, replication/partitioning, multi-tenant isolation, data repair, or database reliability beyond ordinary schema/query work.

## Contents

1. Objective
2. Query-plan analysis
3. Index design
4. Transaction anomalies
5. Locking and deadlocks
6. Migrations and backfills
7. Replication and freshness
8. Partitioning/sharding
9. Connections and saturation
10. Multi-tenancy
11. Data repair and reconciliation
12. Observability
13. Edge cases

## Objective

Protect data invariants first, then optimize representative access patterns. Database changes are often operational changes; local success on empty data is weak evidence.

## Query-plan analysis

For a meaningful slow query:

1. capture exact query shape/parameters class;
2. representative row/cardinality distribution;
3. actual/estimated plan using the database's safe tooling;
4. rows scanned vs returned;
5. joins/sorts/temp/spill/IO;
6. lock/wait time;
7. network/serialization result size.

Fix the dominant cost. Do not add an index solely because a column appears in WHERE.

## Index design

Consider:

- predicate selectivity;
- join/filter/sort order;
- composite left-prefix/order;
- covering/include support;
- partial/filtered indexes;
- uniqueness as invariant;
- write amplification/storage;
- hot-page/contention;
- build/lock behavior on live tables.

Measure after change with the same workload/plan.

## Transaction anomalies

Know the actual DB isolation semantics.

Watch for:

- lost update;
- write skew;
- phantom/range races;
- check-then-insert duplicate;
- stale read/replica;
- non-repeatable read where logic assumes stability.

Prefer atomic statement/constraint/version compare before stronger locking/isolation when sufficient.

## Locking and deadlocks

Keep transactions short and lock only what protects the invariant.

For deadlocks/contention inspect:

- lock order;
- transaction duration;
- rows/ranges touched;
- missing index causing broad locks/scans;
- external calls inside transaction;
- retry behavior after deadlock/serialization failure.

Use consistent acquisition order where possible and retry only errors the DB documents as safe/retriable.

## Migrations and backfills

Use expand/contract for live systems:

1. additive compatible schema;
2. deploy code that tolerates old/new state;
3. backfill in bounded resumable/idempotent batches;
4. validate data/constraint;
5. switch reads/writes;
6. observe;
7. remove old column/path later.

Before applying, understand whether DDL rewrites table, blocks writers/readers, or builds indexes online/concurrently for the actual DB/version.

A giant one-shot backfill transaction is usually a risk: lock duration, WAL/log growth, replication lag, rollback size, and restart cost.

## Replication and freshness

If reads can use replicas/caches, define which operations require read-after-write or monotonic freshness.

Handle:

- replication lag;
- failover role change;
- stale routing;
- transaction visibility;
- replica unavailable/degraded behavior.

Do not diagnose a stale replica symptom as an application cache bug without tracing the actual read source.

## Partitioning/sharding

Use only when measured data/throughput/operational constraints justify it.

Choose partition/shard key from dominant access and ownership patterns. Account for:

- skew/hot partitions;
- cross-partition queries/transactions;
- uniqueness constraints;
- rebalancing/migration;
- tenant growth;
- operational tooling.

Partitioning does not automatically make queries faster if pruning cannot occur.

## Connections and saturation

A connection pool is a queue/resource budget.

Inspect:

- active vs idle;
- wait time;
- transaction duration;
- DB max connections;
- serverless/process multiplication;
- leaked/unreturned connections;
- long-running queries.

Blindly increasing pool size can make the database collapse faster.

## Multi-tenancy

Verify tenant isolation at the authoritative DB access path.

If using RLS/policies:

- test policy behavior;
- ensure application role/session context is correct;
- index policy predicates at expected scale;
- prevent bypass/admin connections from leaking into ordinary request paths.

For separate schemas/DBs/partitions, account for migrations, pooling, routing, and noisy-neighbor behavior.

## Data repair and reconciliation

Separate:

- immediate repair of existing bad data;
- root-cause prevention;
- validation/reconciliation job for missed cases.

Before destructive/wide repair:

- preview/count scope;
- preserve audit/backups as appropriate;
- make batches resumable;
- record idempotent progress;
- avoid logging sensitive rows;
- verify downstream/cache/search/event consistency.

## Observability

Use DB-native and existing platform evidence:

- slow query stats;
- query plans;
- locks/waits/deadlocks;
- connections/pool waits;
- replication lag;
- cache hit/IO;
- table/index growth;
- vacuum/maintenance health where relevant.

## Edge cases

- **Index improves SELECT but hurts writes:** compare total workload, not one query.
- **Migration passes staging:** production table size/write load may make lock/rewrite behavior different.
- **Serializable retry:** transaction body must be safe to retry without external side effects.
- **Replica read after write:** route critical freshness to authority or use a version/freshness strategy.
- **Unique constraint with soft delete:** define whether deleted rows still reserve identity and design index accordingly.
