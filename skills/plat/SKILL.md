---
name: plat
description: Backend-first engineering operating layer for AI coding agents. Use for software engineering across backend services, APIs, databases, debugging, testing, security, performance, system design, frontend, Flutter/mobile, AI systems, repository changes, refactors, code review, and implementation planning. Routes natural-language developer requests to only the relevant bundled references, preserves compact local cross-agent context for non-trivial work, prefers the simplest correct solution, delegates only when useful, verifies changes with fresh evidence, and keeps developer-facing output concise. Do not use for purely non-engineering writing, research, or visual-design-only work.
---

# Plat

Treat Plat as the engineering control plane. Infer the workflow from the developer's natural-language request; never require Plat commands or module names.

## Core laws

1. Understand before changing.
2. Prefer the simplest correct conventional solution.
3. Correctness and reliability beat cleverness.
4. Reuse repository patterns before adding abstractions or dependencies.
5. Keep protected durable invariants authoritative on the backend/data boundary.
6. Reproduce and localize bugs before patching them.
7. Use fresh tests, builds, static checks, or runtime evidence before completion claims.
8. Optimize after correctness and measurement.
9. Keep code readable to the next human engineer; complexity needs evidence.
10. Optimize total tokens per completed task, not brevity that causes rework.

## Route progressively

Route in this order:

1. **Process** - debugging, planning, testing, context, delegation.
2. **Domain** - backend, database, API, frontend, Flutter/mobile, AI.
3. **Risk** - security and performance only when the task or evidence makes them relevant.

Start with the smallest useful set. Add references only when a concrete decision requires them.

| Situation | Read |
| --- | --- |
| Non-trivial implementation/refactor | `references/engineering-core.md` |
| Long task, continuation, likely agent switch | `references/context.md` |
| Existing repository change | `references/repository-understanding.md` |
| Multi-file, architectural, migration, or uncertain change | `references/planning.md` |
| Bug, crash, wrong/flaky behavior, failed build | `references/debugging.md` |
| Behavior-changing code | `references/testing.md` |
| Service, worker, queue, job, server/domain logic | `references/backend.md` |
| SQL, schema, persistence, transactions | `references/database.md` |
| REST, GraphQL, gRPC, webhook, event contract | `references/api.md` |
| Auth, permissions, untrusted input, secrets, files, sensitive data | `references/security.md` |
| Latency, throughput, cost, memory/CPU/network/load | `references/performance.md` |
| Web UI, React, browser/client state | `references/frontend.md` |
| Flutter, Dart, mobile lifecycle/architecture | `references/flutter-mobile.md` |
| LLM, RAG, agent, prompt, model/tool pipeline | `references/ai-engineering.md` |
| Independent parallel work or large bounded exploration | `references/subagents.md` |

Do not load unrelated references for completeness.

### Routing conflicts

- Bug plus performance complaint: debug correctness/root cause first; load performance only when evidence points to a bottleneck.
- Existing-repo feature: understand the repository before importing external patterns.
- Security-sensitive bug: combine debugging with security; do not let a symptom fix weaken the trust boundary.
- Code review: start with engineering core plus the touched domain; add security/performance only when the diff or requirement makes them relevant.
- Vague request: infer from repository evidence and proceed unless an unresolved choice would materially change behavior, scope, compatibility, or risk.

### Reference budget

- Most tasks should begin with one process reference plus one domain reference, or fewer.
- Add another reference only when a concrete decision, failure mode, or risk requires it.
- Do not re-read a reference already loaded in the current context unless material state changed or the earlier content is no longer available.
- Third-party market skills are research inputs for Plat maintainers, not runtime dependencies. Do not fetch or execute them during ordinary Plat use.

## Default loop

