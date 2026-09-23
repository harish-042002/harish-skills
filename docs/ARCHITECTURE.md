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

## Specialist federation

Plat uses a tiered capability model:

1. core router;
2. built-in Plat reference;
3. installed external skill when a concrete deeper specialty remains unresolved;
4. parallel/subagent specialists only when independent work justifies coordination;
5. external research/docs when installed knowledge is absent or version-sensitive.

The orchestrator discovers installed skills **metadata-first** rather than loading every skill body. It consults one best candidate first. Communication is bounded to the current goal, known evidence, unresolved question, constraints, expected output, and stop condition.

Specialists return domain findings with evidence/confidence. P-01 owns final integration. Conflicts are resolved by current runtime/repository evidence and the smallest discriminating check, not by vote or specialist popularity.

This keeps Plat extensible without turning the always-loaded core into a copy of every domain skill.

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