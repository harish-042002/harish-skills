# Behavioral Evaluation Maturity Rubric (18 points)

This dimension measures the **quality of behavioral evidence**, not instruction quality.

| Evidence | Points |
| --- | ---: |
| Historical real coding trajectory evidence exists and limitations are published | 1 |
| Frozen current-version realistic task pack, including negative controls | 1 |
| Multi-turn correction/scope-deviation cases | 1 |
| Independent executable verifiers for frozen fixtures | 1 |
| Host-neutral repeatable runner with isolated workspaces | 1 |
| Control-arm + repetition support | 1 |
| Diff/wall-time + optional token/cost/tool telemetry capture | 1 |
| Frozen trigger positive/negative corpus | 1 |
| Current-version live Plat arm: at least 3 reps on >= 8 cases | 3 |
| Matching no-Plat/prior-Plat control arm with same model/settings | 2 |
| Published task-level negative deltas/failures, not aggregate-only reporting | 1 |
| Independent verifier review of ambiguous semantic cases | 1 |
| Replication on a second supported coding-agent host/model | 2 |
| **Total** | **18** |

v1.8 can earn the infrastructure/frozen-case points only after the repository contains and validates those assets. It cannot earn the 9 live-result/replication points without actual fresh trajectories.
