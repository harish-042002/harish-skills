---
name: plat
description: Engineering control layer for AI coding agents that prevents one-size-fits-all reasoning. Use for software engineering work where the agent should reconstruct active intent from current conversation and repository evidence, choose the minimum sufficient depth, load only relevant specialist guidance, reuse local mechanisms, course-correct when evidence changes, and verify behavior before claiming completion. Covers repository work, debugging, system design, backend, frontend/mobile, UI/UX, databases, APIs, security, performance, delivery, testing, and AI/RAG. Do not use for unrelated non-engineering work.
---

# Plat

Use the **smallest engineering path that can solve the real problem correctly**. Prevent both over-engineering simple work and under-engineering risky work.

## Active truth

Use this order:

**latest developer request/correction > unresolved current task > current repo/runtime evidence > fresh session state > optional project cache > developer profile > Plat defaults**

For vague, referential, corrective, or continuation messages, read `references/routing.md`. Do not guess, and do not reflexively ask. Reconstruct active intent from evidence first.

## Fast gate

Before loading more guidance, answer internally:

1. What exact outcome is active?
2. What is explicitly **in scope / out of scope**?
3. What owns it, at minimum sufficient depth?
4. What direct proof will show it worked?

Treat **only, alone, just, no/no need, do not/don't, keep X, work on these** as hard scope constraints. Never turn a requested copy/catalogue/field change into new modes, stages, learning signals, telemetry, abstractions, dependencies, or adjacent refactors unless current repo correctness requires them. If the diff starts crossing extra subsystems, stop and re-localize before editing further.

If scope is tiny/local/reversible and ownership is clear, use **target -> act -> direct proof**.

## Depth

- **Quick** - tiny/local/reversible/obvious ownership.
- **Standard** - normal engineering; usually one primary reference.
- **Deep** - material concurrency/distributed state, production-only failure, security, money/tenant isolation, public migration, major architecture, hard performance/AI/mobile lifecycle, or repeated failed hypotheses.
- **Research** - broad verified understanding/decision support; read-only unless edits are requested.

A request for a detailed/deep answer changes output detail, not engineering depth. Read `references/adaptive-depth.md` only when depth is genuinely uncertain, several domains interact, or Deep/Research may be earned.

## Core rules

1. Understand the observable outcome and current owning boundary before changing code.
2. Inspect repository truth before inventing a helper, service, cache, queue, abstraction, contract, or dependency.
3. Diagnose root cause before patching symptoms.
4. Keep durable protected invariants authoritative at backend/data boundaries.
5. After correctness and required safety/compatibility, minimize **total tokens, tool calls, rereads, repair turns, coordination, and wall time**.
6. Stop discovery once ownership, approach, and direct proof are clear.
7. Claim completion only from **fresh evidence after the final relevant edit**.
8. Deep internal work does not require a long final response.

For non-trivial implementation/refactoring, read `references/engineering-core.md`. For routing/efficiency audits, read `references/agent-failure-modes.md`.

## Primary routes

Load one primary reference first; add another only when evidence crosses a real boundary.

- Existing repo -> `repository-understanding.md`
- Planning/migration -> `planning.md`
- Debugging -> `debugging.md`
- Testing/proof -> `testing.md`
- Backend -> `backend.md`
- Database -> `database.md`
- API/events -> `api.md`
- Security -> `security.md`
- Performance -> `performance.md`
- Delivery -> `delivery.md`
- Frontend -> `frontend.md`
- Flutter/mobile -> `flutter-mobile.md`
- AI/RAG/agents -> `ai-engineering.md`
- Delegation -> `subagents.md`
- Efficiency -> `efficiency.md`

Deep specialist mapping lives in `references/adaptive-depth.md`. Load one deep specialist first; a second requires evidence that the task truly crosses that boundary.

## External specialist bench

For Deep/Research work, or when a concrete specialty exceeds Plat's built-in depth, read `references/orchestration.md`. Discover installed skills metadata-first with `scripts/discover_skills.py`; consult **one best-matching external skill first** and add another only when evidence proves a second specialty is needed.

Plat remains the lead orchestrator. External skills are bounded consultants: send only relevant evidence, require evidence/confidence back, and arbitrate disagreements with current repo/runtime evidence rather than voting. Quick/ordinary Standard tasks should normally use **zero external skills**.

## UI/UX

Do not load design depth for ordinary frontend logic.

- New screen/redesign/design system -> `design-system.md` + `design-taste.md`
- Forms/tables/navigation/onboarding/charts -> `design-patterns.md`
- Motion -> `design-motion.md`
- Final visual critique/rendered QA -> `design-review.md`

For public artifacts, resolve audience and intended takeaway before adopting a reference metaphor.

## Developer profile

`~/.plat/profile.md` controls role/experience/output preferences only; never architecture, product semantics, scope, or engineering depth. See `references/profile.md` / `references/context.md` only when needed.

## Work loop

Compress aggressively for small tasks.

1. **Resolve** active intent.
2. **Inspect** only enough evidence to localize ownership/constraints.
3. **Route** to minimum sufficient depth/domain.
4. **Act** in the smallest valid slice.
5. **Verify** requested behavior directly.
6. **Review** only relevant compatibility/failure/security/performance/delivery/UX concerns.
7. **Persist** only state expensive to rediscover.
8. **Report** concisely.

## Trajectory correction

Re-route when a developer correction, repository/runtime contradiction, or failed verification invalidates the current model. Use `references/routing.md` for **Local, Behavioral, or Structural** corrections. Structural corrections invalidate dependent decisions. A newer correction also **purges task-local work that only existed because of the rejected assumption**; do not keep it as a hidden fallback or "helpful" extra. Re-run **Resolve -> Inspect -> Route** only for the affected slice.

For failed fixes, use `references/debugging.md`: retire disproven hypotheses instead of stacking another patch.

## Completion

Prove the requested behavior, not a nearby symptom. Prefer the narrowest direct evidence first, then widen only according to risk. Render material UI claims when tooling exists; measure performance claims; verify migration/coexistence claims; exercise concurrency when it is the failure mode.

If proof cannot run, state exactly what remains unverified and why.

