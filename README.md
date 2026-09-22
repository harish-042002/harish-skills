# Harish Skills

Reusable, vendor-neutral Agent Skills for software engineering.

## Plat

**Plat is an engineering operating layer for AI coding agents.**

It is designed to make coding agents behave more like disciplined software engineers: understand the repository before changing it, choose the simplest correct design, debug from evidence, verify before claiming completion, delegate only when useful, and keep context/token usage under control.

Plat is intentionally **backend-weighted but full-stack**: roughly **60% backend/data/reliability** and **40% frontend/mobile/client engineering**. The engineering ratio stays stable; a separate deep UI/UX branch is loaded only when visual design, redesign, motion, or polish is actually part of the task.

> Current candidate: **v0.7.0**  
> Status: **Deep UI/UX design architecture added; static validated, live rendered-UI A/B pending**

---

## Why Plat?

Coding agents are already good at generating code. The harder problem is getting them to consistently:

- understand an existing repository before editing it;
- avoid speculative architecture and unnecessary dependencies;
- diagnose root causes instead of patching symptoms;
- course-correct when user feedback or fresh evidence disproves the current direction instead of defending sunk work;
- protect API, database, security, and compatibility boundaries;
- test the actual behavior they changed;
- verify with fresh evidence before saying "done";
- use subagents only when parallelism is worth the coordination cost;
- preserve useful context across Claude Code, Codex, Cursor, and other agents;
- stay concise without becoming careless.

Plat provides one engineering control plane for those behaviors.

It is **not** a giant prompt and does not load every rule for every task. A small `SKILL.md` router progressively loads only the reference modules needed for the current engineering problem.

---

## Quick Start

### Browse the repository skills

```bash
npx skills add harish-042002/harish-skills --list
```

### Install Plat globally

Choose the coding agent you use:

#### Claude Code

```bash
npx skills add harish-042002/harish-skills --skill plat -g -a claude-code -y
```

#### Codex

```bash
npx skills add harish-042002/harish-skills --skill plat -g -a codex -y
```

#### Cursor

```bash
npx skills add harish-042002/harish-skills --skill plat -g -a cursor -y
```

#### Install for multiple agents

```bash
npx skills add harish-042002/harish-skills \
  --skill plat \
  -g \
  -a claude-code \
  -a codex \
  -a cursor \
  -y
```

Remove `-g` if you want a **project-local** install instead of a global/user install.

You can also install directly from the skill path:

```bash
npx skills add https://github.com/harish-042002/harish-skills/tree/main/skills/plat
```

---

## How to Use Plat

There are no Plat commands to memorize.

Use your coding agent normally.

Examples:

```text
This endpoint sometimes creates duplicate orders.
Find the root cause and fix it.
```

```text
Add webhook support for payment completion.
Keep it backward compatible with the current clients.
```

```text
This Postgres query became slow after the dataset reached 20 million rows.
Investigate it before changing anything.
```

```text
This Flutter screen occasionally updates after it has been disposed.
Fix the actual lifecycle issue.
```

```text
Review this RAG pipeline. Retrieval quality is poor and the model is becoming expensive.
```

Plat infers the engineering workflow and loads the relevant guidance automatically.

---

## How Plat Works

```text
Natural-language engineering request
              |
              v
        Plat SKILL.md
       semantic router
              |
              v
      Understand repository
              |
              v
     Load minimum guidance
              |
      +-------+-------+
      |       |       |
    Process Domain   Risk/
                   Delivery
      |       |       |
      +-------+-------+
              |
              v
     Smallest correct change
              |
              v
       Fresh verification
              |
              v
      Compact final response
```

Routing is semantic rather than keyword-based.

For example:

```text
"Two users buy the final item at the same time
and stock becomes negative."
```

should naturally involve:

```text
repository understanding
+ debugging
+ backend
+ database/concurrency
+ testing
```

The developer does not need to say "race condition" or select modules manually.

---

## Core Engineering Loop

Plat follows this operating loop:

```text
UNDERSTAND
    |
SIMPLIFY
    |
DESIGN
    |
IMPLEMENT
    |
PROVE
    |
HARDEN
    |
OPTIMIZE
    |
DOCUMENT STATE
```

The loop compresses for tiny changes. Plat should never create more process than the task requires.

### Lightweight course correction

Normal feature work does **not** require a formal spec. Plat keeps ordinary builds lightweight: understand the outcome, give a short approach when the work is substantial, implement, and prove.

Only when a developer correction or fresh evidence invalidates the current direction does Plat use a tiny 1-3 line direction anchor: current outcome, changed assumption, next valid slice. It then preserves valid work, reworks only what depended on the wrong assumption, and continues. It should not merely say "you're right," keep extending the old path, or run periodic reflection without new evidence.


### Deep design architecture

Visual design is deliberately separated from ordinary frontend engineering so backend work and behavior-only frontend work do not pay for a large design prompt.

When appearance, art direction, interaction feel, or UI polish is materially in scope, Plat progressively loads five deeper layers:

