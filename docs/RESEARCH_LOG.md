# Plat Research Log

## v1.3 — Fast routing, vague intent, and trajectory correction

### Problem

Plat's router had grown heavier, vague user messages could be mishandled as either guesses or unnecessary clarification questions, and corrections could be acknowledged without invalidating the downstream decisions built on the old assumption.

### Sources inspected

#### obra/superpowers — MIT

Relevant material:
- `systematic-debugging`
- `brainstorming`
- `verification-before-completion`

Useful principles:
- use request + available context to discover intent before asking;
- ask a focused question only when missing information materially blocks the outcome;
- find root cause before fixing;
- test one hypothesis minimally;
- if a fix fails, stop and form a new hypothesis instead of stacking another patch;
- verification must precede success claims.

Not adopted:
- mandatory design approval gates for normal bounded work. They conflict with Plat's low-ceremony/fast-path goal.

#### OthmanAdi/planning-with-files — MIT

Relevant material:
- durable task_plan/findings/progress state;
- context-loss recovery;
- published eval notes.

Useful principles:
- persistent state is valuable when long tasks must survive context loss;
- current workspace/diff should be consulted when resuming;
- state must answer where we are, goal, learned facts, and completed work.

Important counter-signal:
- the project's own eval notes show structured planning carries overhead on small tasks.

Plat adaptation:
- keep session state optional;
- never inject/rebuild it every turn;
- create/read it only when rediscovery cost is material.

#### wshobson/agents — MIT

Relevant material:
- context-management restore workflow;
- parallel-debugging.

Useful principles:
- incremental/lazy context restoration;
- explicit context/token budgets;
- dynamic expansion only when relevance justifies it;
- competing hypotheses are useful for genuinely ambiguous debugging;
- evidence strength/confidence should influence arbitration.

Plat adaptation:
- depth-specific context budgets;
- do not parallelize hypotheses by default;
- use competing hypotheses only when several plausible causes remain after cheap evidence.

#### Trail of Bits skills — CC BY-SA 4.0

Relevant material:
- differential-review README.

Useful principles:
- risk-first analysis;
- blast-radius estimation;
- use history to understand risky changes/regressions;
- adaptive depth.

License decision:
- concepts only; no copied/adapted text or code is included in Plat because Plat remains MIT.

Plat adaptation:
- blast-radius/history checks are conditional, not default;
- use them for structural/public/security/value-transfer/high-impact changes where they can change the decision.

### v1.3 behavior target

- vague messages inherit only evidence-supported active intent;
- one safe interpretation → act;
- multiple materially different interpretations → inspect cheaply, then ask one question if still unresolved;
- simple tasks stay on a zero/one-reference fast path;
- structural corrections invalidate dependent decisions and re-route;
- failed verification can invalidate the current model rather than trigger patch stacking;
- repository/history/blast-radius exploration stops once ownership, impact, and direct proof are clear.


### Daily update-check research

#### vercel-labs/skills — update/check implementation

Relevant material:
- `src/update.ts`
- update tests and CLI routing

Useful principles:
- update checks should be deterministic and non-interactive when automated;
- source/version state should be tracked outside agent reasoning;
- update failure should not corrupt or remove the current installed skill;
- current installation scope/path matters when deciding what is outdated.

Plat adaptation:
- background checker uses the GitHub Releases API once per day;
- installed Plat paths are registered in `~/.plat/installations.json`;
- results are cached in `~/.plat/update-status.json`;
- update-check failure is non-fatal and never affects engineering work;
- the checker **notifies only**; it does not silently replace a skill mid-session.

Market result:
- the major skills inspected did not provide a cross-platform once-daily background update scheduler, so Plat implements this with native user schedulers (LaunchAgent / systemd-or-cron / Windows Scheduled Task) rather than adding runtime agent instructions.


## v1.5 — External specialist federation and evidence arbitration

### Problem

