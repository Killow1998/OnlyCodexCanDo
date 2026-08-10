## Robotics Validation

Merge this module only into robotics or embodied-AI workspaces after the owner confirms that its evidence model applies.

- Separate algorithm-level tests, build or workflow smoke tests, simulation evidence, and live-hardware evidence. State what each level proves and does not prove.
- Do not claim complete robot behavior from compilation, a connected graph, an API response, or simulation alone when the acceptance criterion requires planner, controller, sensor, visualization, or hardware behavior.
- Keep coordinate frames, state sources, module responsibilities, safety constraints, and the boundary between planning, perception, control, and hardware explicit and observable.
- Add behavior-level regression evidence before deep planner, controller, estimator, or systems refactors when the current behavior can be captured safely.
