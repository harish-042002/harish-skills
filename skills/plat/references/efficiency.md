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

Use `scripts/host_context.py` + `scripts/context_guard.py` for non-trivial/output-heavy work. The common guard always works from proxy signals; real host telemetry overlays it when available.

Proxy starting thresholds:
- YELLOW: >=64 KB returned evidence, >=3 large outputs, >=2 repeated reads, >=12 file reads, or >1 broad-suite run.
- RED: >=128 KB returned evidence, >=6 large outputs, >=4 repeated reads, or >=24 file reads.

Real-telemetry starting thresholds:
- YELLOW: context utilization >=65% or task-local cache-read delta >=8M.
- RED: context utilization >=80% or task-local cache-read delta >=20M.

The first real telemetry sample becomes the task baseline; Plat acts on deltas rather than lifetime/session totals. These are benchmarkable starting defaults, not universal provider limits.

On YELLOW, stop broad raw returns and use summaries + pointers. On RED, run `precompact_checkpoint.py`, then use one fresh-context worker if supported; otherwise compact/reset and resume from disk.

## Five-minute watchdog

Record task start time for non-trivial work. Around meaningful boundaries, check whether roughly five minutes have elapsed since the last checkpoint. Do not create a separate LLM turn just to read the clock; use deterministic local time/state when available.

Time alone is not a failure. A long build/test/download can be healthy. Evaluate whether the interval produced meaningful progress.

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
- `>=20m` on an ordinary task with weak progress: Brain review is strongly preferred before any further exploration.

Use `scripts/task_state.py` to make these thresholds deterministic where supported.

## Stop generic discovery

Once ownership, required delta, and direct proof are known, another search/read is forbidden unless a named unresolved question or new contradictory evidence justifies it.

A search must answer a concrete question. "Be thorough" is not a question.

## Evidence ledger

For long work keep compact accepted facts + pointers. Use `evidence_read.py` for large/repeated ranges: unchanged consumed evidence should collapse to a digest/pointer instead of being replayed. Re-read only when the file changed or a new question requires exact content.

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

Brain review is not implementation. Build the input with `scripts/brain_packet.py`; hard cap the packet at 4 KB. Include only goal, hard constraints, slice, health, counters, evidence pointers, and one corrective question.

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