Plat's built-in references intentionally stay smaller than entire dedicated skill ecosystems. For very complex tasks, copying every specialty into Plat would make the hot path heavier, duplicate upstream knowledge, and age badly. The target is to keep Plat as the lead router/orchestrator while reusing already-installed deep specialist skills only when they can change the outcome.

### Sources inspected

#### wshobson/agents — MIT

Relevant material:
- `docs/agent-skills.md`
- `parallel-debugging`

Useful principles:
- large skill ecosystems can stay token-efficient through progressive disclosure;
- specialist capabilities should be independently installable;
- ambiguous debugging benefits from competing hypotheses and evidence arbitration;
- evidence quality matters more than specialist count.

Plat adaptation:
- internal Plat references remain the first, cheap tier;
- installed external skills become an optional specialist bench;
- one specialist is consulted first; parallel work requires independent questions;
- P-01 integrates by evidence rather than majority vote.

#### vercel-labs/skills — MIT

Relevant material:
- installed skill listing/discovery;
- documented project/global skill locations;
- copy/symlink installation model.

Useful principles:
- installed skills are discoverable as filesystem packages;
- project-local and global scopes can coexist;
- metadata-first discovery avoids loading all skill bodies.

Plat adaptation:
- `scripts/discover_skills.py` scans supported project/global skill roots;
- project-local duplicate wins over global duplicate;
- only candidate metadata is read first;
- the full `SKILL.md` of one best candidate is loaded only after the selection gate.

#### Anthropic skills/tool-use documentation — public reference

Useful principle:
- tool/skill libraries scale better when the agent searches/discovers only relevant capabilities rather than loading every definition up front.

Plat adaptation:
- external specialist discovery is conditional and lazy;
- no universal slash-command behavior is assumed;
- native host activation is preferred when available, otherwise the installed `SKILL.md` is consulted directly.

No Anthropic code/text was copied into Plat.

#### obra/superpowers — MIT

Relevant principles retained:
- root-cause evidence before fixes;
- failed hypotheses are retired rather than patched over;
- specialist/process invocation should match the actual task.

### Orchestrator contract

The new orchestrator uses:

```text
active intent
  -> minimum sufficient depth
  -> internal specialist first
  -> external installed specialist only if a concrete unresolved capability remains
  -> bounded evidence packet
  -> evidence/confidence response
  -> P-01 arbitration
  -> direct verification
```

External skills are consultants, not authority. Current developer intent and repository/runtime evidence remain above all specialist advice.

### Cost controls

- Quick tasks: zero external skills.
- Ordinary Standard tasks: normally zero external skills.
- Deep/Research: discover externally only for a concrete unresolved specialty.
- Load one candidate first.
- A second specialist must be evidence-earned.
- Parallel specialists require independent work and critical-path benefit.
- Stop orchestration once another specialist is unlikely to change the decision.


## v1.6 — Lead orchestrator, specialist communication, and evidence arbitration

### Problem

The v1.5 federation layer could discover and consult specialist skills, but the orchestration contract was still too loose for Plat's most important job: deciding **who should work, what they are allowed to decide, how specialists communicate, when parallelism is worth the cost, and how conflicting recommendations are resolved without drifting away from the developer's actual request**.

The main risks were:

- uncontrolled specialist fan-out;
- duplicated repository discovery across agents;
- specialists implicitly owning architecture/integration decisions;
- majority-vote behavior when reports conflict;
- parallel mutation of shared state;
- repeated specialist rounds on the same unresolved question;
- invoking every installed skill simply because it is available;
- context and token growth erasing the speed benefit of specialization.

### Sources inspected first

#### OpenAI Agents SDK — MIT

Relevant material:
- `docs/multi_agent.md`
- manager-style agents-as-tools vs handoffs

Adopted principles:
- keep a lead/manager in control when multiple specialists contribute to one integrated answer;
- use handoff only when a specialist should actually own the rest of a separable interaction;
- deterministic/code-style routing is preferable where predictable speed/cost behavior matters;
- parallelism only helps independent work.

