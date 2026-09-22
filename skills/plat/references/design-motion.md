# Motion and Interaction Craft

Use when animation, transitions, micro-interactions, perceived responsiveness, gesture feedback, or interaction polish materially affects the requested experience.

## Contents

1. Purpose
2. Motion decision framework
3. Frequency and restraint
4. Purpose categories
5. Timing and easing
6. Enter, exit, and transform origin
7. Press, hover, focus, drag
8. Layout and shared-element changes
9. Loading and perceived performance
10. Scroll and marketing motion
11. Motion tokens
12. Accessibility
13. Performance
14. Platform adaptation
15. Motion review checklist

## Purpose

Motion should make state, causality, spatial relationships, and feedback easier to understand. It should not become decoration that slows frequent actions or distracts from task completion.

A polished interface often feels better because the invisible interaction details are coherent: controls acknowledge input immediately, overlays emerge from sensible locations, state changes preserve continuity, and repeated actions stay fast.

## Motion decision framework

Before adding animation, answer in order:

1. Should this animate at all?
2. What user-facing purpose does the motion serve?
3. How frequently will the user experience it?
4. What is entering, exiting, changing, or responding?
5. What duration/easing matches that physical relationship?
6. What happens under reduced-motion preference?
7. Can the target device render it smoothly?

If the first two answers are weak, keep the interaction static or nearly instant.

## Frequency and restraint

Frequency should reduce tolerated motion.

### Very frequent

Keyboard commands, command palettes used constantly, list navigation, repeated productivity actions:

- use no animation or near-instant feedback;
- never delay the result to showcase an effect;
- preserve tactile feedback only when it does not slow throughput.

### Frequent

Hover/focus, expanding rows, common menus:

- keep motion short and subtle;
- emphasize responsiveness over spectacle.

### Occasional

Dialogs, drawers, toasts, route transitions:

- use standard transitions that preserve spatial continuity.

### Rare / expressive

Onboarding, milestone completion, portfolio/marketing moments:

- richer motion can add personality if it remains controllable and performant.

## Purpose categories

Valid purposes include:

- **Feedback** - confirms input was received.
- **State change** - communicates selection, success, expansion, completion, or mode switch.
- **Spatial continuity** - shows where content came from or where it went.
- **Hierarchy** - helps users track overlays, drawers, nested navigation, or progressive disclosure.
- **Explanation** - demonstrates a product concept or process.
- **Attention** - highlights a rare, important event.
- **Jarring-change prevention** - smooths abrupt layout/content replacement.

"It looks cool" is insufficient for high-frequency product interactions.

## Timing and easing

Use timing ranges as starting points, then tune in the rendered product.

- press/tap feedback: roughly 80-160ms
- tooltip/small popover: roughly 120-200ms
- dropdown/menu: roughly 140-240ms
- small expand/collapse: roughly 160-260ms
- dialog/drawer: roughly 180-400ms
- route/large spatial transition: roughly 220-500ms when justified
- marketing/explanatory motion: may be longer because comprehension, not immediate command response, is the goal

Prefer interactions that respond immediately and settle smoothly.

### Easing intent

- entering/revealing: strong ease-out usually feels responsive
- moving/morphing on screen: ease-in-out or spring-like motion when appropriate
- simple color/opacity hover: standard ease can be enough
- continuous movement: linear when constant velocity is meaningful
- avoid slow ease-in for direct UI response because it delays visible reaction

Do not cargo-cult one curve everywhere. Use a small motion token family.

## Enter, exit, and transform origin

### Enter

Elements usually feel more natural entering with opacity plus a small amount of scale/translation rather than materializing from zero scale or traveling huge distances.

### Exit

Exit can be slightly faster than entry because the user has already understood the element.

### Origin

Contextual surfaces should visually relate to their trigger where possible:

- menu/popover -> originate near trigger
- drawer -> emerge from its edge
- tooltip -> attach to target
- modal -> remain centered unless the product uses another clear spatial model

The transform origin should reinforce causality, not be arbitrary.

## Press, hover, focus, drag

### Press/tap

Give immediate tactile acknowledgement through a small transform, color/elevation change, or platform-native feedback. Avoid exaggerated scaling.

