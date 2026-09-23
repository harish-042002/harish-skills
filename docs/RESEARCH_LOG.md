# Plat Research Log

## v1.3 — Fast routing, vague intent, and trajectory correction

### Problem

Plat's router had grown heavier, vague user messages could be mishandled as either guesses or unnecessary clarification questions, and corrections could be acknowledged without invalidating the downstream decisions built on the old assumption.

### Sources inspected

#### obra/superpowers — MIT

Relevant material:
- `systematic-debugging`
- `brainstorming`
- `verification-before-completion`

Useful principles:
- use request + available context to discover intent before asking;
- ask a focused question only when missing information materially blocks the outcome;
- find root cause before fixing;
- test one hypothesis minimally;
- if a fix fails, stop and form a new hypothesis instead of stacking another patch;
- verification must precede success claims.

Not adopted:
- mandatory design approval gates for normal bounded work. They conflict with Plat's low-ceremony/fast-path goal.

#### OthmanAdi/planning-with-files — MIT

Relevant material:
- durable task_plan/findings/progress state;
- context-loss recovery;
- published eval notes.

Useful principles:
- persistent state is valuable when long tasks must survive context loss;
- current workspace/diff should be consulted when resuming;
- state must answer where we are, goal, learned facts, and completed work.

Important counter-signal:
- the project's own eval notes show structured planning carries overhead on small tasks.

Plat adaptation:
- keep session state optional;
- never inject/rebuild it every turn;
- create/read it only when rediscovery cost is material.

#### wshobson/agents — MIT

Relevant material:
- context-management restore workflow;
- parallel-debugging.

Useful principles:
- incremental/lazy context restoration;
- explicit context/token budgets;
- dynamic expansion only when relevance justifies it;
- competing hypotheses are useful for genuinely ambiguous debugging;
- evidence strength/confidence should influence arbitration.

Plat adaptation:
- depth-specific context budgets;
- do not parallelize hypotheses by default;
- use competing hypotheses only when several plausible causes remain after cheap evidence.

#### Trail of Bits skills — CC BY-SA 4.0

Relevant material:
- differential-review README.

Useful principles:
- risk-first analysis;
- blast-radius estimation;
- use history to understand risky changes/regressions;
- adaptive depth.

License decision:
- concepts only; no copied/adapted text or code is included in Plat because Plat remains MIT.

Plat adaptation:
- blast-radius/history checks are conditional, not default;
- use them for structural/public/security/value-transfer/high-impact changes where they can change the decision.

### v1.3 behavior target

- vague messages inherit only evidence-supported active intent;
- one safe interpretation → act;
- multiple materially different interpretations → inspect cheaply, then ask one question if still unresolved;
- simple tasks stay on a zero/one-reference fast path;
- structural corrections invalidate dependent decisions and re-route;
- failed verification can invalidate the current model rather than trigger patch stacking;
- repository/history/blast-radius exploration stops once ownership, impact, and direct proof are clear.


### Daily update-check research

#### vercel-labs/skills — update/check implementation

Relevant material:
- `src/update.ts`
- update tests and CLI routing

Useful principles:
- update checks should be deterministic and non-interactive when automated;
- source/version state should be tracked outside agent reasoning;
- update failure should not corrupt or remove the current installed skill;
- current installation scope/path matters when deciding what is outdated.

Plat adaptation:
- background checker uses the GitHub Releases API once per day;
- installed Plat paths are registered in `~/.plat/installations.json`;
- results are cached in `~/.plat/update-status.json`;
- update-check failure is non-fatal and never affects engineering work;
- the checker **notifies only**; it does not silently replace a skill mid-session.

Market result:
- the major skills inspected did not provide a cross-platform once-daily background update scheduler, so Plat implements this with native user schedulers (LaunchAgent / systemd-or-cron / Windows Scheduled Task) rather than adding runtime agent instructions.


## v1.5 — External specialist federation and evidence arbitration

### Problem

Plat's built-in references intentionally stay smaller than entire dedicated skill ecosystems. For very complex tasks, copying every specialty into Plat would make the hot path heavier, duplicate upstream knowledge, and age badly. The target is to keep Plat as the lead router/orchestrator while reusing already-installed deep specialist skills only when they can change the outcome.

### Sources inspected

#### wshobson/agents — MIT

Relevant material:
- `docs/agent-skills.md`
- `parallel-debugging`

Useful principles:
- large skill ecosystems can stay token-efficient through progressive disclosure;
- specialist capabilities should be independently installable;
- ambiguous debugging benefits from competing hypotheses and evidence arbitration;
- evidence quality matters more than specialist count.

Plat adaptation:
- internal Plat references remain the first, cheap tier;
- installed external skills become an optional specialist bench;
- one specialist is consulted first; parallel work requires independent questions;
- P-01 integrates by evidence rather than majority vote.

#### vercel-labs/skills — MIT

Relevant material:
- installed skill listing/discovery;
- documented project/global skill locations;
- copy/symlink installation model.

Useful principles:
- installed skills are discoverable as filesystem packages;
- project-local and global scopes can coexist;
- metadata-first discovery avoids loading all skill bodies.

Plat adaptation:
- `scripts/discover_skills.py` scans supported project/global skill roots;
- project-local duplicate wins over global duplicate;
- only candidate metadata is read first;
- the full `SKILL.md` of one best candidate is loaded only after the selection gate.

#### Anthropic skills/tool-use documentation — public reference

Useful principle:
- tool/skill libraries scale better when the agent searches/discovers only relevant capabilities rather than loading every definition up front.

Plat adaptation:
- external specialist discovery is conditional and lazy;
- no universal slash-command behavior is assumed;
- native host activation is preferred when available, otherwise the installed `SKILL.md` is consulted directly.

No Anthropic code/text was copied into Plat.

#### obra/superpowers — MIT

Relevant principles retained:
- root-cause evidence before fixes;
- failed hypotheses are retired rather than patched over;
- specialist/process invocation should match the actual task.

### Orchestrator contract

The new orchestrator uses:

```text
active intent
  -> minimum sufficient depth
  -> internal specialist first
  -> external installed specialist only if a concrete unresolved capability remains
  -> bounded evidence packet
  -> evidence/confidence response
  -> P-01 arbitration
  -> direct verification
```

External skills are consultants, not authority. Current developer intent and repository/runtime evidence remain above all specialist advice.

### Cost controls

- Quick tasks: zero external skills.
- Ordinary Standard tasks: normally zero external skills.
- Deep/Research: discover externally only for a concrete unresolved specialty.
- Load one candidate first.
- A second specialist must be evidence-earned.
- Parallel specialists require independent work and critical-path benefit.
- Stop orchestration once another specialist is unlikely to change the decision.