```text
Design System & UI/UX Intelligence
        ↓
Product & Component Patterns
        ↓
Visual Taste & Art Direction
        ↓
Motion & Interaction Craft
        ↓
Rendered Visual Review & Polish
```

The layers synthesize current public patterns from **UI/UX Pro Max**, **Taste Skill**, **Emil Design Engineering**, and **Impeccable** into Plat's own vendor-neutral guidance. Plat does not require or fetch those skills at runtime.

A normal UI state/API change may load only `frontend.md`. A new screen or redesign can load design system + taste. Pattern, motion, and final visual-review references are added only when the task needs them. This allows pure design work to spend significantly more context without imposing that cost on the rest of Plat.

---

## Engineering Principles

### Simplest correct solution

Plat prefers this order:

```text
Do not build it if unnecessary
        |
Reuse existing repository behavior
        |
Standard library / language capability
        |
Native framework / platform / database feature
        |
Existing installed dependency
        |
Minimum conventional custom code
        |
Additional complexity only with evidence
```

"Simple" means easy to reason about — not artificially short or primitive.

### Evidence before claims

A task is not complete because the code "looks right."

Plat prefers:

```text
reproduce / define expected behavior
        |
implement the smallest correct change
        |
run the narrowest direct proof
        |
run broader checks justified by blast radius
        |
report exact verification
```

### Backend owns protected invariants

Frontend and mobile can provide validation and optimistic UX, but protected durable rules such as permissions, money, inventory, entitlement, quotas, and persisted transitions remain authoritative on backend/data boundaries.

### Measure before optimizing

Performance changes should begin with a representative baseline and identify the dominant cost before changing architecture or code.

---

## Runtime Modules

Plat currently contains focused guidance for:

| Module | Purpose |
| --- | --- |
| Engineering Core | Simplicity, scope, architecture, code quality |
| Repository Understanding | Task-scoped repository mapping and version awareness |
| Planning | Multi-file changes, migrations, architecture and rollout |
| Debugging | Evidence-driven root-cause debugging |
| Testing | Regression-first verification and claim-to-evidence mapping |
| Backend | Services, workers, queues, reliability and distributed failure |
| Database | Schema, SQL, indexing, concurrency and migrations |
| API | REST, GraphQL, gRPC, webhooks, events and compatibility |
| Security | Auth, authorization, trust boundaries, secrets and abuse paths |
| Performance | Latency, throughput, cost, memory and capacity |
| Delivery | CI/CD, deployment, IaC, release and Git integration |
| Frontend | Web/client state, forms, async flows, responsive behavior, SSR/hydration, accessibility and browser verification |
| Design System | Product context, surface mode, visual dials, tokens, typography, color, layout and accessibility |
| Design Patterns | Page architecture, navigation, forms, tables, states, mobile patterns and data visualization |
| Design Taste | Art direction, hierarchy, typography craft, composition, restraint and anti-generic UI guidance |
| Design Motion | Interaction frequency, timing/easing, spatial continuity, perceived performance and reduced motion |
| Design Review | Rendered browser/device review, responsive/a11y/state QA, bounded polish and stop conditions |
| Flutter / Mobile | Lifecycle, state, navigation, responsive/adaptive UI, accessibility, networking, offline, performance and device verification |
| AI Engineering | LLMs, RAG, agents, tools, evals and model economics |
| Context | Compact same-developer cross-agent continuation |
| Subagents | Bounded scouting, implementation, review and parallel work |

These are not separate user-facing skills. They are progressively loaded internal references behind **one Plat skill**.

---

## Cross-Agent Continuity

For non-trivial unfinished work, Plat can maintain:

```text
.plat/session.md
```

It contains only high-signal continuation state:

```text
Goal
Constraints
Verified State
Decisions
Assumptions / Risks
Verification
Next
```

This is intended for the **same developer and same project** moving between agents, for example:

```text
Claude Code
    |
    v
Codex
    |
    v
Cursor
```

It is not developer-to-developer runtime communication.

Plat prefers `.git/info/exclude` for local-only `.plat/` state so private agent working context is not accidentally pushed to the repository.

---

## Subagent Philosophy

Plat does **not** spawn agents by default.

It delegates only when the expected benefit is greater than coordination cost.

Typical worker modes:

- **Scout** — inspect/search and return a compact repository map.
- **Implementer** — make a bounded change with explicit verification.
- **Reviewer** — independently inspect an artifact or diff for correctness and risk.

Architecture, shared contracts, integration, destructive/security-sensitive decisions, and final completion judgment remain with the main agent.

---

## Token Efficiency

Plat is designed around **minimum sufficient context**.

Plat uses progressive loading. v0.7 keeps deep design knowledge outside the ordinary engineering path:

| Scenario | Approx. Plat context |
| --- | ---: |
| v0.6 root router | ~1.73k proxy tokens |
| v0.7 root router | ~2.00k proxy tokens |
| Root increase for design routing | ~270 proxy tokens |
| Five deep design references, all loaded | ~14.9k proxy tokens |
| Backend / ordinary engineering task | Does not load deep design references |
| Pure design/redesign task | May deliberately load several design references |

