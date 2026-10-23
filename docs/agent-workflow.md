# Composable Agent Workflow

English | [中文](agent-workflow.zh-CN.md)

This document defines a public, composable workflow for coding agents. It separates a small broadly applicable core from user-selected host and workspace modules. It is a decision framework, not a demand for hidden chain-of-thought or a ritual delay before every answer.

## Outcomes

- Preserve the user's real goal, authorization, and acceptance surface.
- Produce the simplest complete solution with evidence, not the fastest plausible reply.
- Keep the shared core small enough to remain useful across languages, hosts, tools, and development domains.
- Add language, tool, host, experiment, documentation, or domain behavior only when the user chooses the relevant module after understanding its effect and cost.

## Reasoning Preflight

Before a non-trivial action, answer three questions internally:

1. **First principles:** What result does the user need, what is fact or inference, what authority applies, and how will success be observed? If one example reveals a broader pattern, what relevant scope should be checked for the same cause?
2. **Occam's razor:** Which mature maintained solutions already address the need, and would direct adoption, composition, or a narrow custom MVP produce the lowest total lifecycle complexity?
3. **Socratic questions:** What weak premise, counterexample, failure mode, or alternative would change the proposed path?

Ask the user only when an unresolved answer materially changes architecture, data, permissions, security, compatibility, user-visible behavior, or authorization. Otherwise inspect the available evidence, state a low-risk assumption when useful, and continue.

“Pause before answering” should become this internal preflight, not fixed waiting time or a verbose reasoning transcript.

## Instruction Layers

Use each layer for one kind of information:

