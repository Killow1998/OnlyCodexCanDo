## UI Verification

- Do not write unit tests for UI components, markup, styles, layouts, or UI interactions. Open the actual interface, check the changed flow for obvious breakage, and provide a usable preview for the user's review. Add browser or end-to-end automation only for a concrete recurring failure, not for every visual edit.
- Independently test business logic, calculations, data transformations, and API behavior when warranted. Preserve existing tests unless their removal is separately authorized; a passing build does not replace visual and interaction checks.
- For UI, figures, PDFs, and prose, the user decides whether the presentation and expression are satisfactory. Provide the current artifact and a short account of the changes; do not encode temporary wording, element positions, or figure choices as permanent assertions. Fix obvious technical defects, then seek user feedback before further aesthetic revisions.
