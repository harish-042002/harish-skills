# Plat Benchmarks

Plat keeps positive results, mixed results, and failures in the same record. The current evidence is useful but not yet sufficient to claim a universal correctness or efficiency advantage.

## 1. Real full-stack build signal

Same broad task, fresh Claude Code Sonnet 5 sessions.

| Metric | No Plat | Plat | Difference |
| --- | ---: | ---: | ---: |
| Input tokens | 210 | 106 | -49.5% |
| Output tokens | ~1.7k | 464 | -72.7% |
| Cache read | 12.2M | 5.7M | -53.3% |
| Cache write | 97.9k | 74.9k | -23.5% |
| Cost | $3.22 | $1.72 | -46.6% |
| API time | 7 min | 5 min | -28.6% |
| Wall time | 9 min | 6 min | -33.3% |

Both implementations completed the direct CRUD flow. The no-Plat result had a slight initial micro-copy/visual-polish edge. This is a **single manual run**, so it is a signal, not a general claim.

## 2. Independent v0.6 pilot

10 cases × 2 conditions × 1 repetition = **20 real Claude Code Sonnet 5 trajectories**.

| Scenario | Plat | No Plat | Plat token delta | Plat cost delta | Plat time delta |
| --- | --- | --- | ---: | ---: | ---: |
| Bug root-cause | PASS | PASS | -180 | -$0.0325 | -2.7s |
| Existing-repo feature | PASS | PASS | -540 | -$0.0433 | -6.4s |
| Backend idempotency | PASS | PASS | +689 | +$0.0516 | +15.6s |
| Frontend states | PASS | PASS | -67 | -$0.0012 | -0.5s |
| Tiny edit | PASS | PASS | +8 | +$0.0001 | -1.5s |
| Performance reasoning | PASS | PASS | +11 | -$0.0122 | +2.3s |
| Verify-before-claim | PASS | PASS | +7 | +$0.0002 | -0.3s |
| Course correction | FAIL | PASS | -986 | -$0.0618 | -20.6s |
| Negative control | PASS | PASS | -25 | -$0.0003 | -0.5s |
| Lightweight feature | PASS | PASS | +88 | +$0.0019 | +2.5s |

Reliable deterministic assertions:

- No Plat: 10/10
- Plat: 9/10

Aggregate signals:

| Metric | Plat vs No Plat |
| --- | ---: |
| Mean tokens | -10.1% |
| Median tokens | +33.5% |
| Mean cost | -6.8% |
| Median cost | +7.3% |
| Mean time | -8.1% |
| Median time | +27.6% |

The mean/median disagreement was driven by outliers. The pilot did **not** demonstrate a correctness advantage.

### Course-correction failure

The repository required an existing shared cache abstraction. The Plat run added a process-local module cache, while the control found and reused the repository's SharedCache. That failure directly motivated stronger repository-truth and course-correction controls.

## 3. Structural release gate

The adaptive architecture has also been tested statically:

- 305/305 deterministic architecture/behavior checks;
- 38/38 semantic-control mutations killed;
- 65 adaptive edge-case scenarios.

Static gates prove routing/structure coverage only. They do not prove a live coding-agent advantage.

## Benchmark limitations

- The independent pilot used one repetition per arm.
- Tool-call telemetry was incomplete in the harness, so external verification is preferred.
- The manual full-stack run was not independently replicated.
- Current live evidence predates some later Plat routing/onboarding changes.
- Community-scale usage evidence does not exist yet.

## Next benchmark protocol

Future claims should use frozen comparable runs with:

1. same repository state;
2. same exact task;
3. same model/settings/permissions;
4. fresh session per arm;
5. repeated runs;
6. external verifier after each trajectory;
7. correctness as the primary endpoint;
8. tokens, cache, cost, wall time, turns, changed files, and repair work as secondary endpoints.

Priority cases:

- vague continuation with one evidence-supported referent ("do it", "continue", "remove that");
- vague request with multiple materially different targets where one focused clarification is required;
- tiny known-file edit;
- greenfield full-stack build;
- existing-repo feature;
- production/intermittent bug;
- large-codebase research;
- frontend redesign;
- RAG/agent regression;
- live-compatible API/database migration;
- public-facing artifact from a reference;
- mid-course user correction that invalidates the current framing.

## 4. v1.6 orchestration regression gate

The lead-orchestrator update adds deterministic regression coverage for orchestration policy. These are **policy/structure tests**, not proof that a live multi-agent run is better.

Current frozen checks include:

- 25 vague-intent/depth/trajectory routing cases;
- 24 orchestration-policy cases;
- external-skill discovery tests including project-over-global preference, unrelated-skill rejection, folded metadata parsing, and specific-specialist-over-broad-orchestrator selection;
- update-check tests proving notification deduplication and network failure isolation;
- structural assertions for P-01 lead ownership, one-level delegation, evidence arbitration, specialist caps, and circuit breakers.

The orchestration cases cover:

- Quick/Standard specialist suppression;
- Deep/Research specialist budgets;
- parallel read-only work vs sequential shared mutation;
- external-skill selection only after a capability gap;
- handoff gating;
- recursive-delegation prevention;
- same-question circuit breaking;
- manager topology as the default.

### What this does not prove

It does not yet prove that specialist federation improves correctness or lowers total cost on real coding tasks. The next live benchmark should compare **P-01 alone vs P-01 + evidence-earned specialist federation** on the same model/repository/task conditions.

