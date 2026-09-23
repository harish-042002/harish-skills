# Precise Routing, Vague Requests, and Trajectory Control

Use when the latest developer message is short, referential, ambiguous, corrective, or likely to continue work already in progress. The goal is to act from evidence without guessing, while keeping routing overhead tiny.

## Contents

1. Routing objective
2. Active-intent evidence
3. Vague-message resolution
4. Confidence gate
5. Fast path
6. Scope lock
7. Diff-expansion circuit breaker
8. Correction severity
9. Correction purge
10. Dependency invalidation
11. Re-route protocol
12. Repository inspection budget
13. Specialist budget
14. Stop conditions
15. Examples

## Routing objective

Choose the **minimum sufficient action** that is strongly supported by current evidence.

Avoid both failure modes:

- **guessing** from a vague message when several materially different actions are plausible;
- **over-clarifying** when the active task and recent evidence make the intended action obvious.

The router should normally be cheaper than the work it routes.

## Active-intent evidence

Resolve the current task from the strongest available evidence in this order:

1. explicit nouns, verbs, constraints, corrections, and acceptance criteria in the latest developer message;
2. the latest unresolved developer request or correction in the current conversation;
3. the immediately active task: last requested edit, failing command, test, diff, file, screen, or artifact;
4. current workspace evidence: changed files, failing tests, logs, errors, current branch/diff, rendered state;
5. repository-local instructions and authoritative implementation evidence;
6. compact current-session state when it exists and is fresh;
7. developer preference profile;
8. Plat defaults.

Do not let an older plan outrank a newer correction. Do not let a profile infer product requirements.

## Vague-message resolution

Treat short messages such as these as likely **continuations**, not automatically new tasks:

- "do it"
- "fix it"
- "yes"
- "same"
- "continue"
- "this one"
- "remove that"
- "make it better"
- "now update"
- "still wrong"

Before asking a question, use this ambiguity ladder:

1. identify the most recent unresolved action/correction;
2. inspect what changed since it: last tool result, failing command, diff/worktree, screenshot/render, or test output;
3. inspect the narrowest repository evidence that can resolve the referent;
4. check whether one interpretation clearly dominates;
5. only then ask one focused question if materially different interpretations remain.

A vague message can safely inherit **scope**, **artifact**, and **accepted constraints** from the active task. It must not inherit assumptions that the developer already corrected.

## Confidence gate

Act without clarification when all are true enough:

- one interpretation is clearly better supported by the latest conversation/workspace evidence;
- the action is within the active task boundary;
- the action is reversible or already authorized;
- no unresolved choice materially changes behavior, compatibility, cost, security, data, or a hard-to-reverse design decision.

Ask **one concise question** only when two or more plausible interpretations would cause materially different work and cheap evidence cannot resolve them.

Prefer direct evidence (current code/test/runtime/diff) over recollection or inference. Treat old plans, summaries, comments, and session notes as leads until material claims are rechecked.

If a safe read/test/render can disambiguate the request, inspect first instead of asking.

## Fast path

Use a fast route when the active intent and owning boundary are already clear.

Fast path:

1. resolve referent;
2. inspect target + nearest proof only;
3. act;
4. run direct verification;
5. report briefly.

Do not load planning, deep routing, repository maps, or multiple specialists merely because Plat is active.

Typical fast-path cases:

- typo/copy/constant change;
- isolated styling fix;
- obvious known-file correction;
- rerun after a narrow failed command;
- developer says "remove that" immediately after identifying one element.

## Scope lock

Before mutating code, bind the latest request into four facts when scope could drift:

```text
MUST: exact requested behavior/artifact
MUST NOT: explicit exclusions/negations
PRESERVE: accepted current behavior not being replaced
PROOF: smallest direct evidence for the requested delta
```

Words such as **only, alone, just, no/no need, do not/don't, keep, exactly, these alone** are constraints, not conversational filler. They outrank earlier inferred enhancements.

Do not substitute a product idea for the request. A developer asking for more catalogue variants, stronger copy, or one new user-state dimension has **not** implicitly asked for confidence tiers, new progression stages, additional learning signals, telemetry, selector rewrites, or new persistence. Those require their own evidence-backed requirement.

Adjacent changes are allowed only when they are mechanically required for the requested behavior to compile, run, preserve an existing contract, or pass the direct proof. Keep them minimal and name why they were required.

## Diff-expansion circuit breaker

Treat unexpected patch growth as evidence that the task may have been reinterpreted. Before continuing, stop and re-localize when any of these occurs:

- a local/copy/catalogue request crosses into a second subsystem with no proven dependency;
- a new state dimension, mode, stage, signal, abstraction, dependency, schema field, telemetry path, or background process appears without an explicit requirement;
- touched files materially exceed the owning implementation + nearest tests/docs required by the change;
- the explanation for a touched file is "it would be better" rather than "the requested outcome requires it."

This is not a numeric file-count rule. One requirement may legitimately span many files; one copy change may legitimately need one. The gate is **causal necessity**. If extra scope is not necessary, do not do it.

## Correction severity

Classify a material correction before continuing.

### Level 1 — Local

Changes one local value/detail without invalidating the approach.

Examples:
- spacing, wording, color, threshold;
- rename one field;
- use 5 minutes instead of 10.

Action: update the local slice and direct proof. Do not re-route the task.

### Level 2 — Behavioral

Changes behavior or a contract inside the same general architecture.

Examples:
- cache lifetime semantics change;
- different validation rule;
- old clients must remain compatible;
- notification should schedule from a different event.

