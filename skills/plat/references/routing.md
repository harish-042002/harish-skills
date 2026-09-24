# Routing, Alignment, and Course Correction

Use only when intent is vague/corrective, the execution path is uncertain, or the current trajectory may have drifted.

## Objective

Resolve the **smallest strongly supported next action** without turning routing into a second task.

## Active evidence order

1. latest explicit request/correction and acceptance criteria;
2. current task capsule goal/constraints/current slice;
3. latest tool/test/render/diff result;
4. current repo/runtime truth;
5. durable project cache/preferences.

Older plans never outrank newer corrections or current code.

## Alignment gate

Compare the latest request against:

```text
GOAL
MUST / MUST NOT / PRESERVE
CURRENT SLICE
PROOF
```

Choose one outcome:

- **Aligned** -> continue silently.
- **Clear correction** -> update capsule, purge task-local work that depended on the rejected assumption, continue.
- **Evidence reroute** -> choose another in-scope approach and continue.
- **Authority boundary** -> ask one focused question only if alternatives materially change product semantics, compatibility, cost, security, data, or an irreversible choice.

Do not ask merely because the wording is short. "do it", "continue", "same", "still wrong", and similar messages normally inherit the active task when one interpretation clearly dominates.

## Scope lock

Before mutation when drift is plausible, bind:

```text
MUST: requested behavior/artifact
MUST NOT: explicit exclusions
PRESERVE: accepted behavior not being replaced
PROOF: smallest direct evidence
```

Unexpected introduction of a new mode, stage, signal, schema field, dependency, persistence path, telemetry path, background process, or unrelated refactor is a **scope-drift signal** unless mechanically required.

## Execution path selection

### DIRECT
Use when ownership is obvious, scope is local/reversible, and proof is cheap.

### STANDARD
Default when normal repository inspection and one domain knowledge card are sufficient.

### ESCALATED
Use only when a named unresolved boundary materially changes risk or implementation: distributed state/concurrency, security/tenancy/money/data loss, public migration/compatibility, production-only failure, major architecture, measured performance/capacity, complex AI behavior, mobile lifecycle, or repeated failed hypotheses.

A large prompt, large repository, or request for detailed prose does not by itself earn ESCALATED.

## Diff-expansion circuit breaker

If a local request begins crossing extra subsystems, stop and ask internally:

> Is each added surface causally required for the requested outcome?

If not, remove it. If yes and still inside authority, continue. If it changes product semantics or a protected boundary, ask one focused question.

## Correction purge

A developer correction replaces rejected task-local assumptions; it is not additive. Remove/revert task-local machinery that only existed because of the rejected assumption unless an independent current contract still requires it.

## Failed trajectory

Do not stack patches indefinitely.

- one local failure -> inspect the narrow slice and repair;
- second failed hypothesis/reroute on the same question -> mark trajectory RED and use Brain review when available;
- Brain says current direction is wrong -> update capsule, preserve only independently valid work, resume from the smallest valid point.

## Inspection stop condition

Stop discovery immediately when all are true:

- requested outcome is clear;
- owning boundary is known;
- required delta is known;
- direct proof is known;
- another read is unlikely to change one of those.

Then act.
