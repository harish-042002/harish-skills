# Subagents and Delegation

Use when bounded independent work, broad exploration, isolated-context review, or parallel verification materially improves speed/context quality.

## Default

P-01 remains the lead. Do not delegate by reflex.

Subagents are separate execution contexts, not authorities. They should receive only the context needed for their bounded task and should report evidence back to P-01.

Keep with P-01:

- architecture and high-impact trade-offs;
- ambiguous scope;
- shared contracts/schemas/invariants;
- security/destructive decisions;
- cross-domain integration;
- conflict arbitration;
- final completion judgment.

Delegate only when expected value exceeds briefing + execution + integration cost.

## Good delegation cases

- 2+ truly independent investigations.
- Reading-heavy discovery that would pollute the lead's context.
- One bounded implementation with settled interfaces.
- Independent test/review work after implementation is stable.
- A fresh reviewer can challenge a subtle/high-risk artifact.
- A cheaper/faster worker can safely handle mechanical work without likely repair turns.

Poor fits:

- tiny single-step tasks;
- unsettled architecture;
- several workers touching the same shared state;
- tasks where one result determines the next;
- "use subagents" as a goal by itself.

## Worker roles

### Scout

Read-only. Locate ownership, relevant symbols/files, evidence, existing patterns, and unresolved risks.

### Domain specialist

Read-only by default. Answer one specific engineering question with evidence/confidence.

### Implementer

May mutate only settled bounded scope. Must not widen into shared contracts without returning the dependency to P-01.

### Reviewer

Fresh context where possible. Receive current diff/artifact + acceptance criteria + hard constraints. Report findings with direct evidence.

### Verifier

Runs focused proof against the requested behavior. Does not redesign the solution unless verification exposes a wrong model.

## One-level topology

Workers do not spawn other workers or invoke additional specialists on P-01's behalf.

If a worker needs another capability, return:

```text
Needs: <capability>
Why: <one sentence>
Evidence: <pointer>
```

P-01 decides whether to add that specialist.

This prevents recursive fan-out and keeps cost visible.

## Dispatch contract

A dispatch must be self-contained because the worker may not share the lead's conversation history.

Use the smallest useful brief:

```text
GOAL
Observable result.

QUESTION / TASK
One bounded problem.

EVIDENCE
Paths, test/log IDs, versions, accepted facts.

SCOPE
Read-only or allowed files/components.

CONSTRAINTS
Contracts/invariants/do-not-change areas.

VERIFY
Exact proof expected.

RETURN
Conclusion/changes + evidence + confidence + unknowns.
```

Reference files by path instead of copying whole plans, chat logs, or source files into the brief.

## Return contract

Read-only specialist:

```text
Conclusion:
Evidence:
Confidence: high | medium | low
Impact:
Recommendation:
Unknowns:
Needs:
```

Implementer:

```text
Changed:
Verified:
Unverified:
Risks:
Needs:
```

P-01 checks the evidence before accepting the result.

## Parallel execution

Parallelize only independent work.

1. Resolve shared contracts and ownership first.
2. Group work by independent problem domain.
3. Launch only unblocked tasks.
4. Avoid parallel mutations to the same fragile files/state.
5. Use isolation/worktrees/file ownership when the host supports them.
6. Reconcile each wave before launching dependent work.

Start with at most **3 concurrent specialists**. More is normally only justified for clearly partitioned Research.

Batch small same-shape independent edits into one worker instead of spawning one worker per file.

## Fresh context vs continuity

Use fresh context when independence is valuable: review, alternate hypothesis, isolated research.

Resume an existing worker when continuity is valuable: a bounded fix/re-review loop where the worker already understands the local scope.

Do not repeatedly brief fresh workers on the same question if the current worker can efficiently continue.

## Context and model economy

Everything copied into a worker brief and returned into the lead context has a cost.

Prefer:

- file paths and symbols over pasted files;
- concise evidence reports over narration;
- low-cost models for bounded reading/mechanical work when quality is adequate;
- stronger models for architecture, subtle debugging, integration, or high-risk review.

Optimize total turns and repair cost, not price per token. A cheap worker that requires several retries is not cheap.

## Failure and circuit breakers

- If one worker's hypothesis is falsified, retire it instead of stacking another patch.
- After 2 unsuccessful rounds on the same question, P-01 must re-localize/re-route before another dispatch.
- Do not keep adding reviewers after direct verification plus one risk-appropriate independent review are clean.
- If parallel workers produce conflicting advice, use `orchestration.md` evidence arbitration rather than majority vote.

## Acceptance

A worker saying "done" is not proof.

P-01 owns integration and final verification. The task is complete only when fresh evidence after the final relevant edit supports the developer's requested behavior.
