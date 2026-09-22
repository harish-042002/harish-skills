# Deep Debugging and Incident Analysis

Use for production-only/intermittent failures, distributed systems, several plausible root causes, repeated failed fixes, concurrency/timing/resource issues, or incidents spanning multiple components.

## Contents

1. Objective
2. Incident vs debugging mode
3. Failure localization
4. Competing hypotheses
5. Evidence quality
6. Boundary instrumentation
7. Concurrency and timing
8. Distributed failure patterns
9. Resource and degradation failures
10. Failed-fix discipline
11. Parallel investigation
12. Root-cause proof
13. Post-fix verification
14. Edge cases

## Objective

Turn uncertainty into discriminating evidence before changing behavior. The deep workflow exists to avoid expensive guess-and-patch loops.

## Incident vs debugging mode

During an active production incident, separate two goals:

- **Mitigate** user/system impact with the smallest reversible control.
- **Diagnose** root cause without destroying evidence.

A restart, feature disable, retry increase, queue purge, or traffic shift may be a mitigation. Do not call it the root fix unless evidence proves it removes the cause safely.

## Failure localization

First bound where the system becomes wrong.

Trace:

```text
input/event
-> boundary
-> transformation
-> state read/write
-> async/network boundary
-> downstream effect
-> observed symptom
```

At each boundary compare expected vs observed values/state/timing.

Useful discriminators:

- works vs fails;
- before vs after deployment/config change;
- tenant/user/data cohort;
- one region/worker/version vs another;
- low vs high load;
- first attempt vs retry;
- cold vs warm cache/process;
- serialized vs concurrent execution.

## Competing hypotheses

When several causes are plausible, create a small hypothesis table rather than committing to the first story.

Cover relevant failure classes:

1. Logic/algorithm.
2. Data/serialization/schema.
3. State/cache/concurrency.
4. Integration/version/config/network.
5. Resource/capacity/leak/saturation.
6. Environment/timezone/locale/permissions/runtime.
7. Deployment/coexistence/rollback mismatch.

For each serious hypothesis record:

```text
Hypothesis:
Why plausible:
Evidence expected if true:
Evidence that would falsify it:
Cheapest discriminating check:
```

Do not create ten speculative hypotheses when two evidence-backed ones dominate.

## Evidence quality

Prefer:

1. Direct reproducible observation.
2. Trace/log/state evidence tied to the same request/entity/time.
3. Controlled comparison/experiment.
4. Correlation with deployment/config/data cohort.
5. Anecdotal report.

Absence of a log is not proof an event did not happen unless the logging path itself is known reliable for that event.

## Boundary instrumentation

In multi-component systems, instrument the boundaries that distinguish hypotheses:

- request/event identity;
- input/output shape or safe hashes/metadata;
- config/version/feature-flag state;
- queue delivery attempt and message identity;
- transaction/version/revision values;
- external dependency latency/status;
- worker/process/region/build identity.

Add temporary diagnostics only where existing telemetry cannot answer the question. Avoid sensitive payloads and noisy permanent logging.

## Concurrency and timing

For races/intermittency, capture:

- operation identities;
- ordering and timestamps from a consistent clock source where possible;
- transaction/lock/version boundaries;
- retry attempts and idempotency keys;
- cache version/freshness;
- task/thread/worker ownership;
- cancellation/timeouts;
- lease expiry/renewal/fencing state.

Do not "fix" timing bugs with sleeps. Make the real synchronization/condition explicit.

## Distributed failure patterns

Investigate only those relevant to evidence:

- duplicate delivery or client retry;
- out-of-order events;
- partial success across durable systems;
- stale cache/read replica;
- timeout after side effect committed;
- poison message/retry storm;
- split-brain/stale lease holder;
- old/new version contract mismatch;
- clock/expiry assumptions;
- cascading dependency saturation;
- missing correlation across services.

Exactly-once claims require proof from the actual transport/state design; assume at-least-once/retry realities unless guaranteed.

## Resource and degradation failures

For memory/CPU/pool/backlog/file-descriptor/connection exhaustion:

- establish a time-series symptom and baseline;
- identify which resource climbs/saturates;
- correlate with workload/deployment;
- distinguish leak from legitimate load growth;
- inspect queue/pool wait time, not only utilization;
- reproduce with controlled load where safe;
- verify recovery and steady-state after the fix.

## Failed-fix discipline

- A failed hypothesis must be retired or revised explicitly; do not stack another patch on top.
- After two materially different failed fixes, rebuild the evidence map.
- After three evidence-backed attempts fail or each reveals new coupling, question the architecture/boundary before Fix #4.
- Developer correction is new evidence and may invalidate the current causal story.

## Parallel investigation

Use competing-hypothesis scouts only when investigations are independent and the issue is expensive enough to justify coordination.

Good split:

- Scout A: DB/concurrency evidence.
- Scout B: queue/retry/delivery evidence.
- Scout C: deployment/config/version evidence.

Bad split:

- three agents all reading the same stack trace and proposing fixes.

Each scout returns evidence and falsification status, not implementation patches. Main agent arbitrates root cause.

## Root-cause proof

Before fixing, be able to explain a causal chain:

```text
trigger/condition
-> first incorrect state/decision
-> propagation
-> observed symptom
```

The explanation should account for why the bug appears under the observed conditions and why nearby successful cases do not fail.

## Post-fix verification

1. Original reproduction/incident condition no longer fails.
2. Regression test or durable reproducer distinguishes old vs fixed behavior.
3. Relevant concurrency/retry/error path is covered.
4. Broader tests justified by blast radius pass.
5. Telemetry shows the failure signal stops under representative conditions when production evidence is required.
6. Temporary instrumentation/mitigation is removed or deliberately retained with reason.

## Edge cases

- **Cannot reproduce:** gather production evidence; do not fabricate a local cause.
- **External dependency root cause:** prove the boundary and implement only justified resilience/fallback; do not mask permanent errors with retries.
- **Multiple contributing causes:** identify primary trigger plus enabling conditions; one issue may legitimately have compound causality.
- **Heisenbug:** minimize intrusive instrumentation and use trace IDs/counters/sampling that preserve timing where possible.
- **Data corruption:** preserve forensic copy/audit trail before repair; separate repair procedure from prevention fix.
