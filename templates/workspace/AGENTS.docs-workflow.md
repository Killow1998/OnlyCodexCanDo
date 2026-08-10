## Workspace Documentation Workflow

Merge this section into the nearest applicable project `AGENTS.md` only after the workspace owner approves it. Reuse existing paths that already serve the same purpose instead of creating duplicates.

- Before substantial work, read the relevant current spec or plan under `docs/active/`, then read related algorithm or interface documents under `docs/design/` as needed.
- Keep current goals, scope, acceptance criteria, progress, and next steps in `docs/active/`. Do not use `AGENTS.md` as a progress log.
- Keep stable algorithm, interface, architecture, responsibility, and safety design in `docs/design/`. Do not put daily progress there.
- After a meaningful stage is complete, write a dated entry under `docs/worklog/` using `docs/worklog/worklog-template.md`. Organize it by objective, approach, verified result, and remaining problems rather than by command history.
- Update documents only when the plan, design, verified result, or next step materially changes. Small edits do not require ceremonial documentation.
- When a task finishes, preserve long-lived design in `docs/design/` and results in `docs/worklog/`, then move the completed plan out of `docs/active/` using the project's existing archive or cleanup convention.
- Preserve pre-existing user documents unless their owner authorizes removal. Remove only task-created scratch or completed plan files whose useful information has already been retained.
