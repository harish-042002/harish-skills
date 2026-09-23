# Deep AWS Engineering

Use when the unresolved engineering boundary is specifically AWS: service selection, IAM, account/region safety, serverless/event semantics, containers, networking, data services, IaC/deployment, observability, cost, quotas, resilience, or incident diagnosis. Load only after the basic owning domain is known; do not use this file merely because a repository happens to deploy to AWS.

## Contents

1. Objective and freshness rule
2. Account, region, identity, and blast radius
3. Workload classification and service selection
4. IAM and trust boundaries
5. Networking and connectivity
6. Compute and serverless
7. Messaging, events, and workflows
8. Data and storage
9. IaC and deployment safety
10. Observability and operations
11. Reliability, backup, and disaster recovery
12. Performance, quotas, and scaling
13. Cost discipline
14. Security and data protection
15. Incident diagnosis
16. Verification matrix
17. Cross-domain routes
18. AWS anti-patterns

## Objective and freshness rule

Make AWS decisions from the **current workload, current account/region/version, and current AWS documentation**, not generic cloud memory.

Use the AWS Well-Architected pillars as review lenses when material: operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability. Do not turn every AWS edit into a full Well-Architected review.

Version-sensitive or quota-sensitive facts change. Before making a production decision about service availability, runtime versions, quotas, pricing, regional support, API behavior, or newly released features, verify current official AWS documentation or current AWS tooling when available.

## Account, region, identity, and blast radius

Before any production-impacting AWS action, establish the target:

```text
account / organization
region / partition
role or profile
workload / environment
IaC stack/workspace
resource identifiers
blast radius
```

For read-only diagnosis, confirm target context when confusion is plausible. For mutation/deploy/delete, target identity is mandatory evidence.

Useful read-only checks include:

```bash
aws sts get-caller-identity
aws configure get region
aws configure list
```

Do not assume `us-east-1`, the default CLI profile, or the currently logged-in account is correct. In multi-account systems, prefer explicit workload identity and environment separation over naming conventions inside one account.

Never execute a destructive or high-impact AWS operation merely because an IaC/CLI command is available. Inspect the plan/diff and get the authorization required by the parent task.

## Workload classification and service selection

Choose services from workload constraints, not familiarity.

Ask only the dimensions that change the decision:

- request/traffic shape: steady, bursty, scheduled, event-driven;
- execution duration and runtime constraints;
- statefulness and data consistency;
- latency/SLO;
- scaling envelope and quotas;
- networking/private-resource needs;
- compliance/tenant isolation;
- operational ownership;
- cost model;
- recovery expectations.

Typical compute routing:

- **Lambda**: event/request driven, bounded execution, automatic scaling, minimal server operations.
- **ECS/Fargate**: containerized long-running services/jobs where Kubernetes is unnecessary.
- **EKS**: Kubernetes is already an organizational/platform requirement or its ecosystem materially pays for the complexity.
- **EC2/Auto Scaling**: host-level control, special runtimes/networking/storage, persistent processes, or economics justify owning instances.
- **Managed service integration**: prefer direct service integrations when they remove custom compute without hiding required business logic.

Do not split a working system across AWS services merely because AWS offers a managed component for each concern.

## IAM and trust boundaries

AWS identity is part of the application security model.

Defaults:

- human access should use federation/SSO and temporary credentials;
- workloads should use IAM roles/temporary credentials, not embedded long-lived keys;
- start from required actions/resources, then grant least privilege;
- distinguish identity policies, resource policies, permission boundaries, session policies, SCPs, and service control behavior;
- protect cross-account/service trust against confused-deputy paths with appropriate source/account/resource conditions when supported;
- validate policy semantics before claiming least privilege.

Before widening permissions because something returns `AccessDenied`, identify the denied principal, action, resource, explicit-deny layers, trust policy, resource policy, KMS policy, VPC endpoint policy, and Organizations controls that can participate.

Never fix IAM by adding `Action: "*"` or `Resource: "*"` unless the service semantics genuinely require it and the blast radius is explicitly accepted.

## Networking and connectivity

For a connectivity failure, trace the complete path instead of randomly changing security groups:

```text
name resolution
-> route
-> subnet / route table
-> IGW / NAT / TGW / peering / endpoint
-> security group
-> NACL
-> load balancer / listener / target
-> service policy / TLS / application
```