Plat adaptation:
- manager topology is now the default;
- true handoff is rare and explicitly gated;
- P-01 owns integration, arbitration, and final proof.

#### Anthropic managed multi-agent guidance — Apache 2.0 for the claude-api skill

Relevant material:
- coordinator roster design;
- context-isolated worker threads;
- self-contained task briefs;
- cheaper workers for reading-heavy bounded work;
- one-level delegation;
- poor fit for small single-step tasks.

Adopted principles:
- specialists receive only the paths, constraints, question, and report contract they need;
- the lead keeps architecture and final synthesis;
- one-level delegation prevents recursive fan-out;
- context-heavy reading can be moved to bounded workers when that actually saves lead context;
- small tasks stay single-agent.

Plat adaptation:
- explicit dispatch/result contracts;
- recursive specialists report `Needs: <capability>` back to P-01 instead of spawning another specialist;
- soft specialist caps and circuit breakers.

#### obra/superpowers — MIT

Relevant material:
- `subagent-driven-development`;
- `dispatching-parallel-agents`;
- fresh-context workers, scoped briefs, review loops, batching same-shape work, model/cost selection.

Adopted principles:
- isolate independent tasks;
- batch tiny same-shape work rather than over-dispatching;
- keep the controller responsible for integration;
- fresh review is valuable for high-risk work;
- cheapest model is not always cheapest overall when it causes more turns/rework.

Not adopted:
- mandatory per-task review/subagent ceremony for ordinary Plat work;
- permanent ledgers for every task.

Plat adaptation:
- review and worker use are evidence/risk gated;
- 2 failed rounds on the same question trigger re-routing instead of another automatic dispatch.

#### LangGraph Swarm — MIT

Relevant material:
- active-agent routing;
- explicit handoff tools carrying a task description;
- shared state vs isolated agent state.

Adopted principles:
- handoffs should carry an explicit bounded task, not assume shared understanding;
- shared conversation state can cause unnecessary context exposure;
- active specialist state should be explicit when handoffs are used.

Plat adaptation:
- specialists get self-contained minimal briefs;
- no assumption that subagents inherit the current conversation;
- P-01 remains the active integration owner by default.

#### Microsoft AutoGen swarm code — MIT for code

Relevant material:
- handoff target validation;
- explicit current-speaker state;
- termination/max-turn concepts.

Adopted principles:
- specialist transitions need explicit ownership and termination;
- orchestration requires circuit breakers rather than open-ended loops.

Plat adaptation:
- explicit specialist limits, same-question circuit breaker, parallel cap, and stop conditions.

#### Trail of Bits skills — CC BY-SA 4.0 documentation

Relevant concept:
- risk-first analysis and blast-radius awareness.

License decision:
- concepts only; no copied/adapted text or code is included in Plat.

Plat adaptation:
- history/blast-radius expansion remains conditional on actual risk and is not part of the normal orchestration path.

### v1.6 design decisions

1. **P-01 is always the engineering lead** for integrated software work.
2. **Manager topology first**; handoff is only for a truly separable specialist-owned interaction.
3. **One-level delegation only**; specialists cannot recursively federate skills/agents.
4. **External skill federation remains metadata-first** and specific specialists outrank broad orchestrators.
5. **Dispatch packets are bounded** to goal, unresolved question, evidence pointers, scope, constraints, proof, and return format.
6. **Specialist outputs are evidence packets**, not final decisions.
7. **No voting**; conflicts are reduced to a concrete proposition and resolved by the smallest discriminating check.
8. **Parallelism is read-only/independence-first**; shared mutations are sequential unless isolation is explicit.
9. **Soft budgets:** Quick 0, Standard normally 0, Deep starts at 1, Research up to 3 independent read-only specialists initially.
10. **Circuit breaker:** two unsuccessful rounds on the same question force re-localization/re-routing.
11. **Total economics** means tokens + tool calls + duplicate reads + repair turns + integration + wall time.

### Tests added

