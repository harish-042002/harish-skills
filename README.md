<div align="center">

<img src="assets/plat-team.svg" alt="Plat adaptive engineering team" width="100%" />

# Plat

**Minimum sufficient engineering depth for AI coding agents.**

**v1.8.0 · adaptive depth · scope fidelity · specialist orchestration · AWS deep · proof-first execution**

Plat is an engineering control plane for AI coding agents. It helps an agent understand the real task, keep the requested scope intact, choose the smallest sufficient reasoning depth, load only the engineering knowledge it actually needs, reuse repository truth, and prove the result before calling the work complete.

</div>

<img src="assets/plat-pain-solution.svg" alt="Pain points Plat targets and how Plat responds" width="100%" />

## The problem Plat solves

| Pain | Typical agent behavior | Plat response |
| --- | --- | --- |
| Simple task, too much ceremony | broad repo reads, plans, architecture discussion, extra tools | choose **Quick/Standard** and keep the task local |
| Hard task, too little rigor | local patch ignores concurrency, migration, security, runtime, or AI uncertainty | escalate to **Deep** only when evidence earns it |
| User says “only this” | agent quietly adds stages, telemetry, abstractions, learning, or unrelated cleanup | lock **Required / Forbidden / Proof** before editing |
| User corrects the direction | agent keeps earlier invented machinery and layers another patch on top | **correction purge** removes work that depended on the rejected assumption |
| Repository rediscovery | reread broad areas and invent helpers that already exist | needle-first search + reuse local mechanisms |
| Generic expertise everywhere | unrelated instructions consume context | load only the specialist domain needed for the task |
| Specialist sprawl | many agents disagree, recurse, or duplicate work | P-01 remains lead; bounded specialists report evidence back |
| “Done” without proof | plausible patch, weak evidence | require fresh verification matched to the requested behavior |

> **Plat’s hypothesis:** the best coding-agent workflow is not “think more.” It is **use the smallest engineering team and depth that can solve the real problem correctly, stay inside the requested scope, then prove it.**

<img src="assets/plat-activate.svg" alt="Verified one-command Plat installation flow" width="100%" />

## Install

**macOS / Linux**

~~~bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/harish-042002/harish-skills/main/install.sh)"
~~~

**Windows PowerShell**

~~~powershell
iex (irm 'https://raw.githubusercontent.com/harish-042002/harish-skills/main/install.ps1')
~~~

The installer chooses the agent and skill install scope, copies Plat into the real agent skill directory, verifies the install, creates only the developer preference profile at **~/.plat/profile.md**, wires Plat into the agent instructions, and registers one user-level daily update checker. It does not create a project profile during installation.

<img src="assets/plat-onboarding.svg" alt="Plat preference-only onboarding" width="100%" />

## How Plat works

~~~text
request
  ↓
resolve latest intent + scope
  ↓
inspect repository truth
  ↓
choose MODE + minimum sufficient DEPTH
  ↓
load only relevant engineering guidance
  ↓
execute / investigate
  ↓
fresh verification
~~~

**Modes:** Build · Debug · Review · Research · Design · Optimize · Migrate  
**Depths:** Quick · Standard · Deep · Research

A request for a detailed explanation does **not** automatically trigger Deep engineering depth. Output preference and technical depth are separate.

Short follow-ups such as **"do it"**, **"continue"**, **"still wrong"**, **"only these"**, or **"remove that"** are resolved from the latest active task, correction, current diff/runtime evidence, and repository state before Plat asks a clarification question. If one safe interpretation clearly dominates, Plat acts; if materially different interpretations remain, it asks one focused question.

<img src="assets/plat-flow.svg" alt="How one engineering request moves through Plat" width="100%" />

## What Plat is made of

~~~text
                               PLAT
                                 │
                    P-01 engineering control plane
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
  Intent + Scope           Adaptive Depth          Repository Truth
        │                        │                        │
