# Visual Taste and Art Direction

Use when the user wants a new visual direction, redesign, premium polish, stronger visual hierarchy, less generic AI-looking UI, a marketing/portfolio surface, or explicit aesthetic improvement.

## Contents

1. Purpose
2. Preserve vs replace
3. Commit to a visual world
4. Signature and restraint
5. Composition
6. Typography craft
7. Color craft
8. Spacing and rhythm
9. Shape, borders, shadows
10. Imagery and iconography
11. Product UI vs expressive UI
12. Density and hierarchy
13. Copy and labels
14. Delight
15. Anti-generic rules
16. Design critique questions
17. Completion bar

## Purpose

Produce interfaces with a clear point of view instead of averaging toward familiar AI-generated SaaS templates. Distinctiveness must still serve product truth, accessibility, and task success.

Taste is not random novelty. A good design feels intentional because typography, composition, color, spacing, interaction, and content reinforce the same idea.

## Preserve vs replace

### Refinement

When the request is "polish", "improve", "clean up", or a narrow visual fix:

- preserve product identity and information architecture unless they are causing the problem;
- reuse existing tokens/components;
- fix hierarchy, spacing, typography, states, contrast, and craft without inventing a second brand;
- do not rewrite factual copy or brand voice without reason.

### Redesign

When the user explicitly asks for a redesign or the current visual language is the problem:

- preserve product truth, content meaning, functionality, accessibility, and platform expectations;
- treat the old visual language as evidence, not an obligation;
- choose a replacement direction and execute it consistently instead of splitting the difference between old and new.

## Commit to a visual world

Before substantial visual work, be able to state the direction in one sentence.

Good direction statements combine mood, composition, and material/typographic character:

```text
Calm editorial product UI with compact Swiss typography, warm neutral surfaces, and one electric accent.
```

```text
Dense operations console with sharp alignment, low-chrome surfaces, high-contrast status color, and restrained motion.
```

Avoid vague directions such as "modern", "clean", or "premium" without explaining how that appears in the interface.

A direction should answer:

- What should this feel like?
- What visual choices create that feeling?
- What should it deliberately not look like?

## Signature and restraint

Strong design usually needs one or two memorable moves, not novelty everywhere.

Possible signature areas:

- headline typography
- unusual but usable composition
- a distinct navigation treatment
- one material/surface language
- a strong illustration/photo system
- a meaningful animation motif
- a unique data visualization or interaction

Spend boldness where users notice it. Keep utility UI quieter so the signature remains legible.

## Composition

Build hierarchy with relationships, not decoration.

### Establish levels

Every major surface should make the following distinguishable:

1. dominant focus;
2. primary supporting content/actions;
3. secondary context;
4. quiet metadata/chrome.

If everything is large, colorful, carded, or bold, nothing is dominant.

### Alignment

Use alignment to create invisible structure. Break alignment only to create a deliberate focal point or rhythm shift.

### Symmetry and asymmetry

Symmetry communicates stability and clarity. Asymmetry can create energy and editorial character. Neither is inherently better; use the one that serves the surface mode.

### Whitespace

Whitespace is active hierarchy. Use it to group, separate, pace, and emphasize. Do not compensate for weak hierarchy by wrapping every group in a card.

### Section rhythm

Marketing/read/experience pages benefit from changes in scale, density, media, alignment, or background treatment as the story progresses. Avoid a page that feels like one repeated template block copied six times.

## Typography craft

Typography should carry information hierarchy before decorative effects do.

### Display

Use display type to set personality on expressive surfaces. It may be larger, tighter, more distinctive, or paired with editorial line breaks.

### UI/body

Optimize for repeated reading and controls. Use stable metrics, clear weights, adequate line height, and predictable labels.

### Hierarchy tools

Use combinations of:

- size
- weight
- line height
- width/measure
- tracking
- case
- color/contrast
- surrounding spacing

Do not create hierarchy by font size alone.

### Practical rules

- Avoid using too many weights and sizes.
- Avoid all-caps paragraphs.
- Avoid tiny low-contrast labels as a default aesthetic.
- Keep paragraph measure readable.
- Use tabular numerals where changing numeric data needs alignment.
- For data-heavy UI, prioritize scanability over dramatic display type.
- Preserve font loading/performance constraints; a beautiful type system that causes layout shift or large payloads is not finished.

## Color craft

Color should reinforce hierarchy and meaning.

### Build from roles

Use neutrals/surfaces for structure, one primary accent for emphasis, and semantic colors for state.

### Saturation discipline

High saturation everywhere feels cheap and reduces meaning. Reserve strongest chroma for actions, selection, data emphasis, or brand signature.

### Temperature

Warm and cool neutrals create different character even before accent color. Choose intentionally and keep them coherent.

### Contrast hierarchy

Primary text, secondary text, disabled text, borders, surfaces, and background need intentional contrast relationships. Muted does not mean barely visible.

### Gradients

Use gradients when they belong to the visual world or communicate depth/state. Do not add them because "AI/SaaS hero" feels empty.

## Spacing and rhythm

Good spacing is relational.

- Tight spacing signals one unit.
- Moderate spacing separates related subgroups.
- Large spacing separates concepts/sections.

