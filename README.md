# OnlyCodexCanDo

English | [中文](README.zh-CN.md)

This is my agent workflow repository: a record of the collaboration principles, project workflows, reusable Skills, and lessons I use and refine through real development.

Reusable rules, templates, and tools are maintained here and deployed to selected hosts and projects. Project progress and work records stay with their projects; lessons useful across projects are distilled back into this repository.

## Where to Start

| What you want to do | Start here |
| --- | --- |
| Understand judgment, execution, verification, and collaboration | [Agent workflow](docs/agent-workflow.md) |
| Configure a host's global `AGENTS.md` | [Rule explanations and options](docs/global-agents.md), [minimal core template](templates/AGENTS.global.md) |
| Resume project development after an interruption | [Workspace continuous documentation](docs/workspace-continuous-documentation.md), [project rule snippet](templates/workspace/AGENTS.docs-workflow.md) |
| Select useful Skills and control their triggers | [Skill selection across hosts](docs/skill-management.md), the Skills list below |

Keep local documents current as development progresses: `active/` holds current plans, `design/` preserves stable design, and `worklog/` records stage results, evidence, and lessons. Update when information materially changes; small edits do not require new documents. Cloud archiving, including Feishu/Lark, is a separate on-demand action and does not block local development.

## Deploy the Workflow

There are two independent deployment paths:

| Path | Scope | Source |
| --- | --- | --- |
| Host-global behavior | One agent host, across its workspaces | [Core and option explanations](docs/global-agents.md), [minimal core](templates/AGENTS.global.md), and user-selected optional or platform modules |
| Workspace workflows | One repository, across agents and hosts | [Three-directory workflow](docs/workspace-continuous-documentation.md), independently selected [workspace modules](templates/workspace/), and that repository's existing `AGENTS.md` and `docs/` |

Global configuration defines how the agent works; workspace configuration maintains the project's plans, designs, and work records. We recommend using them together, though either can be deployed on its own.

### Configure a PC's global AGENTS.md

Give the following prompt to the Codex agent running on that PC:

```text
Configure this PC's global Codex AGENTS.md from the public repository https://github.com/Killow1998/OnlyCodexCanDo.git.

1. Read templates/AGENTS.global.md as the only automatically recommended cross-platform core. Also read docs/global-agents.md to understand the available choices.
2. Inspect the actual runtime environment and the existing global AGENTS.md before proposing anything. Classify existing rules as keep, rehome behind progressive disclosure, or propose for removal; identify conflicts and do not preserve discoverable, drift-prone, or one-off details merely because they do not conflict. Do not overwrite the whole file blindly.
3. Consider only relevant host modules and explain behavior, benefit, and cost. Reuse my stated preferences; batch remaining questions through an available interactive choice tool with free-text answers. Do not ask once per module or treat recommended/preselected options as consent. If no choice tool is available, ask one concise question. Language, names, session titles, delegation/context policy, worktrees, RTK, time zones, and other host policies remain independent choices.
4. For names, ask for the user name and agent nickname and keep them in private host configuration. For record or title time zones, confirm the IANA zone and replace the relevant placeholders. For session titles, verify metadata and rename capabilities; do not present an instruction template as an installed hook. Verify prerequisites for RTK, resource limits, and platform modules too; detection is not approval.
5. Keep project workflows and domain rules out of the host-global file. Workspace documentation, experiments, and robotics validation are selected separately inside each workspace.
6. Show the exact merged diff, selected modules and parameters, and every proposed rule removal or rehome; explain any change in authority. Obtain confirmation through the supported approval mechanism, back up, then apply without repeating unchanged approved decisions. Verify unique core/module inclusion, resolved parameters, and preserved approved local rules; validate actual behavior for functional modules. Preference answers are not filesystem permission escalation.

Do not modify project repositories, remote hosts, or install any Skill unless I separately authorize it.
```

### Configure optional agent workflows in a workspace

Run this prompt from the target workspace. It can configure continuous documentation, experiment records, robotics validation, or any relevant subset, and it does not modify the host's global `AGENTS.md`:

```text
Configure selected agent workflows in this workspace using https://github.com/Killow1998/OnlyCodexCanDo.git.

1. Read docs/workspace-continuous-documentation.md and inspect this workspace's branch, working tree, AGENTS.md or equivalent instructions, README, and existing docs before proposing changes. Preserve unrelated work and reuse equivalent documents instead of creating duplicates.
2. Treat each workspace module as an independent choice. Explain the relevant benefit and maintenance cost of continuous documentation (templates/workspace/AGENTS.docs-workflow.md plus the worklog template), explicit experiment records (templates/workspace/experiments.md), and robotics evidence levels (templates/workspace/robotics-validation.md). Recommend only modules supported by the actual project, but do not infer approval from a repository name or technology alone.
3. Reuse stated choices and batch remaining relevant preferences through an available interactive choice tool. Continuous documentation, experiment discipline, robotics validation, and UI conventions (templates/workspace/ui-conventions.md) do not imply one another.
4. If continuous documentation is selected, show how existing documents map to three roles: current specs/plans -> docs/active/, stable algorithm and technical design -> docs/design/, and completed-stage records -> docs/worklog/. Reuse equivalent paths instead of copying content merely to match directory names.
5. Create only missing structures required by selected modules. For continuous documentation, place the template at docs/worklog/worklog-template.md and merge only stable routing rules into the nearest applicable project AGENTS.md; do not require a plan or worklog for every small edit.
6. Show the workspace-only diff and selected-module list before writing. Apply only after I confirm, then verify referenced paths, rules, and templates, and confirm there is no duplicate workflow or task-created scratch left behind.

Do not modify the host's global AGENTS.md, other workspaces, remote hosts, or install any Skill unless I separately authorize it.
```

