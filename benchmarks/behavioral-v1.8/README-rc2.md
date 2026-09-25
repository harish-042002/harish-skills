# Plat 2.4.0-rc.2: reproducible benchmark package

This candidate includes the prior rc1 fixes and the runtime/evaluator fixes found
by the 25 September 2026 follow-up. GitHub and installed agents are unchanged.

## What has actually run

- 166 tests pass locally, including restored behavioral fixture tests and new
  evaluator/runtime/schema boundary tests. Scripted fixture adapters are unit
  tests, NOT model trajectories.
- Five runtime operations, three versions, 15 timed samples each: 225 samples.
  Warmups and Python allocation probes are excluded from timed samples.
- Three deliberately invalid solutions pass old verifiers and fail the corrected
  verifiers. Valid reference solutions also pass the unit checks.
- Live comparison preflight was invoked with --run but stopped before model calls:
  no Codex CLI or local credentials in this environment. Actual cost is unknown.

## Local verification

From candidate/:

```sh
python -m pip install -r benchmarks/requirements.txt
python -m unittest discover -s tests -p 'test_*.py'
python scripts/validate_plat.py
python -m compileall -q scripts skills/plat/scripts tests benchmarks
bash -n install.sh
```

PyYAML is an evaluation dependency, not a skill runtime dependency. Native Windows
and macOS integration, hosted CI and native Codex execution were NOT tested here.

## Reproduce runtime results

From the package root:

```sh
python run_balanced.py
python replay_verifiers.py
```

run_balanced.py preserves completed files on restart. To do a completely fresh
measurement, move results/balanced/ elsewhere first. The measured operations are
file-read helpers, transcript parsing, and a wrapped trivial Python command.
They do not measure model reasoning, coding quality, tokens, or invoice cost.

## Native coding-agent comparison: requires your authenticated host

Install/login to Codex through its official setup on your machine. No credentials
should be pasted into chat or put into the benchmark artifact directory.
Use a disposable environment; these are trusted fixtures, not an adversarial-agent
sandbox. The launcher uses an isolated temporary HOME/CODEX_HOME and workspace-write
sandbox, copies local auth only into that temporary directory, then deletes it.

From candidate/, start with a single-case smoke comparison:

```sh
python benchmarks/behavioral-v1.8/run_comparison.py \
  --model YOUR_EXACT_AVAILABLE_MODEL_ID --effort low \
  --baseline ../baseline/skills/plat \
  --case tiny-timeout-only --repetitions 1 \
  --timeout 180 --output ../live-smoke
```

That is preflight only. Add --run to invoke the model (may consume paid usage).
The model name and effort must actually be supported by your host; no particular
Luna identifier or model price has been assumed or verified here.

After that smoke run succeeds, omit --case and use --repetitions 3 with a new
--output directory. That plans 45 task runs (5 cases x 3 arms x 3 repetitions),
up to 63 model invocations because one case has three user turns. Each case has a
180-second agent deadline plus up to 30 seconds for the independent verifier.
This is a time bound, NOT a dollar cap. Stop rather than buying an expensive run
merely to finish the matrix. Do not run the model inside the timing microbenchmark.

Arms are no-Plat, original v2.3, and candidate. Each uses the same requested model,
effort, fixture, and verifier; arm order rotates. Raw stdout/stderr, manifests,
changed files, requested settings, usage coverage and hashes are retained.
Each user turn starts a fresh CLI process with the current workspace, prior user
requirements, and prior final responses; it is not a native resumed-session test.
Provider cache state is not controlled. Generic adapters need their own isolation
and telemetry validation. Only the Codex adapter is supplied here; its schema and
preflight are tested, but a live host integration remains unverified.

Optional --rates PATH takes JSON with model, input_usd_per_million,
cached_input_usd_per_million and output_usd_per_million. Supply current verified
rates yourself. Those produce estimated_cost_usd, never actual invoice charges.
Cached input is a subset of input for this adapter; reasoning output is not charged
twice. Missing/partial telemetry is not silently converted to free usage.

```sh
python benchmarks/behavioral-v1.8/score_results.py ../live-results/results.json --json
```

Do not claim a speed/cost win unless task completion and scope are acceptable.
A tiny five-task fixture pack is a pilot, not certification of all models/projects.
Treat old trigger-cases.json as a historical corpus, not a newly measured result.
