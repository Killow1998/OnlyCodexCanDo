# Progressive Project Records

English | [中文](workspace-continuous-documentation.zh-CN.md)

Projects do not need to install a documentation workflow. The host-global `AGENTS.md` may route a meaningful completed stage to the globally installed [`organized-proj`](../skills/organized-proj/SKILL.md) Skill. The Skill is loaded only then, reuses the project's existing records, and skips small edits.

## What counts as a meaningful stage

Close a stage when work produced an independently reviewable result, changed long-lived design, or left a next action that must survive the current conversation. A command finishing or a response ending is not enough.

## What the Skill records

Inspect the affected project and update only existing authoritative documents whose content changed:

- the current plan or progress record;
- stable design or interface documentation;
- a completed-stage worklog or equivalent record;
- affected user-facing usage guidance.

Do not create `docs/active`, `docs/design`, `docs/worklog`, a project `AGENTS.md` section, or another documentation hierarchy merely to match this repository. If a project already uses those paths, keep using them. Record results and evidence by objective rather than copying commands or chat history.

Git commits, cloud archives, publishing, remote writes, and document deletion still require their own authority. A local project record is enough to close the stage.

## Global deployment

When configuring a host-global `AGENTS.md`, check whether `organized-proj` is installed globally. If absent, explain its stage-close behavior and ask once whether to install it from `skills/organized-proj/`. If the user declines, omit the Skill reference and retain a generic instruction to use the project's existing record. Do not ask again in each project.

## Domain references remain on demand

The files under [`templates/workspace/`](../templates/workspace/) are references, not project installation requirements:

- [`experiments.md`](../templates/workspace/experiments.md) for real experiments;
- [`robotics-validation.md`](../templates/workspace/robotics-validation.md) for simulation or hardware evidence;
- [`ui-conventions.md`](../templates/workspace/ui-conventions.md) for interface work;
- the worklog templates when a project has no preferred record format.

Read only the reference relevant to the current task. Add a project-local rule only when the project has a stable convention that cannot be discovered from its existing files.
