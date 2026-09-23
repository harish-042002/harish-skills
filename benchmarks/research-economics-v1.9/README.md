# Plat v1.9 Research Economics Benchmark

This benchmark tracks the failure class that surfaced in a real DAY1 cross-branch adapter-mapping session: the reasoning quality was strong, but a broad Research trajectory used an expensive general-purpose subagent heavily, accumulated large cache reads, and duplicated broad-suite work.

## Observed baseline

One real pre-v1.9 session reported:

- session cost: **$29.94**
- API/model time shown by host: **49m 53s**
- active time shown by host: **7m 32s**
- cache read: **7.4M**
- cache write: **187k**
- general-purpose subagent share: **91%**
- output tokens shown: **544**

These figures are a single host/session observation, not a controlled benchmark and not directly comparable to future runs unless model, repository state, task, permissions, and host telemetry are matched.

## What was good

The trajectory correctly:

- identified Hydration as the golden/reference flow;
- merged the required branches and resolved conflicts;
- ran verification;
- compared failures against a clean baseline instead of blaming the merge;
- detected stale documentation and moved to a more authoritative repository source.

v1.9 does **not** remove those behaviors.

## What v1.9 targets

The optimization is specifically:

1. lead-first Research orientation before general-purpose delegation;
2. derive the golden-flow comparison matrix once;
3. batch peer/adapter inspection against that matrix;
4. explicit cheaper worker model/tier where host supports it;
5. default Research parallel cap of 2 after orientation, with a third worker only for explicit wall-time benefit;
6. evidence ledger to prevent rereading unchanged large files;
7. focused-current tests first;
8. if a broad suite fails, baseline the **failing tests**, not the entire baseline suite;
9. AFK/report mode minimizes progress narration;
10. measure wall time and aggregate model/API time separately.

## Controlled rerun protocol

Use the same:

- repository commit/branch tips;
- merge inputs and conflict resolutions;
- exact user prompt;
- model/settings/permissions;
- host/version.

Run at least 3 repetitions per arm:

- v1.8 control;
- v1.9 candidate.

Primary endpoint:

- report correctness/completeness verified against a frozen adapter matrix.

Secondary endpoints:

- total cost;
- input/output/cache tokens;
- wall time;
- aggregate API/model time;
- tool calls;
- file reads and duplicate reads;
- subagent count;
- subagent share of tokens/cost;
- broad-suite runs;
- baseline-suite runs;
- repair turns.

## Candidate efficiency targets

These are **targets, not achieved claims**:

- preserve report correctness;
- reduce total cost by **>=30%**;
- reduce cache-read volume by **>=30%**;
- reduce aggregate API/model time by **>=30%**;
- keep broad full-suite runs to **<=1** unless new mutations justify another;
- baseline only failing tests after a broad-suite failure;
- keep subagent share **<50%** for a single-golden-reference mapping task unless the work is explicitly partitioned into independent domains;
- do not increase wall time by more than 10%; preferably reduce it.

No target is counted as passed until repeated live trajectories are published.