- Global `~/.codex/AGENTS.md`: the minimal core plus only the stable language, reporting, tool, platform, and host modules selected for that machine.
- Repository or nested `AGENTS.md`: durable team and codebase rules, commands, and boundaries that cannot be discovered reliably from the project itself.
- Selected Markdown guides beside the global file: backend, frontend, or Git preferences read for the relevant work. See [on-demand routing](global-agents.md#on-demand-development-guides). Review-only requests produce findings; simplification requests authorize scoped changes.
- Project documentation: the project's existing plans, design records, progress notes, and worklogs; no fixed directory layout is required.
- Skills: repeatable procedures that benefit from richer instructions, scripts, references, assets, or checks.
- Memories and session indexes: private local context. Curate or index them; do not copy raw histories into public repositories.

Keep each instruction in one authoritative place. Keep shared guidance in the entry point; route conditional detail through a link that says when to read it. Replace stale passages and remove repeated explanations. This applies to guides and Skills as well as `AGENTS.md`; see [writing for agents](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md).

An always-loaded rule earns its instruction budget only when it is stable at that scope, hard or costly to rediscover, relevant to nearly every task there, and consequential when missed. Treat `/init` and other generated `AGENTS.md` output as candidate inventory, not a finished instruction file: remove or rehome repository maps, current file or service locations, implementation details, progress, one-off corrections, and language or domain procedures that code search, manifests, nested `AGENTS.md`, project documentation, or a Skill can disclose when needed. Audit existing rules with the same admission test instead of preserving every non-conflicting line. See the official [AGENTS.md discovery rules](https://learn.chatgpt.com/docs/agent-configuration/agents-md) and the practical [progressive-disclosure guide](https://www.aihero.dev/a-complete-guide-to-agents-md).

### Resolve conflicts at their source

When a Skill demands a planning interview, new files, subagents, or external writes, check whether that behavior belongs to this task and is authorized. A workflow guideline does not override explicit user intent or grant permissions. Name the exact conflicting rule instead of silently stopping, expanding the task, or treating an earlier unchanged approval as expired. System and developer instructions and host permissions still apply.

Fix the source of recurring conflict. For example, an optional tool rule should not coexist with an imported instruction that makes the same tool mandatory. Narrow an overbroad Skill trigger or make it explicit-only; do not keep adding compensating paragraphs to the global core. See [Skill selection and multi-host use](skill-management.md).

OpenAI's [Astra guidance](https://developers.openai.com/api/docs/guides/latest-model#instruction-following) specifically recommends reviewing Skills and `AGENTS.md` for conflicting instructions. Our response is to clarify scope and remove contradictions, not to disable useful capabilities or prescribe one reasoning level for every task. Compare model settings on representative work before changing defaults.

### Subagents only by explicit request

The [subagent-collaboration module](../templates/optional/subagent-context.md) requires the user to explicitly authorize subagents for the current task or a clearly stated scope. Ordinary task requests do not count. Within the authorized scope, pass a fresh task-specific context packet with the objective, necessary facts or file pointers, allowed actions, write ownership, and expected result. The main agent remains responsible for synthesis, integration, and completion.

### Treat session location as a hint

When maintaining a private session archive, do not assign project ownership from `cwd` alone. Combine the working directory with the relevant Git root, touched paths or artifacts, the user's stated objective, and whether the record is a root thread, fork, or subagent. A session may span projects or belong to personal operations, and copied subagent context is not evidence that every referenced project was actually changed. Keep the raw mapping private and publish only curated lessons that remain useful across projects.

## One Global Entry, Progressive Project Records

Use the host-global `AGENTS.md` as the normal workflow entry. It contains the minimal shared behavior and explicitly selected host preferences, never project state, session history, or private host inventory.

After a meaningful stage, the global rule may load `organized-proj`. The Skill inspects the owning project and updates only its existing relevant records; it does not install a project workflow or impose a directory layout. Small edits need no record. Experiment, robotics, UI, and worklog references under `templates/workspace/` are loaded only when the current task needs them.

See [Host-Global AGENTS Rule Reference](global-agents.md) for installation choices and [Progressive Project Records](workspace-continuous-documentation.md) for stage close-out behavior.

### Select modules instead of inheriting them

The cross-platform core does not carry personal language, worktree, subagent, time-zone, or domain policy. During installation, the agent inspects the host and existing rules, filters out irrelevant modules, and explains the remaining choices before the user selects them.

- Do not ask the user about clearly irrelevant modules. A robotics module does not belong in a general web workspace merely because the host also contains robotics repositories.
- Do not infer one option from another. Selecting Chinese does not select a recorded time zone; selecting continuous documentation does not select experiment or robotics rules.
- A selected module must appear exactly once, and parameterized modules such as time zone must not retain unresolved placeholders.

Machine paths, version snapshots, credentials, session state, and host inventories do not belong in public modules.

## Core and Optional Defaults

The minimal core keeps only behavior that remains useful across most development settings: independent judgment, authorization and secret boundaries, focused implementation, evidence-driven debugging, compatibility decisions, proportional verification, and candid reporting.

The following are explicit choices rather than universal defaults:

- conversation language and treatment of English technical identifiers;
- subagent use only after explicit authorization, with fresh context and clear ownership;
- not using Git worktrees unless explicitly requested;
- a recorded time zone;
- detailed Git repository safeguards; and
- experiment discipline, robotics validation, and other domain procedures loaded on demand.

The option catalog is in [templates/optional/](../templates/optional/), and project choices are in [templates/workspace/](../templates/workspace/). Module files contain only the instructions that should run after selection; selection criteria, prerequisites, and tradeoffs stay in this guide and the deployment reference. The deployment agent should recommend a small relevant set, explain it in plain language, and obtain approval through the proposed diff.

## Compatibility Is a Decision

Do not preserve or remove backward compatibility by reflex.

| Context | Default direction | Decision evidence |
| --- | --- | --- |
| Personal research, prototype, unpublished experiment | Prefer direct migration and removal of obsolete paths | Active consumers, reproducibility needs, rollback cost |
| Shared lab infrastructure, multi-user tooling, public package, industrial or production system | Prefer a bounded compatibility or migration plan | Supported versions, downstream users, deprecation window, rollback and observability |
| Context is unclear or the choice changes architecture or user behavior | Ask the developer | Exact consumers, required contract, acceptable breakage |

When compatibility is required, prefer an explicit version boundary, migration path, and removal condition over permanent fallbacks and silent dual behavior.

## Implementation Discipline

- Choose the path with the lowest total lifecycle complexity that fully meets the current requirement. “Simple” concerns lifecycle cost, not merely the smallest diff.
- Before building substantial infrastructure, search for a small set of mature, maintained open-source solutions. Compare direct adoption, composition or adaptation, and a narrow custom MVP. If the choice materially changes architecture, dependencies, or long-term ownership, present concrete options and a recommendation to the user. Reuse proven interfaces and operating patterns even when a focused custom implementation is the better fit.
- Implement the requested behavior without adding adjacent features, future extension points, or explanatory scaffolding. When unrequested work is removed, remove its narrative residue too: names, comments, tests, commits, and pull-request summaries should describe the delivered behavior, not advertise unrelated omissions.
- This applies to every delivered surface, including UI, help, and documentation—not just pull requests. User-facing text should explain the product, not repeat the development prompt or display the agent's internal constraints.
- Use file length, cyclomatic complexity, nesting depth, and dependency count as review signals rather than universal gates. A project-owned limit may be enforced, but do not create a global threshold that merely pushes one responsibility into more files or wrappers.
- Do not add hashes, frozen contracts, baselines, gates, shadow state, or bespoke validation by default. First name the concrete failure they prevent and why Git, versioning, primary keys, transactions, uniqueness, types, or ordinary targeted tests are insufficient. Preserve existing safeguards and use stricter controls at authentication, data-safety, irreversible-operation, release, and other demonstrated high-risk boundaries.
- For a non-obvious problem, use evidence to locate the broken responsibility, constraint, invariant, or data flow before choosing a fix. Restore the correct model with the smallest precise change; do not preserve a tiny diff by stacking temporary patches.
- Grow working systems in verified layers. Each layer should run end to end before the next capability is added.
- Keep concerns separated, but do not add speculative abstractions, configuration, or extension points.
- Preserve unrelated work and touch only files traceable to the request or a necessary induced fix.
- Keep production code free of debug artifacts, dead code, stale branches, and temporary files created by the task.
- Prefer long-lived architectural choices, but do not build an imagined future before the present acceptance criteria are met.

When work spans several hosts, projects, or requested outputs, check each target before reporting completion; one successful target does not close the others. Keep this list in the task or existing plan, not as a new global registry. If a prerequisite fails, distinguish authorization, a persistent failure, and a transient condition. Recheck time-sensitive facts when they determine whether authorized work can continue; do not turn an old resource snapshot or one network failure into an indefinite blocker.

## Verification That Serves Delivery

Define the public behavior and observable outcome, then use the smallest realistic check that can expose a consequential failure. Prefer the real user or caller entry point. A successful command or implementation-shaped assertion is not enough when it does not observe the requested result.

Reuse existing checks and stop when relevant evidence is sufficient. If a check fails, distinguish a product regression from a stale assertion, an environment problem, or an unrelated failure. Do not change correct behavior or build new test infrastructure merely to satisfy the checker; report any material limit.

For UI, figures, documents, and prose, fix obvious technical defects and provide the actual artifact for human review. The user decides whether presentation and expression are satisfactory. Do not write unit tests or permanent assertions for temporary wording, element positions, figure choices, or layout.

Use stricter verification when shared logic, authentication, data safety, irreversible operations, or releases are actually affected. This is a risk decision, not a fixed test count, coverage quota, or default full-suite ritual.

## Progressive Project Records

At the end of a meaningful stage, inspect the project's existing documentation and update only the authoritative records affected by the work. Preserve verified results, durable design changes, unresolved risks, and the next action where the project already keeps them. Do not create fixed `active`, `design`, or `worklog` directories merely to satisfy this workflow. Small edits and tasks with no durable result require no close-out record.

## Packaging Gate

Do not create a Skill merely because a workflow can be written as one. Package it only when:

- the trigger and expected output are stable;
- the process repeats across tasks or projects;
- progressive disclosure is useful;
- scripts, references, assets, or automated checks add real value; and
- installation, updates, and generated state do not cost more than the workflow saves.

A meta-skill or Skill framework may help with authoring and evaluation, but its own benchmark is only candidate evidence. Review its code, dependencies, generated files, context footprint, and reproducibility before installation.

## Updating This Workflow

Change stable rules after repeated feedback, a corrected assumption, a recurring failure, or a verified tool/platform change. Put broadly applicable behavior in the core; put user, tool, host, platform, and domain choices in named modules. Keep one-off preferences and machine state out of the public guide. Update the English and Chinese versions together when their meaning changes.
