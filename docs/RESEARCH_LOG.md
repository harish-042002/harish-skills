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
