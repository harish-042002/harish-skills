# Visual Review, Audit, and Polish

Use for UI review, critique, polish, design QA, pre-ship visual verification, redesign assessment, or after substantial visual implementation. Load late for build tasks; load at the start only when the task itself is review/audit.

## Contents

1. Review philosophy
2. Evidence setup
3. Bounded review loop
4. Review passes
5. Severity model
6. Hierarchy and composition
7. Typography
8. Color and contrast
9. Layout and responsive integrity
10. Interaction and states
11. Accessibility
12. Content and UX copy
13. Motion
14. Performance and stability
15. Anti-generic inspection
16. Existing-product consistency
17. Mobile/native review
18. Final report format
19. Stop conditions

## Review philosophy

Rendered evidence outranks code intuition for visual claims.

A UI is not visually verified because it compiles or because the CSS looks plausible. Inspect the real surface in the actual runtime when tooling is available.

Review the whole affected slice before polishing micro-details. Fix issues in batches so the agent does not burn tokens oscillating between tiny edits and screenshots.

## Evidence setup

Use the best available runtime/browser/device tooling.

For web, inspect at least:

- a narrow phone-sized viewport;
- a representative desktop viewport;
- any intermediate width where layout changes materially.

For native/mobile, inspect the shipped device classes/orientations relevant to the change.

Also exercise the states the user can actually encounter:

- loading
- populated/default
- empty
- validation error
- backend/network error
- success
- disabled/pending
- open menus/dialogs/drawers
- hover/focus/keyboard where applicable

Read console/runtime errors. Visual review does not replace functional verification.

## Bounded review loop

For normal design work, use this ceiling:

1. Build the intended slice fully enough to judge it.
2. Run one broad visual pass across affected viewports and important states.
3. Collect concrete defects before editing.
4. Fix the batch.
5. Run one focused confirmation pass.
6. Stop.

Continue beyond that only when:

- the user explicitly asks for additional visual iteration;
- the confirmation exposes a blocker/high-severity regression;
- the brief materially changes.

Do not enter an endless aesthetic self-polish loop.

## Review passes

### Pass A - product truth

- Does the surface solve the requested user problem?
- Is the primary action obvious?
- Are important states represented?
- Did the implementation add unsupported claims, fake data, or invented product behavior?

### Pass B - visual direction

- Is there a coherent visual world?
- Does the surface mode fit the task: Persuade, Operate, Read, or Experience?
- Is the design distinct without becoming arbitrary?

### Pass C - craft

- hierarchy
- typography
- color
- spacing/rhythm
- alignment
- imagery/iconography
- component consistency
- motion/feedback

### Pass D - robustness

- responsiveness
- accessibility
- content stress
- error/empty/loading states
- performance/layout stability
- interaction edge cases

## Severity model

Classify findings so polish work stays rational.

### Blocker

Prevents task completion, creates inaccessible essential interaction, severe overflow/occlusion, broken navigation, invisible critical content, or dangerous ambiguity.

### High

Materially damages usability, hierarchy, responsive behavior, contrast, state clarity, or product credibility.

### Medium

Noticeable craft/consistency problem that does not block the main task.

### Low

Minor refinement with limited user impact.

Fix Blocker and High before calling the visual work complete. Fix Medium findings that are clearly in scope. Do not chase Low findings indefinitely.

## Hierarchy and composition

Check:

- one clear primary focus/action;
- meaningful grouping without excessive containers;
- stable alignment;
- sufficient distinction between page title, section heading, body, metadata, and actions;
- no competing CTAs with equal visual weight unless they truly are peers;
- whitespace reflects relationships;
- section rhythm does not become repetitive template stacking;
- operational UI uses viewport space efficiently;
- expressive UI has a recognizable signature rather than random decoration.

Watch for:

- all-center composition by default;
- every element inside a card;
- giant headline occupying useful dashboard space;
- excessive badges/pills;
- decorative side panels with no purpose;
- weak grouping compensated by borders/shadows everywhere.

## Typography

Check:

- font choices match product/brand context;
- hierarchy is visible at a glance;
- line height and measure are comfortable;
- body/label text remains readable at real device density;
- long titles wrap intentionally;
- weights are available and not fake-synthesized in an ugly way;
- numeric alignment is appropriate in data UI;
- font loading does not cause severe layout shift;
- text scaling/zoom does not break controls.

## Color and contrast

Check:

- primary/secondary/muted hierarchy is clear;
- action accent is not diluted across everything;
- semantic colors remain distinguishable;
- disabled state remains understandable without looking like missing content;
- light and dark modes have independently usable contrast where both exist;
- charts do not rely solely on similar hues;
- tinted surfaces do not contain unreadable gray text;
- focus state remains visible against the actual background.

