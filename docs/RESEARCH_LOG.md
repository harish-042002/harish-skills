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
