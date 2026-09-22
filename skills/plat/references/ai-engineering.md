# AI Engineering

Use for LLM calls, RAG, agents, prompts, model routing, structured generation, AI memory, evaluations, and tool-using systems.

## Deterministic boundary

Do not use a model for work normal code, schemas, parsers, constraints, rules, or queries can perform reliably and cheaply. Keep deterministic orchestration around probabilistic model calls.

Use models where language ambiguity, semantic retrieval, synthesis, classification, planning, or generation actually benefits.

## Define the contract

For each model step identify:

- Exact responsibility and success predicate.
- Input/context source and trust level.
- Structured output/schema when machine-consumed.
- Tool permissions and side-effect boundary.
- Retrieval/memory source of truth and provenance.
- Timeout/retry/fallback behavior, including whether a fallback changes quality/capability guarantees.
- Latency/token/cost budget across model input/output, retrieval, tool calls, retries, and fallback.
- Evaluation signal and observable failure classes.
- Privacy/security constraints.

## Context discipline

- Supply the minimum evidence needed for the decision.
- Prefer targeted retrieval/search over dumping repositories/documents.
- Separate trusted instructions from user/retrieved/tool/web content.
- Compress history into current decisions/state; do not persist hidden reasoning.
- Treat stale/conflicting memory as a potential source of incorrect behavior, not automatic truth.

## Structured outputs and side effects

Use schema-constrained output when downstream code consumes model results. Version machine-consumed schemas/contracts when independent producers/consumers can coexist. Validate again before DB writes, permissions, money, destructive operations, tool calls, or external messages.

Model output is a proposal until deterministic validation authorizes the side effect.

## RAG

Evaluate retrieval separately from generation:

- Did the right evidence enter context?
- Is it current and from the intended source?
- Can the answer preserve document identity/provenance when grounding matters?
- Are chunking/filtering/ranking failures visible separately from model failures?

Do not compensate for poor retrieval by only increasing prompt size/model size.

## Agents and tools

Use an agent only when dynamic tool selection/multi-step adaptation is actually required. Prefer a deterministic workflow when steps are known.

- Grant least-privilege tools/credentials.
- Validate tool arguments/results.
- Define a termination predicate and bound loops, retries, tool calls, and spend.
- Make retried side effects idempotent where possible.
- Require explicit approval at the product's intended boundary for destructive/high-impact operations.

## Model routing

Route by capability, risk, and economics rather than vendor/model brand:

- Strong reasoning: architecture, ambiguity, subtle debugging, high-risk review.
- Fast/economical: bounded extraction, search, classification, formatting, routine isolated work when quality is adequate.

A cheap model that causes repeated retries/rework is not cheaper. Do not hard-code provider model names into Plat policy.

## Evaluation

For non-trivial AI behavior create reproducible representative cases before trusting demos. Because model behavior is probabilistic, use enough repeated/representative runs to detect unstable success when the risk justifies it. Measure relevant quality/failure classes plus latency and cost. Include adversarial/edge cases where permissions, prompt injection, hallucination, or retrieval failure can cause harm.

Separate offline evals from production telemetry; both answer different questions.

## Observability

Capture enough safe metadata to diagnose model/version/prompt-or-config version/tool/retrieval latency, failure type, token/cost, and fallback behavior without logging secrets or sensitive prompts by default.

## Security

Treat user text, retrieved docs, web content, model outputs, tool results, and MCP/connector content as untrusted. Treat prompt injection as a data-boundary attack: data-borne instructions must never expand permissions, alter tool authority, or override higher-priority policy. Validate before side effects and minimize exposed secrets/data.
