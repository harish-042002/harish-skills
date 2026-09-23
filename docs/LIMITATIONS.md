# Plat Limitations

Plat is an early-stage engineering skill. These limitations are intentionally public.

## Evidence

- There is not yet enough repeated live A/B evidence to claim that Plat universally improves correctness, cost, token usage, or wall time.
- The strongest efficiency result so far is a single manual full-stack comparison.
- The independent pilot was mixed and included one real correctness failure.

## Probabilistic behavior

Plat is instruction-based. It can increase the probability of disciplined behavior but cannot guarantee that every supported coding agent follows every rule perfectly.

## Host differences

Claude Code, Codex, Cursor, and other hosts differ in skill discovery, slash-command exposure, context behavior, tool telemetry, and filesystem conventions. Plat is vendor-neutral at the instruction layer, but installation/invocation details can vary.

## Community validation

Plat is new and does not yet have broad external adoption, contributor history, or community-scale validation. Stars and forks are not substitutes for benchmark evidence, but external usage feedback is still valuable and currently limited.

## Profiles and continuity

The developer profile is local preference context, not hidden authority. Cross-agent continuity only works when the agents can access the same Plat/repository state.

## Context overhead

Plat itself consumes context. Progressive loading is designed to keep ordinary task overhead small, but a routing error can still load unnecessary specialist guidance. This is why over-escalation is treated as a first-class failure mode.

## Update behavior

Plat does not perform a network update check on every coding request. Users receive updates through repository releases and update explicitly, avoiding hidden per-task tool/token overhead.

## Not a replacement for engineering evidence

Plat does not replace:

- tests;
- runtime logs/telemetry;
- profilers;
- database query plans;
- threat modeling/security review;
- deployment verification;
- browser/device inspection;
- human product judgment.

It is a control layer for deciding when and how to use those forms of evidence.

## Background update checks

The installer attempts to register one user-level daily scheduler (LaunchAgent on macOS, systemd user timer or cron on Linux, Scheduled Task on Windows). Locked-down environments may block scheduler registration. That failure does not break Plat; installation continues and reports the warning. The cached checker never runs inside an engineering prompt.


## Specialist federation

External skills and subagents can add domain depth, but they also add coordination cost and may contain stale, generic, or conflicting guidance.

Plat therefore cannot assume that an installed skill is correct merely because it is specialized. P-01 must validate specialist claims against current repository/runtime evidence and actual installed versions.

Multi-agent speedups depend on real independence. Parallelizing coupled work can increase tokens, duplicate discovery, and create conflicting mutations. The v1.6 orchestration policy limits fan-out, but live multi-agent A/B evidence is still pending.


## v1.7 evidence boundary

v1.7 now has strong deterministic and adversarial evidence for scope-fidelity controls and installed-specialist trust boundaries. The unchanged external red-team passes 12/12 and the independent scope-policy suite passes 24/24.

This still does **not** prove that Plat v1.7 improves real coding outcomes on average. Missing evidence includes:

- repeated fresh-session v1.7 vs no-Plat/prior-Plat execution;
- current trigger activation precision/recall across a realistic positive/negative prompt set;
- current token/tool-call/repair-turn/wall-time distributions;
- cross-host/model behavioral replication;
- task-level negative-delta analysis.

External-skill validation proves package shape, containment, and routing hygiene; it does not prove that a syntactically valid third-party skill is semantically correct, safe for every task, or better than Plat's built-in guidance.

Until those live lanes exist, the v1.7 industry score should be read as **architecture/governance/adversarial readiness**, not certification or a task-success percentage.


## v1.8 behavioral-evaluation boundary

v1.8 materially improves **evaluation infrastructure**: frozen current-version fixtures, multi-turn correction cases, executable verifiers, repeated/control-arm runner support, diff metrics, optional token/cost/tool telemetry, and a trigger corpus now live in the repository. This earns 8/18 on the published Behavioral Evaluation Maturity rubric.

It still does **not** provide new repeated live v1.8 coding-agent outcomes. The release therefore makes no claim that AWS depth or scope controls improve average correctness, cost, or speed until fresh Plat vs control trajectories are run and published.

The AWS deep reference is also not a substitute for current AWS documentation, Service Quotas, pricing, account configuration, or runtime evidence. Version/region/quota/pricing-sensitive claims must be checked against current authoritative sources when they affect a decision.
