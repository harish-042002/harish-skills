# Deep Mobile Engineering

Use for complex Flutter/native/mobile lifecycle, offline-first behavior, synchronization, background work, deep links, notifications, process death, permissions, app upgrades, or device-specific performance.

## Contents

1. Objective
2. Lifecycle and process death
3. State restoration
4. Offline and sync
5. Background work
6. Navigation/deep links
7. Notifications
8. Permissions
9. Local storage/security
10. Performance/memory
11. Platform/version differences
12. Testing
13. Edge cases

## Objective

Design for the reality that mobile processes disappear, networks flap, users background/resume, OS policies interrupt work, and multiple device/app versions coexist.

## Lifecycle and process death

Distinguish:

- widget/view disposal;
- app background/foreground;
- activity/view-controller recreation;
- full process death and cold start.

Do not rely on in-memory state for data that must survive process death. Cancel/ignore async work owned by a disposed view and make restart behavior explicit.

## State restoration

For important flows decide what should restore after interruption:

- navigation destination;
- form draft;
- upload/job progress;
- authentication/session;
- pending mutation;
- selected filters/context.

Restore only from safe persisted state and revalidate server-authoritative facts.

## Offline and sync

If offline matters, define:

- local source/cache ownership;
- freshness and stale presentation;
- queued writes;
- operation identity/idempotency;
- conflict policy;
- retry/reconnect behavior;
- deletion/tombstone semantics;
- user-visible sync state.

Do not call a cached online app "offline-first" without a durable mutation/reconciliation model.

## Background work

Account for OS restrictions, battery, network, quotas, and execution windows.

Use platform-approved schedulers/background APIs. Work must be resumable/idempotent because the OS may stop it.

Avoid long-lived background loops that assume desktop/server semantics.

## Navigation/deep links

Treat deep links as untrusted input and a navigation contract.

Define:

- cold-start deep link;
- warm/background handling;
- auth-gated destination;
- missing/expired entity;
- back-stack behavior;
- duplicate link delivery;
- version compatibility.

## Notifications

Separate:

- permission state;
- token registration/refresh;
- delivery payload;
- foreground presentation;
- tap/open routing;
- dedupe/update/collapse semantics;
- expired or unauthorized target handling.

Notification delivery is not proof the user saw or acted on it.

## Permissions

Model:

- not requested;
- granted;
- denied;
- permanently denied/restricted;
- OS setting changed later.

Explain context before system prompt when useful, but do not manipulate or repeatedly nag users. Provide settings/recovery path when permission is essential.

## Local storage/security

Classify data:

- cache/reconstructable;
- user draft;
- sensitive credential/token;
- durable offline domain state.

Use platform secure storage for secrets that need local persistence. Encrypting arbitrary local data does not replace server authorization or device-compromise assumptions.

## Performance/memory

Measure device/runtime behavior:

- frame/jank traces;
- rebuild/recomposition breadth;
- image decoding/cache pressure;
- large list virtualization;
- startup time;
- network chatiness;
- serialization;
- synchronous CPU work on UI thread/isolate;
- leaks from subscriptions/controllers/native handles.

Test on realistic lower/mid devices when performance matters, not only simulator/high-end hardware.

## Platform/version differences

Check installed framework/plugin versions and OS behavior for:

- background execution;
- notification permission/model;
- storage permissions;
- deep links/universal links/app links;
- keyboard/insets;
- safe areas;
- webviews;
- native SDK changes.

Do not rely on generic latest-platform memory when the project pins older versions.

## Testing

Use:

- unit for pure/state/domain logic;
- widget/view tests for rendering/interaction;
- integration/device tests for lifecycle/navigation/deep links/permissions/notifications/platform channels;
- real-device profiling for performance/memory/battery-sensitive behavior;
- upgrade/migration tests when local persisted schema changes.

## Edge cases

- **User kills app mid-write:** server/local operation must reconcile safely.
- **Token refresh while offline:** keep auth error/retry semantics explicit.
- **Notification opens stale entity:** route to a safe fallback, not a broken screen.
- **App update changes local schema:** migrations must handle users skipping several versions.
- **Keyboard opens on small screen:** primary action/error must remain reachable.
- **Clock/timezone changes:** scheduled/local-time behavior must define its intended semantics.
