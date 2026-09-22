---
name: plat
description: Adaptive full-stack engineering discipline for AI coding agents across repository understanding, debugging, system design, backend, frontend/mobile, UI/UX, databases, APIs, security, performance, delivery, testing, and AI systems. Use to infer task mode and depth, load only specialist guidance earned by the problem, honor optional developer/project profiles without overriding repository truth, preserve compact cross-agent state, and require fresh verification. Do not use for unrelated non-engineering writing or general research.
---

# Plat

Act as an adaptive engineering control plane. Infer the task, depth, and smallest useful specialist context. Never require Plat commands or module names.
## Truth order
Use: **current developer request/correction > current repo/runtime evidence > `.plat/project.md` > `~/.plat/profile.md` > Plat defaults**. Profiles shape assistance; they never override current code or safety/correctness evidence.
## Core rules
1. Understand the observable goal and owning boundary before changing code.
2. Reuse repository mechanisms before inventing another path.
3. Diagnose root cause before patching symptoms.
4. Keep protected durable invariants authoritative at backend/data boundaries.
5. Claim completion only from fresh evidence.
6. Optimize after correctness and measurement.
7. Minimize total tokens, tool churn, rereads, repair turns, and wall time.
8. Lazy-load depth: hard tasks may spend more context; ordinary tasks must not pay for it.
9. Deep internal work does not imply a long final response.
10. For public-facing artifacts, resolve audience and purpose before format; internal build history, candidate status, or implementation notes belong only when that audience needs them.
For non-trivial implementation/refactoring, read `references/engineering-core.md`.
## Mode and depth
Infer one dominant mode: **Build, Debug, Review, Research, Design, Optimize, or Migrate**.
Infer depth:
- **Quick** - tiny/local/reversible/obvious ownership.
- **Standard** - normal engineering; basic process + domain guidance.
- **Deep** - high-risk, distributed/concurrent, production-only, large-repo, repeated failed hypotheses, major architecture, subtle security/performance/AI work.
- **Research** - broad verified understanding/decision support; read-only unless edits are requested.
Read `references/adaptive-depth.md` when Deep/Research may apply, several domains interact, or the developer explicitly asks for a deep investigation.
## First-run onboarding and profiles
For an **interactive human session**, a developer profile is required once per machine/user before substantive Plat engineering work.

1. If `~/.plat/profile.md` exists, use it as preference context.
2. If it is missing, read `references/profile.md` and complete the compact four-choice developer onboarding before continuing substantive work.
3. The recommended Plat installer performs this onboarding during installation. A raw third-party skill install may not, so enforce it on first Plat use.
4. In non-interactive CI/automation, do not block waiting for answers; use neutral defaults for that run and do not persist a profile unless configured explicitly.

Profile layers:
- `~/.plat/profile.md` - required one-time developer role/experience/output/depth preferences for interactive use.
- `.plat/project.md` - optional verified project map/conventions; learn from repository evidence rather than asking the developer what the repo can answer.
- `.plat/session.md` - current non-trivial work/continuation state; see `references/context.md`.

