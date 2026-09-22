# Design System and UI/UX Intelligence

Use for new pages/screens, redesigns, design-system work, visual direction, typography/color/layout choices, product UX shaping, or when a frontend request materially changes how an interface looks or feels.

## Contents

1. Purpose
2. Design context
3. Surface mode
4. Design dials
5. Existing product vs greenfield
6. Design-system output
7. Typography
8. Color
9. Spacing, shape, depth
10. Layout and responsive behavior
11. Accessibility and interaction floor
12. Product archetypes
13. Component decisions
14. Charts and data display
15. Stack adaptation
16. Persistence and token discipline
17. Failure modes

## Purpose

Turn a vague visual request into a coherent implementation direction without forcing a heavyweight design specification. Establish enough design truth to prevent generic defaults, contradictory styling, and repeated rediscovery.

Do not invent a visual world for a narrow engineering-only frontend change. If the task changes behavior but not appearance, `frontend.md` is usually enough.

## Design context

Before making visual decisions, resolve from the request and repository where possible:

- What is the product and who is using this surface?
- What must the user accomplish here?
- What visual language already exists in tokens, CSS, theme, components, screenshots, or assets?
- Is this preservation, refinement, or an explicit redesign?
- What platform and stack are actually present?
- What constraints matter: brand, accessibility, content density, localization, device class, performance, asset availability?

Ask the developer only when an unresolved choice would materially change the visual direction. Do not ask them to choose routine values the skill can infer.

## Surface mode

Classify the surface by the visitor's primary success mode. The same product can use different modes on different surfaces.

- **Persuade** - landing, pricing, campaign, marketing. Design earns attention and action; hierarchy and differentiation can be expressive.
- **Operate** - app UI, dashboard, editor, admin, settings. Scanability, speed, consistency, and native expectations outrank spectacle.
- **Read** - docs, articles, guides, help, changelog. Comprehension, rhythm, measure, navigation, and content hierarchy lead.
- **Experience** - portfolio, gallery, showcase, immersive product demo. The artifact or experience leads; interface chrome recedes.

Do not apply landing-page drama to dense operational UI. Do not make persuasive surfaces look like generic internal admin tools.

## Design dials

Use three compact dials to control the design without writing a long style brief. Express them as low / medium / high unless a numeric scale is genuinely useful.

### Variance

Controls how far composition departs from conventional centered/grid defaults.

- Low: restrained, symmetric, familiar.
- Medium: deliberate asymmetry or one distinctive composition move.
- High: bold scale shifts, unconventional composition, stronger visual tension.

### Motion

Controls how much movement communicates state or personality.

- Low: only essential feedback and state continuity.
- Medium: standard micro-interactions and selected entrances/transitions.
- High: richer choreography for rare, expressive surfaces; never at the cost of usability or reduced-motion support.

### Density

Controls information and spacing density.

- Low: spacious marketing, editorial, premium showcase.
- Medium: general product UI.
- High: admin/data tools where scan speed and information throughput matter.

Pick dials from the surface mode and product context. Do not default every project to medium values if the brief clearly implies otherwise.

## Existing product vs greenfield

### Existing product

Treat the incumbent system as evidence:

- Read tokens, theme, fonts, core components, spacing patterns, radii, shadows, icon set, and representative screens.
- Preserve established identity for refinement work.
- Reuse components and tokens unless they are the thing being intentionally redesigned.
- Do not introduce a second design system inside one feature.

### Explicit redesign or greenfield

Define a compact design system before implementation. Keep it implementation-ready, not essay-like.

## Design-system output

For substantial new visual work, resolve these items before deep implementation:

```text
Mode: Persuade | Operate | Read | Experience
Direction: one sentence describing the visual world
Dials: variance / motion / density
Type: display + body/UI roles
Color: background / surface / text / muted / accent / semantic roles
Space: base rhythm and section/component scales
Shape: radius/border/shadow language
Signature: one memorable element or compositional move
States: loading / empty / error / success / disabled / focus
Responsive: narrow / medium / wide behavior
```

This can live in working context. Do not create a design document for a one-screen task unless persistence will save real rediscovery.

## Typography

- Choose type for the product, not because a font is fashionable.
- Existing brand fonts win unless redesign is requested or they are unavailable.
- Prefer one family with enough weights/styles, or at most two complementary families for most product work.
- Build hierarchy through size, weight, line height, width, tracking, case, and spacing together.
- Keep body copy comfortably readable; avoid ultra-light weights for essential text.
- Keep long-form text to a readable measure rather than full-width lines.
- Dense product UI needs compact but distinct hierarchy; do not shrink everything equally.
- Display typography can carry personality on persuasive/experience surfaces, but supporting UI should remain legible and calm.
- Avoid using monospace decoratively everywhere unless the product language genuinely calls for it.

## Color

Define roles before shades:

- page/background
- raised/surface
- primary text
- secondary/muted text
- border/divider
- primary accent/action
- success/warning/error/info
- focus/selection

Rules:

- Contrast and state recognition beat novelty.
- Avoid low-contrast gray-on-color combinations for important content.
- Do not use gradients as an automatic "premium" signal.
- Reserve strong accent color for meaning and hierarchy instead of painting every component.
- Dark mode is not an inversion filter; re-evaluate contrast, elevation, borders, illustrations, and semantic colors.
- For charts, differentiate series with more than hue alone when interpretation matters.

## Spacing, shape, depth

