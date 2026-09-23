# Plat Maintenance Protocol

Every material change to Plat must begin with external evidence, not only local intuition.

## Mandatory sequence

1. **Define the failure or capability**
   - What concrete behavior is wrong, missing, slow, or expensive?
   - What regression case will prove the change?

2. **Scan relevant public work first**
   - Inspect at least 2-3 strong public skills/projects that solve the same or adjacent problem.
   - Prefer current repositories with real usage, explicit methodology, tests/evals, or known failure-mode documentation.
   - Record what is genuinely relevant; do not copy a whole workflow merely because it is popular.

3. **Check licensing before reuse**
   - MIT/Apache/BSD: code/text may be reused only with required notices.
   - Copyleft/ShareAlike licenses: do not copy/adapt text/code into Plat unless the resulting licensing obligations are intentionally accepted.
   - Unknown/no license: inspiration only; no code/text reuse.
   - Prefer re-implementing the principle in Plat's own architecture unless literal reuse has a clear benefit.

4. **Extract the principle**
   - State what the external work proves or suggests.
   - State what Plat should adopt.
   - State what Plat should deliberately reject because it increases ceremony, context, or conflicts with Plat's goals.

5. **Implement the smallest useful delta**
   - Preserve Plat's core priorities: correctness first; then minimum total tokens, tool calls, rereads, repair turns, coordination, and wall time.
   - Do not add a new runtime step unless its expected value exceeds its permanent overhead.

6. **Test the behavior**
   - Reproduce the original failure.
   - Add adversarial/regression cases around likely edge conditions.
   - Compare against the prior behavior when possible.
   - Test speed/context overhead for changes to routing or always-loaded instructions.

7. **Validate and package**
   - Validate the Skill structure.
   - Package the full skill as `skill.zip`.
   - Update VERSION/release notes only after behavior is validated.

8. **Publish evidence**
   - Update benchmark/limitation docs when the change affects a public claim.
   - Keep failed cases visible.

## Market scan record

For each material change, keep **both** records current:

1. append a human-readable entry to `docs/RESEARCH_LOG.md`;
2. append/update the machine-readable release entry in `docs/maintenance-evidence.json`.

The machine record must include:

- a stable evidence ID and date;
- capability/failure being changed;
- every material file covered by the evidence;
- at least 2 relevant public sources;
- source license and reuse mode (`principle-only`, `adapted`, or `copied`);
- adopted principles;
- rejected patterns and why;
- tests added/run.

`scripts/maintenance_gate.py` enforces this for material Plat changes in CI. The human research log must reference the same evidence ID and inspected repositories.

This gate is deliberately **repository-maintenance only**. It must never be called from Plat's normal engineering runtime.

## What this protocol must NOT become

Do not run a market scan during normal end-user engineering requests. This protocol is for **developing Plat itself**.

Do not search the market for trivial documentation fixes where external comparison cannot materially improve the change.

Do not treat popularity/stars as proof of correctness. Use implementation details, methodology, tests/evals, and observed failure handling as stronger evidence.