### Hover

Hover can preview clickability or reveal secondary information, but essential actions must remain usable without hover.

### Focus

Focus is functional state, not decoration. Keep it visible and compatible with the visual system. Do not animate focus in a way that makes keyboard navigation laggy.

### Drag

Dragged objects should feel attached to the pointer/touch and preserve origin/destination context. Use clear drop targets and cancellation behavior. Avoid heavy spring motion that makes precision difficult.

## Layout and shared-element changes

For meaningful layout change:

- preserve the user's object of attention;
- animate the smallest meaningful set of properties;
- prefer transform/opacity for smoothness;
- avoid simultaneously moving every element unless choreography is part of an expressive surface;
- prevent content from jumping before/after the transition due to measurement changes.

Shared-element transitions are strongest when they clarify continuity between states, not when added merely for novelty.

## Loading and perceived performance

Motion can make waiting feel better only when it communicates progress or continuity.

### Fast operations

Do not flash a spinner for work that completes almost immediately. Consider a short delay before showing loading UI to avoid flicker.

### Unknown duration

Use calm indeterminate feedback and preserve layout.

### Known/progressive work

Show meaningful progress when the underlying system can report it accurately.

### Skeletons

Use skeletons when they approximate the final structure and reduce layout shift. Avoid complex shimmering placeholders that are more distracting than the load.

### Optimistic interaction

When safe, update UI immediately and reconcile with the server. Motion can communicate the transition, but rollback/error recovery must remain clear.

## Scroll and marketing motion

Scroll-linked animation belongs mainly on persuasive/experience surfaces.

Rules:

- do not hijack normal scrolling;
- preserve reading order and keyboard access;
- avoid making essential content depend on exact scroll timing;
- limit simultaneous parallax layers;
- keep motion smooth on ordinary hardware;
- provide a reduced-motion path;
- avoid long pinning sequences that trap users unless the narrative genuinely requires them.

## Motion tokens

For substantial product UI, define a tiny shared motion vocabulary rather than unique values per component.

Example conceptual tokens:

```text
instant: direct feedback
fast: tooltip / micro-state
base: menu / compact transition
slow: dialog / large spatial change
enter easing: responsive ease-out
move easing: smooth ease-in-out or tuned spring
```

Use existing project tokens when present.

## Accessibility

Respect `prefers-reduced-motion` or equivalent platform settings.

Reduced motion should:

- remove large translation/parallax/choreography;
- keep essential state feedback through opacity/color/instant change;
- avoid auto-playing movement that can trigger vestibular discomfort;
- preserve the same functionality and information.

Do not disable all feedback if doing so makes state changes harder to understand.

## Performance

Prefer properties the compositor can handle efficiently, especially transforms and opacity.

Avoid:

- animating layout-heavy properties across large trees without need;
- measuring and writing layout every frame;
- huge blurred layers or filters on low-end devices;
- many independent animated elements in dense operational UI;
- unbounded requestAnimationFrame loops;
- JS animation libraries for trivial CSS transitions when native/CSS capability is sufficient.

Profile visible jank rather than guessing.

## Platform adaptation

### Web

Use CSS transitions/animations for simple interactions. Use framework/native animation tools only when state orchestration or complex sequencing justifies them.

### Flutter / React Native / native mobile

Use platform/framework-native animation primitives, preserve 60/120Hz smoothness where supported, and account for lifecycle/interruption/gesture cancellation.

### Desktop productivity UI

Favor immediacy. Keyboard-heavy workflows should feel instant. Reserve expressive animation for onboarding, rare state changes, or nonblocking polish.

## Motion review checklist

Before shipping motion, verify:

- each animation has a user-facing purpose;
- frequent actions are not delayed;
- press/tap feedback is immediate;
- menus/popovers/drawers have sensible spatial origin;
- entry and exit durations feel responsive;
- focus remains usable;
- reduced motion works;
- no essential action depends on hover;
- no layout jump occurs before/after animation;
- no obvious jank in the real runtime;
- animation still works with slow network/data arrival and rapid repeated input;
- cancellation/interruption leaves a valid state.