Remember the important distinctions:

- security groups are stateful; NACLs are stateless;
- public IP, public subnet, and internet reachability are not the same property;
- private AWS API access may use VPC endpoints/PrivateLink instead of NAT where appropriate;
- NAT gateways and cross-AZ/cross-region data transfer can be material cost drivers;
- VPC-attached Lambda/containers need actual route/DNS/endpoint reachability to dependencies;
- DNS/Route 53/resolver behavior can be the failure even when TCP rules look correct.

Do not make a workload private by default if its legitimate ingress/egress model requires public endpoints; secure the actual boundary instead.

## Compute and serverless

### Lambda

Treat event delivery as retryable unless the exact source contract proves otherwise.

- make side-effecting handlers idempotent when duplicate delivery can matter;
- bound timeouts/retries and understand the source retry policy;
- for SQS/Kinesis/DynamoDB Streams, understand batch size, partial failures, visibility/iterator behavior, concurrency, and poison-message handling;
- use reserved concurrency to protect downstream systems or isolate capacity when needed; do not set it reflexively;
- tune memory from measured duration/cost because CPU/network scale with configuration;
- keep initialization outside the handler only when reuse is safe;
- VPC-enable only for dependencies that require it;
- alarms should cover errors, throttles, duration/timeouts, concurrency pressure, DLQ/on-failure depth, and business-critical failure signals.

A module-level in-memory dedupe set is not a durable idempotency mechanism across cold starts, concurrency, or multiple execution environments.

### API Gateway / ALB / function URLs

Choose the front door from auth, protocol, routing, throttling, transformation, WebSocket, latency, and cost requirements. Do not silently switch API types or authorization models during a local change.

Validate CORS at both gateway and backend boundaries. A gateway can throttle/retry/fail independently of the application; correlate request IDs/logs across layers.

### ECS / Fargate / EKS

For container incidents inspect image/version, task/pod scheduling, CPU/memory reservations/limits, health checks, IAM/task roles, network path, secrets, autoscaling signals, load balancer registration, logs, and deployment events.

Do not treat a running task count as proof the service is healthy.

For EKS, distinguish Kubernetes control/data-plane issues from AWS VPC/IAM/load-balancer/storage integrations before changing cluster architecture.

## Messaging, events, and workflows

Assume asynchronous systems can duplicate, delay, reorder, or partially fail unless the service contract says otherwise.

### SQS

- visibility timeout must cover expected processing/retry behavior;
- choose Standard vs FIFO from ordering/deduplication requirements, not aesthetics;
- use DLQs/redrive policies for poison messages with a recovery/replay plan;
- control consumer concurrency so queues do not overwhelm dependencies;
- handle partial batch success when the integration supports it;
- delete/ack only after the intended durable state is safe.

### SNS / EventBridge

- verify filtering, retry, DLQ/on-failure behavior, target permissions, and event contract versioning;
- design consumers to tolerate redelivery;
- do not use an event bus as a replacement for an owned domain contract.

### Step Functions

Use when explicit orchestration, retries/timeouts, compensation, human callbacks, long-running coordination, or direct AWS service integrations justify a workflow state machine. Keep payloads small and avoid placing secrets in execution state/history.

Do not add orchestration merely to sequence two simple calls that already belong in one reliable transaction/application flow.

## Data and storage

### DynamoDB

Start from access patterns and authorization boundaries.

- design partition/sort keys for required queries; avoid Scan as a primary access path;
- reason about partition hot spots and write/read concentration;
- use conditional writes for concurrency/idempotency where one item owns the invariant;
- use transactions only when multiple-item atomicity is required;
- understand eventual consistency and GSI propagation before treating an index as authoritative immediately after a write;
- choose on-demand/provisioned from measured/predictable workload economics, not habit;
- TTL is asynchronous cleanup, not an exact scheduler;
- Streams consumers need retry/idempotency/replay reasoning.

### RDS / Aurora

- distinguish Multi-AZ availability from read-scaling replicas;
- size connection pools from database capacity and process/container/Lambda concurrency;
- consider RDS Proxy or equivalent connection management when bursty serverless connection pressure is the issue;
- make schema changes compatible with overlapping app versions;
- verify backups/PITR and restore procedures;
- inspect slow queries, waits, locks, indexes, connection saturation, storage/IO, and replica lag before scaling blindly.

