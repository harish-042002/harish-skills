# Deep Security Engineering

Use for high-impact auth/authorization, multi-tenancy, sensitive data, uploads, code execution, secrets, cryptography integration, supply chain, AI/tool permissions, or explicit security review/threat modeling.

## Contents

1. Objective
2. Focused threat model
3. Authentication/session
4. Authorization and tenant isolation
5. Input/output trust boundaries
6. Files, URLs, and code execution
7. Secrets and cryptography
8. Supply chain
9. AI and tool security
10. Abuse and cost controls
11. Security review of changes
12. Verification
13. Edge cases

## Objective

Identify concrete assets, actors, trust boundaries, abuse paths, and controls. Deep security is risk-driven; do not turn ordinary CRUD into a ceremonial audit.

## Focused threat model

For the affected slice answer:

```text
Assets: what must be protected?
Actors: legitimate and attacker roles?
Entry points: where can untrusted input/action arrive?
Trust boundaries: where does privilege/data ownership change?
Abuse paths: how could a control be bypassed?
Controls: what authoritative check stops each material path?
Residual risk: what remains and why?
```

Prioritize paths that can cause account takeover, tenant crossing, data exposure/modification, money/value impact, secret/code execution, or large cost/availability impact.

## Authentication/session

Use mature framework/provider mechanisms.

Check relevant:

- token/session issuance and verification;
- expiry/rotation/revocation;
- secure cookie attributes;
- CSRF for cookie-authenticated state changes;
- reauthentication/MFA for sensitive actions;
- replay/session fixation;
- logout/device/session invalidation;
- OAuth/OIDC redirect/state/nonce/PKCE semantics for the actual flow.

Do not invent custom auth protocols.

## Authorization and tenant isolation

Authenticate identity, then separately authorize the object/action.

Check every authoritative access path, including:

- REST/GraphQL/gRPC endpoints;
- background jobs/schedulers;
- queues/event consumers;
- admin/support tools;
- object storage;
- caches/search indexes;
- database policies/RLS;
- exports/reports.

A tenant/resource ID supplied by the client is not authorization.

Use deny-by-default/least privilege where the framework/domain supports it. Test cross-tenant/cross-role negative cases explicitly.

## Input/output trust boundaries

Treat all external/user/retrieved/tool content as untrusted.

Use context-appropriate controls:

- schema/type/range/size validation;
- parameterized SQL;
- safe command/process APIs and strict allowlists where command execution is intended;
- output encoding/sanitization for the actual sink;
- mass-assignment protection;
- path canonicalization/traversal defense;
- safe deserialization formats;
- query depth/complexity bounds.

Validation is not one generic "sanitize" function; controls depend on sink and semantics.

## Files, URLs, and code execution

### Files

Validate filename/path, type/content, size, storage location, access control, and serving headers. Do not execute uploaded content accidentally.

### Outbound URLs

For user-controlled destinations consider SSRF:

- scheme allowlist;
- hostname/IP resolution and private/link-local/metadata ranges;
- redirect revalidation;
- DNS rebinding/time-of-check behavior;
- request size/time bounds.

### Code/templates

Avoid eval/dynamic code execution from untrusted input. Sandboxing is not a substitute for minimizing capability and validating the threat model.

## Secrets and cryptography

Secrets:

- never hard-code or log;
- least-privilege scopes;
- environment separation;
- rotate/revoke when exposure occurs;
- avoid copying into profile/session/test fixtures.

Cryptography:

- use current vetted libraries/protocols;
- do not design custom crypto/password storage;
- verify algorithm/mode/key-management guidance against authoritative current documentation when security-critical.

## Supply chain

Before adding/upgrading sensitive dependencies:

- verify source/provenance/maintenance;
- use lockfiles/integrity/signature mechanisms available;
- review transitive/native/build-script risk where material;
- avoid install scripts from untrusted sources in privileged CI;
- scope CI tokens/permissions and untrusted fork behavior;
- inspect generated/vendor changes for unexpected behavior when risk warrants it.

## AI and tool security

Treat prompts, retrieved docs, web pages, MCP/tool results, model outputs, and generated code as untrusted data.

Prompt/data instructions must not:

- expand tool permission;
- reveal secrets;
- change tenant scope;
- authorize destructive actions;
- override higher-priority policy.

Use least-privilege tools, constrained arguments, deterministic authorization, and explicit approval for high-impact effects.

## Abuse and cost controls

Security includes availability/economic abuse.

Bound expensive actions by actor/tenant/system:

- request rate;
- upload size;
- search/report complexity;
- AI token/tool budgets;
- fan-out/batch size;
- concurrency;
- retries.

Avoid controls that allow one tenant/user to exhaust shared resources.

## Security review of changes

For an existing diff/change, prioritize by risk rather than LOC.

Inspect:

- removed validation/auth checks;
- changed privilege/public visibility;
- new external calls;
- new deserialization/file/URL/code paths;
- data-model/tenant boundary changes;
- secret/IAM/network exposure;
- error/logging leakage;
- high-blast-radius shared helpers.

Use Git history/blame when removed security behavior may be a regression. Familiarity with the codebase is not evidence the change is safe.

## Verification

Use relevant:

- positive + negative authz tests;
- cross-tenant tests;
- CSRF/session/OAuth fixtures;
- injection/path/SSRF adversarial cases;
- permission/IAM policy validation;
- dependency/static scanners as evidence, not sole proof;
- secret scanning;
- security-focused integration tests at authoritative boundaries.

State coverage limits honestly.

## Edge cases

- **Hidden UI control:** does not protect backend operation.
- **Admin/service account:** ensure privileged credentials cannot leak into ordinary request paths.
- **Signed webhook:** verify raw canonical payload before parsing/re-serializing if provider requires it.
- **Redirect allowed URL:** validate each redirect hop when SSRF matters.
- **Soft delete:** authorization/search/export must respect deleted/retention semantics.
- **AI tool call:** valid JSON is not authorization; deterministic policy still gates the action.
