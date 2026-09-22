# Deep Performance and Capacity Engineering

Use for serious latency/throughput/memory/cost regressions, tail-latency issues, saturation, capacity planning, profiling, or optimization requiring representative experiments.

## Contents

1. Objective
2. Experimental method
3. Latency decomposition
4. Profiling
5. Queues, pools, and saturation
6. Database/network/storage
7. Frontend/mobile
8. AI workloads
9. Caching
10. Load and capacity tests
11. Regression gates
12. Tradeoffs
13. Edge cases

## Objective

Find and improve the dominant measured cost without shifting failure elsewhere. Performance is an experiment: comparable baseline, one causal change, comparable after measurement.

## Experimental method

Define:

- user/system symptom;
- target/SLO/budget;
- representative workload/data/concurrency;
- environment and warm/cold assumptions;
- baseline distribution and resource signals;
- hypothesis about dominant cost;
- measurement that can falsify it.

Change one dominant variable at a time when possible.

## Latency decomposition

Break end-to-end latency into waits/work:

```text
client/render
+ network
+ queue/pool wait
+ app CPU
+ DB/cache/storage
+ external dependencies
+ serialization
+ retry/fallback
```

Tail latency often comes from queueing/stragglers/retries, not average CPU time.

Measure p50/p95/p99 or the distribution appropriate to the product. Averages can hide saturation.

## Profiling

Use the stack's profiler/APM/native diagnostics before guessing.

Look for:

- CPU hot paths/flame graphs;
- allocation/memory growth;
- blocking I/O/event-loop stalls;
- lock contention;
- garbage collection;
- thread/task explosion;
- database query/wait time;
- browser main-thread/render/layout work;
- mobile frame/jank traces.

A profiler sample is evidence of time spent, not automatically a safe optimization target; check causality and workload representativeness.

## Queues, pools, and saturation

For a resource with arrival rate and limited service capacity, inspect:

- queue depth/age;
- pool wait time;
- utilization;
- service time;
- concurrency limit;
- timeout/retry amplification;
- downstream quotas.

Increasing pool/concurrency can lower wait temporarily while overwhelming the downstream system. Prefer bounded concurrency/admission/backpressure based on the bottleneck.

## Database/network/storage

Check high-impact causes first:

- N+1/round trips;
- scans/sorts/bad plans;
- locks/transactions;
- oversized payloads;
- chatty APIs;
- cross-region latency;
- object/disk IO;
- serialization/compression cost;
- connection reuse/pooling.

Use `database-deep.md` when DB semantics are the dominant issue.

## Frontend/mobile

Measure:

- request waterfalls;
- bundle/startup cost;
- render/rebuild work;
- large list/image memory;
- layout shifts;
- interaction latency;
- main-thread/UI-isolate blocking;
- network/data duplication.

Optimize real user-critical paths before low-level JS/Dart micro-optimizations.

## AI workloads

Decompose:

- retrieval/embedding/reranking;
- prompt/context size;
- model latency/token throughput;
- tool loops;
- retries/repair turns;
- fallback routing;
- cache hits/writes.

A cheaper/faster model can worsen total task cost if it causes more loops or lower solve rate. Compare end-to-end tasks, not one call.

## Caching

Measure repeated expensive work first.

Define:

- key/cardinality;
- hit rate;
- freshness/TTL;
- invalidation;
- stampede behavior;
- memory/storage cost;
- stale fallback;
- failure behavior.

A low hit-rate cache with complex invalidation may be a net loss.

## Load and capacity tests

A useful load test specifies:

- traffic shape/ramp;
- request/data mix;
- concurrency/arrival rate;
- duration/warmup;
- success/error criteria;
- percentile latency;
- resource saturation;
- downstream limits;
- test-environment limitations.

Find the capacity cliff and safe operating margin. Do not test production destructively without explicit authorization and safeguards.

## Regression gates

For critical paths, keep lightweight performance regression evidence in CI/benchmarks when stable enough to be meaningful. Avoid flaky hard thresholds on noisy shared runners; use representative controlled environments or trend/range checks.

## Tradeoffs

Performance changes can trade:

- CPU vs memory;
- latency vs throughput;
- consistency vs cache freshness;
- cost vs quality;
- startup vs steady state;
- tail latency vs resource utilization.

State the tradeoff and verify no higher-priority correctness/security property regressed.

## Edge cases

- **Benchmark faster, users not:** workload or bottleneck mismatch; re-measure end-to-end.
- **Mean improves, p99 worsens:** investigate queueing/stragglers/retry amplification.
- **More concurrency helps local test:** check downstream saturation at expected peak.
- **Cache makes DB quiet:** verify stale/invalidation behavior and memory/tenant key bounds.
- **Optimization changes result/order:** correctness wins; performance proof cannot excuse semantic regression.