The objective is not "shortest prompt."

The objective is:

> **minimum total tokens required to complete the task correctly.**

A slightly larger first pass can be cheaper than a small prompt that causes repeated failed edits, repository rereads, and repair turns.

---

## Benchmark Status

Plat v0.7.0 is the current design-craft candidate. v0.6.0 remains the last live-tested engineering baseline.

### v0.7.0 deep-design static validation

The v0.7.0 design architecture currently passes:

- **122 / 122** targeted design-architecture / structural checks;
- **15 / 15** semantic mutation tests;
- skill validator and package integrity checks;
- **0** known long exact duplicate instruction blocks;
- root-router increase limited to about **270 proxy tokens** versus v0.6.0;
- about **14.9k proxy tokens** of deep design knowledge kept behind progressive-loading routes.

This is static evidence that the architecture is coherent and routable. It is **not** yet a claim that v0.7 improves rendered UI quality, correctness, cost, or time. The next phase is a controlled rendered-UI A/B using the same task/model/settings.

### v0.6.0 frontend + lightweight course-correction validation

The v0.6.0 change passed:

- **46 / 46** targeted structural/behavior checks;
- **31 / 31** engineering categories derived from current Anthropic/Vercel/Flutter frontend/mobile skills;
- **14 / 14** semantic mutation tests;
- **20** updated course-correction scenarios;
- skill validator and package integrity checks;
- root router is about **1.4% smaller** (~24 proxy tokens fewer) than v0.5.0 despite the added frontend/mobile coverage.

The 31/31 result is a static engineering-coverage checklist, not a claim that Plat replaces specialist visual-design or framework-specific skills.

### v0.5.0 targeted course-correction validation

The v0.5.0 course-correction change passed:

- **34 / 34** targeted behavioral/structural checks;
- **13 / 13** semantic mutation tests;
- **20** frozen multi-turn course-correction scenarios;
- skill validator and package integrity checks;
- root router growth limited to **+4.9%** (~82 proxy tokens) versus v0.4.0.

### v0.4.0 pre-runtime baseline

The prior v0.4.0 release passed:

- **25 / 25** focused hardening rounds;
- **112 / 112** deterministic review assertions;
- **242 / 242** industry-style deterministic engineering/skill checks;
- **300** adversarial routing/context prompts;
- **40 / 40** semantic mutation tests;
- **0** broken internal references;
- **0** reference files over the configured size threshold;
- **0** known long exact duplicate instruction blocks.

### v0.3.0 -> v0.4.0

On the current v0.4 gate:

```text
v0.3.0: 197 / 241
v0.4.0: 241 / 241
```

The v0.4 router is also about **27% smaller** than the v0.3 router.

### What has not been claimed yet

The project does **not** currently claim that Plat improves real coding-agent solve rate by a specific percentage.

The next benchmark phase is a controlled live experiment:

```text
same repository
same commit
same task
same model/settings

CONTROL     -> agent without Plat
TREATMENT   -> same agent with Plat v0.6.0
```

The benchmark will compare correctness, hidden tests, total tokens, cost, wall time, repair turns, files/lines changed, dependency/abstraction growth, verification quality, and final response overhead.

---

## Repository Structure

```text
harish-skills/
├── README.md
└── skills/
    └── plat/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── ai-engineering.md
            ├── api.md
            ├── backend.md
            ├── context.md
            ├── database.md
            ├── debugging.md
            ├── delivery.md
            ├── design-motion.md
            ├── design-patterns.md
            ├── design-review.md
            ├── design-system.md
            ├── design-taste.md
            ├── engineering-core.md
            ├── flutter-mobile.md
            ├── frontend.md
            ├── performance.md
            ├── planning.md
            ├── repository-understanding.md
            ├── security.md
            ├── subagents.md
            └── testing.md
```

The runtime package stays intentionally small. Research notes, benchmark corpora, and maintenance material are kept separate from the skill that agents load.

---

## Compatibility

Plat is written as a vendor-neutral Agent Skill and avoids hard-coding model brands into engineering policy.

The same source is intended to work across Agent Skills-compatible coding environments such as:

- Claude Code
- Codex
- Cursor
- OpenCode
- Gemini CLI
- other agents supported by the open skills ecosystem

Exact installation/discovery behavior depends on the coding agent and installer version.

---

## Release Policy

Plat follows evidence-driven iteration:

```text
Build
  ->
Static/adversarial validation
  ->
Freeze release
  ->
Live A/B benchmark
  ->
Analyze failures
  ->
Next version
```

Once a benchmark candidate is frozen, it should not be edited midway through that experiment. Findings become inputs to the next version. Freeze v0.7.0 for the next rendered-design A/B before making further design-policy changes.

---

## Source

Plat source:

```text
skills/plat/
```

GitHub:

https://github.com/harish-042002/harish-skills

Open skills CLI:

https://github.com/vercel-labs/skills