- deterministic orchestration policy script;
- 24 frozen orchestration cases covering caps, parallelism, external-skill selection, handoff gating, recursive-delegation prevention, and circuit breakers;
- skill discovery tests proving a specific specialist outranks a broad orchestrator;
- structural validation for manager ownership, arbitration, specialist contracts, and stop conditions.


## 2026-09-23 — Enforced maintenance evidence gate

Evidence ID: `2026-09-23-maintenance-evidence-gate`

### Problem

Plat already required maintainers to scan relevant public skills/projects, check licensing, adapt the useful principle, and test the result before material changes. That rule lived only in documentation, so a future change could silently skip the research/license/test record while still passing CI.

### Sources inspected first

#### NVIDIA/skills — Apache-2.0 source code; CC-BY-4.0 documentation/skills

Inspected repository validation/evaluation structure, per-skill `BENCHMARK.md` evidence/freshness language, and publication/readiness checks that separate deterministic validation from stronger behavioral claims.

Adopted principle: validation evidence should be explicit, refreshable, and machine-checkable when behavior changes. No NVIDIA skill text or code is copied into Plat.

#### jscraik/Agent-Skills — Apache-2.0

Inspected changed-surface validation, proof taxonomy separating structural proof from behavioral/outcome proof, and deterministic promotion/audit gates.

Adopted principle: CI should validate the evidence appropriate to the surface that changed. Rejected the larger SDK/command surface because it adds ceremony Plat does not need.

#### gohypergiant/agent-skills — Apache-2.0

Inspected skill audit workflows, eval co-maintenance, verification-report discipline, and change-history practices for behavior-bearing instructions.

Adopted principle: behavior-bearing skill updates should carry explicit verification evidence and keep evaluation assets aligned. Rejected per-skill changelog machinery for this single-skill repository.

### Plat adaptation

Added `scripts/maintenance_gate.py`, `docs/maintenance-evidence.json`, and deterministic tests. Material changes to `skills/plat/**`, repository validation scripts, installers, or Plat CI/release workflows now require the same change set to update both the machine-readable maintenance evidence record and this human research log.

The gate requires at least two inspected public sources, explicit license/reuse classification, coverage of every material changed file, and recorded tests. Unknown/no-license sources can only be recorded as principle-only inspiration.

The gate stays completely outside the normal Plat runtime, so ordinary engineering requests do **not** pay a market-research token/tool cost.

### Tests added

- 12 maintenance-gate unit tests;
- docs-only negative control;
- missing-evidence-file failure;
- fewer-than-two-sources failure;
- missing/invalid license-reuse failure;
- unknown-license copy rejection;
- uncovered material-file failure;
- missing-test-record failure;
- research-log cross-check failure;
- `.github` path-normalization regression test.

The first adversarial run exposed a real normalization bug where `.github/...` lost its leading dot; the implementation was corrected before repository integration. Final diff review then added a base-relative freshness check so touching the evidence files cannot reuse the previous evidence entry, plus mandatory attribution metadata for adapted/copied reuse.


## v1.7 — Scope fidelity, correction purge, and specialist trust