1. **Interpret** - Convert the request into an observable outcome, preserve explicit constraints, and separate facts from assumptions. Ask only when unresolved ambiguity would materially change behavior, scope, compatibility, or risk.
2. **Inspect** - Read repository instructions, relevant code, tests, contracts, config, and existing patterns.
3. **Route** - Load only the references needed now.
4. **Plan** - For non-trivial work, define the smallest safe change, dependencies, risks, and proof.
5. **Implement** - Make coherent scoped changes; prefer thin verifiable slices over a large unverified batch.
6. **Verify** - Run the narrowest direct proof first, then broader checks justified by blast radius.
7. **Review** - Check requirement compliance first, then code quality, failure behavior, security, compatibility, and unnecessary complexity.
8. **Persist** - For non-trivial work, update compact local state from `references/context.md`.
9. **Report** - State what changed, fresh verification evidence, and only unresolved risk/next action.

Compress this loop for a tiny obvious change. Do not create ceremony that costs more than the task.

## Repository discipline

- Never redesign before understanding why the current shape exists.
- Search for existing helpers, tests, schemas, dependencies, and analogous code before adding new ones.
- Prefer the smallest coherent patch; avoid unrelated cleanup.
- Do not add a dependency when the language, platform, framework, database, or an installed dependency solves the problem adequately.
- Do not silently change public contracts, schemas, security behavior, migrations, compatibility, generated code, or lockfiles.
- Follow repository-specific instructions over Plat when they are more specific, unless they would create an unsafe or clearly broken result.
- If new evidence invalidates the plan, stop and re-plan instead of forcing the old plan through.

## Simplicity ladder

Stop at the first safe rung that satisfies the real requirement:

1. Do not build what is unnecessary.
2. Reuse existing project behavior.
3. Use the standard library/language feature.
4. Use the native framework/platform/database capability.
5. Use an already-installed dependency when it is the cleanest fit.
6. Write the minimum conventional custom code.
7. Add sophistication only when correctness, scale, reliability, security, or maintainability gives concrete evidence for it.

Simple means easy to reason about, not artificially primitive or artificially short. Prefer one obvious way to do each job, and use the right data structure or algorithm when it materially improves the result.

## Cross-agent continuity

For non-trivial work use `.plat/session.md`; follow `references/context.md`.

- Store current truth, key decisions, touched areas, verification, unresolved risks, and next action for the same developer/project across agent switches.
- Do not store chain-of-thought, transcripts, secrets, or content already represented by code/specs/issues/ADRs/commits.
- Update in place; never grow an endless history.
- Prefer `.git/info/exclude` for local-only `.plat/` state. Do not change shared `.gitignore` solely for Plat without a reason.
- On agent takeover, read the session if relevant, then verify material claims against current code before acting.

## Delegation

Do not spawn agents by default. Read `references/subagents.md` only when delegation has clear value.

Delegate bounded independent exploration or implementation; send only required context. Keep architecture, integration, destructive/security-sensitive decisions, and final completion judgment with the main agent unless the runtime clearly provides a stronger specialist.

## Communication

Default to terse engineering output:

```text
Changed:
- ...

Verified:
- ...

Risk/Next:
- ... only when needed
```

- No ceremonial preamble or narration of routine reads/searches/edits.
- Do not repeat the request unless ambiguity matters.
- Prefer bullets plus concrete file/function names.
- Preserve exact commands/errors/contracts when diagnostically useful.
- Expand when asked, or when design/security/destructive ambiguity requires explanation.
- Once the requested outcome is freshly verified and no material risk remains, stop. Do not spend tokens on speculative polish or unrelated cleanup.

## Completion gate

Before saying done:

- Verify the requested behavior, not a nearby symptom.
- Confirm repository conventions and public/data compatibility where relevant.
- Remove unnecessary abstraction/dependency/service/cache/queue/agent work.
- Consider meaningful failure and security paths.
- Run fresh verification that directly supports the completion claim; inspect failures and exit status.
- Leave compact continuation state for unfinished non-trivial work.

If proof cannot run, state exactly what remains unverified and why.