### S3

- use least-privilege bucket/object policies and block public access unless public delivery is intentional;
- use versioning/lifecycle/replication only when they satisfy explicit retention/recovery needs;
- event notifications are not a transactional database log; consumers must tolerate duplicates and ordering limitations;
- encrypt appropriately and separate data-key/access concerns from object permissions;
- validate pre-signed URL scope/expiry/content restrictions for sensitive uploads/downloads.

### ElastiCache / Redis-compatible services

Treat cache loss/eviction/failover as normal possibilities unless the product is deliberately being used as durable state. Bound key cardinality, TTLs, connection counts, hot keys, memory, and failover behavior.

## IaC and deployment safety

Prefer the repository's current IaC dialect: CDK, CloudFormation/SAM, Terraform, or established automation. Avoid console drift except incident response; reconcile emergency changes afterward.

Before apply/deploy:

1. confirm account/region/workspace/stack;
2. synth/validate/plan;
3. inspect create/update/replace/delete and IAM/network changes;
4. protect stateful resource identity and data;
5. verify old/new app/schema/event compatibility;
6. define promotion, abort, rollback or forward-fix;
7. deploy;
8. verify runtime and business health.

CDK/CloudFormation-specific:

- logical identity changes can replace resources; treat stateful renames as migrations unless diff proves preservation;
- review `cdk diff` / CloudFormation change sets before production deploy;
- avoid hotswap/watch-style production deployment paths that bypass normal CloudFormation reconciliation;
- cross-stack exports/references require phased consumer/producer changes when removing or renaming.

Terraform-specific:

- inspect the plan and state backend/lock/workspace;
- understand `replace`, import/moved blocks, lifecycle rules, and provider version effects;
- never normalize `-target`, manual state surgery, or forced replacement as routine fixes.

## Observability and operations

An AWS workload should make it possible to answer: what failed, for whom, where, since when, after which change, and whether it is recovering.

Use the existing observability stack and relevant AWS signals:

- structured application logs with safe correlation identifiers;
- CloudWatch metrics/alarms and service-native metrics;
- CloudTrail for control-plane/API change history;
- distributed tracing where cross-service latency/failure diagnosis needs it;
- dashboards/SLOs for critical user/business flows;
- queue backlog, age-of-oldest, DLQ depth, throttles, connection saturation, replica lag, error rate, and latency where relevant.

Alarm on symptoms/actions that matter. Avoid high-volume alarms with no runbook/owner.

## Reliability, backup, and disaster recovery

Start with business RTO/RPO and failure domains.

- use Multi-AZ/service-native redundancy where it materially matches availability needs;
- multi-region is a major data/traffic/operational commitment, not a default best practice;
- define dependency degradation behavior, retry budgets, backpressure, and failover ownership;
- backups require retention, encryption, access control, and **restore testing**;
- verify DNS/traffic failover and data reconciliation for DR plans;
- include third-party/external dependencies in failure exercises.

A backup that has never been restored is not strong recovery evidence.

## Performance, quotas, and scaling

AWS failures under load are often quota/capacity/dependency problems rather than code bugs.

Check:

- service quotas and regional availability;
- Lambda concurrency / event-source scaling;
- API throttles;
- DynamoDB partition/capacity hot spots;
- RDS connections/IO/CPU/locks;
- ECS/EKS desired vs schedulable capacity;
- NAT/ENI/port/network limits;
- S3/request-pattern constraints when applicable;
- downstream vendor/API rate limits.

Measure before raising quotas or adding capacity. Verify current quota values from Service Quotas/current AWS docs before making hard claims.

## Cost discipline

Cost is part of architecture when it can change the decision.

Common AWS cost traps include:

- idle EC2/RDS/ElastiCache/EKS capacity;
- NAT gateway hourly/data processing cost;
- cross-AZ/cross-region/data egress;
- excessive CloudWatch log retention/high-cardinality custom metrics;
- over-provisioned concurrency/capacity;
- wrong S3/EBS/storage class and retained snapshots;
- chatty serverless designs with avoidable invocation/state-transition/data-transfer cost;
- missing tags/allocation boundaries that make ownership invisible.

