# Database Engineering

Use for schemas, SQL, persistence, migrations, transactions, locks, indexes, query tuning, and data consistency.

## Model invariants first

Identify:

- Entity identity/ownership.
- Required uniqueness and valid state.
- Nullability/ranges/relationships/deletion behavior.
- Read/write access patterns and expected cardinality/growth.
- Concurrency/consistency requirements.
- Retention, audit, tenant/security boundaries when relevant.
- Which layer is authoritative for tenant isolation/access control; if the database uses RLS/policies, treat policy behavior as part of the schema contract, test it, and ensure policy predicates have suitable access paths at expected scale.

Use durable DB constraints for invariants the database can enforce: PK/FK, uniqueness, checks, and appropriate not-null constraints.

## Query discipline

- Select only needed data when volume matters.
- Avoid N+1 round trips; batch when semantics allow.
- Bound scans/background jobs and paginate unbounded collections.
- Use deterministic ordering for pagination; prefer cursor/keyset patterns when offset becomes unstable/expensive at scale.
- Parameterize queries; never build SQL by concatenating untrusted values.
- Never rely on accidental row order.
- Compare plans and row estimates against representative production-like cardinality; a local tiny dataset can hide bad scans/joins.
- Inspect the actual query plan before guessing about meaningful performance issues.

Use `EXPLAIN ANALYZE` or production diagnostics carefully; do not execute an expensive/mutating plan in production merely to inspect it.

## Indexes

Add indexes for demonstrated access patterns. Consider filter/join columns, sort order, composite column order, selectivity, partial/covering opportunities supported by the DB, write amplification, lock/build cost, and storage.

More indexes are not automatically safer or faster.

## Transactions and concurrency

Choose the simplest mechanism that preserves the invariant:

1. Atomic statement/constraint.
2. Optimistic version/compare-and-set.
3. Row/advisory/pessimistic locking where appropriate.
4. Stronger isolation/serializable transaction when truly required.

Watch for lost update, write skew, check-then-write races, stale reads, duplicate retries, deadlocks, and lock contention. Keep transactions short; acquire locks in consistent order where possible. When concurrent writers expose versions/ETags/revisions, enforce the compare at the authoritative write rather than only in application memory.

## Connections

Respect the database's connection budget. Use the application's established pool/proxy strategy; do not solve load by blindly increasing max connections. Diagnose pool exhaustion, long transactions, idle connections, and slow queries as separate causes.

## Migrations

For live systems:

1. Prefer backward-compatible additive changes.
2. Account for old/new app versions coexisting.
3. Understand table rewrite/lock/index-build behavior for the actual database/version.
4. Backfill large data in bounded resumable batches with progress/restart semantics; do not assume one giant transaction is safe.
5. Introduce/validate constraints using database-safe techniques for the workload.
6. Switch reads/writes only after data and compatibility are ready.
7. Remove old paths/columns only after consumers are migrated.
8. Define rollback or forward-fix for risky changes.

A migration that is safe on an empty local DB may be dangerous on a hot production table.

## Data safety

Confirm scope and recovery expectations before destructive or wide updates. Prefer explicit predicates, previews/counts, transactions where appropriate, and backups/recovery mechanisms consistent with repository operations. Never put credentials or sensitive rows into logs/session notes/examples.
