## Experiment Workflow

Merge this module into a project `AGENTS.md` only when the workspace owner chooses explicit experiment discipline. Reuse the project's existing experiment records when they serve the same purpose.

- Before a real experiment, training run, benchmark, deployment attempt, hardware test, dataset conversion, or long simulation, record the objective, hypothesis, exact command or configuration, acceptance or stopping conditions, and chosen time zone.
- During a run, distinguish noisy intermediate signals from a defined failure condition. Do not restart, retune, or redesign from noise alone.
- After the run, record start and finish time, actual result, verification evidence, failure cause or lesson, and whether another experiment is justified.
- If the workspace also uses the continuous documentation module, keep the current experiment plan in `docs/active/` and the completed record in `docs/worklog/`; otherwise use the project's existing approved locations.
