# Task Capsule and Cross-Agent Continuity

Use for long/non-trivial work, context pressure/compaction, agent switching, or unfinished work that would be expensive to rediscover.

## Goal

Preserve the smallest durable set of facts needed to resume correctly. Repository/code/tests remain authority; the capsule is a cache of current task truth.

Task truth: `.plat/session.json`  
Context pressure: `.plat/context.json`  
Optional normalized host telemetry: `.plat/telemetry.json`  
Consumed evidence index: `.plat/evidence-index.json`  
Full noisy evidence: `.plat/logs/`  
Latest compaction checkpoint: `.plat/checkpoints/precompact-latest.json`

Prefer local exclusion through `.git/info/exclude` unless the developer explicitly wants shared state.

## Capsule budget

Target <= 2 KB; treat 4 KB as a hard warning threshold. Store facts and pointers, never transcripts, reasoning history, raw logs, or full tool output.

Recommended shape:

```json
{
  "goal": "observable outcome",
  "must": ["hard requirement"],
  "must_not": ["explicit exclusion"],
  "preserve": ["accepted behavior"],
  "owner": ["current owning boundary"],
  "current_slice": "smallest active slice",
  "proof": ["direct verification"],
  "next": "exact next action",
  "execution": {
    "route": "STANDARD",
    "worker_tier": "cost-efficient-latest",
    "brain_tier": "one-tier-stronger-cost-effective",
    "started_at": "...",
    "last_progress_at": "...",
    "brain_reviews": 0,
    "reroutes": 0
  },
  "health": {"status": "GREEN", "action": "continue"}
}
```

Use `scripts/task_state.py` for deterministic start/checkpoint/Brain-budget bookkeeping when the host can execute local scripts.

## Write/update rules

Create/update only when continuity has real value. Skip tiny one-shot changes.

Update the capsule when:

- a material developer correction changes goal/scope;
- ownership or implementation direction becomes clear;
- a slice is verified;
- task health changes materially;
- a Brain review changes direction;
- work is about to compact/switch/stop unfinished.

Replace stale values; do not append history.

## Alignment gate

For each new developer message compare against `goal`, `must`, `must_not`, and `current_slice`.

- Clearly aligned -> continue silently.
- Clear correction -> update capsule and self-correct.
- Materially different interpretations -> inspect cheap evidence first; ask one focused question only if ambiguity remains.
- New work that exceeds authority or contradicts an explicit exclusion -> ask before crossing that boundary.

## Context-pressure recovery

Start with `scripts/host_context.py` when a host exposes telemetry through a canonical JSON payload/file or transcript path. `scripts/context_guard.py` separates current occupancy from cumulative work proxies; telemetry is optional and must never become a blocker.

For source reads, prefer `scripts/evidence_read.py` when a range is large or likely to be revisited. Only fully delivered ranges may collapse to a pointer/digest within the same context epoch. Truncated ranges expose continuation offsets and are never marked consumed. Use --refresh for exact content on a new question.

Read counts and cumulative cache traffic cannot trigger RED. YELLOW means stop returning large raw output and rely on summaries + pointers. RED means run `scripts/precompact_checkpoint.py` before continuing. Hook-capable hosts may call `scripts/context_hook.py` on PreCompact/preCompact; hosts without hooks use the same checkpoint path from the normal Plat loop.

If the host supports isolated execution, allow one fresh-context worker for the current slice. Give it only the capsule, a <=4 KB task/evidence brief, exact evidence pointers, allowed scope, and proof. It returns <=2 KB of result/evidence pointers. This worker is context garbage collection, not a second planner/reviewer.

If isolated context is unavailable or already used, compact/reset the host context where supported and resume from disk state. Host capability claims are dynamic inputs (for example through `PLAT_HOST_CAPABILITIES_JSON`), never permanent provider assumptions.

## Compaction/resume fast path

Only after confirmed context replacement, call `context_guard.py reset` to invalidate consumption masks and epoch-local counters. Do not reset on PreCompact alone. Keep every requirement, exclusion and proof obligation intact even when the capsule exceeds its soft size target.

1. Read the capsule once.
2. Inspect branch/HEAD and the smallest useful diff/worktree summary.
3. Read only evidence pointers needed for stale facts.
4. Resume `next` if evidence agrees.

Do not replay conversation history, raw logs, or repository discovery merely because context compacted.

## Keep only high-signal state

Good state:

- exact goal and exclusions;
- current owner and slice;
- accepted facts with file/symbol pointers;
- current proof and result;
- unresolved blocker;
- next action;
- elapsed/health counters.

Never store:

- hidden chain-of-thought;
- chat transcripts;
- secrets/credentials/private keys;
- customer/user sensitive data;
- large source/tool output;
- rejected ideas that no longer constrain the task.

## Completion cleanup

When fully complete, delete the capsule unless near-term continuation has clear value. If retained, leave only a tiny verified final state.
