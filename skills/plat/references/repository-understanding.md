# Repository Understanding

Use before changing an existing codebase, especially when the task is unfamiliar or cross-cutting.

## Build a task-scoped map

Do not read the whole repository. Find only what can affect the requested behavior:

1. Repository/agent instructions.
2. Behavior entry point.
3. Direct implementation files.
4. Callers, dependencies, and ownership boundary.
5. Models/schemas/contracts/config/feature flags.
6. Relevant tests and fixtures.
7. Similar existing patterns.
8. Build/lint/test commands.
9. Generated/vendor files that should not be hand-edited.

## Search order

Prefer targeted discovery:

- `AGENTS.md`, `CLAUDE.md`, README/contributing/tool config.
- Exact symbols/routes/errors named by the task.
- Usages/imports/call sites.
- Tests covering the path.
- Nearby analogous code.
- Config/environment boundaries only when relevant.

Use symbol/search tooling before broad recursive reading. For many same-shape peers/adapters, derive the comparison matrix from the golden/reference implementation once, then inspect peers against that matrix instead of rediscovering each flow independently.

## Dependency/source freshness

When behavior depends on a framework/library/API:

- Identify the repository's actual version from lockfile/manifest/config.
- Prefer installed types/source and bundled docs for the actual version; use current official documentation when local evidence is insufficient or behavior is version-sensitive.
- If generic/latest documentation conflicts with the installed version, the repository's actual version wins unless the task includes an upgrade.
- Do not "upgrade to the latest" unless the task requires it.
- Distinguish current repository behavior from generic model memory.

## Before editing

Be able to state internally:

- likely files/ownership;
- direct proof/test;
- whether a public/data/security/deployment boundary changes.

Inspect callers/consumers, history/blame, and rollback/blast radius **only when risk earns it**. Do not calculate a broad blast radius for an isolated local edit.

For a trivial isolated edit this can stay implicit.

## Existing patterns

Reuse repository conventions for dependency injection, validation, errors, logging, transactions, API responses, state management, tests, naming, and layout. Do not import an external "best practice" that fights the codebase unless the current pattern causes a concrete problem or risk.

## Staleness rule

Treat `.plat/session.md`, plans, issues, docs, comments, and prior agent outputs as leads, not authority. Verify material claims against current code/tests/config before acting.


## Discovery stop condition

Stop repository exploration when all are true:

- the active outcome is clear;
- ownership is localized;
- an existing pattern or minimal approach fits the evidence;
- the direct verification path is known;
- another search/read is unlikely to change the decision.

Large repository size alone is not permission for broad reading. Keep an evidence ledger of accepted facts + pointers during long Research so unchanged large files are not reopened merely to recover context.
