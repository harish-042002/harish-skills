# Flutter and Mobile Engineering

Use for Flutter/Dart and mobile architecture, state, lifecycle, networking, persistence, performance, and platform behavior.

## Responsibilities

Preserve the repository's architecture and visual language unless redesign is requested, but keep concerns distinct:

- **View/UI** - rendering, gestures, navigation, animation, presentation behavior.
- **State/controller/view-model** - user intent, screen state, orchestration.
- **Domain/application** - client-side business decisions/use cases where justified.
- **Data/repository** - remote/local access, caching, mapping, persistence.

Do not put network/database/business orchestration directly in widgets when a project already has or clearly needs a data/state boundary.

## State and async lifecycle

- Keep a single source of truth for each state value.
- Prefer one-way flow: intent -> logic -> state -> UI.
- Model meaningful loading/success/empty/error/offline states explicitly.
- Do not duplicate backend-authoritative state across multiple client stores.
- Dispose subscriptions/controllers and cancel/ignore stale async work according to widget/app lifecycle.
- Guard UI updates/navigation from async completions after the owning view is gone using the framework/project's established pattern.

## Widgets and rendering

- Keep widgets small enough to reason about without fragmenting trivial markup into meaningless files.
- Use immutable/`const` construction where natural.
- Avoid expensive synchronous work in `build` or the UI isolate.
- Keep identity/keys stable where list/widget identity matters.
- Reuse the project's state-management solution; do not add another package for one feature without evidence.

## Network, local data, and offline behavior

- Model timeout, failure, auth expiry, stale cache, retry, and connectivity changes when the feature can encounter them.
- Do not blindly retry non-idempotent writes.
- Define cache freshness/source-of-truth rules for offline or optimistic flows.
- Use platform-appropriate secure storage only for secrets/tokens that genuinely need local persistence; ordinary app data does not become "secure" merely because it is local.

## Mobile platform boundary

Consider only when relevant: permissions and denial states, background/foreground transitions, process death/restoration, deep links, notification lifecycle, app updates/version compatibility, platform channels/native APIs, and OS restrictions on background execution.

## Performance

Profile before broad rewrites. Investigate excessive rebuilds, large/unvirtualized lists, synchronous CPU work on the UI isolate, image/memory pressure, lifecycle leaks, chatty APIs, and unnecessary serialization. Move CPU-heavy work off the UI isolate only when measurement or workload justifies it.

## Security and authority

Local validation/optimistic/offline behavior improves UX but does not own protected durable invariants. Treat deep links, intents, local files, notifications, and remote payloads as untrusted input at their boundaries.

## Verification

Use widget/unit tests for logic where appropriate, but verify meaningful device/runtime behavior for lifecycle, navigation, permissions, deep links, notifications, platform integration, and performance-sensitive UI. Prefer one broad affected-flow/device-class pass plus one focused confirmation after fixes over open-ended polishing loops.
