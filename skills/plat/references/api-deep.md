# Deep API, Event, and Integration Design

Use for public APIs, webhooks/events, independently deployed consumers, compatibility/versioning, high-risk integrations, streaming, or contract evolution where ordinary API guidance is insufficient.

## Contents

1. Objective
2. Consumer and ownership map
3. Compatibility
4. Command idempotency
5. Pagination/query semantics
6. Webhooks
7. Events and schemas
8. Async/streaming APIs
9. Error contracts
10. Security and abuse
11. Contract verification
12. Evolution and migration
13. Edge cases

## Objective

Design interfaces that survive retries, independent deployment, partial failure, and evolution without forcing coordinated releases.

## Consumer and ownership map

Before changing a shared contract, identify:

- owning service/module;
- known internal/external consumers;
- mobile/web versions that may lag;
- generated SDK/client dependencies;
- event subscribers;
- persisted payloads/replay sources;
- rollout/deprecation constraints.

Observed behavior that real consumers depend on may be a contract even if undocumented.

## Compatibility

Prefer additive evolution:

- add optional fields with safe defaults;
- accept old/new input during transition;
- avoid changing field meaning under the same name;
- preserve stable machine-readable errors;
- define unknown-field behavior;
- avoid breaking enum expansion for clients that assume exhaustive values;
- treat ordering/default/timing changes as compatibility risks when consumers rely on them.

Version only when compatibility cannot be maintained or independent semantics truly need separation. Versioning does not remove migration obligations.

## Command idempotency

For harmful duplicate operations define:

- operation identity/idempotency key;
- key scope (actor/resource/endpoint);
- request equivalence rules;
- in-flight duplicate behavior;
- completed response replay;
- retention window;
- authoritative dedupe store/constraint.

A timeout can occur after the server committed; client retry must not duplicate protected effects.

## Pagination/query semantics

For collections define:

- deterministic order;
- page/cursor semantics;
- max page size;
- stable continuation under inserts/deletes where required;
- filter/sort grammar;
- query cost bounds.

Cursor/keyset pagination is often safer at scale, but only if ordering/key semantics fit the product.

## Webhooks

Assume sender retry and duplicate delivery.

- verify authenticity exactly as provider documents, often over raw/canonical payload;
- check replay/timestamp tolerance when supported;
- return acknowledgement within provider timeout where practical;
- process slow work asynchronously;
- persist event identity before harmful side effects when necessary;
- handle out-of-order events by version/state semantics, not arrival order alone;
- define replay/manual recovery.

Never log signatures/secrets or full sensitive payloads by default.

## Events and schemas

Treat event schemas as contracts.

Define:

- event identity and correlation/causation IDs;
- producer source/version;
- partition/order scope;
- required vs optional fields;
- schema evolution rules;
- consumer idempotency;
- retention/replay assumptions.

Prefer facts about completed domain events over imperative cross-service commands when loose coupling is the goal, but do not force event-driven design into simple synchronous workflows.

## Async/streaming APIs

For async jobs define job identity, accepted/running/succeeded/failed/cancelled states, polling/webhook/stream semantics, retention, authorization, and idempotent retry/cancel behavior.

For streaming define reconnect/resume semantics, ordering, heartbeats, backpressure, and what state is lost/replayed.

## Error contracts

Errors should support both humans and machine clients.

Define stable code/type plus useful message/details without leaking internals. Distinguish:

- invalid input;
- authentication;
- authorization;
- not found vs forbidden disclosure policy;
- conflict/concurrency;
- rate/capacity;
- dependency/transient failure;
- internal error.

Retry guidance belongs to semantics, not a generic 500 handler.

## Security and abuse

Bound:

- body/upload size;
- pagination/query complexity;
- batch size;
- expensive AI/search/report operations;
- fan-out;
- webhook destination/SSRF risk;
- rate/cost per actor/tenant.

Authenticate and authorize at the authoritative operation/resource boundary. Client-supplied owner/role/tenant fields are input, not permission.

## Contract verification

Use:

- schema/OpenAPI/protobuf validation;
- generated client build checks;
- consumer/provider contract tests where useful;
- overlap tests between old/new producer/consumer versions;
- webhook signature fixtures;
- replay/idempotency tests;
- representative load/query-cost checks for public collection/search APIs.

## Evolution and migration

Plan:

1. additive producer/server support;
2. deploy compatible consumers/clients;
3. observe usage/versions;
4. switch defaults/behavior when safe;
5. deprecate with real migration path;
6. remove only after consumer evidence supports it.

## Edge cases

- **Mobile clients lag months:** server must tolerate old contracts for the supported window.
- **Enum gains value:** old exhaustive clients may crash; consider unknown/fallback handling.
- **Webhook provider retries after 2xx lost in network:** dedupe by event identity.
- **Cursor includes mutable field:** updates can skip/duplicate rows; choose stable ordering semantics.
- **Error text used by clients:** introduce stable codes before rewriting messages when possible.
