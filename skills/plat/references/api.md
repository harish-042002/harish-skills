# API and Interface Design

Use for REST, GraphQL, gRPC, webhooks, events, SDK-facing interfaces, and internal service/module contracts.

## Contract first

Define:

- Caller and owning boundary.
- Input shape, validation, and limits.
- Authentication/authorization.
- Success semantics.
- Stable error semantics.
- Idempotency/retry behavior for commands.
- Pagination/filter/sort semantics for collections.
- Compatibility/versioning/deprecation expectations.

Keep storage implementation details behind the contract unless they are intentionally part of it.

## Boundary behavior

- Normalize/validate untrusted input once at the appropriate boundary, then pass meaningful typed/domain data inward.
- Authenticate identity and authorize the specific resource/action.
- Bound expensive/unbounded inputs, page sizes, filters, uploads, response payloads, and query complexity/depth where applicable.
- Return stable machine-readable error codes/fields when clients need programmatic branching.
- Do not leak stack traces, SQL/vendor errors, secrets, or internal topology.

## Commands and retries

When network/client retries can duplicate a harmful operation:

- Define an idempotency key or other stable operation identity.
- Persist/deduplicate at the authoritative boundary when needed.
- Specify how duplicate in-flight/completed requests respond.
- Do not call a POST "safe" merely because current clients rarely retry it.
- For read-modify-write APIs where lost updates matter, use an authoritative version/precondition mechanism when supported instead of silently overwriting concurrent changes.

## Events and webhooks

Assume duplicate delivery unless the transport contract proves otherwise.

- Include stable event identity and useful correlation identity.
- Make consumers idempotent.
- State ordering assumptions explicitly; partition keys/order scopes matter.
- Verify webhook authenticity over the provider-defined canonical/raw payload, validate timestamp/replay protections, and follow current provider guidance; parsing/re-serializing before verification can invalidate signatures.
- Acknowledge receipt separately from slow processing when that improves delivery reliability.
- Evolve payloads additively where possible.

## Compatibility

Treat observed behavior that real consumers depend on as a contract even when it was not intended. Before changing meaning, field shape, status/error semantics, defaults, ordering, or timing-sensitive behavior, find consumers and plan coexistence.

Prefer additive evolution. Deprecate before removal when external/independent consumers exist. If old/new clients or producers coexist, test the overlap window rather than only each version in isolation.

## Client/backend split

Client validation and optimistic UX improve responsiveness; they do not replace authoritative server validation/authorization. Do not trust client-provided ownership, price, role, entitlement, or other protected state.

## Operability

For important distributed APIs, propagate/request correlation identifiers through existing tracing/logging mechanisms so failures can be followed across boundaries without exposing sensitive data.