Use repeated spacing intervals to establish rhythm. Introduce larger jumps at hierarchy boundaries.

Avoid uniform gaps everywhere. A page with `gap: 24px` applied to every relationship has no pacing.

## Shape, borders, shadows

### Radius

Choose a radius family appropriate to the product personality. Sharp, small, medium, and highly rounded systems imply different character.

Do not make every object a pill or 20px rounded rectangle.

### Borders

Use borders for structure and separation. Very low-contrast hairlines can disappear on real displays; verify them.

### Shadows

Use shadows for elevation/interaction when depth is part of the system. Avoid identical soft shadows on every card.

### Surfaces

Before adding a card, ask whether grouping can be expressed with layout, whitespace, divider, type hierarchy, or background change.

## Imagery and iconography

### Imagery

Use real product imagery, supplied assets, or truthful generated/abstract visuals appropriate to the brief. Never fabricate customer evidence or product capabilities.

Image crops, aspect ratios, and placement should be art-directed rather than dropped into generic rounded rectangles.

### Icons

Use one coherent icon family. Icons should support recognition, not decorate every label. Provide text or accessible names where meaning is not obvious.

Avoid the generic pattern of an icon in a colored rounded square above every feature title unless the product identity specifically uses it.

## Product UI vs expressive UI

### Operational product UI

Design serves repeated task performance.

Prioritize:

- fast scanning
- predictable interaction
- compact hierarchy
- stable component behavior
- high-quality states and feedback
- quiet brand expression

Distinctiveness can come from typography, spacing, iconography, color precision, micro-interactions, and one signature element rather than dramatic layout everywhere.

### Marketing / portfolio / showcase

Design itself contributes to persuasion or identity. Allow stronger scale contrast, composition, media, typographic character, and motion when they support the story.

Do not confuse expressive with cluttered. Keep one clear reading path.

## Density and hierarchy

Match density to the job.

### Spacious

Useful for persuasion, premium positioning, editorial content, and showcases. Large whitespace should make important content feel deliberate, not merely sparse.

### Balanced

General product interfaces. Enough whitespace for clarity without reducing information throughput.

### Dense

Operations/admin/data products. Use compact controls and rows, but strengthen alignment, grouping, type hierarchy, and hover/focus states so density does not become noise.

## Copy and labels

Interface language is part of design.

- Use user-recognizable nouns and verbs.
- Prefer active, direct labels.
- Button labels should describe the action, not generic "Submit" where a clearer verb exists.
- Error messages should say what happened and what the user can do.
- Empty states should explain the next useful step.
- Keep headings meaningful; avoid filler like "Powerful features" when a more specific claim exists.
- Never invent proof, metrics, awards, testimonials, or enterprise logos.

## Delight

Delight should amplify meaning, not interrupt work.

Good places:

- successful completion of a meaningful action
- first-run moments
- an expressive marketing interaction
- an elegant transition that preserves spatial understanding
- subtle tactile feedback on controls

Bad places:

- every hover
- repeated keyboard-driven actions
- waiting states where animation makes the wait feel longer
- critical/error flows where decoration distracts from recovery

Read `design-motion.md` when motion is material.

## Anti-generic rules

Actively challenge these common defaults:

- generic centered hero + gradient blob + two CTAs
- endless 3-column feature cards
- purple/blue gradient used without brand reason
- every section inside rounded cards
- nested cards / card inside card inside card
- rounded-square icon badge above every heading
- all sections centered
- all text using the same width and alignment
- giant marketing typography inside operational dashboards
- random glassmorphism
- excessive pills
- decorative charts
- low-contrast gray text on tinted surfaces
- identical shadows everywhere
- using the same familiar font/style combination across unrelated products
- adding animation because static layout feels under-designed

Do not ban a pattern if the user explicitly asks for it or the existing brand legitimately uses it. The rule is intentionality, not contrarianism.

## Design critique questions

Before calling a visual surface strong, ask:

### Hierarchy

- Can a user identify the primary purpose/action in a few seconds?
- Is there one dominant focal point rather than several competing ones?

### Cohesion

- Do type, color, spacing, radius, iconography, imagery, and motion belong to the same visual world?
- Are exceptions intentional?

### Distinctiveness

- What would make this recognizable if the logo disappeared?
- Is there at least one intentional signature beyond generic component defaults?

### Product fit

- Does the style help the user's task and product positioning?
- Is an operational surface too theatrical or a persuasive surface too sterile?

### Restraint

- What can be removed without losing meaning?
- Are cards, borders, shadows, badges, pills, gradients, and motion being used to solve real hierarchy problems?

### Reality

- Does it still work with long copy, empty data, errors, mobile width, keyboard focus, and reduced motion?

## Completion bar

Visual quality is not complete at code compile time.

For substantial design work:

1. Build the whole intended slice before micro-polishing.
2. Render it in the real runtime.
3. Inspect desktop and mobile/narrow states together.
4. Fix concrete hierarchy, overflow, spacing, typography, state, and interaction defects in one batch.
5. Run one focused confirmation pass.
6. Stop unless the user explicitly asks for another design iteration.

Use `design-review.md` for the full visual QA pass.
