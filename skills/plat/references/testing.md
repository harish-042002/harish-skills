# Testing and Verification

Use whenever behavior changes. Scale proof to risk.

## Verification ladder

Run the cheapest check that directly proves the changed behavior, then widen only as justified:

1. Focused reproducer/unit/property test.
2. Focused integration/contract test.
3. Static/type/lint checks relevant to touched code.
4. Related module suite.
5. Build/package check.
6. Runtime/end-to-end/browser/device verification.
7. Load, concurrency, migration, recovery, or failure testing for risks lower layers cannot prove.

Do not start with an enormous suite when a narrow check can fail faster.

## Regression-first when practical

For a reproducible behavior change or bug:

1. Write or identify proof that fails for the old behavior.
2. Confirm it fails for the intended reason.
3. Implement the minimum change.
4. Confirm the proof passes.
5. Refactor/simplify only while preserving green evidence.
6. Run nearby regression checks.

Do not force test-first ceremony for throwaway exploration, generated/config-only changes, or layers that cannot express the failure yet. Still leave durable proof at the nearest useful boundary.

## Test quality

Derive tests from acceptance criteria, invariants, contracts, and known fault classes. A test should fail for a meaningful defect, not merely execute code. Cover relevant fault classes:

- Happy path and boundaries/empty/null.
- Invalid input, permissions, and authorization.
- Error propagation/recovery.
- Retry/duplicate/concurrency/order/time/expiry.
- Persistence/transaction semantics.
- Backward compatibility of contracts and stored data.

Prefer focused readable assertions over tests coupled to implementation detail. Use table/property/generative tests when a compact invariant covers a large input space better than hand-picked examples; do not add them where ordinary examples are clearer.

## Mocks and realism

Mock true external boundaries when useful, but do not mock away semantics under test. Use realistic fakes/containers/integration tests when correctness depends on database transactions, serialization, queues, framework routing, or network contracts.

## Verification map

For a non-trivial change, be able to map each material completion claim to evidence: behavior claim -> direct test/reproducer, compatibility claim -> contract/integration evidence, migration claim -> migration/rollback evidence, performance claim -> comparable measurement. Do not let a broad green suite stand in for a risk it cannot observe.

## Fresh evidence rule

Never claim completion from remembered/stale test output. Before a completion claim:

1. Identify the check that proves the claim.
2. Run it after the relevant final change.
3. Inspect exit status and failures, not only a partial log.
4. State exactly what passed and what was not run.

Example:

```text
Verified:
- pytest tests/orders/test_create.py - 12 passed
- ruff check src/orders - exit 0
```

Avoid "fully tested" unless the executed evidence actually justifies it.
