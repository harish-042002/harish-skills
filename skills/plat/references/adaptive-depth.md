# Adaptive Task Mode and Depth

Use when a task may deserve deep specialist reasoning, crosses several domains, involves a large codebase, or is broad Research. This file controls **how much Plat should load**, not how much prose it should produce.

## Contents

1. Goal
2. Mode selection
3. Depth selection
4. Escalation triggers
5. De-escalation triggers
6. Specialist routing
7. Cross-domain combinations
8. Context ROI
9. Research mode
10. Response depth
11. Edge cases

## Goal

Spend specialist context only where it is likely to reduce mistakes, rediscovery, tool churn, or repair turns. Deep mode is an investment, not a status symbol.

A task can be cognitively deep but produce a concise final answer. A broad research request can produce a long structured answer without triggering implementation workflows.

## Mode selection

Choose the dominant mode from the requested outcome:

- **Build** - the primary artifact is changed behavior/code.
- **Debug** - the primary artifact is an explained and corrected failure.
- **Review** - the primary artifact is findings on existing work.
- **Research** - the primary artifact is verified understanding/decision support.
- **Design** - the primary artifact is a user-facing interaction/visual/product-flow change.
- **Optimize** - the primary artifact is a measured improvement.
- **Migrate** - the primary artifact is a safe transition between contracts/data/runtime states.

Mixed requests can have one dominant mode plus supporting concerns. Do not run separate full workflows for every label.

## Depth selection

### Quick

Use when all are true enough:

- ownership is obvious;
- scope is local;
- behavior is simple and reversible;
- risk is low;
- repository conventions are already clear;
- direct verification is cheap.

Examples: rename, copy change, isolated CSS correction, straightforward config edit, single obvious null guard with existing test pattern.

### Standard

Default for normal product engineering. Use basic process + domain guidance and targeted repository inspection.

### Deep

Escalate when one or more material triggers exist:

- production-only/intermittent failure;
- concurrency, ordering, distributed state, retries, idempotency, or partial failure;
- public contract/data migration with coexistence risk;
- authentication, authorization, money, tenant isolation, destructive action, sensitive data, code execution;
- major architecture boundary or service decomposition;
- large/legacy/monorepo path where ownership is not obvious;
- repeated failed hypotheses/fixes;
- performance/capacity problem that needs profiling or load evidence;
- AI behavior with evaluation/retrieval/tool/memory complexity;
- mobile lifecycle/offline/platform behavior that cannot be proven in a local widget/unit test;
- user explicitly asks for a deep investigation and the task actually has depth to explore.

### Research

Use for broad codebase/subsystem understanding, architecture archaeology, comparison, audit planning, or a request whose main goal is knowledge rather than edits.

Research is not automatically Deep implementation. Keep the workspace read-only unless the user also asks to change something.

## Escalation triggers

Escalate from Standard only when the extra specialist context can answer a concrete question such as:

- Which boundary actually owns the invariant?
- Why does this fail only under concurrency/load/deployment overlap?
- Which of several plausible hypotheses best matches evidence?
- What is the blast radius through callers/contracts/data?
- What migration sequence keeps old/new versions compatible?
- Which part of an AI pipeline is failing: retrieval, generation, routing, tool use, memory, or evaluation?
- Which performance resource dominates the measured symptom?
- Which testing technique can expose a fault ordinary examples cannot?

If no concrete question exists, remain Standard.

## De-escalation triggers

Return to Standard/Quick when:

- evidence localizes the problem to one simple boundary;
- the supposedly distributed issue is a deterministic local bug;
- a deep reference has already answered the needed decision and no second specialist adds value;
- the user requests a small scoped change and no high-risk constraint requires extra work;
- further investigation would only produce completeness, not a different decision.

Do not stay Deep because the task started Deep.

## Specialist routing

Load the **basic domain reference first** when it is small enough to orient the work, then one deep specialist that addresses the actual hard part.

- Repository scale/unknown architecture -> `repository-deep.md`
- Complex production debugging -> `debugging-deep.md`
- Major architecture/evolution -> `system-design-deep.md`
- Distributed backend -> `backend-systems.md`
- Frontend architecture/performance/state -> `frontend-deep.md`
- Mobile lifecycle/offline/platform -> `mobile-deep.md`
- Database concurrency/migrations/scale -> `database-deep.md`
- API/event/public contract evolution -> `api-deep.md`
- Security/threat/abuse review -> `security-deep.md`
- Profiling/capacity -> `performance-deep.md`
- Complex delivery/rollout/IaC -> `delivery-deep.md`
- Advanced verification -> `testing-deep.md`
- RAG/agent/eval/memory economics -> `ai-deep.md`

Design has its own deep stack in the root router.

## Cross-domain combinations

Load the smallest useful pair, not the whole neighborhood.

### Production duplicate writes

`debugging.md` + `backend.md` -> if evidence shows race/retry semantics, add `backend-systems.md`; add `database-deep.md` only if the invariant depends on DB concurrency/constraints.

### Large legacy feature change

`repository-understanding.md` + domain basic -> add `repository-deep.md` to build a subsystem map; add a domain deep file only after ownership is localized.

### AI latency/cost regression

`ai-engineering.md` + `performance.md` -> add `ai-deep.md` if routing/retrieval/model loops are the issue; add `performance-deep.md` if representative profiling/capacity work is required.

### Authentication migration

`security.md` + `planning.md` -> add `security-deep.md`; add `api-deep.md` or `delivery-deep.md` only for contract/rollout coexistence concerns.

## Context ROI

Treat every extra file/tool call as an investment.

Load more context only if it is likely to:

- eliminate a plausible wrong path;
- avoid rereading many repository files;
- expose a hidden failure mode;
- resolve a high-impact tradeoff;
- produce stronger verification;
- shorten the critical path through safe parallel discovery.

Avoid:

- loading all deep modules for completeness;
- rereading already available references;
- broad repository dumps;
- asking subagents to rediscover the same scope;
- generating long plans that restate the request;
- copying source files into session/project profiles.

## Research mode

Research should progressively widen evidence instead of starting exhaustive.

1. **Orient** - repository instructions, project profile if present, manifests, top-level architecture/docs.
2. **Locate** - named behavior, routes, entry points, symbols, tests, configs.
3. **Trace** - relevant call/data/event path and ownership boundaries.
4. **Validate** - compare docs/profile assumptions against current code/tests/config/history where material.
5. **Expand** - only into unresolved/high-impact branches.
6. **Synthesize** - produce a structured map with evidence and explicit unknowns.

A useful Research output may be longer than normal execution output, but do not turn uncertain inference into fact.

## Response depth

Developer profile may request concise or explanatory output. Respect it unless the current request explicitly asks otherwise.

- Quick/Standard execution: concise changed/verified/risk summary.
- Deep execution: still concise by default; include root cause/tradeoff evidence when material.
- Research: structured and sufficiently detailed to preserve the map/findings.
- Review: prioritized findings with evidence, not a long tutorial.

## Edge cases

- **User says "quick" on a high-risk task:** keep communication concise, but do not skip correctness/security verification needed to avoid harm.
- **User says "deep" on a trivial task:** explain or inspect more if useful, but do not manufacture architecture complexity.
- **Large repo but tiny known file change:** stay Standard if ownership and proof are already clear.
- **Small repo but distributed production incident:** Deep can still be required; repository size is not risk.
- **Profile says backend expert but task is frontend:** use the profile only for explanation level, not to avoid the frontend specialist.
- **Several deep domains appear relevant:** localize first. Add the second specialist only after evidence crosses that boundary.
