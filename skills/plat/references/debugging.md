# Debugging

Use for bugs, exceptions, incorrect/flaky behavior, regressions, failed builds/integrations, production incidents, or "I don't know what's wrong" requests.

## Law

No fix before enough root-cause evidence exists to explain the failure. A plausible suspicious line is not evidence.

## Compact approach

For a non-trivial bug, before editing state only the useful approach: observed symptom, evidence/hypothesis to test, and the proof that will confirm the fix. Keep it to 2-4 bullets; do not narrate every diagnostic step.

After the fix, report **Root cause -> Fix -> Verified evidence**.

## Workflow

1. Capture observed vs expected behavior.
2. Reproduce with the smallest reliable case when possible. For legacy behavior without coverage, first add a characterization test/reproducer that records the current observable behavior before refactoring around it.
3. Preserve exact error/stack/input/timing/environment/log evidence that matters.
4. Trace backward to the first point where state or behavior becomes wrong.
5. Compare working vs failing paths/environments when available.
6. Form one falsifiable hypothesis at a time.
7. Test the hypothesis with the smallest discriminating check/change. Do not change multiple causal variables in one experiment.
8. Identify root cause and blast radius.
9. Create/strengthen a regression test or durable reproducer when practical.
10. Implement one root-cause fix; avoid bundled cleanup.
11. Re-run the reproducer, targeted tests, and broader checks justified by blast radius.

## Localization prompts

- Was the value produced, persisted, transported, cached, transformed, or rendered incorrectly?
- Is failure deterministic, timing/load/data/environment dependent?
- Did dependency/config/schema/API/deployment behavior change?
- Could retry, duplication, race, stale read, timezone, serialization, expiry, or boundary behavior explain it?
- Is the visible symptom downstream from the actual fault?

## Flaky and timing failures

Do not fix a flaky test by adding arbitrary sleeps or retries unless the product contract itself is eventual. Capture repetition rate, timing/order/concurrency evidence, clocks/timeouts, shared state, and environment differences. Make the test wait for the real condition or fix the race.

## Failed-fix discipline

A failed hypothesis or developer correction is new evidence, not permission to stack another patch on top.

- If new evidence disproves the current explanation, explicitly retire that hypothesis before forming the next one.
- After **2 materially different failed fixes**, stop patching and rebuild the evidence/hypothesis map.
- After **3 evidence-backed fix attempts** fail or each exposes new coupling/shared-state failures, question whether the architecture/boundary itself is wrong before attempting another fix.
- Change one causal variable at a time when diagnosing.

## Production debugging

If service restoration needs an urgent mitigation, label it **mitigation**, keep blast radius small/reversible, preserve evidence, and continue root-cause work. Do not rebrand a temporary guard, feature disable, restart, or retry increase as the root fix.

Prefer existing telemetry: structured logs, traces, metrics, request/job IDs, queue metadata, DB state, deployment/config history, and error monitoring. Correlate evidence by request/entity/time. Add temporary instrumentation only where it can discriminate between hypotheses; avoid permanent noisy logs.

Never expose secrets or sensitive payloads while debugging.

## Completion

The bug is fixed only when the intended behavior is freshly reproduced as correct and meaningful regression evidence passes. Exception disappearance alone is insufficient.
