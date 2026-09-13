## UI Verification

- Do not write unit tests for UI components, markup, styles, layouts, or UI interactions. Verify UI changes in the actual rendered interface and through relevant user flows; use browser or end-to-end checks when they provide useful evidence.
- Independently test business logic, calculations, data transformations, and API behavior when warranted. Preserve existing tests unless their removal is separately authorized; a passing build does not replace visual and interaction checks.
