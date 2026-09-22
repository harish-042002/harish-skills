# Deep AI Engineering

Use for complex RAG, agents, model routing, memory, evaluation, tool use, prompt optimization, fine-tuning decisions, multimodal pipelines, or AI cost/reliability problems beyond a simple model call.

## Contents

1. Objective
2. Decompose the pipeline
3. Evaluation first
4. Retrieval systems
5. Agents and tools
6. Memory and context
7. Model routing and fallback
8. Prompt/system design
9. Structured outputs and side effects
10. Cost and latency
11. Observability
12. Safety and prompt injection
13. Fine-tuning decisions
14. Edge cases

## Objective

Make probabilistic components measurable and bounded. Separate failures by stage so the fix targets retrieval, prompt, model, routing, memory, tools, or orchestration instead of blindly increasing model size/context.

## Decompose the pipeline

Map the actual path:

```text
input
-> deterministic preprocessing/router
-> retrieval/memory/tool context
-> model step(s)
-> structured validation
-> deterministic business decision/side effect
-> user/system output
```

For each model step define responsibility, success predicate, input provenance, schema, tools, budget, fallback, and evaluation signal.

## Evaluation first

Before claiming an AI change is better, freeze representative cases and a baseline.

Use the strongest feasible evaluation source:

1. deterministic correctness/contract checks;
2. human-labeled goldens/reference facts;
3. domain metrics;
4. calibrated pairwise/LLM judge where deterministic truth is unavailable;
5. production telemetry/user feedback for online behavior.

Track quality **and** latency/cost/failure rate. Improvements that only move one metric can still make the product worse.

For probabilistic systems, repeat enough runs to expose instability when risk justifies it. Do not claim significance from one lucky output.

## Retrieval systems

Evaluate retrieval separately from generation.

### Retrieval quality

Consider:

- Recall@K / Precision@K / MRR / NDCG where labels exist;
- source freshness;
- tenant/access filtering;
- chunk granularity and overlap;
- metadata filters;
- hybrid lexical + semantic retrieval;
- query rewriting/multi-query only when measured useful;
- reranking when candidate recall is good but ordering is weak.

### Retrieval failure taxonomy

- relevant document never indexed;
- chunk split destroyed context;
- embedding/query mismatch;
- filter removed relevant evidence;
- stale/duplicate corpus;
- correct candidate retrieved but ranked too low;
- too much irrelevant context dilutes generation.

Do not compensate for bad retrieval by stuffing more context or upgrading the model first.

## Agents and tools

Use dynamic agents only when the sequence/tool choice genuinely depends on intermediate results. Prefer deterministic workflows for known steps.

For agent loops define:

- allowed tools/permissions;
- termination/success predicate;
- max steps/retries/spend/time;
- tool argument validation;
- side-effect confirmation boundary;
- idempotency for retried actions;
- recovery from tool/model failure;
- loop/cycle detection where relevant.

A planner that repeatedly replans without new evidence is waste, not intelligence.

## Memory and context

Classify memory:

- current-turn/task context;
- short session state;
- project/domain memory;
- user preference memory;
- durable business data.

Memory is cached evidence, not authority. Verify stale facts against current sources before high-impact decisions.

Store compact state/decisions, not hidden reasoning transcripts. Retrieve selectively by task relevance and permission scope.

Avoid feeding entire conversation histories when a verified summary + relevant artifacts is enough.

## Model routing and fallback

Route by capability, quality requirement, latency, risk, and total task economics.

Measure the end-to-end effect of cheaper models. A low-cost model that causes retries, repair turns, tool loops, or human correction may be more expensive overall.

Fallbacks must define what guarantee changes. Do not silently serve a low-quality fallback for a safety/contract-critical function if the product cannot tolerate it.

## Prompt/system design

Keep instructions separated from untrusted data. Use clear contracts rather than long persuasive prose.

Prefer:

- explicit role/responsibility;
- relevant constraints;
- structured output when machine-consumed;
- small high-quality examples only when they improve measured behavior;
- retrieved evidence with provenance;
- deterministic post-validation.

Avoid prompt growth as the first fix for every failure. Remove obsolete/conflicting instructions.

## Structured outputs and side effects

Model-generated JSON/schema output still requires validation.

Before DB writes, payments, permissions, messages, code execution, or destructive tools:

- validate schema and business constraints;
- authorize independently;
- constrain tool arguments;
- re-check current state when concurrency matters;
- require user approval at the intended product boundary.

Model output is a proposal until deterministic code authorizes the effect.

## Cost and latency

Budget the full pipeline:

- input/context tokens;
- output/reasoning tokens;
- retrieval/reranking calls;
- embeddings;
- tool calls;
- retries/repair loops;
- fallback models;
- cache reads/writes;
- wall time.

Optimize the dominant cost. Common high-value moves:

- better retrieval instead of larger context;
- deterministic preprocessing instead of model work;
- route bounded tasks to adequate smaller models;
- parallelize independent I/O safely;
- cache stable deterministic/retrieval results with clear freshness;
- reduce repeated agent rediscovery through project/session state.

## Observability

Capture safe metadata needed to diagnose:

- model/provider/version/config;
- prompt/template version;
- retrieval query/corpus version and doc IDs when safe;
- tool selected/result class;
- latency by stage;
- tokens/cost/cache;
- fallback/retry count;
- structured validation failures;
- user feedback/eval outcome.

Do not log secrets or sensitive raw prompts/documents by default.

## Safety and prompt injection

Treat user/retrieved/web/tool/MCP content as untrusted data.

Data-borne text cannot:

- expand permissions;
- reveal secrets;
- override system/developer policy;
- authorize destructive actions;
- change tenant/access scope.

Use least-privilege tools and data retrieval. Validate citations/provenance where grounding is required.

## Fine-tuning decisions

Fine-tune only when the failure is stable and data-driven enough to justify it.

Before training, compare simpler options:

- prompt/contract improvement;
- retrieval/data quality;
- deterministic logic;
- model routing;
- better examples;
- tool/workflow design.

If fine-tuning is chosen, build the eval harness/golden set first, freeze a base-model baseline, separate train/eval data, and gate promotion on quality + regression + cost/latency evidence.

## Edge cases

- **Good demo, poor production:** check distribution shift, retrieval freshness, tool errors, and missing hard cases.
- **LLM judge agrees with itself:** calibrate against human/reference examples and guard judge bias/leakage.
- **RAG answer hallucinated despite citation:** verify evidence actually supports the claim; citation presence is not groundedness.
- **Memory conflict:** current authoritative source wins; stale memory should be corrected/ignored.
- **Agent loops:** cap and diagnose why termination evidence is missing rather than increasing max steps.
- **Cost regression:** compare complete task cost including retries/cache/tooling, not only per-call price.
