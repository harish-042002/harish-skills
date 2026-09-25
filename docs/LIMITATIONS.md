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

The installer attempts to register one user-level two-hour scheduler (LaunchAgent on macOS, systemd user timer or cron on Linux, Scheduled Task on Windows). Locked-down environments may block scheduler registration. That failure does not break Plat; installation continues and reports the warning. The cached checker never runs inside an engineering prompt.


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


## v1.9 Research-economics evidence boundary

v1.9 adds explicit cost/time controls for broad Research and AFK report work, including lead-first orientation, matrix-driven peer comparison, explicit worker-tier selection, read deduplication, and focused failure attribution.

The motivating DAY1 session is a **single observed baseline**, not a controlled before/after experiment. The published 30% cost/cache/API-time reduction goals are rerun targets only.

Plat cannot guarantee a cheaper worker tier on hosts that do not expose per-subagent model selection. In those hosts, the skill raises the delegation bar instead.

Parallelism can reduce developer wall time while increasing aggregate model/API time. v1.9 therefore treats those as separate metrics and does not call a trajectory "faster and cheaper" unless both the user wait time and total compute economics support that claim.


## v2.3 cross-agent context boundary

v2.3 makes the context-control architecture portable, but coding-agent hosts expose different levels of observability.

- The proxy guard (returned bytes, large outputs, total/repeated reads, broad-suite runs) is the common baseline.
- Real token/cache/context telemetry is opportunistic. It is used only when the host, wrapper, hook, or transcript exposes compatible data.
- Lifecycle hooks such as PreCompact are optional accelerators; unsupported hosts still checkpoint from the normal RED-context path.
- Transcript JSONL normalization is best-effort because host schemas can evolve. It must never be treated as stronger authority than the host's own usage UI/API.
- Dynamic host capability inputs can enable isolated-context behavior, but Plat cannot create a host feature that the coding agent itself does not support.

The 65/80% context and 8M/20M task-local cache-read thresholds are starting benchmark values, not provider guarantees. They may need tuning after matched runs across Codex, Claude Code, Cursor, Kiro, Cline, OpenCode, and other hosts.


## v2.4.0-rc.1 audit candidate (not a released performance claim)

This candidate replaces the v2.3 recovery interpretation above: cumulative cache replay, file-read counts and byte totals are not context occupancy and cannot independently trigger RED recovery. Missing or stale current occupancy remains unknown. The optional wrappers are not universal host interception. Command timeouts apply only to commands routed through the wrapper.

The candidate has Linux Python runtime tests, not repeated live coding-model experiments or native Windows/macOS host verification. Older benchmark assets are absent from the downloaded CI validation snapshot; its behavioral test class cannot run in that snapshot. Full upstream repository validation must still run before a release.

A smaller entrypoint is a measured byte reduction, not proof of an equal token, cost or latency reduction. No exact duration or savings for the user's two-to-three-hour Luna runs has been established.
