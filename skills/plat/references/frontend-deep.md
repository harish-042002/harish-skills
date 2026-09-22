# Deep Frontend Engineering

Use for large frontend applications, complex state/data ownership, SSR/RSC/hydration issues, frontend performance, design-system architecture, multi-route flows, or subtle browser/runtime behavior beyond ordinary component work.

## Contents

1. Objective
2. Architecture map
3. State ownership
4. Server/client boundaries
5. Async and concurrency
6. Data fetching and cache semantics
7. Rendering and hydration
8. Component/system boundaries
9. Forms and workflows
10. Performance
11. Accessibility at scale
12. Failure and resilience
13. Testing/runtime evidence
14. Edge cases

## Objective

Keep frontend behavior understandable under async data, navigation, concurrent rendering, responsive layouts, and evolving product complexity without inventing a parallel architecture.

Visual art direction belongs in the design references; this file focuses on engineering depth.

## Architecture map

For a complex screen/flow, identify:

- route/entry point;
- server vs client execution boundary;
- remote data sources and ownership;
- local UI state;
- shared application state;
- mutation path and optimistic behavior;
- component/design-system primitives;
- navigation/deep-link state;
- verification path.

Do not introduce a global state solution before proving local/server-state boundaries are insufficient.

## State ownership

Classify state before choosing a store:

- server/remote authoritative state;
- URL/navigation state;
- form draft state;
- local presentation state;
- cross-feature client state;
- ephemeral interaction state.

Keep each value in one canonical place when possible. Derive values instead of synchronizing duplicates.

Watch for:

- effects that copy props/query data into local state;
- duplicated caches between framework/query/store layers;
- module-level mutable request state in SSR;
- stale closures/async writes;
- global stores used only to avoid passing data one or two levels.

## Server/client boundaries

For SSR/RSC/hybrid frameworks:

- keep secrets/privileged operations server-side;
- minimize data serialized to clients;
- avoid duplicate server + client fetches;
- authenticate/authorize server actions like APIs;
- keep browser-only APIs behind client boundaries;
- account for request isolation;
- validate hydration assumptions.

Do not cargo-cult client components around everything just because one nested interaction needs browser state.

## Async and concurrency

Eliminate avoidable waterfalls:

- start independent I/O early and await late;
- parallelize independent requests;
- defer expensive work until the branch needs it;
- cancel/ignore stale requests when navigation/input supersedes them;
- handle race between optimistic state and authoritative response;
- keep loading transitions stable under rapid input.

For search/typeahead, define debouncing/cancellation and stale-result ordering explicitly.

## Data fetching and cache semantics

Understand the framework/query library actually installed.

Define:

- cache owner;
- key identity;
- freshness/staleness;
- invalidation/revalidation;
- deduplication;
- optimistic update/rollback;
- pagination/infinite-scroll cursor;
- offline behavior where relevant.

Do not add a second cache layer because a request looks repetitive before checking existing framework semantics.

## Rendering and hydration

Investigate:

- nondeterministic server/client output;
- time/random/locale differences;
- browser-only state read during server render;
- layout shifts from fonts/media/client data;
- conditional rendering that changes structure unexpectedly;
- expensive render work repeated per keystroke/scroll;
- hidden vs unmounted component lifecycle expectations.

Suppress hydration warnings only when the mismatch is deliberate and understood.

## Component/system boundaries

Reuse existing primitives and variants.

Create an abstraction when it represents a repeated product concept or behavior, not merely repeated markup.

At scale, keep:

- domain feature boundaries clear;
- cross-feature primitives stable and narrow;
- component props meaningful rather than generic option bags;
- CSS/theme/tokens centralized according to project conventions;
- accessibility behavior inside primitives where reuse is beneficial.

## Forms and workflows

For complex flows:

- preserve draft state across recoverable errors/navigation when required;
- validate locally for feedback and authoritatively on server;
- handle duplicate submit/retry;
- map backend field/global errors consistently;
- maintain focus on validation/step changes;
- support partial save only when product semantics define it.

A multi-step wizard should exist because the workflow has real stages/dependencies, not because the form is long.

## Performance

Prioritize by impact:

1. request/data waterfalls;
2. bundle/client JS and third parties;
3. server/client serialization;
4. repeated remote work;
5. large images/media;
6. unvirtualized large collections;
7. rerender/subscription breadth;
8. layout/paint/animation cost;
9. local JS micro-optimizations.

Measure with the available browser/framework tooling before broad memoization or architectural rewrites.

Do not memoize every callback/value. Optimize the actual hot path.

## Accessibility at scale

Reusable primitives should carry correct semantics/focus/keyboard behavior so every feature does not reinvent it.

Test:

- keyboard-only navigation;
- dialogs/popovers focus lifecycle;
- dynamic status/error announcements;
- zoom/text scaling;
- reduced motion;
- long/localized/RTL content where supported;
- touch target size on hybrid/mobile web.

## Failure and resilience

Model meaningful states:

- initial/partial loading;
- empty/no-results;
- recoverable error;
- auth/session expiry;
- offline/reconnect if relevant;
- mutation pending;
- conflict/stale update;
- permission loss;
- partial data.

Do not let an exception boundary replace product-level recovery where users can act.

## Testing/runtime evidence

Match proof to risk:

- unit for pure state/formatting;
- component tests for rendering/interaction;
- integration for data + routing boundaries;
- browser E2E for critical flows;
- performance trace/profile for perf claims;
- real rendered visual review for visual claims.

Static code review cannot prove hydration, focus, network ordering, responsive layout, or browser runtime errors.

## Edge cases

- **Fast repeated navigation:** stale async completion must not update the wrong route/view.
- **Optimistic failure:** rollback/reconciliation must not erase newer user edits.
- **SSR multi-user process:** shared mutable module state can leak across requests.
- **Large table:** preserve comparison semantics before converting to mobile cards.
- **Feature flag:** both old/new component/data paths may coexist during rollout.
- **Accessibility vs custom widget:** prefer native/established accessible primitive unless custom interaction has a clear product requirement.
