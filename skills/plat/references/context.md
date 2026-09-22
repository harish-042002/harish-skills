# Context and Cross-Agent Continuity

Use for long/non-trivial work, context pressure, agent switching, or resuming unfinished work.

## Principle

Repository/code/tests/specs are durable truth. `.plat/session.md` is a compact routing layer to that truth, not a second project history. It exists for the same developer/project to continue across agents or context resets; it is not a team communication channel.

Store decisions and verified current state, not conversation.

## Local state

Default:

```text
.plat/session.md
```

Prefer local-only exclusion through `.git/info/exclude`:

```text
.plat/
```

Do not alter shared `.gitignore` solely for Plat unless the developer wants session state shared.

## Create/update only when useful

Create a session when work spans meaningful steps, important discoveries would be expensive to rediscover, several files/boundaries are involved, context reset/agent switching is plausible, or work remains unfinished.

Skip it for tiny one-shot changes.

Update at checkpoints, not after every tool call:

- Plan/approach materially changes.
- Important verified discovery changes the task model.
- A slice is completed/verified.
- A blocker/risk appears.
- Before an agent/context switch or unfinished stop.

## Session format

Keep it decision-dense; target under 60 lines and treat 100 lines as a warning that durable artifacts should be referenced instead of copied:

```markdown
# Plat Session

## Goal
Observable outcome in 1-2 lines.

## Constraints
Only implementation-changing constraints.

## Verified State
- Current facts, with file/function/artifact pointers.

## Decisions
- Decision - short reason.

## Assumptions / Risks
- Anything not yet verified or still uncertain.

## Verification
- Exact check - result.

## Next
- Exact next action, or Done.
```

When practical, note a cheap workspace anchor such as branch plus HEAD/commit. If the workspace diverges materially on takeover, re-verify inherited state instead of reconciling from memory.

## Truth discipline

- Put claims in **Verified State** only when supported by current code/tests/tool evidence.
- Put uncertain inherited claims under **Assumptions / Risks** until checked.
- On takeover, validate material session claims against current repository state before changing code.
- If the session conflicts with code/tests/config, current repository evidence wins.

## Do not duplicate

Do not copy content already represented by specs, plans, ADRs, issues, commits, diffs, tests, or source files. Reference path/identifier instead.

Keep a rejected alternative only when forgetting it would likely repeat an expensive mistake; record one-line reason.

Never store:

- Hidden reasoning/chain-of-thought or chat transcript.
- Secrets, credentials, private keys, or sensitive user data.
- Large code/tool output already available elsewhere.
- Historical state no longer relevant to continuation.

## Context budget

When attention becomes crowded:

1. Keep goal/constraints/interfaces/current failure evidence/decisions/next action.
2. Replace long tool output with the shortest decisive result plus source/path.
3. Drop narration and explored paths that no longer constrain the solution.
4. Use targeted symbol/search/file reads instead of reloading broad directories.
5. Send subagents only task-specific context and merge back compact findings.
6. Do not re-read a Plat reference already available in the current context unless material state changed or context compaction removed it.
7. Load another Plat reference only when a concrete decision needs it.

Do not add a large compression protocol merely to save a few output words; optimize total input + output + rework across the task.

## Completion cleanup

When the task is fully complete, remove the session unless near-term continuation has clear value; otherwise leave only a tiny verified final state. Never let `.plat/session.md` become an append-only diary.
