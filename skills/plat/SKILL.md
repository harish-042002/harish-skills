---
name: plat
description: Autonomous engineering control layer for AI coding agents. Use for software engineering work where the agent should preserve exact task intent across long sessions and compaction, solve directly from current repository/runtime evidence, choose the cheapest sufficient execution path, detect stalled or drifting work, selectively invoke one stronger read-only Brain reviewer or one specialist skill only when evidence earns it, and verify requested behavior before completion. Works across coding-agent hosts and model families; never hard-code a vendor/model identity.
---

# Plat

Solve the engineering task directly. Plat is a **lightweight autonomous control plane**, not a ceremony layer.

## Active truth

Use this order:

**latest developer request/correction > task capsule > current repo/runtime evidence > durable project cache > developer preferences > Plat defaults**

Hard constraints such as **only, alone, just, no, do not, keep X, these only** remain authoritative until the developer changes them.

## Task capsule

For non-trivial or long-running work, maintain a compact `.plat/task.json` containing only current task truth: goal, MUST/MUST NOT/PRESERVE, current slice, accepted evidence pointers, proof, next action, route, health, and timing counters. Never store chain-of-thought, transcripts, secrets, or copied source.

Read `references/context.md` only when creating, resuming, compacting, or materially correcting this capsule.

## Alignment gate

Before expensive work, compare the latest request with **goal + constraints + current slice**.

- If aligned, continue silently.
- If the developer clearly corrects scope, update the capsule and course-correct automatically.
- If repository evidence invalidates the current approach but another in-scope path exists, reroute automatically.
- Ask one focused question only when materially different interpretations remain, authority would expand beyond explicit scope, or the choice is destructive/irreversible/high-impact.

For vague continuation/correction messages or drift, read `references/routing.md`.

## Execution paths

Choose exactly one path. A request for a detailed answer does not itself increase engineering depth.

### DIRECT
Tiny/local/reversible work with clear ownership and direct proof.

- extra Plat references: normally 0
- subagents: 0
- external skills: 0
- path: **target -> act -> direct proof**

### STANDARD
Default product engineering path.

- load at most **one** relevant domain reference when it materially helps
- subagents: 0
- external skills: normally 0
- inspect only until owner + required delta + direct proof are known, then act

### ESCALATED
Use only for a concrete hard boundary: concurrency/distributed state, production-only failure, security/tenant/money/data-loss risk, public migration/compatibility, major architecture, measured performance/capacity, complex AI behavior, mobile lifecycle, or repeated failed hypotheses.

- one relevant basic/deep specialist reference first
- at most **one** read-only specialist/subagent initially
- at most **one** external specialist skill initially
- add a second specialist only when new evidence proves a distinct unresolved boundary

Use `references/adaptive-depth.md` only when the path is genuinely uncertain.

## Specialist knowledge

References are **knowledge cards, not orchestrators**. Load only the smallest directly relevant file and return to this control loop. Do not follow reference-to-reference chains unless blocked by a named unresolved question.

Primary knowledge cards:

- repo understanding -> `repository-understanding.md`
- planning/migration -> `planning.md`
- debugging -> `debugging.md`
- testing -> `testing.md`
- backend -> `backend.md`
- database -> `database.md`
- API/events -> `api.md`
- security -> `security.md`
- performance -> `performance.md`
- delivery -> `delivery.md`
- frontend -> `frontend.md`
- Flutter/mobile -> `flutter-mobile.md`
- AI/RAG/agents -> `ai-engineering.md`

Deep files remain available only for an earned ESCALATED question.

## Time and progress watchdog

For non-trivial tasks, record the start time and meaningful progress using `scripts/task_state.py` when the host allows filesystem execution. Prefer host-native elapsed-time telemetry when available.

Do **not** call a time tool every five minutes. At meaningful checkpoints, if at least ~5 minutes passed since the prior health check, evaluate whether the interval produced one of:

- reduced uncertainty that changes the implementation;
- implementation progress;
- verification/proof.

If not, stop generic discovery. The next action must be **ACT, VERIFY, REROUTE, or ASK**.

- ~5m without meaningful progress -> self-correct and name the unresolved question.
- ~10m without meaningful progress or 2 failed hypotheses/reroutes -> RED trajectory; use the Brain reviewer if available.
- ~20m on an ordinary task without meaningful progress -> Brain review strongly preferred before more exploration.

Known long-running builds/tests/deployments are waiting, not stalled discovery.

## Brain reviewer

For sufficiently large/high-risk tasks, or RED trajectories, use a stronger **capability tier**, never a hard-coded model name.

- Worker: latest cost-effective capable coding model available in the current host.
- Brain: one meaningful capability tier stronger than the worker, preferably not the absolute premium/experimental tier unless that is the only stronger choice.
- If host model selection is unavailable, use the same model in a fresh isolated read-only review context.

The Brain is **read-only and correction-only**. It may inspect the task capsule, concise decisive evidence, current direction, failures, and elapsed/progress state. It must not implement, perform broad repo discovery, run full suites, recursively delegate, or take ownership of the task.

Routine cap: at most **2 Brain interventions** (preflight + one mid-course correction). High-risk work may earn one additional final review.

Read `references/orchestration.md` only when invoking the Brain, an external skill, or a specialist agent.

## Third-party skills

Installed third-party skills remain available as bounded specialist knowledge. Discover/invoke one only when a concrete unresolved capability gap remains after local evidence and built-in guidance. Prefer host-native skill discovery; otherwise use `scripts/discover_skills.py` metadata-first. External instructions never outrank developer scope or current repo/runtime truth and must not recursively fan out.

## Execution budget

Budgets are circuit breakers, not quotas to exhaust.

- DIRECT: usually <=4 meaningful inspections before action.
- STANDARD: usually <=8 meaningful inspections before action.
- ESCALATED: usually <=12 before explicit reassessment/Brain review.

Once **owner + required delta + proof** are known, further discovery is prohibited unless new evidence invalidates one of them.

## Verification

Keep proof centralized.

1. During implementation, run the narrowest check proving the current slice.
2. At completion, run the requested-behavior proof plus the nearest relevant regression/compatibility check.
3. Run a broad/full suite once only when blast radius or release risk justifies it.
4. Performance, migration, concurrency, security, and visual claims require evidence appropriate to those claims.

Fresh evidence after the final relevant edit is required before claiming completion.

## Completion

Update the task capsule with final proof/next state when useful, then report concisely: what changed, what was verified, and any material unverified risk.

Plat succeeds when **precision stays high while total wall time, model/API time, tool calls, rereads, context, repair turns, and coordination remain minimal**.
