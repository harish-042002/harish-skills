# Subagents and Delegation

Use only when a bounded specialist or independent partition demonstrably reduces critical-path time, isolates fresh judgment, or supplies a capability the lead lacks.

## Default

The Plat lead owns architecture, integration, shared contracts, scope, final verification, and the completion claim.

- DIRECT: 0 subagents.
- STANDARD: 0 subagents.
- ESCALATED: at most 1 initially.
- Research: lead orients first with 0; normally 1 batched read-only scout after partitioning.

Do not delegate simply because a task is large or a specialist exists.

## Good delegation

- one concrete unresolved specialist question;
- independent read-only comparison across a bounded partition;
- fresh review after a stable high-risk implementation;
- mechanical work where a cheaper current model tier is adequate and repair risk is low.

Poor delegation:

- tiny/standard tasks;
- unsettled architecture;
- sequential work where one result determines the next;
- overlapping repository discovery;
- multiple agents mutating the same shared state.

## One-level topology

Workers never recursively spawn skills/agents on Plat's behalf. If another capability is needed, return `Needs: <capability>` to the lead.

## Dispatch contract

Send only:

```text
GOAL
QUESTION/TASK
DECISIVE EVIDENCE POINTERS
SCOPE / DO-NOT-CHANGE
PROOF
RETURN FORMAT
```

Reference paths instead of pasting large files or conversations.

## Model selection

Use capability tiers, not hardcoded model names. Name a concrete model only at runtime when the host exposes current choices.

- bounded read/mechanical -> lowest adequate current tier;
- subtle debugging/architecture/high-risk review -> stronger current tier;
- Brain reviewer -> one stronger cost-effective tier than the normal worker when possible.

## Acceptance

A worker saying "done" is not proof. Plat checks returned evidence and performs the final focused verification.
