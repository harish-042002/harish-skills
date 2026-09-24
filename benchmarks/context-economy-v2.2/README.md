# Plat v2.2 Context Economy Benchmark

This benchmark records the real Claude Code trajectory that motivated Plat v2.2. The task quality was strong and runtime was far better than earlier multi-hour Plat sessions, but context economics deteriorated sharply.

## Observed trajectory

The later session snapshot reported:

- cost: **$29.41**
- API/model time: **43m 17s**
- active time: **34m 02s**
- cache read: **108.1M**
- cache write: **797.3K**
- cache hit: **99%**
- `/platSkill` usage share: **70%**
- Sonnet: **90M cache read / 2.5K output**
- Opus: **18.1M cache read / 66.1K output**

The engineering result itself remained strong: broad backend/mobile regression evidence, explicit separation of pre-existing integration/environment failures, and clear remaining device-only validation. The optimization target is therefore **not less verification**. It is less model-visible output and less replay of already-known evidence.

## v2.2 hypothesis

Plat v2.2 adds four controls:

1. **Output firewall** — noisy commands store full output under `.plat/logs/` and return only a bounded evidence summary.
2. **Context watchdog** — host-neutral proxies detect large/repeated output before provider token telemetry is available.
3. **Fresh-context worker** — one isolated execution worker may be used when context is RED; this is garbage collection, not specialist fan-out.
4. **Brain packet** — Brain input is deterministically capped at 4 KB and excludes full chat/log streams.

## Controlled rerun

Use the same repository tips, task prompt, Claude Code version, selected models/settings, permissions, and verification requirements.

Run at least three repetitions per arm:

- v2.1 control;
- v2.2 candidate.

Primary endpoint: same requested behavior and verification quality.

Secondary endpoints:

- active/wall time;
- API/model time;
- cache read/write;
- output tokens;
- raw command bytes returned to model;
- repeated file reads;
- broad-suite count;
- Brain reviews;
- fresh-context worker count;
- repair turns;
- total cost.

## Candidate gates

Targets, not achieved claims:

- preserve correctness;
- active time <=35 minutes for this task shape;
- cache read <40M, stretch <25M;
- cache write <500K;
- zero large raw command/test dumps in model context;
- <=1 fresh-context worker per active slice;
- Brain packet <=4 KB;
- normally <=1 broad final regression per repo state.