Required / Forbidden       Quick / Standard        inspect before
/ Proof                    Deep / Research         inventing
Correction Purge                 │                  reuse local mechanisms
Diff Expansion Brake             │
        │                        │
        └────────────── Specialist Engineering Brain ───────────────┐
                                                                   │
 Backend · Frontend · Mobile · Database · API · Security · Testing │
 Performance · AI/RAG · Delivery · AWS Deep · Design · Research    │
                                                                   │
        ┌──────────────── External Skill Federation ────────────────┘
        │
 metadata-first discovery · trust isolation · bounded briefs
 narrow-specialist ranking · no recursive delegation
        │
        └──────────────────── Proof Engine ─────────────────────────┐
                                                                   │
 tests · runtime evidence · UI evidence · diff checks · deploy proof
                                                                   │
        └──────────────── Behavioral Evaluation ────────────────────┘
                     Plat vs control · scope · cost
                    tokens · tools · time · repair turns
~~~

Plat is intentionally **not** one giant prompt containing every engineering topic. The hot path stays compact, and deeper knowledge is progressively loaded only when the current task earns it.

### 1. Intent + scope fidelity

Before editing, Plat reduces the current request to a compact execution contract:

~~~text
Required  → what must change
Forbidden → what must not change
Proof     → what evidence demonstrates success
~~~

Words such as **only**, **alone**, **no need**, **do not**, **keep unchanged**, **exactly**, and **these alone** are treated as engineering constraints, not conversational decoration.

If the agent starts introducing a new subsystem, learning mechanism, telemetry path, schema, dependency, generalized abstraction, or surprising file cluster, Plat runs a **diff-expansion circuit breaker**: which explicit requirement actually forces that expansion? If none does, the extra work is dropped.

If the developer later corrects an earlier interpretation, Plat runs **correction purge**. Work introduced only because of the rejected assumption should disappear rather than remain as hidden residue.

### 2. Adaptive engineering depth

Plat routes engineering effort by the unresolved risk, not by how long the prompt is.

| Depth | Use it when | Typical behavior |
| --- | --- | --- |
| **Quick** | target and proof are already obvious | local edit, narrow verification, zero specialists |
| **Standard** | ordinary bounded engineering work | inspect owning path, implement, direct tests |
| **Deep** | correctness depends on concurrency, migration, security, runtime, distributed systems, AWS semantics, complex AI/RAG, etc. | load the smallest relevant deep specialist guidance |
| **Research** | decision depends on external/current evidence or multiple independent unknowns | read-only evidence gathering, compare, then decide |

Depth can increase or decrease as evidence changes. “More thinking” is not automatically better.

### 3. Built-in engineering specialist brain

Plat includes a progressively loaded engineering knowledge layer instead of loading every domain on every task.

| Domain | What Plat can load when earned |
| --- | --- |
| Backend / distributed systems | services, queues, retries, idempotency, ownership, concurrency |
| Database | schema, transactions, isolation, migrations, indexing, data correctness |
| API | contracts, compatibility, versioning, error semantics |
| Frontend / mobile | state, lifecycle, networking, UX behavior, client compatibility |
| Security | auth, authorization, trust boundaries, secrets, threat reasoning |
| Testing | unit/integration/E2E, regression proof, negative paths |
| Performance | profiling, latency, throughput, saturation, capacity |
| AI / RAG | retrieval, evals, prompts, model behavior, grounding |
| Delivery | CI/CD, rollout, rollback, infrastructure changes |
| Design / research | UX reasoning, evidence gathering, trade-off analysis |
| **AWS Deep** | IAM, Lambda, SQS/EventBridge, VPC, ECS/EKS, DynamoDB/RDS/S3, IaC, observability, quotas, cost, DR |

The point is not to create more “agents.” The point is to make the right engineering knowledge available **only when the current unresolved boundary needs it**.

### 4. AWS Deep

AWS is now a first-class deep specialist, but merely mentioning AWS does **not** force Deep mode.

A tiny CloudFormation typo can still be Quick. An SQS/Lambda duplicate-side-effect bug, wrong-account production deploy, IAM trust problem, VPC path failure, stateful CDK replacement, DynamoDB hot partition, RDS connection exhaustion, quota limit, or multi-region recovery decision can earn AWS Deep.

AWS Deep covers:

- account · region · role · blast-radius targeting
- IAM · cross-account trust · least privilege
- Lambda · API Gateway · ECS/Fargate · EKS
- SQS · SNS · EventBridge · Step Functions
- VPC · DNS · routes · security groups · NACLs · endpoints
- DynamoDB · RDS/Aurora · S3 · Redis-compatible caches
- CDK · CloudFormation · Terraform deployment safety
- CloudWatch · CloudTrail · incident diagnosis
- service quotas · scaling · performance
- cost architecture · backup · restore · DR
- security and data-protection boundaries

