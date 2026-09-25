# Optional runtime and host integration

Load only for long-task continuity, noisy output, genuine context pressure or integration work. These helpers do not run automatically just because Plat is installed. Prefer host-native equivalents when they already provide the required guarantee.

## Command limits and evidence

`scripts/evidence_exec.py --timeout-seconds 120 -- <command> <args>` runs a non-interactive, finite command. Set a longer declared timeout for a known long build; do not restart a timed-out command unchanged. The 120-second default is a starting policy, not a universal build limit.

It returns at most 6 KB by default and persists captured output under `.plat/logs/`. Exit 124 means timeout, 125 means output limit; other exit codes are preserved. `--max-output-bytes` defaults to 16 MiB: a polled termination threshold, not an operating-system disk quota. Capture is disk-backed. The excerpt is not the whole log: inspect exact ranges when needed. Never infer all tests passed from a partial excerpt.

POSIX process groups are terminated; Windows uses taskkill for live processes. Windows/macOS execution is not validated by the Linux-only candidate tests. Do not use this runner to launch a server, daemon or interactive prompt. It intentionally stops ordinary descendants of finite POSIX commands. It is not a sandbox against deliberately detached processes.

## Safe source reads

`scripts/evidence_read.py FILE --start N --end M` returns a bounded range with its SHA-256. Only a fully delivered, unchanged range in the same context epoch may be masked. Use `--refresh` for a new question requiring exact content.

When `truncated=true`, continue with the returned `next_offset` using `--offset`, the same line range and `--expected-sha256` from the first page. Offset units are characters in the exact decoded requested range (LF/CRLF and final newline are preserved). A changed source rejects continuation rather than stitching different versions. Partial pages are never marked as a fully consumed range.

## Context and cost are different measurements

`host_context.py` accepts explicit telemetry JSON/file or a recognized transcript. Explicit live inputs precede the saved telemetry cache. Known per-message usage is summed once per ID using the latest message record; known cumulative snapshots replace prior totals. Missing counters stay missing. Unknown transcript schemas are not evidence of zero usage. One transcript must represent one session, not concatenated independent sessions.

`context_guard.py` separates current occupancy from repetition warnings. Real occupancy at 65% warns; at 80% it permits recovery. These are tunable starting thresholds, not provider limits. Read counts, returned bytes and cumulative cache replay can warn about efficiency, but cannot by themselves force a new worker or compaction. Current measured occupancy wins over proxies. Do not derive context usage from accumulated input/output totals.

A saved telemetry cache preserves its observation time and does not establish fresh occupancy. Host adapters must provide accurate, current measurements; these scripts cannot discover hidden model reasoning or host cache accounting universally.

## Continuity without replay

Use `task_state.py` and `references/context.md` only when a resumable capsule saves real rediscovery. A pending operation requires `checkpoint --waiting --waiting-until ISO_TIMESTAMP`; an absent or expired deadline yields BLOCKED, not indefinite GREEN. Keep all binding requirements; optional prose can shrink, requirements cannot disappear. `brain_packet.py` rejects a contract that cannot fit its default 4 KB limit instead of silently clipping requirements. Use a verified shared contract, a genuinely independent slice or an explicit larger packet; never repeatedly retry the same oversized brief.

Before compaction, `precompact_checkpoint.py` records task truth and evidence pointers. `context_hook.py` handles PreCompact only if explicitly wired into a supported host. After the host actually replaces context, run `context_guard.py reset`, not before. Reset clears epoch-local counters and masking while retaining the task's fresh-worker budget. A new task uses `start`. Host context replacement is not something this script performs.

## Integration boundary

The installer wires skill instructions, not universal tool interception. No script here prevents an agent from using an unwrapped tool. Configure host time/token/spend limits where supported and record whether enforcement is active. Do not claim hard task budgets when only advisory instructions are installed. Unknown isolated-context capability defaults to unavailable.

For diagnostics, record task identity, model/effort, skill version, actual wall time, tool duration, call count, retries, compact events, per-request usage and provider-reported cost when available. Do not run telemetry polling just to populate a dashboard. Never store secrets or private source unnecessarily.

Telemetry terminal results are aggregate snapshots, not additional model requests. Reasoning tokens are a subset of output tokens when the provider defines them that way; never bill both again. Host-reported cost is not an invoice. Unknown costs must remain unknown, never zero.