Evidence ID: \`2026-09-23-v1.7-scope-fidelity-trust\`

### Observed failure

A real coding trajectory exposed a class of failure that earlier routing tests did not capture strongly enough: a bounded notification-catalogue request was interpreted as permission to add confidence tiers, response stages, extra learning signals, trace fields, and broader selection behavior. The later correction narrowed the requirement to five variants per scenario/user state, explicitly removed medium/high confidence behavior, and said to work on those changes alone.

The problem was not lack of engineering depth. It was **scope fidelity**: Plat let a reasonable product idea outrank the developer's actual requested delta.

### Sources inspected first

#### anthropics/skills — Apache-2.0 for skill-creator

Inspected the current skill-creator validation/evaluation workflow and Agent Skills metadata validation patterns.

Adopted principles:
- parse SKILL frontmatter as YAML rather than a narrow hand parser;
- validate name/description bounds before treating a package as a skill;
- keep behavioral evaluation separate from structural validity.

No Anthropic code or prose was copied into Plat; the controls were reimplemented for Plat's dependency-light discovery broker.

#### wshobson/agents — MIT

Inspected PluginEval's layered quality model, especially triggering accuracy, scope calibration, robustness, progressive disclosure, and semantic evaluation.

Adopted principle:
- scope calibration is a first-class quality dimension; a technically good answer that expands the user's task is still a failure.

Rejected:
- adding a heavy always-on multi-layer evaluator to normal Plat runtime.

#### obra/superpowers — MIT

Inspected scenario-first skill behavior testing, verification-before-completion, and bounded subagent patterns.

Adopted principles:
- test behavior from realistic failure scenarios rather than only instruction presence;
- corrections must change the active trajectory, not merely add another patch layer.

Rejected:
- mandatory planning/subagent ceremony for ordinary bounded work.

#### vercel-labs/skills — MIT

Inspected installed skill locations and symlink-based installation behavior.

Adopted principle:
- skill discovery must allow legitimate package-directory symlinks while rejecting a \`SKILL.md\` file that resolves outside its declared skill root.

### Plat adaptation

1. The hot path now treats **only / alone / just / no / no need / do not / don't / keep / work on these** as hard scope constraints.
2. When scope can drift, the task is reduced to **MUST / MUST NOT / PRESERVE / PROOF** before mutation.
3. Unexpected cross-subsystem diff expansion triggers re-localization unless every extra surface is causally required.
4. A newer correction purges task-local code that existed only because of the rejected assumption.
5. External installed skills are explicitly untrusted instruction-bearing packages.
6. Discovery validates Agent Skills-compatible metadata, blocks \`SKILL.md\` symlink/path escape, suppresses raw untrusted descriptions, and penalizes broad keyword-stuffed orchestrators.

### Evaluation design

The v1.7 industry benchmark is intentionally separate from Plat's frozen routing/orchestration tests. The regression suite records the known failure so it cannot return; the industry benchmark uses a separate scope/trust scenario set plus the earlier external-skill red-team so Plat is not scored merely for matching its own tests.

Live repeated A/B coding-agent evidence is still required before claiming a universal behavioral advantage.


## v1.8 — AWS deep specialist and behavioral evaluation harness

Evidence ID: `2026-09-23-v1.8-aws-behavioral-evals`

### Problem

Plat had broad delivery/backend/database/security depth but no built-in AWS-specific deep layer. This meant AWS tasks either relied on generic cloud guidance or had to discover an installed external specialist. At the same time, v1.7's behavioral-evaluation score remained low because current-version realistic trajectories had no frozen executable harness.

### Sources inspected first

#### aws/agent-toolkit-for-aws — Apache-2.0

Inspected current AWS core skills for serverless, IAM, networking, observability, deployment, billing/cost, messaging, CDK, and DynamoDB.

Adopted principles:
- route by concrete AWS capability, not the word AWS alone;
- verify current service/version/quota facts when precision matters;
- make retries/event delivery/idempotency explicit for serverless/event systems;
- treat account/region/role context as part of operational correctness;
- progressive disclosure across AWS domains instead of one always-loaded knowledge dump.

Reuse: principle-only. No AWS toolkit text/code was copied.

#### aws-samples/sample-agent-skills-for-builders — Apache-2.0

Inspected `aws-cdk-development`, `aws-cost-operations`, `security-scan`, and `end-to-end-testing`.

Adopted principles:
- account identity checks before deployment-impacting operations;
- synth/plan/diff before infrastructure mutation;
- current official AWS documentation for version/region-sensitive decisions;
- evidence capture and explicit pre-reporting validation for E2E evaluation.

Reuse: principle-only.

#### aws-samples/sample-well-architected-skills-and-steering — MIT-0

Inspected the Well-Architected review and guardrail workflows.

Adopted principles:
- use the six Well-Architected pillars as lenses, not mandatory ceremony for every edit;
- absence of evidence is not evidence of absence;
- prefer preventive controls only when they map to an actual workload risk/enforcement point;
- distinguish quick/pillar-scoped/full review depth.

Reuse: principle-only.

#### kndoshn/aws-cdk-skill-plugin — MIT

Inspected CDK risk workflows and `EVALS.md`.

Adopted principles:
- resource replacement/data-loss/IAM widening are first-class IaC review risks;
- stateful resource identity changes require migration thinking;
- behavioral eval prompts should state observable expected outcomes.

Reuse: principle-only.

### Current AWS documentation checked

Current AWS Well-Architected, IAM best-practice, serverless lens, and Lambda idempotency documentation were checked while drafting the specialist. Plat records durable principles and deliberately avoids freezing fast-changing pricing/quota/feature values.

### Plat adaptation

1. Added `references/aws-deep.md` with an AWS-specific evidence hierarchy and deep controls for identity/targeting, IAM, networking, compute/serverless, events, data, IaC, observability, reliability/DR, quotas/performance, cost, security, incident diagnosis, and verification.
2. Added AWS to adaptive deep routing without making AWS a blanket escalation trigger.
3. Added AWS-specific routing regressions for Lambda/SQS duplicates, CDK stateful replacement, production account targeting, and a Quick CloudFormation typo negative control.
4. Added `benchmarks/behavioral-v1.8/` with frozen multi-turn/negative-control/AWS fixtures, executable verifiers, a generic runner, scoring utility, trigger corpus, and an explicit 18-point evidence-maturity rubric.
5. Behavioral evaluation maturity now earns 8/18 based on repository evidence infrastructure; no current live-result points are claimed.

### Harness validation

- `--plan` validates 5 frozen fixture cases;
- 20 frozen trigger cases include positive/negative activation and AWS-deep routing expectations;
- a non-committed fake adapter exercised the complete runner/verifier pipeline and all 5 fixtures passed after fixing pycache-generated false scope violations;
- fake/dry-run outcomes are explicitly excluded from live evidence.


## v1.9 — Research economics and subagent cost control

Evidence ID: `2026-09-23-v1.9-research-economics`

### Triggering real trajectory

A real DAY1 cross-branch adapter-mapping session showed strong reasoning quality but weak economics:

- $29.94 session cost;
- 49m53s aggregate API/model time shown by the host;
- 7m32s active time;
- 7.4M cache-read tokens;
- 187k cache-write tokens;
- 91% general-purpose subagent share.

The trajectory correctly used Hydration as the golden reference, validated merge failures against a clean baseline, and rejected stale documentation. The optimization target is therefore **not less rigor**. It is less duplicate discovery, cheaper bounded delegation, and narrower failure attribution.

### Sources inspected first

#### obra/superpowers — MIT

Inspected recent subagent-driven-development redesign material, especially task-scoped review, explicit worker-model selection, focused re-review, and avoiding repeated package-wide tests.

Adopted principles:
- every worker dispatch should name a model/tier when the host supports it, because omission can silently inherit an expensive lead model;
- bounded reviews should inspect the relevant diff/question rather than crawl the codebase;
- do not rerun broad tests when existing focused evidence already answers the question.

Reuse: principle-only. No Superpowers text/code copied.

#### aws-samples/sample-agent-skill-eval — MIT-0

Inspected functional with-skill/without-skill evaluation, token/cost measurement, timing capture, and Pareto-style cost-efficiency framing.

Adopted principles:
- cost efficiency must be measured alongside quality, not inferred from prompt size;
- compare matched conditions and publish negative/mixed deltas;
- capture token, wall-time, and per-run cost evidence.

Reuse: principle-only.

### Plat adaptation

1. Added `references/efficiency.md` for broad Research/Deep task economics.
2. Research now uses **lead-first orientation**: P-01 establishes the golden/reference flow, peer inventory, comparison dimensions, and report shape before dispatching broad scouts.
3. Golden-reference audits derive one comparison matrix and inspect peers against it instead of rediscovering each architecture independently.
4. Research starts with **0 specialists during orientation**, then normally 1 batched scout or 2 independent read-only scouts. A third requires explicit wall-time value.
5. Worker model/tier must be explicit when the host supports it; bounded reading/mechanical work should use the lowest adequate tier.
6. Evidence ledgers reduce rereads of unchanged large files.
7. Merge/integration verification narrows first; if a broad suite fails, baseline only the failing tests instead of rerunning the whole baseline suite.
8. AFK/report mode minimizes progress narration while preserving verification.
9. Wall time and aggregate model/API time are treated as separate metrics.
10. Added a v1.9 Research-economics baseline + controlled rerun protocol with explicit cost/cache/API/subagent targets that are not claimed achieved until live reruns exist.

### Rejected patterns

- hard token caps that can force under-investigation;
- always-cheapest worker selection regardless of repair risk;
- banning subagents from Research;
- skipping full-suite verification when blast radius genuinely warrants it;
- claiming cost savings before a matched v1.8/v1.9 rerun.



## v2.0 — Fast autonomous runtime kernel

Evidence ID: `2026-09-24-v2-runtime-kernel`

### Triggering failure

Real Plat sessions were producing good output but unacceptable execution economics: ordinary coding tasks could run for one to four hours, and the v1.9 DAY1 baseline already showed 49m53s aggregate model/API time with 91% general-purpose subagent share. The failure was architectural: efficiency guidance remained advisory while routing, verification, delegation, and specialist loading had many imperative paths.

### Sources inspected first

#### openai/codex — Apache-2.0

Inspected current Codex skill/agent patterns and the role of focused skills and bounded agent work.

Adopted principle: keep ordinary coding work with the lead; use specialization only for a concrete unresolved boundary. Reuse: principle-only.

#### openai/skills — Apache-2.0 for system skill-creator

Inspected the current skill-creator guidance on concise SKILL.md control planes, progressive disclosure, one-level references, and scripts for repeatable deterministic logic.

Adopted principle: the hot path should remain small while detailed knowledge is loaded only when needed; deterministic runtime bookkeeping belongs in scripts rather than repeated model reasoning. Reuse: principle-only.

### Plat v2 adaptation

1. Replaced the orchestration-centric hot path with DIRECT / STANDARD / ESCALATED execution.
2. DIRECT and STANDARD are hard single-agent paths: zero subagents and zero external skills by default.
3. Added a compact `.plat/session.json` Task Capsule for goal, hard scope, owner, current slice, proof, next action, time/health counters, and model capability tiers.
4. Added deterministic `task_state.py`: 5-minute cheap checkpoint cadence, YELLOW after 10 minutes without meaningful progress, RED after 20 minutes, BLOCKED for missing authority/access, and a two-review Brain budget.
5. Added interrupt-driven Brain review: course-correct only; no editing, broad discovery, large-suite verification, or recursive delegation.
6. Model policy is host-agnostic: normal worker = latest cost-effective capable coding tier; Brain = stronger cost-effective tier, normally one step above worker. No permanent model/provider names.
7. Third-party skill federation remains available but only after a concrete capability gap; one best match first.
8. References are knowledge cards, not child orchestrators; automatic reference-to-reference chains are prohibited.
9. Compaction/resume uses capsule -> branch/diff -> revalidate stale facts -> next, rather than replaying conversation/repository discovery.
10. Completion still requires fresh direct proof, preserving Plat's existing quality bar.

### Rejected patterns

- per-step Brain approval;
- prompt-length-only escalation;
- provider-specific model hardcoding;
- asking the developer at every alignment checkpoint;
- multi-agent fan-out for Standard work;
- removing third-party skill support entirely.

### Validation target

Plat v2 must preserve or improve correctness while materially reducing time-to-first-edit, tool calls, reference loads, duplicated reads, subagent share, aggregate model/API time, and wall time. Claims of actual percentage savings remain pending matched live A/B runs.


## v2.0.1 — Two-hour checks and multi-install synchronization

Evidence ID: `2026-09-24-v2.0.1-multi-install-updater`

### Problem

Plat could detect a new release, but the original daily checker tracked notification state only by release version. Updating Codex while leaving Claude Code or Cursor outdated could therefore suppress another useful notification for the same release. Re-running the installer also updated only the selected agent copy.

### Sources inspected

#### vercel-labs/skills — MIT

Inspected the current native `skills update` implementation and documentation: named-skill updates, global/project scope selection, source/lock tracking, and reinstallation behavior.

Adopted: use the upstream CLI's native scoped update path first, then verify each Plat registration. Reuse: principle-only.

#### jdx/mise — MIT

Inspected current self-update behavior: explicit interval throttling, non-fatal version checks, deliberate separation between checking and mutation, and safe fallback behavior.

Adopted: keep the scheduled check lightweight/non-fatal and notification-only; perform mutation only after an intentional installer or `--update-all` action. Reuse: principle-only.

### Plat adaptation

1. Background checks move from 24 hours to **2 hours** on LaunchAgent, systemd/cron, and Windows Scheduled Task.
2. Notification dedupe key is now **latest release + exact outdated installation set**, not only release version.
3. Registry schema records project roots so project-local installations can be updated from the correct working directory.
4. `--update-all` updates Plat by scope using `npx skills@latest update plat`, then verifies every registered `VERSION`.
5. Any installation still stale after the native update gets a targeted compatibility reinstall.
6. Re-running the installer for any registered agent registers that copy and then synchronizes all other registered Plat installations.
7. Background checks never silently mutate skill files mid-session.


## v2.0.2 — Full coding-agent catalog installation

Evidence ID: `2026-09-24-v2.0.2-all-agent-installer`

### Problem

Plat's engineering runtime was host-agnostic, but its installer still hardcoded Claude Code, Codex, and Cursor. That created a mismatch: users could run Plat conceptually in many coding agents, while installation verification, registry paths, and fallback updates rejected other valid hosts such as Antigravity, Cline, Kiro CLI, OpenCode, Qwen Code, Roo Code, Windsurf, and Zed.

### Sources inspected

#### vercel-labs/skills — MIT

Inspected the current `agents.ts`, `add.ts`, `list.ts`, and update behavior.

Relevant current capabilities:
- the Skills CLI owns a large and changing agent catalog;
- `--agent '*'` selects the full catalog;
- arbitrary specific agent IDs are validated by the upstream catalog;
- agent storage paths are defined upstream, including universal `.agents/skills` and host-specific directories;
- `skills list --json` returns installed skill path, scope, and the agents connected to that skill;
- scoped `skills update` already knows how to update the installed agent topology.

Plat adaptation: consume those interfaces instead of mirroring the catalog. Reuse: principle-only.

#### jdx/mise — MIT

Re-inspected current update/source ownership patterns.

Adopted principle: when an external package/source manager owns platform-specific installation knowledge, delegate to that manager and keep local state to the minimum needed for verification, scheduling, and compatibility fallback. Reuse: principle-only.

### Plat adaptation

1. Installer accepts `--agent all` or any current Skills CLI agent ID.
2. Interactive installer keeps quick choices for Claude Code/Codex/Cursor, plus **All supported agents** and **Another supported agent ID**.
3. `--agent all` maps to the upstream wildcard rather than a copied Plat list.
4. Installation verification no longer guesses a host-specific skill directory; it calls `skills list --json` and registers the returned Plat path/agent group.
5. Registry schema v3 stores the selector plus upstream display names for the installed group.
6. Update fallback accepts arbitrary upstream agent IDs and wildcard groups.
7. Native scoped `skills update plat` remains the first update path.
8. Existing extra persistent instruction wiring remains only for Claude Code, Codex, and Cursor. Other hosts use their native Skill discovery.
9. The two-hour notification-only update checker remains unchanged in principle.

### Non-goal

Plat does not promise identical host semantics. Installation support means Plat is placed in the host's Skills-compatible location by the current Skills CLI; invocation/model/subagent capabilities still depend on the individual coding agent.