## Skills

Select by task; installing everything is unnecessary. Each entry owns its detailed procedure and limitations.

| Skill / plugin | Purpose | Selection and guidance |
| --- | --- | --- |
| `codex-home-audit` | Diagnose Codex state size and startup issues | On-demand read-only inspection; cleanup needs separate approval. [Instructions](skills/codex-home-audit/SKILL.md) |
| `lark-worklog-archive` | Archive selected development results to Feishu/Lark | Use on explicit request; project docs remain the daily record. [Instructions](skills/lark-worklog-archive/SKILL.md) · [Setup, authorization, and validation status](skills/lark-worklog-archive/references/setup.md) |
| `organizedProj` | Reconcile affected project docs and preserve verified lessons | Bounded stage close-out; reuse existing documents. [Instructions](skills/organized-proj/SKILL.md) |
| `TaskWatch` | Long-job failure and completion notifications | Supports Agent Mail and SMTP. [Agent Mail setup](skills/taskwatch/references/agent-mail.md) · [Usage guide](skills/taskwatch/references/usage.md) |

## Install A Skill

### `organizedProj`

Give this prompt to the agent on the target host or workspace:

```text
Install organizedProj from https://github.com/Killow1998/OnlyCodexCanDo.git using skills/organized-proj (display name organizedProj, invocation $organized-proj). Compare existing copies and preserve local edits. Ask whether it should be available globally or only in this workspace; install only the selected scope, then run its scripts/check.py. Do not scan or rewrite project docs as part of installation. Report discovery checks separately from behavioral validation.
```

### `codex-home-audit`

Give this prompt to Codex on the target host:

```text
Install codex-home-audit from https://github.com/Killow1998/OnlyCodexCanDo.git, deploying only skills/codex-home-audit and preserving other Skills. Compare any installed copy with the source first, preserve local changes, and show conflicts. After installation, run its scripts/check.py and report results; do not blindly overwrite files to eliminate differences. Do not scan or clean the actual CODEX_HOME. Tell me whether a new task is needed to discover the updated Skill.
```

### `lark-worklog-archive`

Set up local capability first; cloud authorization and archiving wait until needed:

```text
Install lark-worklog-archive from https://github.com/Killow1998/OnlyCodexCanDo.git and use the current official stable lark-cli. Inspect the existing installation, app/config, and customized files first. Use the official update command for CLI upgrades and preserve configuration and credentials. Do not overwrite unreviewed local Skill changes. This setup is local only: do not start login, create a Feishu/Lark app or monthly document, upload work records, or schedule uploads or token keepalive. Project docs remain the daily record. When I explicitly request a Feishu/Lark archive, check authorization and the target document, requesting browser consent only when necessary. Report local checks and cloud validation separately; never put private configuration or credentials in Git.
```

See the [setup guide](skills/lark-worklog-archive/references/setup.md) for commands, auth troubleshooting, and validated versions.

### `TaskWatch`

Use [Agent Mail setup](skills/taskwatch/references/agent-mail.md) for command-exit and goal-terminal alerts, or the [usage guide](skills/taskwatch/references/usage.md) for SMTP and Linux progress reports. Select the recipient and notification content before enabling delivery.

After deployment, verify event detection and actual email delivery. Keep credentials in private local configuration.

## Keep Improving

1. Try a workflow in a real project and record results, problems, and evidence in that project's worklog.
2. When a lesson is reusable, update the relevant OCCD rule, template, Skill, or existing guide, retaining useful context and reasons for the choice.
3. Maintain one primary source for each fact and link to it from the README. Lessons can justify removing or merging rules as well as adding them.
4. After source and documentation changes, update only authorized hosts or projects and verify behavior. A repository update does not mean every installed copy has been updated.

## Repository Rules

- Publish only curated knowledge that is safe and useful across projects. Keep raw sessions, host inventories, credentials, and private runtime state in a separately governed private layer.
- Use HTTPS clone instructions for public users.
- Keep real user configuration in ignored local files or user config directories.
- Do not commit secrets, tokens, Feishu/Lark document URLs, OpenID values, app IDs, private API endpoints, or real registry values.

Development notes for `lark-worklog-archive` are tracked in [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md).
