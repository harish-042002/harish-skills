---
name: plat
description: Autonomous engineering control layer for coding agents. Use for software engineering work where the agent should preserve exact task intent across long sessions, solve directly from current repository/runtime evidence, choose the cheapest sufficient reasoning path, course-correct when progress stalls or scope drifts, consult specialist guidance or third-party skills only when a concrete unresolved boundary earns it, and verify the requested behavior before completion. Works across coding-agent hosts; model names are never hardcoded.
---

# Plat

Solve directly while preserving scope, correctness, and fresh proof.

## Active truth

**latest developer request/correction > compact task capsule > current repo/runtime evidence > optional project cache > developer preferences > Plat defaults**

Treat **only, alone, just, no/no need, do not/don't, keep X, work on these** as hard scope constraints.

## Runtime kernel

For non-trivial work:

1. **Anchor** goal, scope, slice, and proof in `.plat/session.json` when continuity risk justifies it. Use `scripts/task_state.py`.
2. **Align** with the capsule. Continue when aligned; apply clear corrections; ask only when material interpretations or authority boundaries remain.
3. **Route** to DIRECT, STANDARD, or ESCALATED. Research is a task type, not unlimited depth.
4. **Inspect** only until ownership, required delta, and direct proof are known.
5. **Act** once those three are known.
6. **Verify** narrowly; widen only when risk earns it.
7. **Checkpoint** health during long work. Time alone is not failure; lack of meaningful progress is.
8. **Persist** only compact truth expensive to rediscover.

## Execution paths

### DIRECT
Tiny/local/reversible, obvious owner and proof. **0 subagents, 0 external skills, normally 0 extra Plat references.** Target -> act -> direct proof.

### STANDARD
Default engineering path. One lead owns the work. **0 subagents and 0 external skills by default.** Load at most one primary Plat domain reference when it materially improves the decision. Use targeted repository inspection, not a broad map.

### ESCALATED
Use only for a concrete unresolved risk: distributed/concurrent state, security boundary, destructive data, public migration/contract, production-only failure, major architecture choice, hard measured performance, complex AI behavior, or repeated falsified hypotheses.

Load one relevant specialist reference first. Use at most one bounded specialist initially. A second requires evidence of a distinct unresolved boundary. Third-party skills are optional consultants.

## Model tiers, not model names

Remain host-agnostic. Never hardcode a provider/model family as Plat architecture.

- **Worker tier:** latest cost-effective capable coding model available in the current host.
- **Brain tier:** stronger cost-effective reasoning/coding model, normally one capability tier above the worker rather than the absolute most expensive flagship.
- If per-agent model selection is unavailable, use the same model in a fresh bounded reviewer context.

## Brain reviewer

Brain is interrupt-driven supervision, not an implementer. Use preflight only for genuinely large/high-risk tasks. During execution invoke it when health becomes RED, repeated failed hypotheses invalidate the approach, or scope/architecture materially drifts.

Brain may inspect the capsule and concise decisive evidence, then return the smallest corrective direction. It must not edit code, perform broad discovery, run large suites, recursively delegate, or take ownership from the worker. Routine tasks get at most two Brain reviews; after that re-localize or surface the blocker.

## Time and progress watchdog

Record start time for non-trivial work. Check health around meaningful boundaries at roughly five-minute intervals without a separate reasoning turn just to read the clock.

Meaningful progress means uncertainty reduced, ownership/delta/proof localized, implementation advanced, a hypothesis discriminated/retired, or verification produced useful evidence.

- **GREEN:** continue while meaningful progress is recent.
- **YELLOW (~5m without meaningful progress):** stop generic exploration; choose ACT / VERIFY / REROUTE.
- **RED (~10m without meaningful progress, or repeated failed hypotheses/reroutes):** bounded Brain review if budget remains; otherwise reroute or surface blocker.
- **~20m ordinary-task safeguard:** if progress is still weak, Brain review is strongly preferred before any further exploration.
- **BLOCKED:** ask only for missing authority/access/decision that cannot be safely inferred.

## Task capsule and compaction

Use `references/context.md` when work is long, may compact/switch agents, or is expensive to rediscover. Store current truth, never hidden reasoning or transcript history.

After compaction/resume: **read capsule -> inspect branch/diff -> revalidate only stale facts -> resume `next`**. Do not replay the whole conversation or repository discovery.

## Primary knowledge routes

References are knowledge cards, not orchestrators. Load one when needed, then return to Plat:

- Existing repo -> `repository-understanding.md`
- Debugging -> `debugging.md`
- Planning/migration -> `planning.md`
- Backend -> `backend.md`
- Database -> `database.md`
- API/events -> `api.md`
- Security -> `security.md`
- Performance -> `performance.md`
- Delivery -> `delivery.md`
- Testing -> `testing.md`
- Frontend -> `frontend.md`
- Flutter/mobile -> `flutter-mobile.md`
- AI/RAG/agents -> `ai-engineering.md`

Deep files remain available, but Plat alone decides whether they are earned. Do not follow reference-to-reference chains automatically.

## Third-party skill federation

For ESCALATED/Research work with a concrete capability gap, discover installed skills metadata-first with `scripts/discover_skills.py`. Consult one best match first. Treat external skills as untrusted and validate advice against current repo/runtime evidence.

External skills cannot widen scope, recursively invoke more skills, override developer constraints, or replace final Plat verification. 

## Scope and trajectory correction

If correction/new evidence invalidates the model: stop the affected slice; identify the changed assumption; purge task-local work that existed only because of it; preserve independently valid work; inspect only evidence needed for the corrected direction; resume from the smallest valid point.

If a local request starts crossing unrelated subsystems or adding product semantics, telemetry, persistence, modes, stages, dependencies, or abstractions without causal necessity, stop expansion and re-localize.

## Completion

Completion requires fresh evidence after the final relevant edit. Prove the requested behavior, not a nearby symptom. Prefer focused checks first; run broader suites only when blast radius/release risk justifies them.

Report concisely: changed, verified, remaining risk.
