# Frontend Engineering

Use for web UI, React/Next.js or similar client frameworks, browser behavior, accessibility, client state, and frontend/backend contracts.

## Philosophy

Server authoritative. Client responsive.

Frontend owns interaction, presentation state, accessibility, loading/error/empty states, optimistic UX where safe, and browser behavior. Backend owns protected durable invariants and privileged side effects. Do not redesign the product's visual language unless the request is actually about design.

## Component and state design

- Follow the repository's component/state architecture before introducing another pattern or state library.
- Keep state at the nearest meaningful owner; separate remote/server state from local presentation state.
- Derive state instead of maintaining synchronized duplicates when practical.
- Keep rendering components understandable; do not split trivial markup into abstraction noise.
- Keep effects for synchronization with external systems, not as a default place for ordinary derivation/business logic.
- Avoid shared mutable module state in request/server-rendered environments unless the framework guarantees the intended lifecycle.
- Respect server/client execution boundaries in SSR/hydrated frameworks; browser-only APIs, secrets, non-deterministic rendering, and duplicated fetches can create hydration or security bugs.

## Data fetching and async work

- Remove avoidable request waterfalls; start independent I/O concurrently when semantics permit.
- Defer expensive/remote work until a branch actually needs it.
- Avoid duplicate fetching across route/component/client layers.
- Cancel, supersede, or ignore stale async work when it can update the wrong view.
- Treat loading, partial, empty, retry, auth-expiry, and error states explicitly where users can encounter them.
- Keep secrets and privileged operations off the client.

## Performance priority

Optimize high-impact causes before micro-tuning JavaScript:

1. Network/data waterfalls.
2. Initial bundle/client JavaScript and heavy third parties.
3. Server/client serialization and duplicate data.
4. Large assets and huge collections.
5. Excessive rerenders/subscriptions/layout work.
6. Hot-path JavaScript only after evidence.

Load large modules/assets only when the feature needs them when supported by the framework. Do not memoize every value/callback by habit; measure or identify a concrete cost.

## Accessibility and UX correctness

Use semantic/native controls where possible. Preserve keyboard access, visible focus, labels/names, meaningful error/status announcements, reduced-motion preferences when relevant, and logical focus after dialogs/navigation/errors.

Visual presence is not proof of accessibility.

## Validation and optimistic UI

Client validation gives fast feedback; backend validation/authorization remains authoritative. Optimistic updates need a clear rollback/reconciliation path when the server rejects or modifies the operation.

## Browser verification

For meaningful UI changes, verify in a real browser/runtime when tooling exists. Inspect the relevant DOM/accessibility behavior, console errors, network requests, responsive states, and interaction flow. Static code review cannot prove hydration, focus, race timing, or rendered layout.

Keep QA bounded: perform one comprehensive pass over the affected states/viewports, fix the batch of concrete defects, then one focused confirmation pass. Do not burn tokens on endless aesthetic self-polishing unless the user requests design iteration.
