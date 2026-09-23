# Delivery, CI/CD, IaC, and Git Integration

Use for CI failures, build/release pipelines, deployments, Docker/Kubernetes/serverless packaging, Terraform/IaC, environment/config changes, release/versioning, or Git integration/conflicts.

## Principle

Delivery code is production code. Prefer the repository's existing pipeline, deployment, IaC, and branching conventions; change the smallest layer that owns the failure/requirement. For AWS-specific service semantics, account/region/IAM safety, serverless/event delivery, CDK/CloudFormation, quotas, or AWS incident diagnosis, add `aws-deep.md` only when that concrete AWS boundary matters.

## CI and build

- Reproduce the failing CI step locally when practical using the same command/version/config.
- Distinguish code failure, flaky test, environment drift, dependency/cache problem, permission/secret issue, and runner capacity.
- Do not "fix" CI by skipping meaningful checks, weakening assertions, widening permissions, or hiding failures.
- Keep local and CI verification commands aligned where practical; deliberate differences should be explicit.
- Pin or constrain tool/action/image versions according to repository policy; avoid silent major-version drift.
- Treat CI from forks/untrusted pull requests as untrusted code: do not expose production credentials or privileged write tokens merely to make a pipeline convenient.

## Deployment and release

Before production-impacting changes, identify artifact/version, environment, config/secrets, schema dependency, old/new version coexistence, health/readiness signal, rollout strategy, and rollback/forward-fix path.

- Prefer immutable/reproducible artifacts and environment-specific configuration outside source where the stack supports it.
- Order schema/app changes so overlapping versions remain safe.
- Use feature flags/progressive rollout only when they reduce real release risk; define removal/cleanup conditions.
- Health checks must reflect the service's ability to serve intended traffic, not merely that a process exists.
- Do not claim production success from a green build alone; verify deployment/runtime signals appropriate to blast radius.

## Infrastructure as code

- Treat plans/diffs as the primary evidence before apply.
- Understand resource replacement/destruction, state/backend/locking, dependency order, and environment/workspace/stack target.
- Avoid manual console drift unless incident response requires it; reconcile emergency changes back into IaC.
- Keep least-privilege IAM/network exposure/secrets handling in scope for any infrastructure change.
- Never apply destructive/high-impact infrastructure changes without explicit user authorization and a reviewed plan.

## Git and collaboration

- Inspect working tree/branch before destructive Git operations.
- Do not discard, overwrite, reset, force-push, rewrite history, or commit unrelated user work without explicit authorization.
- Keep changes reviewable and logically coherent; split unrelated work rather than mixing it into one patch.
- Resolve conflicts by understanding both sides' intent and rerun relevant verification afterward.
- Create commits/tags/releases only when requested or required by the repository workflow.

## Verification

Use the narrowest direct evidence first, then environment/runtime checks justified by risk: pipeline command, artifact build, IaC validate/plan, container/config validation, deploy health, smoke/integration check, rollback readiness, and monitoring/error signals.
