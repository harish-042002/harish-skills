# Plat Benchmarks

Plat keeps positive results, mixed results, and failures in the same record. The current evidence is useful but not yet sufficient to claim a universal correctness or efficiency advantage.

## 1. Real full-stack build signal

Same broad task, fresh Claude Code Sonnet 5 sessions.

| Metric | No Plat | Plat | Difference |
| --- | ---: | ---: | ---: |
| Input tokens | 210 | 106 | -49.5% |
| Output tokens | ~1.7k | 464 | -72.7% |
| Cache read | 12.2M | 5.7M | -53.3% |
| Cache write | 97.9k | 74.9k | -23.5% |
| Cost | $3.22 | $1.72 | -46.6% |
| API time | 7 min | 5 min | -28.6% |
| Wall time | 9 min | 6 min | -33.3% |

Both implementations completed the direct CRUD flow. The no-Plat result had a slight initial micro-copy/visual-polish edge. This is a **single manual run**, so it is a signal, not a general claim.

## 2. Independent v0.6 pilot

10 cases × 2 conditions × 1 repetition = **20 real Claude Code Sonnet 5 trajectories**.

| Scenario | Plat | No Plat | Plat token delta | Plat cost delta | Plat time delta |
| --- | --- | --- | ---: | ---: | ---: |
| Bug root-cause | PASS | PASS | -180 | -$0.0325 | -2.7s |
| Existing-repo feature | PASS | PASS | -540 | -$0.0433 | -6.4s |
| Backend idempotency | PASS | PASS | +689 | +$0.0516 | +15.6s |
| Frontend states | PASS | PASS | -67 | -$0.0012 | -0.5s |
| Tiny edit | PASS | PASS | +8 | +$0.0001 | -1.5s |
| Performance reasoning | PASS | PASS | +11 | -$0.0122 | +2.3s |
| Verify-before-claim | PASS | PASS | +7 | +$0.0002 | -0.3s |
| Course correction | FAIL | PASS | -986 | -$0.0618 | -20.6s |
| Negative control | PASS | PASS | -25 | -$0.0003 | -0.5s |
| Lightweight feature | PASS | PASS | +88 | +$0.0019 | +2.5s |

Reliable deterministic assertions:

- No Plat: 10/10
- Plat: 9/10

Aggregate signals:

| Metric | Plat vs No Plat |
| --- | ---: |
| Mean tokens | -10.1% |
| Median tokens | +33.5% |
| Mean cost | -6.8% |
| Median cost | +7.3% |
| Mean time | -8.1% |
| Median time | +27.6% |

The mean/median disagreement was driven by outliers. The pilot did **not** demonstrate a correctness advantage.

### Course-correction failure

The repository required an existing shared cache abstraction. The Plat run added a process-local module cache, while the control found and reused the repository's SharedCache. That failure directly motivated stronger repository-truth and course-correction controls.

## 3. Structural release gate

The adaptive architecture has also been tested statically:

- 305/305 deterministic architecture/behavior checks;
- 38/38 semantic-control mutations killed;
- 65 adaptive edge-case scenarios.

Static gates prove routing/structure coverage only. They do not prove a live coding-agent advantage.

## Benchmark limitations

- The independent pilot used one repetition per arm.
- Tool-call telemetry was incomplete in the harness, so external verification is preferred.
- The manual full-stack run was not independently replicated.
- Current live evidence predates some later Plat routing/onboarding changes.
- Community-scale usage evidence does not exist yet.

## Next benchmark protocol

Future claims should use frozen comparable runs with:

1. same repository state;
2. same exact task;
3. same model/settings/permissions;
4. fresh session per arm;
5. repeated runs;
6. external verifier after each trajectory;
7. correctness as the primary endpoint;
8. tokens, cache, cost, wall time, turns, changed files, and repair work as secondary endpoints.

Priority cases:

- tiny known-file edit;
- greenfield full-stack build;
- existing-repo feature;
- production/intermittent bug;
- large-codebase research;
- frontend redesign;
- RAG/agent regression;
- live-compatible API/database migration;
- public-facing artifact from a reference;
- mid-course user correction that invalidates the current framing.