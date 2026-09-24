# Task Capsule and Cross-Agent Continuity

Use for long/non-trivial work, context pressure/compaction, agent switching, or unfinished work that would be expensive to rediscover.

## Goal

Preserve the smallest durable set of facts needed to resume correctly. Repository/code/tests remain authority; the capsule is a cache of current task truth.

Default location:

```text
.plat/session.json
```

Prefer local exclusion through `.git/info/exclude` unless the developer explicitly wants shared state.

## Capsule budget

Target <= 2 KB; treat 4 KB as a hard warning threshold. Store facts and pointers, never transcripts or reasoning history.

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

## Compaction/resume fast path

1. Read the capsule once.
2. Inspect branch/HEAD and the smallest useful diff/worktree summary.
3. Revalidate only facts that could have become stale.
4. Resume `next` if evidence still agrees.

Do not replay the conversation, regenerate a long plan, or rebuild a repository map merely because context compacted.

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
