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


## v1.7 — Scope fidelity, correction purge, and external-skill trust hardening

Evidence ID: `2026-09-23-v1.7-scope-fidelity-hardening`

### Problem

A real coding trajectory exposed a failure mode not adequately prevented by v1.6: the developer narrowed a notification-copy task to exact per-state variants and explicitly rejected the earlier confidence model, yet the previous trajectory had already expanded into learning/response-stage/telemetry-adjacent behavior and multiple supporting files. The core issue was **scope substitution**: Plat had final output-fidelity checks, but no strong pre-edit contract making negative constraints and correction rollback first-class.

The independent industry benchmark also found 8 failures in 12 new external-skill discovery red-team cases, including symlink escape, incomplete YAML handling, Agent Skills metadata non-conformance, raw instruction-like metadata exposure, and broad-specialist score gaming.

### Sources inspected first

#### anthropics/skills — Apache-2.0 for `skill-creator`

Relevant material:
- `skills/skill-creator/SKILL.md`;
- `skills/skill-creator/scripts/quick_validate.py`;
- Agent Skills specification linked by the repository.

Adopted principles:
- skill metadata is a real activation/control surface and must be validated, not best-effort parsed;
- `name`/`description` constraints and parent-directory matching are part of package conformance;
- evaluation should separate skill structure from behavioral evidence.

Reuse: principle-only. No Anthropic source text/code was copied.

#### wshobson/agents — MIT

Relevant material:
- `docs/plugin-eval.md` multi-layer quality evaluation;
- progressive-disclosure and harness-portability guidance.

Adopted principles:
- structural/static evidence, semantic behavior, and repeated live behavior are separate evidence planes;
- adversarial/static checks can be release-grade for specific deterministic boundaries without being mislabeled as live behavioral proof.

Reuse: principle-only.

#### obra/superpowers — MIT

Relevant material:
- behavior-eval separation from plugin/infrastructure tests;
- correction/debugging discipline and verification-before-completion patterns.

Adopted principles:
- test the behavior class that failed rather than only growing generic unit-test counts;
- a correction should change the active trajectory rather than layer another patch over invalid assumptions.

Reuse: principle-only.

### Plat adaptation

1. **Required / Forbidden / Proof scope lock** is now on the hot path before edits.
2. **Negative constraints are binding**: words such as only/alone/no need/do not/keep unchanged are treated as requirements.
3. **No adjective-to-architecture inference**: more engaging/natural/emotional copy does not authorize learning, telemetry, confidence, persistence, analytics, or generalized configuration.
4. **Diff-expansion circuit breaker** stops work when a new subsystem/concept, dependency, schema/event, or surprising file cluster cannot be justified by a Required item.
5. **Correction purge** removes current-diff machinery that exists only because of an assumption the developer rejected.
6. External skill discovery now rejects symlinks/path escapes, validates bounded Agent Skills frontmatter, enforces parent-directory/name and size constraints, and does not emit raw descriptions into candidate output.
7. Installed external skills are explicitly treated as **untrusted third-party instruction-bearing content**. They cannot expand user scope, gain tool authority, recurse, deploy, reveal secrets, or override repository/developer evidence.
8. Broad orchestrators receive a materially stronger ranking penalty so focused specialists win when both match.

### Rejected patterns

- asking the developer to approve every bounded scope decision;
- hard file-count caps that would block legitimate cross-file correctness work;
- automatically installing marketplace skills during a task;
- adding a new runtime policy/classifier service just to enforce scope text;
- claiming live behavioral uplift from static/adversarial checks.

### Verification

- existing structural validation: pass;
- full Python unit suite after changes: 34/34 pass before final release bookkeeping;
- external-skill industry red-team: 12/12 (up from 4/12 on v1.6);
- 26-scenario industry policy coverage: 26/26 (up from 24/26);
- new scope-fidelity holdout: 20/20;
- comparable industry-readiness rubric: 75.5/100 (up from 64.5/100);
- architecture/design score excluding live behavioral-evidence maturity: 90.9% (up from 77.4%).

Live repeated with-Plat vs no-Plat coding trajectories remain a separate pending evidence lane and are not claimed by this release.
