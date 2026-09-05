# Workspace Continuous Documentation Workflow

English | [中文](workspace-continuous-documentation.zh-CN.md)

This optional workflow solves one problem: after a person or agent leaves a workspace for a while, they should still be able to see what is being built now, why the system is designed that way, and what was actually completed. A workspace owner chooses it explicitly; host-global setup does not install it automatically.

It is not a general knowledge-management system. The minimum structure has only three directories:

```text
docs/
├── active/    # specs and plans for work currently in progress
├── design/    # stable algorithm, interface, and architecture design
└── worklog/   # completed-stage records and the worklog template
```

`worklog/` is the most important of the three. It preserves work that actually happened, verification evidence, failure causes, and experience worth reusing. When a lesson will continue to shape an algorithm, interface, or architecture, promote it into `design/`; do not create a fourth experience repository.

Projects may keep other directories they already use, but `archive/`, `backlog/`, `reviews/`, `runbook/`, and `handoff/` are not required by this workflow.

## What belongs in each directory

### `docs/active/`: what is being worked on now

Keep only specs or plans that are still active. Before a substantial task, a new agent reads the relevant document here to learn the goal, scope, constraints, acceptance criteria, current progress, and next step.

A useful active document normally includes:

- the problem being solved;
- what is in and out of scope;
- confirmed facts and assumptions that still need evidence;
- implementation stages or steps;
- how each stage will be accepted;
- current progress and the next action.

Do not leave completed plans in `active/` indefinitely. When work finishes, update long-lived algorithm and interface material in `design/`, record actual results in `worklog/`, then archive or clean up the plan using the project's existing convention. Never delete a pre-existing user document without authorization.

### `docs/design/`: why the system works this way

Store designs that continue to affect development, such as:

- algorithms and state transitions;
- module responsibilities and boundaries;
- interfaces, data formats, and error handling;
- safety conditions and required invariants;
- rationale for important design choices.

`design/` is not a daily progress report. Update it when an algorithm, interface, or architecture actually changes. Current execution status stays in `active/`.

### `docs/worklog/`: what was actually done

After a meaningful stage is complete, add a dated or timestamped worklog. It supports review, context recovery, and reusable experience, but it is not a command transcript.

Organize each worklog by objective with four sections:

1. `Background and Goal`: why the work was needed;
2. `Work Completed`: the main approach taken;
3. `Result`: what finished, how it was verified, and any failure causes or lessons worth retaining;
4. `Problems and Next Steps`: remaining, unverified, or risky items.

Commands, files, commits, tests, and log paths may appear as evidence, but they should not define the document structure. Mark unverified claims explicitly. See [worklog-template.md](../templates/workspace/worklog-template.md). When deployed, place it at `docs/worklog/worklog-template.md`.

Evidence needed for a later evaluation or restart must live in an approved durable project location, not only in system temp or chat. Reference large results rather than copying them into Markdown or publishing private artifacts. A past worklog remains a dated record; update the current design without rewriting historical results.

## The complete development loop

```text
Start a task
  -> read the project AGENTS.md
  -> read the relevant current plan in docs/active/
  -> read related docs/design/ documents as needed
  -> implement and verify
  -> update the active plan and design when they materially change
  -> write a docs/worklog/ entry after a completed stage
  -> remove completed plans from active when the task closes
```

In practice:

1. **Before work**: check whether the task already has an active document. Create a spec or plan for substantial work when needed; do not create one for every small edit.
2. **During work**: update the active document only when scope, approach, progress, or the next step materially changes.
3. **When design changes**: update the long-lived algorithm, interface, or architecture document in `design/`; do not leave the change only in chat or a worklog.
4. **After a stage**: update completion state in the active plan and write a worklog with results, evidence, and remaining problems.
5. **At task completion**: make sure `design/` and `worklog/` contain what must survive, then move the finished plan out of `active/`. Reuse an existing archive if the project has one; do not create an archive system just for this workflow.

