# Context and Cross-Agent Continuity

Use for long/non-trivial work, context pressure, agent switching, or resuming unfinished work.

## Principle

Repository/code/tests/specs are durable truth. `.plat/project.md` may cache verified project structure/conventions, while `.plat/session.md` is a compact pointer to current task truth for the **same developer/project** across agents or context resets. Neither overrides current repository evidence. Read `profile.md` for global/project setup rules.

## When to create/update

Create session state only when important discoveries would be expensive to rediscover, work spans several steps/boundaries, switching/reset is plausible, or work remains unfinished. Skip tiny one-shot changes. Do not create a project/global profile merely because a session exists.

Update only when approach/state materially changes, a slice is verified, a blocker/risk appears, or before a switch/unfinished stop.

Prefer local exclusion through `.git/info/exclude`:

```text
.plat/
```

Do not change shared `.gitignore` solely for Plat unless shared state is intentional.

## Session format

Target <60 lines:

```markdown
# Plat Session

## Goal
Observable outcome.

## Constraints
Only implementation-changing constraints.

## Verified State
- Current facts with file/function/artifact pointers.

## Decisions
- Decision - short reason.

## Assumptions / Risks
- Unverified or unresolved items.

## Verification
- Exact check - result.

## Next
- Exact next action, or Done.
```

When cheap, record branch + HEAD/commit as a freshness anchor.

## Truth discipline

- Put claims under **Verified State** only when current code/tests/tool evidence supports them.
- Keep inherited uncertainty under **Assumptions / Risks** until checked.
- On takeover, compare the freshness anchor/current workspace and re-verify material claims before editing.
- Current repository evidence wins over session notes.
- When the developer materially corrects intent, replace stale Goal/Constraints/Decisions/Next entries rather than appending contradictory history. Preserve an old decision only if its rejection still prevents repeated work.

## Keep only high-signal state

Reference specs/plans/ADRs/issues/commits/diffs/tests/source by path or identifier instead of copying them. Keep a rejected alternative only when forgetting it would likely repeat an expensive mistake.

Never store:

- Hidden reasoning/chain-of-thought or chat transcripts.
- Secrets, credentials, private keys, or sensitive user data.
- Large code/tool output available elsewhere.
- Obsolete history.

When context is crowded:

1. Keep goal, constraints, interfaces, decisive evidence, decisions, risks, next action.
2. Replace long outputs with shortest decisive result + source/path.
3. Drop explored paths that no longer constrain the solution.
4. Use targeted search/reads instead of broad reloads.
5. Give subagents task-specific context; merge back compact findings.
6. Do not reread Plat references still available in context.

Optimize total input + output + rework, not compression for its own sake.

## Completion cleanup

When fully complete, delete the session unless near-term continuation has clear value; otherwise leave only a tiny verified final state. Never let it become append-only history.
