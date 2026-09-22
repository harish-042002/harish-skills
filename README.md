<div align="center">

# PLAT v1

### adaptive engineering team for AI coding agents

<img src="assets/plat-team.svg" alt="Plat adaptive engineering team" width="100%" />

**One skill. The right team. The right depth. Fresh proof.**

</div>

<img src="assets/plat-activate.svg" alt="Two simple ways to activate Plat" width="100%" />

## One-time setup

Install Plat globally for your coding agent:

```bash
npx skills add harish-042002/harish-skills --skill plat -g -a claude-code -y
```

Then put one line in your global or project agent instructions — for example `CLAUDE.md`, `AGENTS.md`, or your agent's equivalent:

```text
For software engineering requests, use the installed Plat skill.
```

Now you can ask normally. Plat chooses the mode, depth, and specialist guidance itself.

For one-off explicit use, invoke the installed skill by name. If your agent exposes installed skills as slash commands, use:

```text
/plat fix the invoice race
```

Portable fallback:

```text
Use Plat: fix the invoice race
```

> Skill invocation syntax is agent-specific. Plat itself stays vendor-neutral.

<img src="assets/plat-flow.svg" alt="How Plat routes one engineering request" width="100%" />

## What Plat gives the agent

```text
repository understanding
+ course correction
+ backend / distributed systems
+ frontend / browser runtime
+ mobile
+ AI / RAG / agents / evals
+ testing
+ database
+ API / events
+ security
+ performance
+ delivery
+ system design
+ UI/UX design, taste, motion and rendered review
```

Normal tasks do not load all of this. Plat progressively loads only what can materially improve the current task.

Optional context can make later sessions cheaper:

```text
~/.plat/profile.md       developer preferences / experience
.plat/project.md         verified project map / conventions
.plat/session.md         current task continuation
```

Current request and repository evidence always outrank cached Plat context.

<img src="assets/plat-evidence.svg" alt="Plat benchmark evidence including all ten pilot scenarios" width="100%" />

## Evidence, not promises

The public benchmark record keeps both improvements and failures visible. A real full-stack build showed a strong cost/time/context signal; the independent 10-case pilot was mixed and included one correctness failure.

Plat therefore optimizes for:

**correct result → less rediscovery → fewer wrong paths → fewer repair turns → lower total task cost**

—not a guaranteed token-reduction percentage.

<img src="assets/plat-regression.svg" alt="Plat v1 regression benchmark scenarios" width="100%" />

## Why the last two regression cases exist

A public README should be written for a first-time user, not for the internal development conversation that produced it. Plat now explicitly treats **audience, purpose, metaphor, and information hierarchy** as part of the requirement.

If a developer corrects the framing — for example, "this is a team, not an office" — Plat should re-evaluate the affected artifact rather than merely replace one word.

## More agents

```bash
# Codex
npx skills add harish-042002/harish-skills --skill plat -g -a codex -y

# Cursor
npx skills add harish-042002/harish-skills --skill plat -g -a cursor -y

# Project-local instead of global
# remove -g
```

<div align="center">

### P-01's rule

**understand the task → assemble the smallest useful team → prove the result**

</div>