Treat these steps as one lightweight stage close, not as extra ceremony. A fresh person or agent should be able to tell from `active/`, `design/`, and `worklog/` what was completed, what was verified, and what happens next without reading the previous chat. Do not copy the chat into workspace documentation or create a permanent `handoff` as a fourth source of truth. Small edits remain exempt from this close-out.

## The project `AGENTS.md` only explains how to use the folders

Do not copy specs, designs, or worklogs into the project `AGENTS.md`. It should contain only stable routing rules, for example:

- read `docs/active/` before substantial work;
- read related `docs/design/` before changing algorithms or interfaces;
- write `docs/worklog/` from the template after a completed stage;
- keep current progress and command logs out of `AGENTS.md`.

See [AGENTS.docs-workflow.md](../templates/workspace/AGENTS.docs-workflow.md) for a mergeable rule snippet.

## Deploying into an existing workspace

Do not overwrite existing documentation. Inspect the project first, then make the smallest mapping:

| Needed function | Reuse first | Create when missing |
| --- | --- | --- |
| Current spec or plan | Existing plan, roadmap, or milestone document | `docs/active/` |
| Algorithm and technical design | Existing architecture, design, or spec documents | `docs/design/` |
| Completed-stage record | Existing worklog, devlog, or progress archive | `docs/worklog/` |

If existing paths already serve these roles, keep them and route to them from the project `AGENTS.md`. Do not duplicate a documentation system merely to match directory names.

## Optional workspace modules

Continuous documentation is one workspace module, not a prerequisite for every other module. Deployment should inspect the project, explain only relevant choices, and let the workspace owner select each one independently:

| Module | What it changes | Cost or boundary |
| --- | --- | --- |
| [Continuous documentation rules](../templates/workspace/AGENTS.docs-workflow.md) and [worklog template](../templates/workspace/worklog-template.md) | Adds stable routing for `active/`, `design/`, and `worklog/`. | Requires keeping meaningful plans, design changes, and completed-stage records current; small edits remain exempt. |
| [Experiment workflow](../templates/workspace/experiments.md) | Records the objective, exact configuration, acceptance or stopping conditions, result, and lessons for real experiments; prevents retuning from noisy intermediate signals alone. | Adds pre-run and post-run recording. It can reuse existing experiment paths and does not require the three-directory workflow. |
| [Robotics validation](../templates/workspace/robotics-validation.md) | Separates algorithm, smoke-test, simulation, and live-hardware evidence and keeps frames, state sources, responsibilities, and safety boundaries explicit. | Relevant only when those evidence levels and system boundaries apply. It does not turn simulation into hardware proof and does not require experiment records. |
| [UI conventions](../templates/workspace/ui-conventions.md) | Uses familiar controls, task-appropriate density, restrained visual hierarchy, and review of the implemented interface. | Select for interface work; respect the product brief and accessibility. It does not impose one visual style on every product or require continuous documentation. |

Selecting one module does not select another. A robotics repository may choose robotics validation without continuous documentation; a machine-learning repository may choose experiment records without robotics rules; a long-lived application may choose only the three-directory workflow. Repository names and technology detection support a recommendation but never replace user approval.

The experiment option also distinguishes the formal evaluation protocol from diagnostic variants: an extra metric, harder candidate pool, or new exclusion rule must not silently change reported results. Recheck transient resource/network conditions before preserving an old blocker, and separate independent cleanup from an authorized run where feasible.

For an on-demand documentation close-out, [organizedProj](../skills/organized-proj/SKILL.md) reconciles only affected documents and useful lessons. Installing this Skill and selecting continuous documentation remain independent choices; neither requires automatic cloud archiving.

## What this workflow deliberately does not require

- No separate global-state file; current state belongs in the relevant active spec or plan.
- No transfer document for every session.
- No worklog for every small edit.
- No session transcripts, command dumps, or private host state in the repository.
- No mandatory `archive/`, `backlog/`, `reviews/`, or `runbook/` directories.
- No deletion of unreviewed user documents in the name of cleanliness.

That is the entire continuous-documentation module: **current work lives in `active/`, long-lived design lives in `design/`, and actual results and experience live in `worklog/`.** Experiment and robotics modules remain separately selected additions.