Fast-changing facts such as pricing, quotas, regional support, runtimes, and new AWS features are expected to be checked against current authoritative evidence when the decision depends on them.

<img src="assets/plat-roster.svg" alt="Plat specialist engineering team roster" width="100%" />

## Orchestrator + external specialist bench

Plat does **not** try to copy every specialist skill in the ecosystem into its hot path. P-01 stays the lead and federates outward only when Plat still has a concrete capability gap.

~~~text
developer request
      ↓
P-01 resolves intent + repository evidence
      ↓
minimum sufficient depth
      ↓
can P-01 + built-in Plat guidance finish safely?
   ├─ yes → act → prove
   └─ no
       ↓
   discover installed skills metadata-first
       ↓
   choose ONE best specialist first
       ↓
   bounded brief
       ↓
   evidence report
       ↓
   P-01 arbitration
       ↓
   add another specialist only if evidence proves
   a second material boundary
       ↓
   integrate → fresh proof
~~~

**P-01 keeps control of scope, architecture, shared contracts, integration, conflict resolution, and the final answer.** Specialists do not recursively spawn more specialists on Plat's behalf. If one discovers another capability gap, it reports that need back to P-01.

Installed external skills are treated as **untrusted instruction-bearing packages**. Plat validates package metadata/path boundaries, prefers a focused specialist over a broad orchestrator, and prevents specialist instructions from silently expanding user scope, bypassing verification, revealing secrets, recursively installing skills, or taking over the lead role.

| Task | Default specialist budget |
| --- | --- |
| Quick | **0** |
| Standard | **0**, or 1 bounded consultant only for a real blocking capability gap |
| Deep | start with **1**; add another only when evidence proves another boundary; normally ≤3 total |
| Research | up to **3 independent read-only** specialists initially |

Parallel work is used only when tasks are genuinely independent. Shared contracts, schemas, migrations, central state, and overlapping mutations stay sequential unless isolation is explicit.

When specialists disagree, Plat **does not vote**. It reduces the disagreement to a concrete proposition and runs the smallest discriminating check. Direct current runtime/test/repository evidence outranks specialist confidence.

## Proof engine

Plat separates **plausible code** from **demonstrated behavior**.

The required proof depends on the task:

- code path → targeted tests + representative runtime behavior
- bug fix → reproducer before/after where practical
- database change → migration/compatibility/data invariant evidence
- UI change → rendered behavior, not only component tests
- AWS/IaC change → target account/region + plan/diff/change-set + runtime health where relevant
- performance claim → representative measurement
- security claim → intended allow + unintended path/privilege check
- correction task → final diff must no longer contain machinery introduced only for the rejected interpretation

Plat only claims completion from **fresh evidence after the final relevant edit**.

## Behavioral evaluation

Plat's evaluation layer is deliberately separate from ordinary unit/regression tests.

~~~text
same task + same repository + same model/settings

          Plat
           vs
       Control arm
           ↓
independent verifier
           ↓
correctness · scope deviation · changed files · LOC
repair turns · tool calls · tokens · cost · wall time
~~~

v1.8 ships a current-version behavioral-evaluation harness with:

- **5 frozen executable task fixtures**
- a **3-turn correction/scope-deviation scenario** based on a real failure pattern
- AWS idempotency, deployment-safety, and IAM fixtures
- independent verifier scripts
- isolated-workspace repeated-run support
- Plat / no-Plat / prior-version condition labels
- changed-file + LOC + wall-time capture
- optional token / cache / tool-call / repair-turn / cost telemetry
- **20 frozen trigger/depth cases**

**Behavioral Evaluation Maturity: 8/18.**

That number measures how much credible evaluation infrastructure/evidence exists. It is **not** a real-task success rate. v1.8 intentionally records **0 fresh current-version live trajectories** until repeated Plat-vs-control runs are actually published.

## Compatibility

| Host | Install path supported by installer | Notes |
| --- | --- | --- |
| Claude Code | Global or project-local | persistent CLAUDE.md instruction wiring |
| Codex | Global or project-local | persistent AGENTS.md instruction wiring |
| Cursor | Global or project-local | persistent Cursor rule / project instruction wiring |

