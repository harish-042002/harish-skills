# Plat v2.3 Cross-Agent Context Benchmark

v2.3 changes the context-control transport, not the engineering quality bar.

## Arms

For each coding-agent host that can run the frozen task:

1. **Proxy-only** — disable host telemetry/hooks; use returned bytes, reads, repeated reads, large outputs, and broad-suite count.
2. **Telemetry** — expose canonical token/cache/context metrics when the host supports them.
3. **Telemetry + lifecycle** — additionally route the host's pre-compaction event through Plat when the host supports hooks.

Do not invent missing host capabilities. A host with no telemetry/hook support participates only in arm 1.

## Keep fixed

- same repository commit and dirty state;
- same task prompt and acceptance criteria;
- same host/model/effort/permissions within that host comparison;
- same required tests and completion bar;
- same Plat release.

Run at least three fresh sessions per available arm.

## Capture

- correctness / scope fidelity;
- wall and aggregate model/API time when available;
- input/output/cache read/cache write/cost when available;
- model-visible command/read bytes;
- file reads and repeated reads;
- evidence-mask hits;
- broad-suite count;
- compactions/checkpoints;
- fresh-context worker count;
- Brain reviews;
- repair turns.

## v2.3 success condition

The common proxy-only arm must remain correct on every host. Rich telemetry/hooks may improve economics or trigger isolation earlier, but must not be required for successful completion.

For the existing Claude Code task shape, keep the v2.2 candidate target of <40M cache reads (stretch <25M) with verification quality preserved. Do not generalize that numerical target to hosts that report tokens/cache differently.
