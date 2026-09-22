# UI/UX Product and Component Patterns

Use when the task needs page architecture, information hierarchy, component selection, product-flow design, or chart/data-display choices. This is the deeper pattern library behind `design-system.md`.

## Contents

1. Pattern selection rules
2. Page archetypes
3. Navigation patterns
4. Forms and data entry
5. Search, filters, and command surfaces
6. Lists, tables, and data density
7. Detail and master-detail views
8. Settings and preferences
9. Onboarding and first-run
10. Empty, loading, error, and success states
11. Notifications and feedback
12. Destructive and risky actions
13. Mobile-specific patterns
14. Responsive adaptation
15. Data visualization
16. Content and marketing structures
17. Anti-patterns

## Pattern selection rules

Choose patterns from user intent and information structure, not from visual fashion.

Prefer the familiar pattern when it reduces learning cost. Depart from convention only when the product benefit is clear and the replacement remains discoverable.

When several patterns could work, prefer the one that:

1. exposes the primary task fastest;
2. preserves context during action;
3. minimizes irreversible mistakes;
4. scales to realistic content/data;
5. remains accessible on the target platform;
6. fits the repository's existing interaction language.

## Page archetypes

### Landing / marketing page

Typical hierarchy:

1. Clear value proposition and primary action.
2. Immediate evidence or product visualization.
3. Benefits framed around user outcomes.
4. Demonstration of how it works.
5. Credibility: customers, metrics, quotes, proof, methodology, or transparent detail.
6. Objection handling / comparison / FAQ when useful.
7. Repeated final action.

Do not mechanically use every section. A short product may need only three strong sections. Avoid repeating the same card grid with different headings.

### Product home / dashboard

Prioritize:

- current state
- next useful action
- recent/important work
- exceptions requiring attention
- navigation to deeper tasks

Dashboards should answer questions, not merely display every available metric. Group by decision or workflow, not database entity.

### Admin / operations

Prioritize throughput and clarity:

- dense but readable layout
- strong filters/search
- batch actions where safe
- stable table alignment
- clear status and ownership
- audit/history access when relevant
- minimal decorative motion

### Detail page

Lead with identity and status, then the decisions/actions the user can take. Secondary metadata should not compete with the main task.

### Editor / builder

Preserve context while editing. Common layouts include canvas + inspector, document + toolbar, or preview + controls. Avoid modal-heavy workflows that repeatedly hide the object being edited.

### Settings

Group by user mental model, not backend services. Use clear sections, explain consequences, separate destructive actions, and make save behavior obvious.

## Navigation patterns

### Top navigation

Best for shallow marketing sites or small product areas. Keep the primary route set limited enough to scan quickly.

### Sidebar

Best for multi-area operational products where persistent navigation improves orientation. Use clear grouping and stable ordering. Avoid deeply nested accordions unless hierarchy genuinely requires them.

### Tabs

Use for peer views of the same object/context. Do not use tabs as a substitute for global navigation.

### Segmented control

Use for a small number of mutually exclusive local modes, not major destinations.

### Breadcrumbs

Use when hierarchy matters and users commonly enter deep pages directly. They complement, not replace, primary navigation.

### Bottom navigation

Useful on mobile for a small set of frequent top-level destinations. Avoid overloading it with rarely used actions.

### Command palette

Useful for expert/high-frequency workflows and broad action spaces. It supplements discoverable UI; it should not hide essential functionality from ordinary users.

## Forms and data entry

### Simple form

Use a single-column reading order by default. Group related fields, keep labels persistent, put help text before errors when possible, and place primary action where completion naturally ends.

### Long form

Break into meaningful sections or steps only when it reduces cognitive load. Do not create a wizard for a form users can understand at once.

### Multi-step flow

Use when later steps depend on earlier decisions, when saving progress matters, or when each step has a clear goal. Show progress and preserve data across navigation.

### Inline edit

Use for low-risk, compact changes where context should remain visible. Provide clear edit/save/cancel states and keyboard behavior.

### Validation

- Validate format early when helpful.
- Validate business rules at the authoritative boundary.
- Show errors next to the source and summarize only when the form is large or errors may be offscreen.
- Never erase valid user input after server failure.
- Avoid success states that look like disabled or loading states.

## Search, filters, and command surfaces

### Search

Make scope clear. For large result sets, preserve query state and allow recovery from zero results. Use suggestions/recent items only when they genuinely help.

### Filters

Prefer controls users can understand at a glance. Show active-filter count/state. Keep reset behavior obvious. For complex filters, use a drawer/popover only if inline controls would overwhelm the main surface.

### Sort

Use user-recognizable labels, maintain stable default behavior, and distinguish sort from filter.

### Saved views

Useful for repeated complex filtering or team workflows. Make ownership and update behavior explicit.

## Lists, tables, and data density

### List

Use when each item is read mostly independently and fields do not need column-by-column comparison.

### Table

Use when users compare multiple records across consistent attributes. Preserve alignment and column meaning. Support horizontal adaptation carefully on small screens.

### Cards

Use when items need visual identity, mixed media, or looser content structure. Do not use cards merely because they look modern.

### Dense operational view

Use compact rows, strong alignment, subdued separators, sticky headers/important columns where appropriate, and progressive disclosure for secondary details.

### Row actions

Keep one or two frequent actions visible; move secondary actions to a menu. Avoid a row full of equally weighted icon buttons.

## Detail and master-detail views

Master-detail works well when users repeatedly inspect many records. Preserve selection and list position. On narrow screens, convert to navigation rather than shrinking both panes beyond usefulness.

