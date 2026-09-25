---
name: plat
description: Evidence-led software implementation, debugging, review and migration with minimal overhead. Use for coding tasks that need scope fidelity and verified behavior. Keep small edits direct; add references, state or specialist review only for a concrete unresolved risk. Skip obvious single-line edits unless explicitly invoked. Not for non-engineering requests.
---

# Plat

Optimize for a correct, complete result with the least total work, not the fewest tokens in one answer. Follow host permissions and higher-priority instructions.

## Default loop

1. Lock the requested outcome, exclusions and proof. For a small task, keep this in working context; do not generate a plan document or state file.
2. Locate the owner and an existing analogous implementation or relevant test. Use targeted searches; inspect until the required change and proof are clear, then edit. Do not inventory the repository by default.
3. Make the smallest complete change. Preserve existing conventions and unrelated work. Do not add abstractions, dependencies, telemetry or product behavior without necessity.
4. Run fresh evidence after the final relevant edit: the focused behavior check plus checks required by actual blast radius. Inspect the diff. Finish when the requested outcome is proven.

Use the latest developer request/correction for scope; use current repository/runtime evidence over stale capsule facts. Never silently remove a requirement to meet an effort budget.

## Scale effort, not ceremony

**DIRECT:** obvious, local, reversible task. Target -> edit -> proof -> finish. Zero subagents, external skills, extra references, capsule writes, telemetry polls or review packets by default.

**STANDARD:** ordinary feature or bug. One lead, 0 specialists by default. Load at most one relevant knowledge card if it resolves a named question. Keep a brief requirement-to-proof checklist for multiple outcomes; it need not be a file.

**ESCALATED:** destructive data, security, concurrency, public contracts, production-only failures or genuinely unresolved cross-boundary reasoning. Add only the relevant checks. High risk does not automatically require a second agent. Use `references/orchestration.md` only when a bounded specialist or Brain review is justified. Keep the current capable model; do not research model catalogs mid-task.

## Stop waste without hiding failures

Do not repeat a failed command or hypothesis unchanged. After two failures on the same question, diagnose the missing evidence, environment or authority; change approach once or report a precise blocker. More reasoning cannot supply missing credentials or a missing service.

For extended work, check progress at natural boundaries, not in extra polling turns. Five minutes without progress is a reason to narrow or stop exploration, not automatically create a reviewer. Long commands need an explicit timeout; polling or waiting is not progress. A legitimate long build may use a longer declared timeout.

Do not rerun a full suite after each small edit. Widen testing for shared logic, integration or release risk. Preserve actual failure/skip/error counts; do not relabel failures as zero because they seem unrelated. Claim a failure is pre-existing only with baseline evidence.

## Optional continuity and runtime

Load `references/runtime.md` only for noisy output, genuine context pressure, long-task continuity or host integration. Prefer adequate native host tools; helper scripts are optional, not startup requirements. A skill cannot enforce host-wide token, money or elapsed-time limits by prose.

Never confuse cumulative cache traffic or read counts with current context occupancy. Never treat an unread/truncated range as consumed. After confirmed compaction or handoff, reset the context epoch and read the complete active contract before resuming.

## Knowledge cards

Use only a relevant card under `references/`: `repository-understanding.md`, `debugging.md`, `backend.md`, `frontend.md`, `flutter-mobile.md`, `database.md`, `api.md`, `security.md`, `testing.md`, `performance.md`, `delivery.md`, `ai-engineering.md`, `planning.md`. Do not follow reference-to-reference chains automatically.

## Correct and close

On a correction, remove only task-local changes that depended on the rejected assumption; preserve independently valid and user-authored work. Revalidate the changed scope.

Report what changed, what was actually verified and what remains. For multiple required outcomes, mark each done, unverified or blocked. Missing proof is not a pass. Stop after meeting the contract; do not launch another audit merely to appear thorough.
