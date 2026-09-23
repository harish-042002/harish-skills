# Why Plat Exists

Plat targets a specific failure pattern in AI coding agents: **one-size-fits-all engineering behavior**.

A simple edit can trigger unnecessary repository reads, planning, architecture discussion, and tool calls. A difficult production problem can receive the opposite treatment: a shallow local patch that ignores concurrency, compatibility, distributed state, security, migration overlap, or runtime evidence.

Plat's product hypothesis is that an engineering agent should use the **minimum sufficient engineering depth** required for the current task, then prove the result.

## Pain → response

| Pain | What it costs | Plat response |
| --- | --- | --- |
| Easy tasks are overthought | extra context, tools, latency, and output | Quick/Standard routing keeps local work local |
| Hard tasks are underthought | wrong fixes, regressions, repeated repair | Deep escalation when risk/evidence earns it |
| Agents reread the repository broadly | token/time waste and repeated discovery | needle-first repository understanding |
| Agents reinvent mechanisms | duplicated caches/helpers/services and inconsistent architecture | reuse repository-local patterns before invention |
| User corrections do not change trajectory | stale assumptions survive into new code | stop/re-check/resume course correction |
| Every task receives the same generic expertise | irrelevant instructions consume context | lazy specialist routing by domain and depth |
| Agents say done without direct proof | plausible-looking but unverified changes | completion claims require fresh evidence |
| Deep reasoning creates verbose answers | output cost grows even when user only needs the result | engineering depth is separated from response depth |

## The mechanism

1. Interpret the requested outcome and constraints.
2. Inspect repository truth before choosing a solution.
3. Select one dominant task mode: Build, Debug, Review, Research, Design, Optimize, or Migrate.
4. Select the minimum sufficient depth: Quick, Standard, Deep, or Research.
5. Load only the relevant process/domain specialist guidance.
6. Execute in a bounded thin slice.
7. Verify the requested behavior with fresh evidence.
8. Persist only compact context that is expensive to rediscover.

## What makes Plat different

Plat is not primarily a coding template, spec framework, model router, or collection of prompts. It is a **routing and engineering-discipline layer** that tries to spend context and tools in proportion to task risk.

The USP is not 'more instructions'. It is:

> **Use the smallest engineering team and depth that can solve the real problem correctly, then prove it.**

## Why Plat does not copy every specialist

Dedicated skills can contain far more domain depth than Plat should keep in its own package/hot path. Copying them wholesale would increase context, duplicate maintenance, create licensing/update problems, and make simple tasks slower.

Instead, Plat keeps a compact built-in baseline and can **federate to installed specialist skills** for genuinely complex work. This is capability reuse, not a claim that Plat contains every other skill.

## What Plat does not claim

- It does not guarantee a fixed percentage reduction in tokens or cost.
- It does not guarantee higher correctness from instructions alone.
- It does not replace repository tests, profilers, security review, runtime telemetry, or human judgment.
- It does not force a formal specification for ordinary feature work.
- It does not make a preferred developer stack override the current repository.

Those outcomes must be validated through repeated comparable tasks with external verification. See BENCHMARKS.md and LIMITATIONS.md.