Action: revisit affected implementation, tests, and nearby contract/failure paths.

### Level 3 — Structural

Invalidates the model that produced multiple downstream decisions.

Examples:
- "this is a capability-based team, not an office metaphor";
- "this service cannot own the invariant";
- "the data source is event-driven, not request-driven";
- repository evidence reveals the planned local cache must use an existing shared cache;
- user changes the actual product audience or primary workflow.

Action: invalidate dependent decisions and re-run Interpret → Inspect → Route for the affected artifact/subsystem.

## Correction purge

A newer developer correction is not an additive suggestion. For task-local work created during the current trajectory:

1. identify additions that depended on the rejected assumption;
2. remove/revert them if they are no longer necessary for the corrected outcome;
3. preserve only work that is independently required;
4. re-run the narrowest proof against the corrected truth.

Examples:
- "no medium/high thing" means confidence-gated selection introduced for this task should disappear, not remain as a dormant fallback;
- "work on these alone" means stop touching learning, telemetry, orchestration, or unrelated docs unless the corrected behavior cannot function without a specific dependency;
- "5 variants per state is the only truth" means do not retain a generic competing catalogue path merely because it was built earlier, unless an existing contract requires a fallback.

Do not protect agent-authored work from the developer's correction. The latest accepted requirement owns the trajectory.

## Dependency invalidation

When an assumption changes, ask internally:

> Which current decisions only exist because that assumption was believed?

Invalidate those decisions together.

Do **not** perform global rework when the correction is local. Do **not** perform word-level replacement when the correction is structural.

Keep a temporary correction anchor only when needed:

```text
Changed assumption: ...
Affected decisions: ...
Next valid slice: ...
```

Maximum three lines. Delete/replace it when no longer useful.

## Re-route protocol

Trigger a re-route only on:

- developer correction that invalidates the current direction;
- repository/runtime evidence contradicting a material assumption;
- failed verification showing the implementation model is wrong rather than merely incomplete.

Protocol:

1. stop the affected slice;
2. identify the invalid assumption;
3. preserve work independent of that assumption;
4. inspect only evidence needed to choose the replacement direction;
5. reclassify mode/depth/domain only if the new evidence changes them;
6. resume from the smallest valid point;
7. verify the corrected path.

A re-route is not a retrospective essay.

## Repository inspection budget

Stop discovery when ownership and direct proof are clear.

### Quick

- target file/symbol;
- nearest relevant test/render/check;
- one analogous local pattern only if needed.

### Standard

- entry point;
- owning implementation;
- relevant test;
- one analogous pattern;
- contract/config only when materially touched.

### Deep / Research

Expand to callers, data/event flow, deployment boundaries, concurrency, compatibility, or broader subsystem map only when the unresolved risk requires it.

Use **history/blame** only when current code cannot explain why a risky/public/security/value-transfer behavior exists or when regression evidence matters. Estimate **blast radius** from callers/consumers only when the change can cross a contract or high-impact boundary.

Do not read top-level docs/manifests repeatedly if the current task is already localized.

## Specialist budget

Default load budget:

- **Quick:** zero extra references, or one basic domain if truly needed;
- **Standard:** one primary reference; add a second only when evidence crosses a real boundary;
- **Deep:** one basic domain + one deep specialist first;
- **Second deep specialist:** only after evidence proves the task crosses that boundary;
- **Research:** task-scoped map; expand high-signal branches only.

A user's request for a "deep explanation" changes response detail, not specialist loading.

## Ambiguous debugging

If several plausible causes remain after the cheapest evidence:

- keep 2-4 competing hypotheses instead of committing early to one;
- collect one discriminating piece of evidence per hypothesis;
- retire falsified hypotheses;
- parallelize only when the investigations are genuinely independent and coordination cost is justified.

Do not create competing hypotheses for a deterministic bug whose cause is already localized.

## Stop conditions

Stop inspecting/routing when:

- the requested outcome is clear;
- ownership is clear;
- one approach fits repository evidence and constraints;
- direct verification is known;
- additional context is unlikely to change the decision.

Continue investigating only for a concrete unresolved question.

## Examples

### "do it"

Previous unresolved request: "remove the benchmark history paragraph from README."

Evidence: README still contains that paragraph.

Route: continuation → Quick → edit README → render/read check.

Do not ask "what should I do?"

### "still wrong"

Previous action changed a UI component. Current screenshot shows the issue remains.

Route: Debug current slice. Inspect rendered state and implementation before another edit.

Do not assume the same fix should be repeated.

### "use team, not office"

If "office" only appears in one label, Local may be enough.

If the metaphor shaped characters, layout, copy, and information hierarchy, classify Structural → invalidate dependent visual/content decisions → re-route Design.

### "make it deep"

Task: change one known constant.

Engineering route: Quick. Response may explain the change in more detail if useful, but do not load Deep specialists.

### "fix duplicates"

If recent context identifies duplicate invoice creation under concurrent workers, use that evidence and inspect the owning write path.

If there is no active referent and several duplicate behaviors exist, search narrowly first. Ask one question only if the repository still leaves multiple materially different targets.

### "5 variants per user state; no medium/high; work on these alone"

Previous trajectory added confidence tiers, response stages, extra learning signals, and trace fields while expanding catalogue copy.

Route: latest correction becomes the scope lock -> keep only the requested scenario × state × variant truth plus mechanically required selector/test changes -> purge task-local confidence/stage/telemetry additions that no longer serve the corrected requirement -> direct catalogue/selection proof.

Do not justify the old additions as future-proofing.
