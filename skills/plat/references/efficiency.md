# Research and Execution Economics

Use for broad repository analysis, cross-branch mapping, AFK report tasks, expensive Deep/Research sessions, or any task where tokens, cache reads, tool calls, subagents, full-suite runs, or wall time may dominate cost.

## Objective

Minimize **total cost to a correct verified result**:

```text
correctness / requested scope
        ↓
avoid wrong work + repair turns
        ↓
avoid duplicate discovery + duplicate verification
        ↓
use the cheapest adequate worker/model
        ↓
minimize narration/output overhead
```

Do not optimize one metric while making the whole task worse. A cheaper worker that causes retries is not cheaper. A fast parallel wave that duplicates repository discovery can reduce wall time while multiplying API cost.

## 1. Lead-first orientation

For broad Research, P-01 should orient before delegating.

First establish:

- active goal and hard scope;
- current branch/worktree state;
- golden/reference flow if one exists;
- inventory of peer components/adapters/features;
- comparison dimensions;
- direct evidence sources;
- final report shape.

Do **not** dispatch a general-purpose subagent to rediscover the repository before this map exists.

A subagent becomes useful only after P-01 can give it a bounded partition such as:

```text
Compare adapters A-D against these 8 fixed dimensions.
Return only missing/present/partial + file:line evidence.
Do not inspect unrelated modules.
```

## 2. Golden-reference mapping pattern

When one implementation is the complete example and many peers must be audited:

1. reconstruct the golden flow once;
2. derive a fixed comparison matrix once;
3. enumerate peers;
4. inspect each peer only against the matrix;
5. investigate deltas/unknowns, not already-green dimensions;
6. synthesize one consolidated report.

Do not independently rediscover the full architecture for every peer.

Typical matrix dimensions:

- entry point / trigger;
- context/data acquisition;
- eligibility/rules;
- candidate construction;
- presentation/copy;
- action/deep-link;
- persistence/state;
- orchestration/worker handoff;
- observability/trace;
- tests/fixtures;
- failure/retry behavior;
- integration contract.

Adjust dimensions to the repository; do not force this list mechanically.

## 3. Evidence ledger and read deduplication

Keep a compact evidence ledger during long Research:

```text
Reference: path#symbol / range -> accepted fact
Peer A: present / missing / partial -> evidence
Peer B: ...
Unknown: question -> next smallest check
```

Store pointers and conclusions, not copied source.

Rules:

- search exact symbols before reading whole files;
- read the smallest useful range;
- do not reread an unchanged large file unless a new question requires a different range;
- do not make a subagent read files P-01 already summarized unless independent verification is the point;
- after a fact is accepted, carry its pointer forward instead of re-opening it;
- stop a discovery branch when another read is unlikely to change a matrix cell or decision.

If a graph/index/tool exceeds its useful size or latency budget, fall back immediately to targeted source search instead of repeatedly retrying it.

## 4. Subagent economics

Subagents are for **critical-path reduction or isolated fresh judgment**, not for making Research feel parallel.

Default for broad Research:

1. P-01 orients first.
2. Start with **0 subagents** during orientation.
3. After the work is partitioned, use **1 bounded scout** first when it materially saves context/time.
4. Use a second concurrent scout only for genuinely independent partitions.
5. A third requires a clear wall-time benefit and cheap integration; it is exceptional, not default.

Batch homogeneous peers into one worker rather than one worker per file/adapter.

If a worker returns mostly repository summary that P-01 already knew, do not dispatch another worker of the same shape.

### Model selection

When the host supports per-worker model selection:

- every dispatch names a model/tier explicitly;
- use the lowest adequate tier for bounded search, inventory, mechanical comparison, and deterministic verification;
- use the strongest model for integration, ambiguous architecture, subtle debugging, or high-risk judgment;
- never omit a worker model when omission silently inherits the lead session's most expensive model.

When the host does **not** support worker model selection, raise the delegation bar because a bounded scout may cost the same as the lead.

## 5. Test economics

Use the verification ladder, but avoid duplicate broad suites.

For integration/merge work:

1. run syntax/import/static checks that fail fast;
2. run tests directly covering changed/shared boundaries;
3. widen to the related suite;
4. run the full suite **once** when blast radius justifies it or before final integration confidence.

If a broad suite fails:

- identify the failing tests first;
- compare **those failing tests** against the clean baseline branch/worktree;
- do not rerun the entire baseline suite merely to prove the same failures existed before;
- rerun the full current suite only after changes that could affect its result or when final release evidence requires it.

A baseline comparison should answer one question: **did this change introduce the failure?** Use the cheapest check that separates yes from no.

## 6. Branch / merge research

When the requested analysis requires integrating another branch, the merge can be part of the research workspace.

Economy rules:

- fetch once;
- inspect branch tips/diff before merge when useful;
- resolve required conflicts once;
- record merge/conflict decisions compactly;
- after integration, inspect the resulting changed surfaces rather than rereading unaffected modules;
- if the final deliverable is a report, do not drift into feature implementation.

Use a temporary worktree when it avoids disrupting the developer's active workspace or enables a clean baseline comparison. Do not create worktrees merely as ceremony.

## 7. AFK / report mode

When the developer says they are AFK or asks for a finished report:

- do the work autonomously unless genuinely blocked;
- minimize progress narration;
- keep detailed intermediate notes internal/compact;
- surface only blockers that require user input;
- spend output tokens on the final report, not repeated status prose.

This does not reduce verification. It reduces conversational overhead.

## 8. Parallelism vs cost

Parallel work can make wall time faster while increasing aggregate API time and cost.

Before parallelizing, ask:

- Are the partitions truly independent?
- Will they read mostly different files?
- Is their output easy to merge?
- Does wall-time matter enough to justify duplicated model overhead?
- Can one batched scout finish nearly as fast?

Prefer **one batched scout** over several overlapping scouts.

Measure both:

- **wall time** — what the developer waits;
- **aggregate model/API time** — total compute consumed across concurrent workers.

A 5-minute wall-time result with 40 minutes of aggregate agent time may be fast but expensive.

## 9. Research stop conditions

Stop expanding when:

- the golden/reference flow is understood;
- every peer has a status for each material comparison dimension;
- remaining unknowns do not change the next-step plan;
- another repository read would only add completeness, not a decision;
- failures have been attributed to current change vs baseline;
- the final report can state evidence, gaps, priorities, and unverified areas.

Do not keep reading to make the report feel exhaustive.

## 10. Metrics for live evaluation

For expensive Research/Deep trajectories, capture when the host exposes them:

- verifier/report completeness;
- input/output/cache-read/cache-write tokens;
- model cost;
- wall time;
- aggregate model/API time;
- tool calls;
- repository file reads;
- duplicate reads;
- subagent count and model/tier;
- subagent share of total cost/tokens;
- broad-suite runs;
- baseline-suite runs;
- repair turns.

The optimization target is **same-or-better correctness with lower total economics**, not a specific token number.
