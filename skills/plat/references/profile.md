# Developer and Project Profiles

Use when the developer asks to set up/customize Plat, when an existing profile can save repeated explanation/discovery, or when resuming work in a project that already has Plat metadata.

## Contents

1. Purpose
2. Precedence
3. Global developer profile
4. Project profile
5. Session state
6. Setup flows
7. Read/update rules
8. Privacy and safety
9. Staleness and conflicts
10. Edge cases

## Purpose

Profiles reduce rediscovery and tune explanation/output to the developer. They are **hints and verified summaries**, not hidden policy and not sources of repository truth.

The global developer profile is optional preference context. The installer may offer onboarding, but a missing profile never blocks engineering work. Use neutral defaults and ask preference questions only when the answer affects the current task.

Installation/onboarding creates **only** the global developer profile at `~/.plat/profile.md`.

Project and session state are separate runtime concerns:
- global developer profile - optional for interactive use and the only profile created during installation;
- project profile - optional later runtime cache only when explicitly requested or clearly useful for non-trivial repository work; never create it during installation/onboarding;
- session state - only for non-trivial continuation.

Non-interactive CI/automation may use neutral defaults without creating a persistent profile.

## Precedence

Use:

```text
current explicit request/correction
> current repository/runtime evidence
> .plat/project.md
> ~/.plat/profile.md
> Plat defaults
```

A preferred stack or role never justifies fighting the current project.

## Global developer profile

Location:

```text
~/.plat/profile.md
```

Keep it small, stable, and engineering-only. Recommended target: <50 lines.

Example:

```markdown
# Plat Developer Profile

## Role
Primary: backend
Secondary: ai, fullstack

## Experience
backend: advanced
frontend: intermediate
mobile: intermediate
ai: advanced

## Assistance
Default response: concise
Explanation: skip fundamentals unless asked
Architecture detail: high when tradeoffs matter
Research output: structured

## Familiar stack
Python, FastAPI, AWS, Postgres, DynamoDB, Redis, Flutter

## Preferences
Prefer existing project patterns over introducing new libraries.
```

The familiar stack affects explanation/search shortcuts only. It is not a technology mandate.

Do not store employer identity, credentials, personal secrets, health data, or unrelated personal information.

## Project profile

Location:

```text
<repo>/.plat/project.md
```

Prefer local exclusion via `.git/info/exclude` unless the developer explicitly wants a shared team artifact.

Recommended target: <100 lines.

Example structure:

```markdown
# Plat Project Profile

## Freshness
Branch/HEAD: ...
Last verified: ...

## Stack
- runtime/framework/version pointers
- persistence/cache/queue
- frontend/mobile platform

## Architecture
- owning modules/services and their responsibilities
- important boundaries/source of truth

## Conventions
- validation/error/state patterns
- test/build commands
- dependency/component patterns

## Critical contracts
- public APIs/events/schemas that need compatibility

## Verification
- commands and important environment notes

## Unknown/Stale
- claims needing recheck
```

Reference source paths instead of copying code/docs.

## Session state

`.plat/session.md` remains the current task handoff file. It should point into the project/profile/source rather than duplicating them.

Use `context.md` for session rules.

## Setup flows

### Mandatory developer onboarding

The interactive onboarding has **three required preference choices** and one optional field:

1. Primary work: backend / frontend / full-stack / mobile / AI / design / platform / data.
2. Overall engineering experience: beginner / intermediate / advanced.
3. Response preference: concise / balanced / explanatory.
4. Optional familiar technologies.

Do **not** ask for a preferred reasoning depth. Depth is decided from task evidence. A developer may ask for a detailed answer, but that does not justify loading Deep specialists when the problem is simple.

Do not ask for employer, personal life, credentials, customer data, or information unrelated to engineering assistance.

The repository includes `scripts/setup.py`; the recommended installer runs it automatically. If onboarding is happening inside an agent instead, ask the same compact choices and write `~/.plat/profile.md`.

If a valid profile already exists, preserve it during normal upgrades. Reconfigure only when the developer requests it or runs setup with a force/reconfigure option.

### Global setup result

Write `~/.plat/profile.md` with role, experience, assistance preferences, optional familiar stack, schema version, fixed efficiency policy, and guardrails. Familiar technologies affect explanation/search shortcuts only; they never mandate architecture. The fixed efficiency policy is: after correctness and required safety/compatibility, minimize total tokens, tool calls, rereads, repair turns, and wall time.

### Project setup

When the developer asks to set up Plat for the current project:

1. Inspect repository instructions/manifests/tests/config first.
2. Infer stack and architecture from evidence instead of asking questions the repository answers.
3. Ask only unresolved project constraints that materially matter.
4. Write a compact `.plat/project.md` with source/freshness pointers.
5. Add `.plat/` to `.git/info/exclude` when safe and not already covered; do not edit shared `.gitignore` solely for Plat without intent.

Do not perform project setup during installation. If project context is needed later, derive it from repository evidence during the actual task rather than asking onboarding questions about the project.

## Read/update rules

- In interactive use, check only whether the required global profile exists; do not repeatedly reread or rewrite it for tiny tasks once loaded.
- If a global profile is already known/loaded, reuse it for the session.
- For non-trivial existing-repo work, read `.plat/project.md` when present and useful.
- Verify material project-profile claims against current code/config before acting if HEAD/branch changed or the claim affects correctness.
- Update an existing project profile only when verified durable architecture/conventions changed enough to save future rediscovery.
- Do not append history. Replace stale facts.
- Update global profile only on explicit developer preference change/setup request.

## Privacy and safety

Profiles must never contain:

- API keys/tokens/passwords/private keys;
- customer/user sensitive data;
- hidden chain-of-thought/transcripts;
- large code or tool output;
- unrelated personal attributes;
- credentials or environment secret values.

Profiles should not be sent to external services merely because they exist.

## Staleness and conflicts

Treat profile state as cached knowledge.

Revalidate when:

- branch/HEAD materially changed;
- major framework/dependency versions changed;
- the project architecture was migrated;
- observed code contradicts the profile;
- a new worktree/repository with the same folder name is in use.

When conflict exists, current evidence wins and the stale profile entry should be corrected or moved to Unknown/Stale if the project profile is being maintained.

## Edge cases

- **Monorepo:** record top-level map plus only important subproject boundaries; do not turn project.md into a directory catalog.
- **Multiple worktrees:** use repository identity + branch/HEAD freshness, not path name alone.
- **Role changes by task:** a backend developer doing frontend work still gets frontend correctness; profile changes explanation level, not domain coverage.
- **Shared machine:** do not assume a global profile belongs to the current developer when runtime identity is ambiguous; project/request evidence remains sufficient without it.
- **Team wants shared project knowledge:** durable team architecture belongs in normal repo docs/ADRs. Plat project profile stays a compact agent cache unless the team explicitly adopts it.