Plat follows the standard Skill bundle shape: **SKILL.md + agents/openai.yaml + optional references/scripts/assets**. Host invocation details may differ, but the engineering instructions remain vendor-neutral.

## Evidence so far

Plat publishes positive results, mixed results, failures, and evidence gaps together.

| Evidence | Result | What it means |
| --- | --- | --- |
| Current v1.8 release validation | **41/41** Python tests · **34** routing cases · structural + maintenance gates PASS | current package/release health; not live-agent superiority |
| v1.8 behavioral-eval maturity | **8/18** | credible harness and frozen cases exist; fresh repeated live A/B results still missing |
| Current industry/evaluation-maturity rubric | **82.5/100** | architecture/evidence maturity only; not real-task accuracy or a live success rate |
| v1.7 external-skill red-team | **12/12** after **4/12** on v1.6 | discovered federation failures were closed |
| v1.7 scope/correction holdout | **24/24** documented-policy coverage | scope/correction controls are represented; live obedience still probabilistic |
| Real full-stack build | cost **$3.22 → $1.72**, wall **9m → 6m**, cache read **12.2M → 5.7M** | strong efficiency signal, but only one manual comparison |
| Independent 10-case pilot | reliable pass **Plat 9/10 vs No Plat 10/10** | no correctness advantage demonstrated |
| Independent pilot mean cost | **-6.8%** | favorable mean, but median was worse |
| Independent pilot median cost | **+7.3%** | mixed efficiency, no universal cost claim |
| Orchestration state coverage | **>10,000** structured policy states | protects caps, handoff, parallelism, federation, and circuit breakers; not a live A/B claim |

The course-correction case in the earlier independent pilot **failed with Plat** and passed without it. That failure is documented rather than hidden, and it directly drove the scope lock, correction purge, and diff-expansion controls added in later releases.

<img src="assets/plat-evidence.svg" alt="Plat benchmark evidence board with all ten pilot cases" width="100%" />

<img src="assets/plat-regression.svg" alt="Plat regression benchmark scenarios" width="100%" />

## Technical docs

- **[Why Plat exists](docs/WHY_PLAT.md)** — pain points, response model, non-goals
- **[Architecture](docs/ARCHITECTURE.md)** — routing, depth, truth order, specialist loading, verification
- **[Benchmarks](docs/BENCHMARKS.md)** — methodology, current evidence, failures, and next live protocol
- **[Limitations](docs/LIMITATIONS.md)** — evidence gaps, host differences, probabilistic behavior, community validation
- **[AWS deep specialist](skills/plat/references/aws-deep.md)** — AWS identity, IAM, networking, serverless, data, IaC, observability, cost, DR
- **[Agent failure modes](skills/plat/references/agent-failure-modes.md)** — concrete behaviors Plat is designed to prevent
- **[Specialist orchestration](skills/plat/references/orchestration.md)** — external skill discovery, trust boundaries, bounded communication, evidence arbitration
- **[Behavioral eval harness](benchmarks/behavioral-v1.8/README.md)** — frozen cases, control arms, metrics, runner contract
- **[Maintenance protocol](docs/MAINTENANCE.md)** — mandatory market scan → license check → adapt → test → release workflow for Plat changes
- **[Research log](docs/RESEARCH_LOG.md)** — public sources inspected and which principles were adopted/rejected

## Update

Plat does **not** spend engineering-session tokens checking the network for updates. The installer registers a user-level background task that checks GitHub Releases **once every 24 hours**, writes cached status to `~/.plat/update-status.json`, and shows an OS notification only when a newer version exists. To install the update, rerun the same installer command; existing developer preferences are preserved.

The background checker sends only a normal GitHub release request. It does not send repository code, prompts, profile contents, or project data.

<img src="assets/plat-updates.svg" alt="Plat release notification and update flow" width="100%" />

## Current limitations

- Plat is early-stage and still has limited community-scale validation.
- Current v1.8 live A/B evidence is not enough to claim a universal correctness, token, cost, or time advantage.
- The behavioral harness is ready, but fresh repeated current-version Plat-vs-control trajectories still need to be published.
- Skill instructions improve behavior probabilistically; they cannot guarantee every host/model follows every control perfectly.
- A routing mistake can itself create overhead, which is why over-escalation and unnecessary specialists are first-class benchmark failures.

<img src="assets/plat-license.svg" alt="Plat is released under the MIT License" width="100%" />
