# Plat v1.8 Behavioral Evaluation Harness

This is the current-version behavioral evidence lane for Plat. It is intentionally separate from Plat's deterministic routing/unit tests.

## What it measures

The harness runs a coding agent against frozen mini-repositories and records whether the final workspace satisfies an independent verifier while respecting scope constraints.

Primary dimensions:

- requested-behavior correctness;
- forbidden-scope violations;
- mid-task correction recovery;
- unnecessary changed files/LOC;
- runtime/deployment safety where the task requires it;
- wall time and optional agent telemetry (tokens, cost, tool calls, repair turns).

The included cases cover the real notification misunderstanding class, a tiny negative control, and AWS-specific idempotency/account-region/IAM behavior.

## Important evidence boundary

Shipping this harness improves **behavioral-evaluation maturity**, not live-agent success by itself. A current Plat version earns live-result points only after repeated fresh-session trajectories are captured and published.

## Agent adapter contract

`run_behavioral_eval.py` is host-neutral. Supply an agent command that is invoked once per turn. The runner exposes:

- `PLAT_EVAL_WORKSPACE`
- `PLAT_EVAL_CASE_ID`
- `PLAT_EVAL_TURN_INDEX`
- `PLAT_EVAL_TURN_FILE`
- `PLAT_EVAL_TRANSCRIPT_FILE`
- `PLAT_EVAL_RESULT_FILE`
- `PLAT_EVAL_CONDITION`

The agent command should edit `PLAT_EVAL_WORKSPACE`. It may optionally write JSON to `PLAT_EVAL_RESULT_FILE` containing numeric telemetry such as:

```json
{
  "input_tokens": 1234,
  "output_tokens": 456,
  "cache_read_tokens": 1000,
  "tool_calls": 18,
  "repair_turns": 1,
  "cost_usd": 0.42
}
```

The full transcript file contains all developer turns seen so far so wrappers can maintain context even when the underlying CLI uses fresh invocations.

## Usage

Validate the frozen case pack:

```bash
python benchmarks/behavioral-v1.8/run_behavioral_eval.py --plan
```

Run one agent/condition, 3 repetitions:

```bash
python benchmarks/behavioral-v1.8/run_behavioral_eval.py \
  --agent-command './my-agent-wrapper.sh' \
  --condition plat \
  --repetitions 3 \
  --results /tmp/plat-v18-results.json
```

Run a control arm separately with the same model/settings/repository state:

```bash
python benchmarks/behavioral-v1.8/run_behavioral_eval.py \
  --agent-command './my-no-plat-wrapper.sh' \
  --condition no-plat \
  --repetitions 3 \
  --results /tmp/no-plat-v18-results.json
```

Score/compare captured runs:

```bash
python benchmarks/behavioral-v1.8/score_results.py /tmp/plat-v18-results.json /tmp/no-plat-v18-results.json
```

## Release rule

Do not raise Plat's live-behavior claims from `--plan`, fake adapters, unit tests, or policy inspection. Publish the raw trajectory result JSON and verifier outcomes for the actual model/host runs being claimed.
