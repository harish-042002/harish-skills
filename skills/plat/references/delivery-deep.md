# Deep Delivery, Release, and Infrastructure Engineering

Use for high-risk deployments, schema/app coexistence, canary/progressive rollout, complex IaC, multi-region changes, disaster recovery, or CI/release failures spanning several systems.

## Contents

1. Objective
2. Artifact and environment truth
3. Compatibility order
4. Rollout strategies
5. Health and observation
6. Rollback vs forward-fix
7. Feature flags
8. Infrastructure as code
9. CI and supply-chain boundaries
10. Secrets/IAM/network
11. Disaster recovery
12. Release verification
13. Edge cases

## Objective

Ship changes so old/new versions can coexist where necessary, failure is observable, and recovery is possible without improvising under pressure.

## Artifact and environment truth

Identify:

- exact source commit;
- immutable artifact/image/package/version;
- environment/region/account/project;
- config/secret versions;
- schema/migration dependencies;
- infrastructure plan/state;
- runtime feature flags.

Do not assume a green build proves the intended artifact reached the intended environment.

## Compatibility order

For distributed/schema changes, deploy in an order that preserves overlap:

1. additive compatible backend/schema/contract support;
2. deploy producers/consumers that tolerate both states;
3. migrate/backfill/enable traffic progressively;
4. observe;
5. remove old behavior only after usage/version evidence supports it.

Test overlap, not just start and end state.

## Rollout strategies

Choose only when they reduce real risk:

- rolling deployment;
- canary percentage/cohort;
- blue/green;
- region-by-region;
- feature flag/dark launch;
- shadow traffic where privacy/load semantics allow.

Define promotion/abort signals before rollout.

## Health and observation

Health should reflect ability to serve intended traffic.

Use relevant:

- readiness/liveness/startup distinctions;
- error/latency/saturation;
- queue/backlog;
- DB/replication health;
- business success signal;
- version/config labels.

A process being alive is not enough.

## Rollback vs forward-fix

Rollback is only safe if state/contracts remain backward compatible.

Ask:

- did schema/data migrate irreversibly?
- did clients/events begin using new fields/semantics?
- did external side effects occur?
- will old code understand new data?

When rollback is unsafe, prepare a forward-fix/disable/reconciliation path instead of pretending rollback exists.

## Feature flags

Flags need ownership and removal criteria.

Define:

- default by environment/cohort;
- server/client authority;
- behavior when flag service unavailable;
- data/schema coexistence;
- test matrix for on/off during transition;
- cleanup date/trigger.

Long-lived flags can become hidden architecture and test explosion.

## Infrastructure as code

Before apply:

- validate/plan;
- inspect create/update/replace/destroy;
- verify target workspace/account/region;
- understand state locking/backend;
- check dependency/ordering and data resource protection;
- review IAM/network exposure;
- define recovery.

Never normalize destructive apply as routine automation without explicit authorization.

## CI and supply-chain boundaries

Treat CI as privileged production-adjacent infrastructure.

- least-privilege workflow tokens;
- protect secrets from untrusted fork/PR code;
- pin/constrain actions/images/tools according to repo policy;
- preserve artifact provenance/integrity where supported;
- distinguish cache optimization from cache poisoning/trust risk;
- avoid downloading/executing arbitrary build scripts with privileged credentials.

## Secrets/IAM/network

For deployment changes verify:

- secret source/rotation/least privilege;
- workload identity vs long-lived credentials;
- environment separation;
- IAM diff;
- ingress/egress/security-group/firewall changes;
- private/public endpoint intent.

Do not print secrets while debugging CI.

## Disaster recovery

When the system promises recovery, identify:

- RPO/RTO expectation;
- backup/snapshot frequency and retention;
- restore procedure;
- dependency/order;
- DNS/traffic failover;
- data consistency/reconciliation after restore;
- whether restore has actually been tested.

A backup that has never been restored is weaker evidence than a tested recovery procedure.

## Release verification

Use the smallest evidence that proves each layer:

```text
source -> artifact build
artifact -> deployed version
runtime -> health/smoke
integration -> critical flow
state -> migration/data correctness
observability -> no material regression
```

Record what was and was not verified.

## Edge cases

- **DB migration succeeds then app rollback:** old binary may not understand new schema/data.
- **Canary shares queue/database:** canary blast radius may exceed traffic percentage; account for shared side effects.
- **Feature flag client-controlled:** protected invariant still requires backend authority.
- **IaC says no change but console drift exists:** inspect drift/import/reconciliation before assuming environment matches code.
- **CI cache makes failure disappear:** verify clean build path before concluding root cause fixed.
