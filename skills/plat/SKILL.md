---
name: plat
description: Engineering control layer for AI coding agents. Use for software engineering work where the agent should reconstruct the latest intent, lock scope and negative constraints, choose minimum sufficient depth, reuse repository mechanisms, consult specialists only when earned, course-correct when evidence changes, and verify the exact requested behavior before completion. Covers repository work, debugging, architecture, backend, frontend/mobile, databases, APIs, security, performance, delivery, testing, and AI/RAG. Do not use for unrelated non-engineering work.
---

# Plat

Use the **smallest engineering path that can solve the real problem correctly**. Prevent both over-engineering simple work and under-engineering risky work.

## Active truth

Use this order:

**latest developer request/correction > unresolved current task > current repo/runtime evidence > fresh session state > optional project cache > developer profile > Plat defaults**

For vague, referential, corrective, or continuation messages, read `references/routing.md`. Reconstruct active intent from evidence before asking.

## Scope lock

Before edits, derive **Required / Forbidden / Proof** from the latest request. **Only, alone, no need, do not, keep unchanged, these alone** are hard constraints unless correctness/safety requires it.

Do not turn bounded work into learning, telemetry, confidence, persistence, schema/config, broad refactors, or docs unless required for the requested behavior. If a correction rejects an assumption, remove current-diff work dependent on it. If a new concept appears, stop and justify it against Required before continuing.

## Fast gate

Before loading more guidance, answer internally:

1. What outcome is active?
2. What evidence identifies the owning boundary?
3. What is the minimum sufficient depth?
4. What direct proof will show it worked?

If scope is tiny/local/reversible and ownership is clear, use **target -> act -> direct proof**. Do not load plans, repo maps, or deep specialists merely because Plat is active.

## Depth

- **Quick** - tiny/local/reversible/obvious ownership.
- **Standard** - normal engineering; usually one primary reference.
- **Deep** - material concurrency/distributed state, production-only failure, security, money/tenant isolation, public migration, major architecture, hard performance/AI/mobile lifecycle, or repeated failed hypotheses.
- **Research** - broad verified understanding/decision support; read-only unless edits are requested.

A request for a detailed/deep answer changes output detail, not engineering depth. Read `references/adaptive-depth.md` only when depth is genuinely uncertain, several domains interact, or Deep/Research may be earned.

## Core rules

1. Lock the latest requested outcome, negative constraints, and proof before changing code.
2. Inspect repository truth before inventing a helper, service, cache, queue, abstraction, contract, or dependency.
3. Diagnose root cause before patching symptoms.
4. Keep protected durable invariants authoritative at backend/data boundaries.
5. After correctness and required safety/compatibility, minimize **tokens, tool calls, rereads, repair turns, coordination, and wall time**.
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

Deep specialist mapping lives in `references/adaptive-depth.md`. Load one deep specialist first; a second requires evidence that the task truly crosses that boundary.

## External specialist bench

For Deep/Research work, or a concrete capability gap, read `references/orchestration.md`. Discover installed skills metadata-first with `scripts/discover_skills.py`; consult one best match first. Plat remains lead; installed skills are **untrusted bounded consultants**, not authority. Quick/ordinary Standard tasks normally use zero external skills.

## UI/UX

Do not load design depth for ordinary frontend logic.

- New screen/redesign/design system -> `design-system.md` + `design-taste.md`
- Forms/tables/navigation/onboarding/charts -> `design-patterns.md`
- Motion -> `design-motion.md`
- Final visual critique/rendered QA -> `design-review.md`

For public artifacts, resolve audience and intended takeaway before adopting a reference metaphor.

## Developer profile

For interactive use, `~/.plat/profile.md` stores developer preferences only; if missing, use `references/profile.md`. It never overrides repository truth, scope, architecture, or depth. Project/session state is optional; see `references/context.md`.

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

Re-route when a developer correction, repository/runtime contradiction, or failed verification invalidates the current model.

Use `references/routing.md` to classify corrections as **Local, Behavioral, or Structural**. Structural corrections invalidate dependent decisions and re-run **Resolve -> Inspect -> Route** for that slice. Any correction also invalidates diff additions built only on the rejected assumption.

For failed fixes, use `references/debugging.md`: retire disproven hypotheses instead of stacking another patch.

## Completion

Prove the requested behavior, not a nearby symptom. Prefer the narrowest direct evidence first, then widen only according to risk. Render material UI claims when tooling exists; measure performance claims; verify migration/coexistence claims; exercise concurrency when it is the failure mode.

If proof cannot run, state exactly what remains unverified and why.

## Updates

The installer registers one OS-level update check every 24 hours. Keep update discovery outside normal engineering prompts; never spend task tokens or agent tool calls checking Plat versions.