- Use a small spacing family with clear relationships instead of unrelated pixel values.
- Repetition creates rhythm; exceptions should communicate hierarchy.
- Radii should form a coherent family. Avoid every container becoming a rounded card.
- Borders, shadows, and background contrast are alternative separation tools; do not stack all three without purpose.
- Nested cards usually indicate weak grouping. Prefer layout, whitespace, headings, dividers, or subtle surfaces first.
- Use depth to communicate hierarchy or interaction, not decoration.

## Layout and responsive behavior

Design behavior, not screenshots.

- Establish content hierarchy before choosing columns.
- Let mobile reflow and reprioritize; do not merely shrink desktop.
- Preserve readable line lengths and usable touch targets.
- Use container widths and spacing that adapt smoothly rather than breakpoint explosions.
- Test with realistic long strings, empty data, dense data, validation messages, and localization where relevant.
- Keep primary actions reachable and predictable as layout changes.
- Prevent horizontal scrolling except where the interaction intentionally requires it.

## Accessibility and interaction floor

Never trade these away for visual style:

- semantic/native controls where possible
- keyboard access and logical tab order
- visible focus
- accessible names for controls and icons
- sufficient contrast
- touch targets appropriate to the platform
- status/error announcements when needed
- non-color-only communication for important states
- reduced-motion support
- zoom/text scaling resilience
- labels that remain visible or otherwise understandable during input

## Product archetypes

Use these as starting biases, not templates.

### SaaS / product application

Favor clarity, task flow, reusable components, restrained surfaces, strong empty/error states, and obvious primary actions. Brand appears in type, color, iconography, illustration, and micro-details rather than decorative noise.

### Dashboard / admin / analytics

Favor information hierarchy, compact density, strong alignment, scannable tables/lists, clear filters, sticky context where useful, and restrained motion. Avoid huge marketing-style headers that steal vertical space.

### Landing / marketing

Favor one clear promise, strong hierarchy, credible evidence, purposeful imagery, and a memorable signature element. Sections should progress a story, not become a stack of interchangeable feature cards.

### Commerce

Prioritize product recognition, price/variant clarity, trust, comparison, cart feedback, error recovery, and checkout focus. Decorative complexity must not compete with purchase decisions.

### Content / docs

Prioritize reading rhythm, navigation, code/media treatment, anchors, search/discovery, and accessible typography. Visual personality should support comprehension.

### Portfolio / showcase

Let the work dominate. Navigation and metadata should be easy but visually subordinate. Use composition, motion, and typography to frame content rather than compete with it.

### Mobile app

Favor platform expectations, thumb reach, clear navigation hierarchy, safe areas, keyboard/inset behavior, offline/error states, and concise actions. Avoid web page layouts simply compressed into a phone viewport.

## Component decisions

### Navigation

Choose navigation depth from information architecture. Do not add sidebar + tabs + breadcrumbs + segmented controls unless each level has a distinct purpose.

### Forms

- Group related fields.
- Label clearly.
- Validate near the source of error.
- Preserve entered data on recoverable failure.
- Make pending/success/error states unambiguous.
- Avoid disabling actions without explaining what is missing when the reason is not obvious.

### Tables and lists

- Optimize for scan paths and comparison.
- Align numeric data consistently.
- Keep actions discoverable without turning every row into button soup.
- Use truncation only with a recovery path for full content.
- Consider cards only when the information relationship benefits from them; do not replace useful tabular comparison merely to look modern.

### Dialogs, drawers, popovers

Use the smallest surface that matches the task. Preserve focus, escape/back behavior, and trigger relationship. Do not use modals for content that belongs in the normal page flow.

### Empty states

Explain what the state means and the next useful action. Do not fill every empty state with large generic illustration or motivational copy.

## Charts and data display

Choose the visualization from the question the user must answer:

- comparison across categories -> bar
- trend/order over time -> line
- part of a meaningful whole with few categories -> pie/donut sparingly
- distribution -> histogram/box/strip where supported
- relationship/correlation -> scatter
- progress toward target -> progress/bar/bullet rather than decorative gauge

Always include readable labels/legends, accessible alternatives for critical data, and sufficient contrast. Avoid 3D chart effects and ornamental chart types that obscure comparison.

## Stack adaptation

Detect the actual stack from repository evidence. Use its native primitives and conventions.

- React/Next/Vue/Svelte: preserve existing component, styling, and state patterns.
- Tailwind: reuse configured tokens/utilities; avoid enormous unreadable utility blobs when a local component abstraction is clearer.
- shadcn or other component systems: reuse primitives and variants instead of rebuilding accessibility behavior.
- Flutter/React Native/SwiftUI/Compose: adapt to platform navigation, touch, typography, safe areas, accessibility, and lifecycle patterns.
- Plain HTML/CSS/JS: use semantic HTML, modern layout primitives, custom properties, and progressive enhancement before adding a framework.

## Persistence and token discipline

Deep design work is allowed to spend more context than ordinary engineering, but spend it where it changes the outcome.

- Load this reference for visual-direction decisions, not every frontend bug.
- Load `design-patterns.md` only when page/component/flow pattern choice matters.
- Load `design-taste.md` when distinctiveness and visual craft matter.
- Load `design-motion.md` only when motion/interaction is material.
- Load `design-review.md` during visual verification/audit, not at task start unless the task is review-only.
- Persist a compact design direction only for multi-page or multi-session work where rediscovery would cost more than storing it.

## Failure modes

Avoid:

- styling before understanding the product and surface mode
- choosing a named aesthetic because it is trendy rather than appropriate
- random font/palette selection without role reasoning
- introducing a new component library for visual convenience when the project already has one
- treating responsiveness as "desktop plus one mobile breakpoint"
- calling a page polished without rendering it
- repeatedly redesigning already-correct areas because the agent can keep polishing