Estimate using current AWS pricing for the actual region when cost is material. Compare cost against reliability/operational trade-offs; cheapest is not automatically best.

## Security and data protection

For AWS changes inspect the relevant subset:

- identity/least privilege and cross-account trust;
- secrets in Secrets Manager/Parameter Store or existing approved mechanism, not source/env files committed to repo;
- KMS key ownership/policies/rotation requirements;
- encryption in transit/at rest;
- public exposure and WAF/rate limits where appropriate;
- CloudTrail/audit coverage;
- vulnerability/container/image/dependency scanning where the deployment model requires it;
- tenant/data isolation at both IAM and application/data-key boundaries.

Do not add a customer-managed KMS key, private VPC, WAF, GuardDuty, Config, or Security Hub merely for checklist completeness. Add controls that satisfy an actual threat/compliance/operational requirement.

## Incident diagnosis

For an AWS incident, prefer this evidence order:

1. confirm account/region/resource/version;
2. identify first failing user/business symptom and timestamp;
3. correlate recent deploy/config/IAM/network changes;
4. inspect service-native metrics/events/logs;
5. trace the request/event path across dependencies;
6. check throttles/quotas/backlog/saturation;
7. inspect CloudTrail for control-plane changes when relevant;
8. form the smallest discriminating hypothesis;
9. run a safe read-only check or narrow reproducer;
10. fix the owning boundary and verify recovery.

Avoid console wandering across unrelated services.

## Verification matrix

Use only the rows relevant to the task.

| Change | Minimum direct proof |
| --- | --- |
| Lambda/code | unit/integration test + function config/log/runtime evidence when deployed behavior matters |
| SQS/event flow | duplicate/retry/partial-failure test + DLQ/redrive/concurrency evidence |
| IAM | policy validation + intended allow + unintended deny/privilege check |
| API Gateway | route/auth/CORS/throttle contract + representative request |
| DynamoDB | access-pattern queries/conditional-write behavior + capacity/hot-key evidence when material |
| RDS | migration compatibility + query/lock/connection evidence when material |
| CDK/CloudFormation | synth/validate + diff/change set + deployment health |
| Terraform | fmt/validate + plan + state/workspace target + post-apply health |
| ECS/EKS | task/pod health + LB/service readiness + logs/metrics + rollout status |
| Networking | DNS/route/SG/NACL/endpoint path evidence, not only ping |
| Cost | current regional pricing + representative usage assumptions/measurements |
| DR | restore/failover exercise evidence proportional to RTO/RPO claim |

## Cross-domain routes

Load only the smallest useful pair.

### Lambda duplicate side effects

`backend.md` -> if evidence proves AWS retry/event-source semantics matter, add `aws-deep.md`; add `database-deep.md` only if durable idempotency depends on database isolation/constraints.

### AWS IAM/security incident

`security.md` + `aws-deep.md` -> add `security-deep.md` only if threat/abuse analysis remains unresolved after IAM/resource-policy evidence.

### DynamoDB concurrency/data-model issue

`database.md` + `aws-deep.md` -> add `database-deep.md` for transactions/hot partitions/migration complexity.

### AWS rollout / IaC replacement risk

`delivery.md` + `aws-deep.md` -> add `delivery-deep.md` when coexistence, progressive rollout, multi-region, or DR complexity remains.

### AWS cost/performance regression

`performance.md` + `aws-deep.md`; add `performance-deep.md` only when representative load/profiling/capacity analysis is required.

## AWS anti-patterns

Reject these unless current evidence explicitly justifies them:

- broad IAM wildcard permissions to silence access errors;
- long-lived access keys for workloads;
- assuming the default account/region is the target;
- manual console changes as the normal source of truth;
- deploying an IaC diff without inspecting replacements/destruction;
- treating Lambda/SQS/EventBridge delivery as exactly-once;
- in-memory idempotency for cross-instance side effects;
- adding a VPC, NAT gateway, EKS cluster, Step Functions workflow, multi-region topology, or custom KMS key because it sounds enterprise-grade;
- treating Multi-AZ as a backup strategy or read replica as Multi-AZ failover;
- scaling resources before checking quotas, saturation, locks, hot partitions, or downstream limits;
- claiming AWS production readiness from unit tests or a green pipeline alone;
- quoting remembered pricing/quotas/feature availability when the decision depends on current values.
