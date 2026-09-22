# Flutter and Mobile Engineering

Use for Flutter/Dart and mobile architecture, state, lifecycle, navigation, networking, persistence, accessibility, performance, and platform behavior.

## Responsibilities

Mobile/client engineering is a first-class part of Plat. Preserve the repository's architecture and visual language unless redesign is requested. For visual redesign, product styling, or interaction craft, combine this file with `design-system.md` / `design-taste.md`; add `design-motion.md` for meaningful motion and `design-review.md` for final rendered/device review. Keep concerns distinct:

- **View/UI** - rendering, gestures, navigation, animation, semantics, responsive/adaptive behavior.
- **State/controller/view-model** - user intent, screen state, orchestration.
- **Domain/application** - client-side business decisions/use cases where justified.
- **Data/repository** - remote/local access, caching, mapping, persistence.

Do not put network/database/business orchestration directly in widgets when the project already has or clearly needs a data/state boundary.

## State and async lifecycle

- Keep a single source of truth for each state value and prefer one-way flow: intent -> logic -> state -> UI.
- Model meaningful loading/success/empty/error/offline/stale states explicitly.
- Dispose subscriptions/controllers and cancel/ignore stale async work according to widget/app lifecycle.
- Guard UI updates/navigation from async completions after the owning view is gone using the project's established pattern.
- Do not duplicate backend-authoritative state across multiple client stores.

## Widgets, navigation, and interaction

- Keep widgets small enough to reason about without fragmenting trivial markup into meaningless files.
- Use immutable/`const` construction where natural; keep identity/keys stable where list/widget identity matters.
- Keep expensive synchronous work out of `build` and the UI isolate.
- Reuse the project's state-management/navigation solution; do not add another package for one feature without evidence.
- Treat deep links, nested navigation, back behavior, state restoration, and auth-gated routes as contracts when relevant.
- Account for keyboard/insets, safe areas, orientation/window-size changes, text scaling, semantics/screen readers, touch target size, and reduced-motion/platform accessibility settings where the feature is exposed to them.

## Network, local data, and offline behavior

- Model timeout, failure, auth expiry, stale cache, retry, and connectivity changes when the feature can encounter them.
- Do not blindly retry non-idempotent writes.
- Define cache freshness/source-of-truth rules for offline or optimistic flows.
- Preserve user input through recoverable failures where practical.
- Use platform-appropriate secure storage only for secrets/tokens that genuinely need local persistence.

## Mobile platform boundary

Consider only when relevant: permissions and denial/permanent-denial states, background/foreground transitions, process death/restoration, deep links, notification lifecycle, app updates/version compatibility, platform channels/native APIs, and OS restrictions on background execution.

## Performance

Profile before broad rewrites. Investigate excessive rebuilds, unvirtualized lists, large images/memory pressure, synchronous CPU work on the UI isolate, lifecycle leaks, chatty APIs, unnecessary serialization, and jank during navigation/animation. Move CPU-heavy work off the UI isolate only when workload/measurement justifies it.

## Security and authority

Local validation/optimistic/offline behavior improves UX but does not own protected durable invariants. Treat deep links, intents, local files, notifications, clipboard/share input, and remote payloads as untrusted at their boundaries.

## Verification

Match proof to the behavior:

- Unit tests for pure/state/domain logic.
- Widget tests for rendering, semantics, input, tapping, scrolling, validation, and screen-state transitions.
- Integration/device tests for multi-screen flows, lifecycle, navigation, permissions, deep links, notifications, platform integration, and device/runtime behavior that widget tests cannot prove.
- Profile/runtime inspection for performance-sensitive UI.

Prefer one broad affected-flow/device-class pass plus one focused confirmation after fixes over open-ended polishing loops.
