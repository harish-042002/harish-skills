# Runtime Economics and Progress Watchdog

Use for broad/expensive work, research, repeated stalls, or any trajectory where wall time, model/API time, tool calls, rereads, or subagents may dominate cost.

## Objective

Preserve correctness while minimizing total work to a verified result:

```text
current truth -> smallest useful action -> focused proof
```

Do not optimize token price while creating repair turns. Do not reduce wall time by multiplying overlapping workers.

## Lead-first orientation

Before broad work establish goal, hard scope, current branch state, likely owner/reference flow, proof shape, and the comparison dimensions that actually matter. Do not dispatch a general-purpose scout to rediscover the repository for the lead.

## Output firewall

For commands likely to produce more than a few KB—tests, builds, analyzers, broad diffs, verbose searches—prefer `scripts/evidence_exec.py`. It stores complete stdout/stderr under `.plat/logs/` and returns only a bounded summary/excerpt.

Normal model-visible command output target: <=6 KB. Read exact log ranges only when they can change the current decision. Never paste a full log merely to be thorough.

## Context watchdog

Use the optional runtime only when context/output or continuity makes it useful; see `runtime.md`. Do not add separate polling turns to ordinary tasks.

Measured current utilization warns at 65% and permits context recovery at 80%. Without current utilization, bytes/read counts can warn about unnecessary work, but cannot prove a full context or trigger RED recovery. Cumulative cache-read traffic measures repeated billed work, not current occupancy. Keep these metrics separate.

YELLOW means narrow evidence returns. A measured RED can justify checkpoint plus confirmed context replacement, with at most one fresh-context worker per task when the host actually supports isolation. Call `context_guard.py reset` only after replacement succeeds so old counters and read masks cannot leak into the new context.

## Five-minute watchdog

Record task start time for non-trivial work. Around meaningful boundaries, check whether roughly five minutes have elapsed since the last checkpoint. Do not create a separate LLM turn just to read the clock; use deterministic local time/state when available.

Time alone is not a failure. A long build/test/download can be healthy only with a known operation and an explicit deadline; `--waiting` without `--waiting-until` is not proof of progress. Evaluate whether the interval produced meaningful progress.

Meaningful progress includes:

- a plausible path was eliminated;
- ownership or required delta became clearer;
- implementation advanced;
- a test/log/profiler result discriminated hypotheses;
- requested behavior was proven.

Suggested health thresholds are starting defaults to benchmark, not universal deadlines:

- `<5m without meaningful progress`: continue or tighten the next action.
- `>=5m`: YELLOW -> prohibit generic exploration; choose ACT / VERIFY / REROUTE.
- `>=10m`: RED -> bounded Brain review if available/budgeted; otherwise re-localize or surface the blocker.
- `>=20m` on an ordinary task with weak progress: stop generic exploration and surface the concrete blocker unless a named, testable corrective step is available. Do not repeatedly extend the budget.

Use `scripts/task_state.py` to make these thresholds deterministic where supported.

## Stop generic discovery

Once ownership, required delta, and direct proof are known, another search/read is forbidden unless a named unresolved question or new contradictory evidence justifies it.

A search must answer a concrete question. "Be thorough" is not a question.

## Evidence ledger

For long work keep compact accepted facts + pointers. Use `evidence_read.py` for large/repeated ranges: only fully delivered unchanged evidence in the same context epoch may collapse to a digest/pointer. Follow continuation offsets for truncated output; it is never fully consumed. Re-read only when the file changed or a new question requires exact content.

For same-shape peers/adapters:

1. reconstruct one golden/reference path once;
2. derive a fixed comparison matrix;
3. inspect peers only against that matrix;
4. investigate deltas/unknowns only.

## Worker economics

Normal work stays with the lead.

- DIRECT: no subagents.
- STANDARD: no subagents.
- ESCALATED: one bounded specialist initially.
- Research: orient first with zero specialists; normally one batched read-only scout after partitioning.

When host model selection exists, every delegated worker uses the lowest adequate current tier for its bounded job. Never hardcode provider/model names; map capability tiers to what the host currently offers.

## Brain economics

Brain review is not implementation. Build the input with `scripts/brain_packet.py`; use a 4 KB default packet budget. A complete binding contract is mandatory: the builder rejects oversized contracts rather than clipping requirements. Include only goal, hard constraints, slice, health, counters, evidence pointers, and one corrective question.

Routine Brain budget: maximum two reviews. Full chat history, raw logs, large diffs, and broad repo dumps are forbidden Brain input.

## Test economics

Use the verification ladder:

1. syntax/import/static checks that fail fast;
2. focused behavior test/check;
3. related suite if blast radius warrants;
4. full suite once when release/high-impact confidence warrants.

If a broad suite fails, baseline the failing tests first instead of rerunning the entire baseline suite.

## Research and AFK/report mode

For broad Research, spend output budget on the final artifact rather than repeated progress narration. Parallelize only genuinely independent partitions with cheap integration.

Track both:

- wall time experienced by the developer;
- aggregate model/API time consumed across workers.

A result is not "faster and cheaper" unless both economics improve or the quality gain clearly justifies the difference.

## Stop conditions

Stop expanding when another read, specialist, or test is unlikely to change implementation, proof, risk, or the requested report. Finish the task instead of optimizing the process indefinitely.
