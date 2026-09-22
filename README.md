<div align="center">

# PLAT v1

### adaptive engineering for AI coding agents

<img src="assets/plat-pixel-mascot.svg" alt="Animated Plat pixel mascot explaining adaptive engineering" width="100%" />

[![main](https://img.shields.io/badge/main-v1.0.0-7df9ff?style=for-the-badge&labelColor=10172a)](https://github.com/harish-042002/harish-skills)
[![v0.7](https://img.shields.io/badge/frozen-v0.7-ff6bd6?style=for-the-badge&labelColor=10172a)](https://github.com/harish-042002/harish-skills/tree/plat-v0.7)
[![vendor neutral](https://img.shields.io/badge/vendor-neutral-51f0a5?style=for-the-badge&labelColor=10172a)](#)
[![progressive context](https://img.shields.io/badge/context-progressive-ffcf5c?style=for-the-badge&labelColor=10172a)](#)

</div>

> **Plat is not a bigger prompt.** It is an adaptive engineering control plane that decides *how much engineering depth this task actually deserves*, loads only the relevant specialist brain, remembers verified project context, course-corrects when evidence changes, and requires proof before claiming completion.

---

<img src="assets/plat-pixel-usp.svg" alt="Plat v1 unique selling points in pixel art" width="100%" />

## The USP

**One skill. Variable depth. Project-aware. Cross-agent. Proof-first.**

Most engineering prompts are static: every task gets roughly the same instructions. Plat v1 behaves differently:

```text
tiny change       → tiny context
normal feature    → basic process + one domain
hard incident     → targeted deep specialist
large research    → structured repository map
next session      → reuse verified project/session context
```

The objective is not minimum prompt size. The objective is **minimum total work to reach a correct result**: fewer unnecessary reads, fewer wrong paths, fewer repair turns, less repeated repository discovery.

---

<img src="assets/plat-pixel-map.svg" alt="Plat v1 adaptive engineering architecture map" width="100%" />

## How P‑01 routes a task

```text
MODE
Build • Debug • Review • Research • Design • Optimize • Migrate

DEPTH
Quick • Standard • Deep • Research
```

The router combines the current request with repository evidence and optional Plat context. Deep modules are loaded only when they can change a material decision, expose a failure mode, or avoid likely rework.

### Specialist zones

| Standard brain | Deep brain when earned |
| --- | --- |
| Repository understanding | Large repo / monorepo archaeology |
| Debugging | Production / distributed / competing-hypothesis debugging |
| Backend | Distributed systems / retries / idempotency / backpressure |
| Frontend | Large-app state / SSR / hydration / performance |
| Flutter / Mobile | Process death / offline sync / background work / platform behavior |
| AI | RAG / agents / evals / memory / model economics |
| Testing | Property / mutation / fault / concurrency / migration / load |
| Database | Query plans / anomalies / live migrations / replication |
| API | Public-contract evolution / events / webhooks / streaming |
| Security | Threat modeling / tenant isolation / SSRF / supply chain / AI tools |
| Performance | Profiling / tail latency / capacity experiments |
| Delivery | Rollout / coexistence / IaC / rollback / disaster recovery |
| Design | UI system / patterns / taste / motion / rendered review |

---

## Optional memory, never hidden authority

```text
~/.plat/profile.md        → developer role + experience + output preference
<repo>/.plat/project.md   → verified project map + conventions + test commands
<repo>/.plat/session.md   → current task continuation state
```

Truth order is always:

```text
current request / correction
> current repository + runtime evidence
> project profile
> developer profile
> Plat defaults
```

Profiles reduce rediscovery. They never force a preferred stack or override current code.

---

## Install

### See available skills

```bash
npx skills add harish-042002/harish-skills --list
```

### Claude Code

```bash
npx skills add harish-042002/harish-skills --skill plat -g -a claude-code -y
```

### Codex

```bash
npx skills add harish-042002/harish-skills --skill plat -g -a codex -y
```

### Cursor

```bash
npx skills add harish-042002/harish-skills --skill plat -g -a cursor -y
```

Remove `-g` for a project-local install.

---

## Use it normally

No Plat commands are required.

```text
"This endpoint occasionally creates duplicate invoices under load. Find the root cause."

"Understand the entire notification scheduling flow before we modify it."

"Build this new admin screen using the current product's design language."

"Our RAG quality dropped while token cost increased. Diagnose the pipeline."

"Migrate this public API without breaking old mobile clients."
```

Plat decides the mode, depth, repository slice, specialist guidance, and verification path.

---

## What Plat optimizes for

```text
correctness
   ↓
clear invariants
   ↓
reliability
   ↓
human-readable simplicity
   ↓
security + compatibility
   ↓
measured performance
   ↓
lower total token / tool / repair cost
```

It deliberately avoids architecture theater, universal TDD ceremony, full-spec workflows for ordinary features, blanket deep research, and loading every specialist file "just in case."

---

## Course correction

When the developer or fresh evidence invalidates the current direction, Plat does not simply say *"yes, you're right"* and keep building on stale assumptions.

```text
STOP affected slice
→ name invalid assumption
→ re-check minimum evidence
→ preserve valid work
→ replace stale direction
→ prove corrected behavior
```

For normal work this can be only a 1–3 line direction anchor. Plat is **not** a spec-first framework.

---

## Cross-agent continuity

For the same developer + project:

```text
Claude Code
    ↓
  Codex
    ↓
 Cursor
    ↓
same verified project/session state
```

Durable team knowledge still belongs in normal repository docs, ADRs, specs, tests, and commits. Plat context is a compact working cache.

---

## v1 evidence

The current v1 candidate has passed the static/pre-runtime release gate:

```text
305 / 305  deterministic architecture + behavior checks
38  / 38   semantic-control mutations killed
65          adaptive edge-case scenarios
36          directly routed reference modules
0           known long duplicate instruction blocks
~2,075      proxy tokens in the always-loaded v1 router
~+76        proxy tokens vs v0.7 root (~3.8%)
```

The complete specialist library is much larger, but progressive loading keeps it off ordinary task paths.

**Important:** these numbers prove structural routing/coverage, not a real-world coding-agent win. v1 still needs frozen live A/B testing for correctness, total tokens, cost, wall time, repair turns, and rendered UI quality before claiming those improvements.

---

## Release layout

```text
main
└── Plat v1.0.0 adaptive-engineering candidate

plat-v0.7
└── frozen v0.7 design-craft predecessor
```

Do not modify a frozen benchmark version midway through an experiment. Findings become the next version.

---

<details>
<summary><strong>Repository structure</strong></summary>

```text
skills/plat/
├── SKILL.md
├── agents/
│   └── openai.yaml
└── references/
    ├── adaptive-depth.md
    ├── profile.md
    ├── engineering-core.md
    ├── repository-understanding.md
    ├── repository-deep.md
    ├── planning.md
    ├── debugging.md
    ├── debugging-deep.md
    ├── system-design-deep.md
    ├── backend.md
    ├── backend-systems.md
    ├── frontend.md
    ├── frontend-deep.md
    ├── flutter-mobile.md
    ├── mobile-deep.md
    ├── ai-engineering.md
    ├── ai-deep.md
    ├── testing.md
    ├── testing-deep.md
    ├── database.md
    ├── database-deep.md
    ├── api.md
    ├── api-deep.md
    ├── security.md
    ├── security-deep.md
    ├── performance.md
    ├── performance-deep.md
    ├── delivery.md
    ├── delivery-deep.md
    ├── design-system.md
    ├── design-patterns.md
    ├── design-taste.md
    ├── design-motion.md
    ├── design-review.md
    ├── context.md
    └── subagents.md
```

</details>

<div align="center">

### P‑01's rule

**use the smallest brain that can solve the real problem — then prove it**

`harish-042002/harish-skills`

</div>
