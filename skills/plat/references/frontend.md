# Frontend Engineering

Use for web UI, React/Next.js or similar client frameworks, browser behavior, accessibility, client state, responsive interaction, and frontend/backend contracts.

## Philosophy

Frontend is a first-class engineering surface, not decoration. Server authoritative; client responsive.

Frontend owns interaction, presentation state, accessibility, loading/error/empty states, responsive behavior, optimistic UX where safe, and browser execution. Backend owns protected durable invariants and privileged side effects. Preserve the product's design system/visual language unless redesign is requested. When visual direction, art direction, or polish is materially part of the task, route into Plat's deeper design references instead of stretching engineering guidance into design advice.

## Design-depth routing

- Behavior/state/API-only frontend change: stay in this file unless visual behavior is materially affected.
- New page/screen or explicit redesign: add `design-system.md` and `design-taste.md`.
- Complex forms, navigation, tables, charts, onboarding, or responsive pattern choice: add `design-patterns.md`.
- Motion/animation/interaction feel: add `design-motion.md`.
- Visual critique, polish, or pre-ship UI verification: add `design-review.md` late, after implementation exists.

## Start from the existing product

- Follow the repository's existing frontend architecture. Inspect framework/version, routing, component library/design tokens, state/data-fetching patterns, form utilities, tests, and analogous screens before adding patterns.
- Reuse established primitives and interaction conventions before adding another state library, component kit, CSS system, or abstraction.
- For redesigns, separate **visual intent** from **behavioral contracts** so styling changes do not silently break data flow, accessibility, navigation, or existing states.

## Component and state design

- Keep state at the nearest meaningful owner; separate remote/server state from local presentation state.
- Derive state instead of maintaining synchronized duplicates when practical.
- Model the states users can actually encounter: initial/loading/partial/empty/success/error/retry/offline/expired where relevant.
- Keep effects for synchronization with external systems, not ordinary derivation/business logic.
- Keep components understandable without fragmenting trivial markup into abstraction noise.
- Prefer composition and explicit data flow over context/global state for one-off convenience.
- Avoid shared mutable module state in request/server-rendered environments unless lifecycle semantics guarantee it is safe.

## Data fetching and async work

- Remove avoidable request waterfalls; start independent I/O concurrently when semantics permit.
- Defer remote/expensive work until a branch actually needs it.
- Avoid duplicate fetching across route/component/client layers; follow framework cache/server-state semantics.
- Cancel, supersede, or ignore stale async work when it can update the wrong view.
- Keep secrets and privileged operations off the client.
- Optimistic updates need rollback/reconciliation when the authoritative server rejects or changes the result.

## Forms and user input

- Use native semantics and the repository's established form/validation pattern before inventing another abstraction.
- Preserve entered values across recoverable failures; show field-level/actionable errors at the right boundary.
- Client validation improves feedback; backend validation/authorization remains authoritative.
- Handle submit pending/double-submit/retry behavior explicitly when duplicate writes matter.

## Rendering, responsive behavior, and accessibility

- Respect server/client boundaries in SSR/hydrated frameworks; browser-only APIs, nondeterministic render output, duplicated fetching, and secret access can cause hydration/security bugs.
- Verify layout at affected narrow/wide breakpoints and with realistic content, not only sample content.
- Account for text zoom, long/localized strings, RTL where the product supports it, keyboard navigation, visible focus, semantic/native controls, accessible names, status/error announcements, and reduced-motion preferences.
- Preserve logical focus across dialogs, navigation, validation failures, and dynamic content.
- Touch/click targets and interaction affordances must remain usable; hover-only behavior cannot be the sole path to essential actions.

## Performance priority

Optimize high-impact causes before micro-tuning JavaScript:

1. Network/data waterfalls.
2. Initial bundle/client JavaScript and heavy third parties.
3. Server/client serialization and duplicate data.
4. Oversized images/media and unbounded collections.
5. Excessive rerenders/subscriptions/layout work.
6. Hot-path JavaScript only after evidence.

Use framework-supported lazy loading/code splitting when the feature boundary justifies it. Virtualize genuinely large collections; do not memoize every value/callback or add caches by habit.

## Verification

For meaningful UI work, verify the rendered result and interaction flow in a real browser/runtime when tooling exists. Check relevant DOM/accessibility behavior, console errors, network requests, responsive states, loading/error/empty states, keyboard flow, and hydration/runtime warnings. Static code review cannot prove rendered behavior.

Keep QA bounded: one comprehensive affected-state/viewpoint pass, fix concrete defects, then one focused confirmation. Do not burn tokens on endless aesthetic self-polishing unless the user explicitly requests design iteration.
