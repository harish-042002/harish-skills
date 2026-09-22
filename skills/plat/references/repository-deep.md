# Deep Repository Understanding

Use for large/legacy/monorepo systems, architecture archaeology, cross-service tracing, unclear ownership, subsystem research, or changes where naive broad reading would waste context.

## Contents

1. Objective
2. Scale classification
3. Needle-first discovery
4. Architecture map
5. Trace behavior
6. History and blast radius
7. Monorepos and multi-service systems
8. Generated/vendor boundaries
9. Research artifacts
10. Context economy
11. Project-profile integration
12. Edge cases

## Objective

Build the smallest verified model of the repository that is sufficient for the current question. Do not confuse repository understanding with documenting every directory.
Do not read the whole repository by default; expand only when the evidence boundary requires it.

A deep repository pass should reduce future reads, not create a second copy of the codebase in markdown.

## Scale classification

Use scale to choose discovery strategy, not to infer risk.

- **Small**: most relevant implementation can be read directly.
- **Medium**: search first, then read one-hop dependencies and analogous paths.
- **Large/monorepo**: surgical exploration by entry points, dependency edges, owners, contracts, and runtime boundaries.

A tiny repository can still need deep debugging. A huge repository can still have a trivial known-file change.

## Needle-first discovery

Start from the question, not the directory tree.

1. Read repository/agent instructions and top-level manifest/build config.
2. Search exact names from the request: routes, commands, events, tables, errors, feature flags, UI labels.
3. Find behavior entry points.
4. Follow usages/callers/imports only along the relevant path.
5. Find tests that prove or describe the behavior.
6. Locate source-of-truth data/contracts/config.
7. Find one or two analogous working implementations.
8. Expand only where ownership or behavior remains unresolved.

Prefer symbol/call/reference search over recursive file reading.

## Architecture map

For deep work, maintain an internal/task artifact like:

```text
User/API/Event entry
  -> boundary/controller
  -> application/domain owner
  -> persistence/cache/queue/external systems
  -> emitted events/side effects
  -> consumers/rendering
```

For each node record only:

- path/symbol;
- responsibility;
- authoritative state/contract;
- important upstream/downstream edges;
- verification source.

Do not list helper files that do not change the current decision.

## Trace behavior

Trace both **control flow** and **data/state flow**.

Questions:

- Where is the request/event created?
- Where is identity/authorization established?
- Where is input normalized?
- Which layer decides business behavior?
- Where is state persisted or cached?
- What async/event boundaries split the flow?
- What transforms the data between boundaries?
- What consumes the result?
- Which tests/telemetry prove the path?

When documentation conflicts with code, current code/tests/config win unless the task is specifically to reconcile docs.

## History and blast radius

Use Git history selectively when it can answer why or regression risk:

- recent commits around the failing/changed code;
- blame for removed validation/security/compatibility logic;
- old fixes for the same symptom;
- migration history around a schema/contract;
- authorship/team ownership only when it helps route understanding, not as proof of correctness.

Estimate blast radius through:

- callers/usages;
- shared contracts/types;
- events/topics;
- schema consumers;
- feature flags/config;
- deployment units;
- tests and fixtures.

Do not recursively inspect all transitive dependencies unless the risk requires it.

## Monorepos and multi-service systems

First identify the repository's real unit boundaries:

- package/workspace/module boundaries;
- deployable services/functions/jobs;
- shared libraries;
- data stores/topics/queues;
- frontend/mobile apps;
- infrastructure packages.

Then localize the current behavior to the minimum set of units.

Avoid assuming directory boundaries equal service/domain boundaries. Verify deployment/config and runtime ownership.

## Generated/vendor boundaries

Identify and avoid hand-editing:

- generated clients/types/schemas;
- compiled/build output;
- vendored dependencies;
- lockfiles except when dependency change is intended;
- migration artifacts managed by tooling;
- generated infrastructure plans/state.

Find the source/template/generator instead.

## Research artifacts

For a broad Research request, a useful structured output can include:

```text
Scope
Subsystem map
Entry points
Data/event flow
Source-of-truth boundaries
Important contracts
Failure/operability paths
Verified evidence
Unknowns/stale docs
```

Do not generate full C4 documentation unless the developer asks for architecture documentation. For ordinary engineering, a task-scoped C4-like map is cheaper and more useful than exhaustive bottom-up documentation.

## Context economy

Use a funnel:

```text
search results
-> candidate files
-> decisive snippets/files
-> compact map
-> targeted expansion
```

Avoid:

- dumping entire trees into context;
- reading every README in a monorepo;
- loading all tests before finding the owning module;
- sending full repo snapshots to subagents;
- keeping obsolete exploration trails in `.plat/session.md`.

For independent unknown areas, a Scout subagent may inspect one bounded slice and return a compact map. Do not run several scouts over the same territory.

## Project-profile integration

If `.plat/project.md` exists:

1. use it as a candidate map;
2. compare freshness/branch/HEAD where recorded;
3. revalidate material paths touched by the current task;
4. update stale durable facts only if profile maintenance is already enabled or setup was requested.

A project profile should make the **second** task cheaper than the first.

## Edge cases

- **Renamed/moved modules:** follow current symbols/import graph; stale profile/docs are leads only.
- **Feature flags:** trace both enabled and disabled paths when rollout behavior matters.
- **Dynamic/plugin loading:** inspect registration/config rather than assuming static imports reveal all consumers.
- **Generated APIs:** inspect source schema and generation config, then generated consumer surface as needed.
- **Polyglot repo:** trace contracts between languages via API/event/schema boundaries rather than trying to understand every language equally.
- **No tests/docs:** use runtime/config/call paths and create a characterization/reproducer if edits follow.
