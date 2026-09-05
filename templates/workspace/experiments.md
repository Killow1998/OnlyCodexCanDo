## Experiment Workflow

Merge this module into a project `AGENTS.md` only when the workspace owner chooses explicit experiment discipline. Reuse the project's existing experiment records when they serve the same purpose.

- Before a real experiment, training run, benchmark, deployment attempt, hardware test, dataset conversion, or long simulation, record the objective, hypothesis, exact command or configuration, acceptance or stopping conditions, and chosen time zone.
- During a run, distinguish noisy intermediate signals from a defined failure condition. Do not restart, retune, or redesign from noise alone.
- Keep the formal evaluation protocol separate from diagnostic variants. Do not promote a harder candidate pool, extra metric, new dataset slice, or post-hoc exclusion into the reported result without an explicit decision; assess comparison validity before spending on a new run.
- Recheck transient resource or network conditions before treating an old snapshot as a blocker. Separate independent cleanup or investigation from the authorized run when feasible, and use agreed stopping conditions rather than inventing a broader halt.
- After the run, record start and finish time, actual result, verification evidence, failure cause or lesson, and whether another experiment is justified.
- If the workspace also uses the continuous documentation module, keep the current experiment plan in `docs/active/` and the completed record in `docs/worklog/`; otherwise use the project's existing approved locations.
