# Deep Testing and Verification Engineering

Use when ordinary unit/integration checks cannot adequately prove risk: concurrency, distributed workflows, contracts, migrations, large input domains, flaky behavior, fault handling, performance, or critical end-to-end flows.

## Contents

1. Objective
2. Technique selection
3. Regression and characterization
4. Contract testing
5. Property-based testing
6. Mutation testing
7. Fuzzing and adversarial input
8. Concurrency/time testing
9. Fault injection and resilience
10. Migration/data testing
11. End-to-end and browser/device
12. Performance/load
13. Test quality and flakiness
14. Cost discipline
15. Edge cases

## Objective

Choose the cheapest test technique that can actually detect the fault class. Coverage percentage and large suites are not substitutes for meaningful assertions.

## Technique selection

Use the risk to select proof:

- deterministic business rule -> focused unit/example test;
- integration serialization/DB/framework semantics -> integration/contract test;
- public API between independently evolving components -> contract compatibility test;
- algebraic/input-domain invariant -> property-based testing;
- uncertainty about whether tests detect logic changes -> mutation testing;
- parser/untrusted binary/text format -> fuzzing where appropriate;
- race/order/idempotency -> controlled concurrency/repetition/model checking style tests where feasible;
- retry/failure/recovery -> fault injection/controlled dependency failures;
- migration -> old/new schema/data coexistence + rollback/forward tests;
- critical user workflow -> E2E/browser/device;
- latency/capacity claim -> representative benchmark/load test.

Do not add specialized libraries when ordinary examples prove the behavior more clearly.

## Regression and characterization

For a bug, prefer a small proof that fails for the old behavior and passes after the root fix.

For legacy behavior with no tests, a characterization test may first capture current externally relied-on behavior before refactoring. Do not freeze known-bad behavior as a permanent contract unless intentionally required.

## Contract testing

For APIs/events/schemas between independent components, verify:

- request/response/event shape;
- required/optional/default semantics;
- error/status behavior;
- auth expectations;
- version/coexistence behavior;
- producer/consumer compatibility.

Use consumer-driven contracts only when actual consumer expectations are the right source of truth; do not let stale consumer tests block intentional contract evolution without review.

## Property-based testing

Use when a strong property exists over a broad input domain.

Useful property families:

- roundtrip: `decode(encode(x)) == x`;
- inverse;
- oracle/reference equivalence;
- idempotence;
- invariant preservation;
- sorting/order properties;
- commutativity/associativity/identity where domain-valid.

Prefer a strong property over "does not crash".

Avoid tautological properties that recompute the implementation, and avoid generators/assumptions that filter nearly all cases. If the project lacks a PBT library, adding one is a dependency decision; use it only when the expected fault-finding value is real.

## Mutation testing

Use mutation testing to assess test effectiveness when ordinary coverage is misleading or a critical module needs stronger confidence.

A surviving mutant can mean:

- missing execution;
- weak assertion;
- equivalent mutation;
- low-value code whose behavior does not matter.

Inspect survivors by business/security risk, not mutation severity alone. Run targeted campaigns on critical modules before broad repository-wide mutation suites.

Do not treat timeout/skipped mutants as proof of coverage.

## Fuzzing and adversarial input

Use fuzzing for parsers/protocols/native code/input spaces where generated malformed data can expose crashes, memory errors, or invariant violations.

Keep fuzzing distinct from property-based testing and mutation testing; choose the tool based on the failure class.

For untrusted web/API input, targeted adversarial examples may be cheaper than a full fuzzer.

## Concurrency/time testing

Make time and concurrency controllable:

- fake/virtual clock where semantics allow;
- barriers/latches/hooks to force interleavings;
- deterministic IDs/random seeds;
- isolated shared state;
- repeated runs only as a supplement, not the sole proof.

Test duplicate/reordered/retried events and stale-version writes when those are real system semantics.

Avoid arbitrary sleeps; wait on the condition/event that represents correctness.

## Fault injection and resilience

For important dependency/recovery behavior, test controlled:

- timeout;
- connection failure;
- partial response;
- duplicate delivery;
- retry exhaustion;
- queue poison message;
- process restart;
- stale cache/replica;
- resource saturation where safe.

Verify both user-facing result and durable state integrity.

## Migration/data testing

Test with representative old data and realistic cardinality.

Verify:

- migration applies from supported prior versions;
- old/new application versions coexist if deployment can overlap;
- backfill is resumable/idempotent;
- constraints/indexes are safe for actual DB semantics;
- rollback or forward-fix plan works where promised;
- skipped versions/upgrades are covered for mobile/local schema when relevant.

## End-to-end and browser/device

Use E2E for a small number of critical cross-boundary flows. Do not recreate every unit test through UI automation.

Prefer stable user-visible semantics over brittle DOM/layout details. Test real browser/device behavior for navigation, focus, network, lifecycle, permissions, and platform integration when those are the risk.

## Performance/load

A performance test needs:

- representative workload/data;
- warmup/state assumptions;
- baseline;
- p50/p95/p99 or relevant distribution;
- throughput/error/saturation;
- resource usage;
- repeatability/environment notes.

Do not compare benchmarks from materially different environments without labeling the limitation.

## Test quality and flakiness

A flaky test is a defect in the test/system evidence.

Classify:

- real race/shared state;
- time/locale/environment dependency;
- external service instability;
- order dependence;
- nondeterministic fixture/data;
- brittle UI locator/timing;
- resource contention.

Retries can gather evidence but should not permanently hide an unresolved flaky cause unless product semantics themselves are probabilistic and the acceptance criterion accounts for it.

## Cost discipline

Advanced testing can become expensive. Use it surgically.

- Start with the narrowest reproducer.
- Run mutation/property/fuzz/load only where the fault model supports it.
- Keep expensive suites targeted/parallel only when the environment can handle it.
- Cache build/setup artifacts safely where the test tool supports it.
- Do not require full E2E/load/security suites for a tiny isolated low-risk edit.

## Edge cases

- **Test passes before implementation:** it does not prove the missing behavior; fix the proof.
- **100% coverage:** may still have weak assertions; mutation/property checks can expose this on critical code.
- **Mutation survivor in logging:** business risk may be negligible; prioritize meaning, not score perfection.
- **E2E flaky only in CI:** investigate environment/resource/browser timing rather than adding blind retries.
- **No seam for a strong property:** a small refactor may expose pure logic; otherwise ordinary examples can be the honest choice.
