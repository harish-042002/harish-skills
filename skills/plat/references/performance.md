# Performance and Scalability

Use for latency, throughput, memory, CPU, database load, bundle size, network waterfalls, cost, high-volume workloads, or explicit optimization requests.

## Measure the actual problem

Define:

- User/system symptom and target/SLO where one exists.
- Representative workload/data volume/concurrency.
- Baseline metric (for example p50/p95/p99 latency, throughput, saturation, memory, DB load, bundle size, or cost).
- Dominant resource or wait state.
- Acceptable trade-off.

Do not optimize from intuition when measurement is available.

## Work from largest cost downward

Common high-cost categories:

1. Remote/network waits and serial waterfalls.
2. Database round trips, scans, locks, sorts, connection contention.
3. Disk/object storage and serialization.
4. Cross-process/queue work and backlog.
5. Bundle/download/render work on clients.
6. CPU/memory algorithms.
7. Small local constant-factor/control-flow changes.

Optimize the dominant term first.

## Concurrency

Parallelize independent I/O only when downstream systems can handle it. Bound concurrency, queue depth, pools, batch sizes, and memory. "More parallel" can turn latency improvement into dependency collapse.

## Caching

Add cache only when a measured expensive/repeated read justifies the consistency and operational cost. Define key ownership, freshness/TTL, invalidation, stampede behavior, failure fallback, and memory/storage bounds.

## Backend/data

Investigate N+1 calls, repeated network/DB work, missing/poor indexes, unbounded scans, large payloads, unnecessary serialization, slow external dependencies, pool exhaustion, and lock contention before micro-optimizing application syntax.

## Frontend/mobile

Prioritize waterfalls, bundle/client code, duplicate requests, oversized assets, large lists, expensive rendering/rebuilds, synchronous UI-thread/isolate work, and memory/image pressure before small language-level optimizations.

## Algorithmic complexity

State time/space complexity when input size makes it material. Choose suitable data structures and algorithms; do not make code harder merely to shave irrelevant constants.

## Capacity cliffs

Check whether the improvement merely moves the failure threshold. Pools, queues, caches, concurrency, memory, rate limits, and downstream quotas can produce sharp saturation cliffs; measure near expected peak, not only at idle.

## Verification

Re-run the same representative workload after the change. Compare before/after and check for shifted cost or regressions (CPU vs memory, latency vs load, cache hit vs staleness). For production-critical performance, prefer percentile/tail behavior and saturation signals over averages alone.
