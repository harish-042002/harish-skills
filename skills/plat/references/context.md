# Task Capsule and Compaction Recovery

Use for non-trivial work, long sessions, compaction/context pressure, agent switching, or continuation after a pause.

## Principle

Repository/code/tests remain durable truth. `.plat/task.json` is a **small exact control capsule**, not a transcript or knowledge dump. Its job is to preserve the current task boundary when conversational context is compacted or lost.

## When to create

Create a capsule when work is expected to span several meaningful steps, may exceed a few minutes, crosses files/boundaries, or is likely to survive compaction/agent switching. Skip trivial one-shot edits.

Use `scripts/task_state.py start` when filesystem execution is available so start/progress timestamps are deterministic.

## Recommended schema

Keep it normally <=2 KB and hard-target <=4 KB:

```json
{
  "status": "active",
  "goal": "observable outcome",
  "must": ["hard requirements"],
  "must_not": ["hard exclusions"],
  "preserve": ["accepted behavior"],
  "current_slice": "smallest active slice",
  "accepted_evidence": ["path#symbol -> fact"],
  "proof": ["direct check"],
  "next": "exact next action",
  "execution": {
    "route": "standard",
    "started_at": "...",
    "last_progress_at": "...",
    "brain_reviews": 0,
    "reroutes": 0,
    "failed_hypotheses": 0
  },
  "health": {"status": "green", "reason": "..."}
}
```

The script may include additional small machine fields such as `schema_version`, `task_type`, or checkpoint timestamps.

## Never store

- hidden chain-of-thought or chat transcripts;
- secrets/credentials/customer-sensitive data;
- copied source/tool output;
- long plans or old decision history;
- every file read;
- speculative facts.

Store pointers + accepted facts only.

## Update rules

Update only when one of these changes materially:

- goal/scope/constraint;
- current slice;
- evidence that changes the implementation;
- reroute/correction;
- proof result;
- next action;
- task health/Brain intervention.

Do not rewrite it after every tool call.

## Progress timing

Meaningful progress is one of:

- evidence that changes/reduces implementation uncertainty;
- an implementation edit or completed slice;
- direct proof/verification;
- a valid correction/reroute that retires a wrong path.

Generic searches, rereads, narration, and repeated planning are not progress.

Use `task_state.py progress` for meaningful events and `checkpoint` when enough time has elapsed to justify a health check. Known long builds/tests/deployments can be marked as waiting so they are not mistaken for stalled investigation.

## Resume after compaction/switch

1. Read the capsule.
2. Inspect current branch/HEAD/worktree or smallest useful diff.
3. Verify only material capsule facts that could have changed.
4. Resume the recorded `next` action if evidence still agrees.

Do not replay the prior conversation, regenerate a full plan, or rebuild the repository map merely because context was compacted.

## Corrections

When the developer changes intent, replace stale scope/current/next entries rather than appending contradictory history. Preserve rejected reasoning only when forgetting it would cause an expensive repeated mistake, and even then keep one short pointer.

## Completion

When done, either delete the capsule or leave a tiny final state with final proof if near-term continuation is likely. Never let it become append-only history.
