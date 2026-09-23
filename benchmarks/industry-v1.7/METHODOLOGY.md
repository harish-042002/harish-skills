# Plat v1.7 Industry Benchmark Methodology

Date: 2026-09-23

## Objective

Evaluate whether Plat v1.7 materially improves the two failure classes observed before this release:

1. developer-intent deviation / over-engineering after a bounded request or correction;
2. unsafe or non-conformant federation of installed external skills.

This benchmark is separate from Plat's normal regression tests. Repository tests are reported as release validation only and do not earn benchmark points.

## Compared versions

- Baseline: Plat v1.6.0, frozen main snapshot at `b57dc1a051a8dc067459b9c232f6ca0befdb2ece`.
- Candidate: Plat v1.7.0, GitHub CI snapshot from PR #2 at `a5715a123875d3ae11c4c925ba07d1042ee22460`.

Both were evaluated as frozen snapshots.

## Evidence lanes

### 1. Unchanged external-skill red-team

The same 12 cases used in the earlier industry audit were rerun unchanged against v1.7.

Coverage includes:

- valid folded-strip YAML;
- multiline quoted YAML;
- `SKILL.md` symlink/root escape;
- invalid skill names;
- directory/name mismatch;
- oversized descriptions;
- broad metadata keyword stuffing;
- prompt-injection-like metadata exposure;
- metadata-first performance with large skill bodies;
- deterministic ranking;
- malformed frontmatter fail-closed behavior.

Because the cases predate v1.7, this is the strongest before/after lane in this report.

### 2. Scope-fidelity / correction benchmark

A separate 24-case policy suite was created from the **failure class**, not copied from Plat's routing regression corpus. It was then run unchanged against both frozen v1.6 and v1.7 instruction corpora.

It checks whether the skill contract covers:

- hard negative constraints such as only / alone / no / do not;
- pre-mutation scope locking;
- rejection of invented product semantics;
- bounded catalogue/copy changes;
- diff-expansion circuit breaking;
- causal necessity for adjacent edits;
- correction purge;
- no hidden fallback after a rejected assumption;
- correction precedence over older plans/profile/session context;
- specialist scope containment;
- external-skill trust, metadata validation, path confinement, licensing, and recursive installation boundaries;
- exact requested-behavior proof;
- separation of while-here cleanup;
- local-task fast-path behavior.

This is a **policy/architecture benchmark**, not a live coding-agent success-rate measurement.

### 3. General industry scenario coverage

The previous 26-case external scenario-coverage suite was rerun unchanged. It spans high-risk routing, evidence arbitration, version-sensitive research, visual/performance proof, migration, DB/mobile/RAG boundaries, correction handling, session/profile state, shared mutations, recursive delegation, license checks, and installed-skill standard validation.

### 4. Static industry rubric

The same 100-point rubric from the prior benchmark was reused:

| Dimension | Points |
| --- | ---: |
| Open Agent Skills conformance | 12 |
| Triggering & scope | 14 |
| Progressive disclosure | 14 |
| Workflow & verification | 14 |
| Security & external-skill trust | 18 |
| Behavioral evaluation maturity | 18 |
| Portability | 6 |
| Maintenance governance | 4 |

The rubric intentionally gives **17 of 18 behavioral-evaluation points no credit** because v1.7 still lacks a repeated clean-context live A/B benchmark against no-Plat/prior-Plat on real coding tasks.

## Release validation kept separate

PR CI validates syntax, deterministic logic and packaging health, but these results do not change the industry benchmark score:

- maintenance evidence gate;
- structural Plat validation;
- full unit test suite;
- Python compilation;
- installer shell syntax;
- validation snapshot packaging.

## Interpretation boundary

Do not interpret policy coverage (24/24 or 26/26) as a 100% live success rate. It means the required control is present in the evaluated skill contract.

Do not call v1.7 industry-certified until repeated live trajectories demonstrate behavioral lift, trigger accuracy, cost/time effects, and failure rates on current v1.7.