For one-off detail tasks, a full page may be clearer than a split view.

## Settings and preferences

- Separate account/profile, behavior, notifications, integrations, security, billing, and destructive actions when those concepts exist.
- Use toggles only for immediate binary states.
- Use buttons for actions and navigation, not toggles.
- Explain high-impact settings before the control, not only after an error.
- Avoid autosave for changes with surprising side effects unless feedback and undo are strong.

## Onboarding and first-run

Onboarding should get the user to first value, not tour every feature.

Prefer:

- a short setup that is genuinely required;
- contextual guidance at the moment a feature becomes relevant;
- seeded examples/template content where it reduces blank-page anxiety;
- progress only when the sequence has real steps.

Allow experienced users to skip nonessential education.

## Empty, loading, error, and success states

### Empty

Explain the state, why it may be empty when useful, and the next meaningful action. Distinguish first-use empty from filtered/no-results empty.

### Loading

Keep layout stable. Use skeletons only when they approximate the real structure; otherwise use clear progress feedback. Avoid fake complexity for very short waits.

### Error

Say what failed in user terms, preserve recoverable work, and offer a relevant retry/recovery action. Do not expose raw stack traces or opaque codes as the primary message.

### Success

Use the lightest feedback that confirms the result. Persistent success banners for routine actions create noise; subtle inline confirmation or toast may be enough.

## Notifications and feedback

Choose the channel from urgency and persistence:

- inline: tied to a field/action or persistent state
- toast: transient confirmation/nonblocking feedback
- banner: page/system issue needing attention
- badge/count: persistent pending items
- modal: only when immediate decision/blocking acknowledgement is necessary

Avoid duplicate feedback through multiple channels for the same event.

## Destructive and risky actions

Use friction proportional to consequence.

- Reversible low-risk action: allow direct action plus undo.
- Significant but recoverable action: concise confirmation may be enough.
- Irreversible/high-impact action: explicit confirmation with clear object/consequence; typed confirmation only for exceptional risk.

Never style destructive and primary-positive actions identically when they sit together.

## Mobile-specific patterns

- Keep frequent actions within comfortable reach when practical.
- Respect safe areas, system bars, keyboards, and platform back behavior.
- Use sheets for contextual actions when they fit the platform; do not force desktop modal geometry onto phones.
- Preserve scroll position and state when navigating back.
- Use bottom navigation for frequent top-level destinations, not every feature.
- Treat permissions as a flow: explain context before the system prompt when denial would block value.
- Provide meaningful denied/permanently-denied recovery paths.

## Responsive adaptation

Do not simply shrink components.

### Wide to medium

- reduce unnecessary whitespace;
- collapse secondary panels;
- maintain readable measures;
- preserve primary navigation/action visibility.

### Medium to narrow

- stack logical groups;
- turn multi-pane layouts into navigation;
- replace dense tables with prioritized rows/details only when column comparison is no longer possible;
- move secondary actions into menus/sheets;
- keep touch targets usable.

### Content stress

Test:

- longest realistic title/name
- empty and one-item states
- very large counts
- error copy
- translated/expanded labels
- zoom/text scaling
- image missing/loading failure

## Data visualization

### Bar

Best for categorical comparison and ranking. Horizontal bars help with long labels.

### Line

Best for ordered/time trends. Do not use many indistinguishable series.

### Area

Useful when magnitude over time matters, but overlapping areas can obscure comparison.

### Stacked bar/area

Use when composition across categories/time matters and totals remain interpretable.

### Pie/donut

Use only for a small number of parts of one meaningful whole. Avoid when precise comparison matters.

### Scatter

Use for relationship/correlation/distribution between two numeric variables.

### Histogram

Use for distribution across numeric bins.

### Progress/bullet

Use for actual-versus-target. Prefer to decorative radial gauges for precise reading.

### Heatmap

Use when two-dimensional intensity patterns matter. Provide legend and accessible alternative for critical values.

### Table plus chart

When users need exact values and patterns, provide both instead of forcing one representation to do both jobs.

## Content and marketing structures

### Hero

A hero needs a clear promise, supporting context, and an obvious next step. It does not always need two CTA buttons, a gradient, an illustration, and social proof simultaneously.

### Social proof

Use actual evidence the user/product provides. Never fabricate logos, metrics, customer quotes, awards, or usage claims.

### Feature explanation

Show the feature in context where possible. Outcome + mechanism + evidence is stronger than generic icon + title + paragraph grids.

### Pricing

Make plan differences, billing cadence, limits, and important exclusions easy to compare. Avoid dark-pattern emphasis that obscures total cost or constraints.

### FAQ

Use for real objections or complex conditions, not as filler to lengthen a page.

## Anti-patterns

Avoid unless the brief specifically calls for them and they serve a purpose:

- hero centered by default with generic gradient blob behind it
- every section becoming three or four identical rounded cards
- icon in rounded square above every heading
- pill-shaped controls for unrelated content
- too many floating surfaces and shadows
- nested cards
- decorative dashboards with no decision hierarchy
- table data converted to cards when comparison is the core task
- giant headings in operational product UI that reduce useful viewport space
- carousels for content users need to compare
- hover-only access to essential actions
- hidden labels replaced by placeholder-only forms
- arbitrary glassmorphism/neumorphism that harms contrast or discoverability
- excessive animation on high-frequency interactions
- dense mobile screens created by simply scaling down desktop
- fake metrics, testimonials, logos, notifications, or activity to make the design look complete