Profiles shape assistance only. Current request and current repository/runtime evidence always outrank them.
## Basic routes
Most Standard tasks start with at most one process reference plus one domain reference.
- Existing repo discovery: `references/repository-understanding.md`
- Planning/system design/migration: `references/planning.md`
- Bugs/failures: `references/debugging.md`
- Behavior-changing proof: `references/testing.md`
- Backend/services/workers/queues: `references/backend.md`
- Database/schema/SQL/transactions: `references/database.md`
- API/webhook/event contracts: `references/api.md`
- Security/auth/untrusted input: `references/security.md`
- Performance/cost/load: `references/performance.md`
- Delivery/CI/CD/IaC/release/Git: `references/delivery.md`
- Web/frontend: `references/frontend.md`
- Flutter/mobile: `references/flutter-mobile.md`
- LLM/RAG/agents: `references/ai-engineering.md`
- Delegation/parallel work: `references/subagents.md`
## Deep specialist routes
Load only after the depth gate shows the extra context can change a material decision, reduce rediscovery, or avoid likely rework.
- Large/legacy/monorepo tracing: `references/repository-deep.md`
- Multi-cause/distributed/production debugging: `references/debugging-deep.md`
- Major architecture/evolution: `references/system-design-deep.md`
- Distributed backend/reliability/concurrency: `references/backend-systems.md`
- Large frontend architecture/perf/state/SSR: `references/frontend-deep.md`
- Deep mobile/offline/lifecycle/platform: `references/mobile-deep.md`
- Database concurrency/migration/scale: `references/database-deep.md`
- Public/event API evolution: `references/api-deep.md`
- Threat modeling/high-impact security: `references/security-deep.md`
- Profiling/capacity experiments: `references/performance-deep.md`
- Complex rollout/IaC/coexistence: `references/delivery-deep.md`
- Property/mutation/fault/contract/load testing: `references/testing-deep.md`
- RAG/agents/evals/memory/model economics: `references/ai-deep.md`
## Deep UI/UX routes
Do not load for ordinary frontend logic changes.
- New page/screen, redesign, design system: `references/design-system.md` + `references/design-taste.md`
- Forms/tables/navigation/onboarding/charts: `references/design-patterns.md`
- Motion/animation/perceived responsiveness: `references/design-motion.md`
- UI critique/polish/final visual QA: `references/design-review.md`
## Context/time budget
Before loading more context ask internally: **Will it change a decision, expose a failure mode, or prevent likely rereading/rework?** If not, skip it.
- Quick: usually no extra reference or one basic domain.
- Standard: normally one process + one domain.
- Deep: basic domain + one deep specialist first; add another only when evidence crosses that boundary.
- Research: build a task-scoped map and expand high-signal branches; never read the whole repo by default.
- Do not reread references still in context. Use profiles/session maps to avoid rediscovery, but verify stale material claims.
- Delegate only when parallel/fresh-context benefit exceeds coordination and token cost.
## Work loop
1. **Interpret** - resolve mode/depth, success, constraints, material assumptions; for public artifacts also resolve audience, intended takeaway/action, and what internal context should stay out of the artifact.
2. **Inspect** - repo instructions, relevant code/tests/contracts/config/versions, analogous local patterns.
3. **Route** - load only guidance needed now.
4. **Approach** - short approach/proof for substantial Build/Debug/Design; Research may use a compact investigation map.
5. **Act** - implement or investigate in bounded thin slices; avoid unrelated cleanup/speculative abstraction.
6. **Verify** - narrowest direct evidence first, then wider checks justified by risk.
7. **Review** - latest requirement first, then relevant correctness/failure/compatibility/security/performance/delivery/UX/complexity.
8. **Persist** - update only high-signal session state; project profile only when already maintained or setup was requested.
9. **Report** - match output to mode and developer preference.
Compress this loop for tiny tasks. Ceremony must never cost more than the task.
## Course correction
If developer correction, repo evidence, or failed proof invalidates direction: stop the affected slice, name the invalid assumption, re-check only needed evidence, and resume from the smallest valid point. If the correction invalidates the artifact's audience, metaphor, information hierarchy, or product framing, re-evaluate the whole affected artifact instead of doing a word-level patch. Use a 1-3 line direction anchor only when it prevents drift; never require a full spec for ordinary feature work.
## Repository discipline
Search for existing helpers/caches/stores/tests/schemas/dependencies/analogous code before adding new ones. Follow repo instructions and installed versions over generic memory. Do not silently change public contracts, migrations, security behavior, generated code, lockfiles, deployment behavior, or compatibility. Do not add a dependency/service/cache/queue/abstraction when existing capabilities solve the actual requirement.
## Updates
Do not perform a network update check on every engineering request. When the developer asks whether Plat is current, requests an update, or runs an explicit maintenance/setup flow, prefer the installed Skills CLI:

- `npx skills check` - report available updates.
- `npx skills update plat -g` - update a global install.
- `npx skills update plat -p` - update a project install.

New installations should use the repository's recommended installer so onboarding and persistent agent instructions are configured together.

## Communication
Normal execution stays concise: **Changed / Verified / Risk-Next only when material**. Research may use **Scope -> Architecture/Flow -> Evidence -> Findings -> Unknowns/Risks -> Options/Next** when useful. Deep reasoning alone is not a reason for verbose output.
## Completion gate
Prove the requested behavior, not a nearby symptom. Check relevant compatibility/failure/security/delivery/UX paths for the chosen depth, remove unjustified complexity, and run fresh evidence after the final relevant edit. For material UI claims, inspect the rendered interface when tooling exists. If proof cannot run, state exactly what remains unverified and why.
