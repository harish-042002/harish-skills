# Plat v1.7 Industry Benchmark Report

Date: 2026-09-23

Baseline: v1.6.0 (`b57dc1a051a8dc067459b9c232f6ca0befdb2ece`)  
Candidate: v1.7.0 PR #2 CI snapshot (`a5715a123875d3ae11c4c925ba07d1042ee22460`)

## Executive result

Plat v1.7 materially closes the two concrete weaknesses targeted by this release: **scope deviation after bounded requests/corrections** and **external specialist trust/conformance**.

The unchanged 100-point industry rubric moves from **64.5/100 to 75.5/100**.

The remaining score gap is dominated by evidence that has deliberately **not** been claimed: current v1.7 still lacks a repeated live coding-agent A/B benchmark, so Behavioral Evaluation remains **1/18**.

## Before / after

| Independent lane | v1.6 | v1.7 | Change |
| --- | ---: | ---: | ---: |
| External-skill red-team | 4/12 | **12/12** | +8 cases |
| Scope-fidelity/correction suite | 8/24 | **24/24** | +16 cases |
| General industry scenario coverage | 24/26 | **26/26** | +2 cases |
| Static industry rubric | 64.5/100 | **75.5/100** | +11.0 |

## 100-point rubric

| Dimension | v1.6 | v1.7 | Max |
| --- | ---: | ---: | ---: |
| Open standard | 12 | **12** | 12 |
| Triggering & scope | 9 | **9** | 14 |
| Progressive disclosure | 13 | **13** | 14 |
| Workflow & verification | 14 | **14** | 14 |
| Security & trust | 7 | **18** | 18 |
| Behavioral evaluation | 1 | **1** | 18 |
| Portability | 4.5 | **4.5** | 6 |
| Maintenance | 4 | **4** | 4 |
| **Total** | **64.5** | **75.5** | **100** |

If the missing live-behavior evidence plane is excluded rather than treated as a failure, v1.7 scores **74.5/82 = 90.9%** across architecture, scope controls, progressive disclosure, workflow, specialist trust, portability, and maintenance. This is an architecture/governance percentage, **not a live task success rate**.

## Real failure addressed

The motivating failure was not that Plat lacked technical sophistication. It over-interpreted a bounded notification request and added product machinery—confidence tiers, response stages, additional learning signals, trace fields, and adjacent selector behavior—that the developer had not asked for.

v1.7 changes the execution contract before editing starts:

- bind **MUST / MUST NOT / PRESERVE / PROOF** when scope can drift;
- treat **only / alone / just / no / no need / do not / don't / keep / work on these** as binding constraints;
- do not infer modes, stages, learning signals, telemetry, persistence, abstractions, or adjacent refactors merely because they seem useful;
- stop on unexplained cross-subsystem diff expansion;
- require causal necessity for every adjacent change;
- when the developer corrects the model, purge task-local machinery that existed only because of the rejected assumption.

The repo regression corpus now includes the concrete variants/state/confidence failure pattern, but those regressions were **not counted** in the independent benchmark score.

## External specialist hardening

The unchanged external red-team moves from 4/12 to 12/12.

v1.7 now:

- parses valid YAML variants including folded-strip and multiline quoted descriptions;
- validates Agent Skills-compatible metadata before ranking;
- rejects invalid names, name/directory mismatch, and oversized descriptions;
- rejects a `SKILL.md` file symlink/path escape outside its skill root;
- keeps legitimate package-directory symlink compatibility;
- suppresses raw untrusted descriptions from discovery output;
- penalizes broad keyword-stuffed orchestrators so focused specialists win;
- treats installed skills as untrusted instruction-bearing packages;
- prevents specialist instructions from widening parent scope, bypassing proof, recursively installing skills, or exposing secrets;
- requires license/provenance review before literal external text/code reuse.

## General scenario coverage

The previous external scenario suite improves from 24/26 to 26/26. The two former gaps were:

1. runtime license/provenance boundaries for external skill reuse;
2. explicit Agent Skills-compatible frontmatter validation before federation.

Both are now represented in the v1.7 contract and implementation.

## Release validation

GitHub PR CI at the evaluated candidate commit passed:

- Maintenance evidence gate: PASS
- Structural validation: PASS
- Hot path: **6,966 chars / 119 lines**
- Routing corpus: **30 cases**
- Version: **1.7.0**
- Python unit tests: **36/36 PASS**
- Python compile check: PASS
- Installer shell syntax: PASS
- Validation snapshot packaging: PASS

Again, these are release-safety checks, not benchmark points.

## What v1.7 still does not prove

The largest remaining industry gap is **live behavioral evidence**. v1.7 should not claim universal correctness, speed, or cost improvement until it has:

1. frozen real coding tasks;
2. fresh isolated sessions per arm;
3. v1.7 vs no-Plat and/or prior-Plat comparisons;
4. multiple repetitions;
5. independent task verifiers;
6. trigger activation positive/negative trials;
7. tokens/tool calls/rereads/repair turns/wall time;
8. negative-delta reporting by task class;
9. ideally more than one supported coding-agent host/model.

That is why Behavioral Evaluation remains 1/18 even though deterministic and adversarial validation is strong.

## Conclusion

v1.7 is a substantial improvement over v1.6 for the failure that was actually observed.

The key architectural shift is **not more engineering ceremony**. It is stronger obedience to the developer's requested boundary:

> deeper engineering is allowed when risk requires it; broader product scope is not.

For external specialists, the equivalent rule is:

> discover narrowly, validate before trust, load only the selected specialist, and never let specialist instructions redefine the parent task.

The release is ready from a structural/adversarial/CI perspective. The next benchmark milestone should be live repeated A/B execution rather than another expansion of deterministic tests.
