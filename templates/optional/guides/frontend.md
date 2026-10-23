# Frontend

Read when designing or changing an interface. Follow an existing design system. For a new interface, start with the choices below and adjust to the rendered result.

## Information and layout

- Organize the screen around the main task. Express structure through grouping, spacing, and action priority.
- Remove repeated labels, taglines, explanations, and decorative eyebrows. Preserve necessary instructions, errors, and accessible names.
- Use language familiar to the audience. Place choices where users actually make the decision.

## Presentation and interaction

- Reuse design tokens and components. For a new web palette, prefer established semantic colors such as Radix Colors.
- Start with three or four type sizes. Distinguish secondary information through weight, space, and color. Keep body text comfortable to read and reserve small text for supporting information.
- Use optical alignment and consistent spacing. Use concentric corners for nested containers. Reduce purely decorative separators, shadows, and colored sidebars.
- Start thin dividers at 0.5–1px and check visibility under zoom.
- Keep motion that helps explain state changes. Start transitions at 250ms ease-out and honor reduced-motion preferences.
- Keep keyboard focus visible. Scroll at viewport edges to reveal the active list item and nearby content.

## Behavior and delivery

- Access the backend through the agreed interface. Cover loading, empty, failure, and recovery states in data interactions.
- Open a preview and exercise the changed interaction. Deliver the actual interface for the user's visual judgment. State missing evidence when a preview is unavailable.
- Do not write UI unit tests or assertions for wording and layout. Verify important business interactions through E2E or existing integration flows.
