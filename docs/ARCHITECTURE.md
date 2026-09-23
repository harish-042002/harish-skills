# Plat Architecture

## Control flow

Plat is a progressive-loading control layer:

    request
      ↓
    reconstruct active intent
      ↓
    inspect only evidence needed to localize ownership
      ↓
    choose MODE + minimum DEPTH
      ↓
    load basic process/domain guidance
      ↓
    add one deep specialist only if evidence earns it
      ↓
    execute / investigate
      ↓
    verify requested behavior
      ↓
    persist compact high-signal context when useful

## Precise routing for vague messages

Plat treats short referential messages as possible continuations of the active task rather than automatically new tasks.

Evidence order:

1. latest explicit request/correction;
2. latest unresolved task;
3. last tool/test/render/diff result;
4. current repository/runtime evidence;
5. fresh session state;
6. developer preference profile.

If one interpretation clearly dominates and the action is within the authorized/reversible task boundary, act. If two materially different interpretations remain after cheap inspection, ask one focused question.

Corrections are classified as **Local, Behavioral, or Structural**. Structural corrections invalidate downstream decisions that depended on the old assumption and re-run routing for the affected slice.

## Task modes

| Mode | Primary output |
| --- | --- |
| Build | changed product/code behavior |
| Debug | explained and corrected failure |
| Review | prioritized findings on existing work |
| Research | verified understanding/decision support |
| Design | user-facing interaction/visual/product-flow change |
| Optimize | measured performance/cost improvement |
| Migrate | safe transition between contracts/data/runtime states |

## Depth model

| Depth | Typical use | Context policy |
| --- | --- | --- |
| Quick | tiny, local, reversible, obvious ownership | almost no extra specialist context |
| Standard | normal engineering | usually one process + one domain reference |
| Deep | concurrency, production-only failure, public migration, security, major architecture, hard AI/perf | basic domain + one earned deep specialist first |
| Research | broad verified understanding | task-scoped map, expand only high-signal branches |

A user asking for a detailed explanation does **not** automatically trigger Deep engineering depth. Output preference and technical depth are separate.

## Specialist domains

Plat contains focused guidance for repository understanding, debugging, system design, backend/distributed systems, frontend, mobile, AI/RAG/agents, testing, databases, APIs/events/webhooks, security, performance, delivery/IaC, and UI/UX design.

Deep references are intentionally lazy-loaded. The full library is not a normal context path.

## Specialist federation and orchestration

Plat uses a lead-controlled capability model:

1. P-01 + built-in Plat reference;
2. installed external skill when one concrete deeper specialty remains unresolved;
3. fresh subagent specialist when isolated context/parallel investigation has clear value;
4. independent reviewer/verifier when risk justifies fresh judgment;
5. current external docs/research when installed knowledge is absent or version-sensitive.

### Manager topology by default

P-01 stays responsible for developer intent, architecture/integration, shared contracts, arbitration, final verification, and the user-facing answer.

```text
developer
   ↓
P-01
   ├─ specialist A ─┐
   ├─ specialist B ─┼─> evidence arbitration -> integration -> proof
   └─ external skill┘
```

A true handoff is used only when the host supports it and one specialist should own a genuinely separable interaction. Engineering work that crosses files, contracts, or domains remains manager-led.

### One-level delegation

Specialists never recursively assemble their own Plat team. If another capability is needed, the specialist reports `Needs: <capability>` to P-01, which re-runs the selection gate.

This keeps delegation depth, permissions, and context cost visible.

### Communication contract

Each specialist receives only:

- observable goal;
- exact unresolved question;
- decisive evidence pointers;
- read/write scope;
- constraints/do-not-change boundaries;
- expected proof;
- concise return schema.

Specialists return conclusion, evidence, confidence, impact, recommendation, unknowns, and any further capability need.

### Evidence arbitration

P-01 never chooses by majority vote.

Evidence order is approximately:

1. direct current runtime/test/data behavior;
2. current repository code/contracts/config for the actual version;
3. authoritative version-correct documentation;
4. current analogous implementation/history;
5. specialist reasoning supported by evidence;
6. generic best practice.

Conflicts are reduced to one concrete proposition and resolved with the smallest discriminating check. One direct failing test outweighs several unsupported specialist opinions.

### Budgets and circuit breakers

- Quick: 0 specialists.
- Standard: normally 0; at most one bounded consultant for a real capability gap.
- Deep: start with one; add a second only when evidence exposes a second material boundary; normally cap at three.
- Research: up to three independent read-only specialists initially.
- Shared mutations stay sequential unless explicit isolation exists.
- Two unsuccessful specialist rounds on the same unresolved question force re-localization/re-routing instead of another automatic dispatch.

The orchestrator discovers installed skills **metadata-first** and prefers a specific specialist over a broad orchestrator. This keeps Plat extensible without turning the hot path into a copy of every skill.

## Truth order

1. current developer request or correction;
2. current repository/runtime evidence;
3. optional project cache;
4. developer preference profile;
5. Plat defaults.

This prevents user preference or stale memory from silently fighting the project.

## Developer onboarding

Installation creates only ~/.plat/profile.md for interactive users. It stores role, experience, response preference, and optionally familiar technologies.

The profile changes explanation assumptions, not architecture and not engineering depth.

## Fast-path budget

- Quick: target + nearest proof; normally zero extra references.
- Standard: one primary reference first.
- Deep: one basic domain + one deep specialist first.
- Second deep specialist: only when evidence proves a second boundary is material.
- History/blame/blast-radius work: only for risky/public/security/value-transfer/regression cases where it can change the decision.

Discovery stops when outcome, ownership, approach, and direct proof are clear.

## Context economy

An extra file, tool call, subagent, or deep specialist should be loaded only when it is likely to:

- change a material decision;
- expose a plausible failure mode;
- prevent likely rereading or rework;
- provide stronger verification;
- reduce the critical path enough to justify its own coordination cost.

## Course correction

When new evidence invalidates the current direction, Plat stops the affected slice instead of merely agreeing and continuing.

    invalid assumption
      ↓
    stop affected work
      ↓
    re-check minimum evidence
      ↓
    preserve valid work
      ↓
    replace stale direction
      ↓
    verify corrected behavior

## Verification

Completion is a claim-to-evidence problem. The narrowest direct proof should run first, then wider checks according to risk.

Examples:

- unit/integration behavior → focused tests;
- frontend visual/layout claim → rendered browser/device review;
- performance claim → comparable measurement;
- migration claim → coexistence/backfill/rollback or forward-fix evidence;
- concurrency claim → controlled concurrent/retry proof;
- RAG/agent change → frozen evaluation cases plus cost/latency signals.