Recommended live metrics:

- verifier pass/fail;
- total input/output/cache tokens;
- total tool calls and repeated repository reads;
- specialist/subagent count;
- duplicate work across specialists;
- repair turns;
- wall time and API/model time;
- changed files/LOC/dependencies;
- unsupported specialist findings rejected by P-01;
- final proof quality.

Priority orchestration tasks:

1. distributed retry/idempotency failure where DB depth is needed only after backend localization;
2. RAG retrieval regression with an installed retrieval specialist;
3. frontend feature with independent rendered QA and backend contract review;
4. high-risk security/performance review with independent read-only specialists;
5. negative control where many relevant skills are installed but the task is a trivial local edit.


## 5. v1.7 independent industry benchmark — scope fidelity and specialist trust

This benchmark is intentionally separate from Plat's own regression suite. The new 30 routing cases and 36 unit tests are release validation only; they do **not** earn industry-benchmark points.

Compared snapshots:

- v1.6.0 baseline: \`b57dc1a051a8dc067459b9c232f6ca0befdb2ece\`
- v1.7.0 candidate code: \`a5715a123875d3ae11c4c925ba07d1042ee22460\`

| Independent lane | v1.6 | v1.7 |
| --- | ---: | ---: |
| External specialist red-team (same 12 cases) | 4/12 | **12/12** |
| Scope-fidelity/correction policy suite | 8/24 | **24/24** |
| General industry scenario coverage (same 26 cases) | 24/26 | **26/26** |
| Static industry rubric | 64.5/100 | **75.5/100** |

The 100-point score remains conservative because **Behavioral Evaluation is still 1/18**: current v1.7 has not yet been measured in a repeated clean-context live coding-agent A/B benchmark.

The main v1.7 improvements are:

- hard scope constraints before mutation;
- correction purge for task-local machinery built from a rejected assumption;
- diff-expansion circuit breaking based on causal necessity;
- explicit untrusted-specialist boundary;
- Agent Skills-compatible external metadata validation;
- \`SKILL.md\` symlink/path confinement;
- resistance to broad keyword-stuffed specialist metadata;
- runtime license/provenance boundary for literal reuse.

See \`benchmarks/industry-v1.7/METHODOLOGY.md\`, \`REPORT.md\`, and \`RESULTS.json\` for the benchmark boundary and exact results.


## 6. v1.8 AWS deep specialist + behavioral evaluation maturity

v1.8 adds two independent capabilities:

1. a built-in `aws-deep.md` specialist for AWS-specific architecture/operations boundaries;
2. a current-version behavioral evaluation harness under `benchmarks/behavioral-v1.8/`.

### AWS deep specialist

The AWS reference is progressively loaded only when the unresolved question is specifically AWS. AWS appearing in a repository or prompt does **not** by itself force Deep routing. The specialist covers account/region/role targeting, IAM, VPC/network path reasoning, Lambda/API Gateway/ECS/EKS, SQS/SNS/EventBridge/Step Functions, DynamoDB/RDS/S3/cache boundaries, CDK/CloudFormation/Terraform safety, CloudWatch/CloudTrail operations, quotas/scaling, DR, security, and cost.

The source scan used current official AWS material and public skill implementations as principle-level inspiration only; no external skill code/prose was copied into Plat.

### Behavioral evaluation maturity

The behavioral-evaluation dimension is now explicitly scored from `benchmarks/behavioral-v1.8/RUBRIC.md`. v1.8 earns **8/18 maturity points**, up from the previous 1/18 evidence state, because the repository now contains:

- a frozen current-version realistic task pack;
- a three-turn scope/correction case based on the real notification misunderstanding class;
- AWS correctness/safety/security fixtures;
- independent executable verifiers;
- a host-neutral runner with isolated workspaces;
- Plat/no-Plat/prior-arm labeling and repetition support;
- changed-file/LOC/wall-time capture plus optional token/cost/tool telemetry;
- a frozen 20-case positive/negative trigger corpus.

This raises the **industry-readiness/evaluation-maturity rubric** from 75.5/100 to **82.5/100** if all other v1.7 dimensions are held constant.

This is **not** a claim that v1.8 succeeds on 82.5% of real tasks. The current-version live-result portion remains unearned: `STATUS.json` records **0 fresh v1.8 live trajectories** at release time. Fake-adapter/dry-run execution validates harness plumbing only and earns no live-result points.

### Frozen behavioral cases

The initial executable pack contains 5 fixture tasks:

1. multi-turn notification variants/correction with explicit no-dynamic/no-learning scope;
2. tiny timeout-only negative control;
3. SQS/Lambda duplicate-side-effect case requiring existing durable idempotency;
4. CloudFormation deploy account/region fail-closed guard;
5. IAM wildcard-to-prefix least-privilege correction.

The runner is designed for repeated real runs using external host wrappers. A result is a pass only when the independent verifier passes **and** there are no unexpected changed files or forbidden-pattern hits.

### Next evidence milestone

To earn the remaining behavioral points, run the frozen pack (and expand to >=8 cases) with the same model/settings in fresh workspaces:

- v1.8 Plat arm: >=3 repetitions per case;
- matching no-Plat or prior-Plat control arm;
- publish raw result JSON, task-level failures, tokens/tool calls/cost/wall time;
- replicate on a second coding-agent host/model.
