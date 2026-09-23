# AI Coding Agent Failure Modes Plat Targets

Use when auditing Plat behavior, diagnosing repeated agent inefficiency, or deciding whether a task should escalate or de-escalate.

## Contents

1. Purpose
2. Failure-mode matrix
3. Routing errors
4. Repository/context errors
5. Execution/verification errors
6. Cost/time errors
7. Design/public-artifact errors
8. Success criteria

## Purpose

Plat exists to reduce **total work required to reach a correct engineering result**. The main risk is not only a wrong answer; it is unnecessary context, broad repository reads, extra tools, stale assumptions, repair turns, and architecture that the task never needed.

## Failure-mode matrix

| Failure mode | Observable symptom | Plat control |
| --- | --- | --- |
| One-size-fits-all reasoning | Tiny edit receives architecture/research ceremony | Quick/Standard/Deep/Research depth routing |
| Underthinking risky work | Distributed/security/data task gets a local patch | Evidence-based Deep escalation |
| Broad repository reading | Agent scans many unrelated files/directories | Needle-first repository discovery |
| Reinventing local mechanisms | New cache/helper/service appears despite existing pattern | Repository discipline + analogous-pattern search |
| Stale trajectory | User correction is acknowledged but old assumptions continue | Course-correction stop/re-check/resume rule |
| Spec/plan overhead | Agent creates large plans for ordinary feature work | Thin-slice + ceremony budget |
| Tool churn | Many searches/commands do not change a decision | Context/time ROI gate |
| Repeated rediscovery | Same project facts are reread across sessions | Compact context caches when justified |
| Premature optimization | Complexity added before measurement | Correctness → measurement → optimization order |
| Weak verification | Agent says done after editing without fresh proof | Completion gate + claim-to-evidence mapping |
| Excessive delegation | Multiple subagents rediscover the same scope | Delegate only when benefit exceeds coordination cost |
| Specialist overload | Several deep references load just in case | One earned specialist first |
| Response bloat | Deep internal reasoning becomes a long user-facing answer | Output depth separated from engineering depth |
| Reference overfitting | Inspiration metaphor copied into wrong product context | Audience/purpose/reference-abstraction review |
| Profile overreach | Preferred stack/role overrides actual project | Repository truth outranks developer profile |
| Specialist fan-out | Every installed skill/agent gets invoked | Evidence-earned specialist gate + soft caps |
| Specialist voting | Lead follows majority opinion instead of current proof | Evidence hierarchy + smallest discriminating check |
| Parallel mutation collision | Multiple agents edit shared contracts/state concurrently | Read-only parallelism by default; shared mutations sequential |
| Recursive delegation | Specialist spawns more specialists and loses cost/ownership control | One-level delegation; capability needs return to P-01 |
| Report concatenation | Final answer mirrors conflicting specialist chatter instead of user request | P-01 re-integrates from latest request + accepted evidence |
| Scope substitution | Bounded request becomes a richer adjacent product/architecture change | Required/Forbidden/Proof scope lock + diff-expansion circuit breaker |
| Correction accumulation | Agent accepts a correction but leaves machinery created for the rejected assumption | Correction purge: remove dependent current-diff additions before continuing |

## Routing errors

### Over-escalation

A task is over-escalated when deeper context does not change a material decision, expose a plausible failure mode, or avoid likely rework.

Examples: a copy change triggers frontend-deep; a local deterministic bug triggers distributed debugging; or a request for a detailed answer triggers expensive Deep routing even though the implementation is simple.

Control: choose the **minimum sufficient engineering depth**. Output preference changes explanation, not technical routing.

### Under-escalation

A task is under-escalated when local reasoning ignores a material boundary such as concurrency, public compatibility, security, migration overlap, process death, distributed state, or probabilistic AI behavior.

Control: escalate only on evidence-backed risk triggers.

### Scope substitution and feature inflation

A task has drifted when the agent implements something plausibly useful but materially different from what the developer asked. Common signals:

- copy/catalogue changes grow into learning, telemetry, confidence or persistence systems;
- a named-file/local request spreads into selectors, schemas, services, docs, or generalized abstractions without a necessary dependency;
- words such as "only", "alone", "no need", or "keep X unchanged" are treated as suggestions instead of constraints;
- a correction is satisfied by layering new behavior on top of old agent-invented machinery rather than removing the invalidated machinery.

Control: lock Required/Forbidden/Proof before edits, use the diff-expansion circuit breaker during implementation, and run correction purge whenever the developer invalidates an assumption.

## Repository/context errors

Truth order:

1. current request/correction
2. current repository/runtime evidence
3. optional project cache
4. developer profile
5. Plat defaults

Do not turn cached context into authority. Search exact symbols/routes/events/contracts first. Expand outward only when ownership or behavior remains unresolved.

## Execution/verification errors

Common failure patterns:

- symptom patch without causal explanation;
- tests proving a nearby behavior rather than the requested one;
- relying on old test output after the final edit;
- visual claims without rendering;
- performance claims without comparable measurement;
- migration claims without coexistence/rollback evidence.

Control: prove the requested behavior with the narrowest direct fresh evidence, then widen checks according to risk.

## Cost/time errors

Track **total task economics**, not only prompt tokens: context loaded + repository reads + tool calls + model output + retries + repair turns + subagent coordination + wall time.

A smaller context is not cheaper if it creates more retries or wrong work. A deep route is not better merely because it is thorough.

## Design/public-artifact errors

For README/landing/docs/showcase work, a first-time reader lacks the current conversation history.

Controls:

- resolve audience and intended takeaway;
- extract principles from references instead of copying their product metaphor;
- separate stable capability from internal release/debug history;
- verify information hierarchy before polish;
- inspect the rendered artifact where tools allow.

## Success criteria

Plat is working when, relative to an otherwise comparable run:

1. correctness is preserved or improved;
2. simple tasks stay simple;
3. hard tasks receive the specialist depth their risk requires;
4. repository-local mechanisms are reused;
5. corrections actually change direction;
6. completion claims have fresh evidence;
7. total tokens, tool calls, rereads, repair turns, and wall time do not grow without a quality reason.

Do not claim these benefits globally from static instructions alone. Validate them with frozen A/B tasks and external verification.