## Layout and responsive integrity

At each relevant viewport:

- no accidental horizontal scroll;
- no clipped controls/text;
- no fixed/sticky element hiding content;
- grid/list adapts intentionally;
- touch targets remain usable;
- primary action remains discoverable;
- tables preserve useful comparison or adapt with a deliberate alternative;
- navigation remains understandable;
- keyboard and safe-area insets do not cover fields/actions on mobile;
- media preserves aspect ratio and does not create layout shift.

Do not accept "it shrinks" as responsive design.

## Interaction and states

Exercise:

- hover where available
- keyboard focus
- click/tap
- rapid repeated click/tap
- open/close overlays
- escape/back/cancel
- submit pending
- success
- retry after error
- disabled state
- empty/no-results
- destructive confirmation/undo where relevant

Check that visual feedback and actual behavior agree. A button that looks enabled but is inert is a design defect even if the code is technically valid.

## Accessibility

Verify, at minimum where relevant:

- semantic control/landmark structure;
- keyboard reachability;
- logical focus order;
- visible focus;
- accessible names;
- labels and instructions;
- status/error announcement strategy;
- contrast;
- non-color-only status meaning;
- reduced-motion path;
- text zoom/scaling;
- touch target size;
- dialog focus containment and restoration;
- image alt behavior appropriate to content/decorative role.

Do not claim accessibility conformance solely from visual inspection. Use automated/runtime tooling when available and state its limits.

## Content and UX copy

Check:

- labels use user language rather than implementation terms;
- buttons describe their actions;
- headings are specific enough to orient the user;
- errors explain recovery;
- empty states explain the next step without filler;
- destructive actions describe consequence;
- success feedback is proportional;
- no fake testimonials, metrics, logos, notifications, activity, awards, or claims were introduced for visual completeness.

## Motion

If motion exists, verify:

- it has a reason;
- repeated actions remain fast;
- no delayed keyboard workflow;
- enter/exit behavior preserves spatial logic;
- reduced motion works;
- no motion causes layout shift or input lag;
- animations can be interrupted without leaving broken state;
- performance remains smooth enough on the target device class.

Use `design-motion.md` for deeper motion decisions.

## Performance and stability

Visual quality includes perceived and actual stability.

Check for:

- cumulative layout shift from media/font loading;
- unnecessarily huge images;
- excessive client JS for simple visual effects;
- heavy blur/filter stacks;
- unvirtualized massive lists;
- rerender loops/jank;
- animation tied to layout-heavy properties;
- render-blocking resources;
- loading UI that flashes unnecessarily.

Do not perform broad optimization without evidence; address visible/relevant problems first.

## Anti-generic inspection

Look specifically for AI-template tells:

- generic gradient hero with little product meaning;
- repeated equal-sized feature cards;
- icon tiles above every heading;
- card nesting;
- excessive pills;
- arbitrary glassmorphism;
- all content centered;
- generic placeholder copy left in production-facing UI;
- decorative charts/data with no user question;
- same radius/shadow treatment on every element;
- motion added everywhere to compensate for weak composition.

Do not remove a pattern merely because it appears on this list. Remove or refine it when it is unintentional, repetitive, or mismatched to the brief.

## Existing-product consistency

For refinement work, compare the changed surface to representative incumbent screens/components:

- token usage
- font/type scale
- icon family
- control height
- radius/border/shadow language
- interaction conventions
- navigation behavior
- state copy
- empty/error/loading patterns

A polished isolated component that looks foreign to the product is not a successful refinement.

## Mobile/native review

Also inspect:

- safe areas/system bars;
- keyboard overlap;
- orientation/window resizing if supported;
- back behavior;
- touch target comfort;
- scroll physics/overscroll expectations;
- native permission prompts and denial recovery;
- text scaling;
- accessibility semantics/screen reader order;
- dark mode/system theme;
- lifecycle interruptions where the flow can be resumed.

## Final report format

Keep review output actionable and prioritized.

```text
Visual review:
- Blocker: ...
- High: ...
- Medium: ...

Fixed:
- ...

Verified:
- viewports/states/runtime checks actually inspected

Remaining:
- only material unresolved issues
```

For a critique-only request, do not silently edit. For an implementation/polish request, fix in-scope findings before reporting.

## Stop conditions

Stop polishing when:

- requested behavior is correct;
- Blocker/High visual defects are resolved;
- relevant responsive/accessibility states are verified;
- the design direction is coherent;
- the confirmation pass is clean enough for the requested scope.

Do not continue because another subjective micro-adjustment is possible. Further iteration should be driven by user feedback, new evidence, or a changed brief.
