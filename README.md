# OnlyCodexCanDo

English | [中文](README.zh-CN.md)

This is my agent workflow repository: a record of the collaboration principles, project workflows, reusable Skills, and lessons I use and refine through real development.

Reusable rules, templates, and tools are maintained here and deployed to selected hosts and projects. Project progress and work records stay with their projects; lessons useful across projects are distilled back into this repository.

## Where to Start

| What you want to do | Start here |
| --- | --- |
| Understand judgment, execution, verification, and collaboration | [Agent workflow](docs/agent-workflow.md) |
| Configure a host's global `AGENTS.md` | [Rule explanations and options](docs/global-agents.md), [minimal core template](templates/AGENTS.global.md) |
| Preserve project context after a meaningful stage | [Progressive project records](docs/workspace-continuous-documentation.md), [`organized-proj`](skills/organized-proj/SKILL.md) |
| Select useful Skills and control their triggers | [Skill selection across hosts](docs/skill-management.md), the Skills list below |

After a meaningful stage, `organized-proj` updates the project's existing records on demand. It does not require every repository to install a workflow or adopt fixed directories. Small edits need no record. Cloud archiving, including Feishu/Lark, remains a separate action.

## Deploy the Workflow

The normal setup has one host-global entry point:

| Path | Scope | Source |
| --- | --- | --- |
| Host-global behavior | One agent host, across its workspaces | [Core and option explanations](docs/global-agents.md), [minimal core](templates/AGENTS.global.md), selected optional modules, and global `organized-proj` when stage records are enabled |
| Domain references | Loaded only when a task needs them | [Workspace references](templates/workspace/) for experiments, robotics, UI, and optional worklog formatting |

Projects keep their own facts and records, but they need no separate workflow installation. Add a project-local rule only for a stable convention that cannot be discovered from existing files.

### Configure a PC's global AGENTS.md

Give the following prompt to the Codex agent running on that PC:

```text
Configure this PC's global Codex AGENTS.md from the public repository https://github.com/Killow1998/OnlyCodexCanDo.git.

1. Read templates/AGENTS.global.md as the only automatically recommended cross-platform core. Also read docs/global-agents.md to understand the available choices.
2. Inspect the actual runtime environment and the existing global AGENTS.md before proposing anything. Classify existing rules as keep, rehome behind progressive disclosure, or propose for removal; identify conflicts and do not preserve discoverable, drift-prone, or one-off details merely because they do not conflict. Do not overwrite the whole file blindly.
3. Consider only relevant host modules and explain behavior, benefit, and cost. Reuse my stated preferences; batch remaining questions through an available interactive choice tool with free-text answers. Do not ask once per module or treat recommended/preselected options as consent. If no choice tool is available, ask one concise question. Language, names, subagent policy, worktrees, time zones, and other host policies remain independent choices.
4. For names, ask for the user name and agent nickname and keep them in private host configuration. For recorded time zones, confirm the IANA zone and replace the relevant placeholder. Subagents require explicit authorization for the current task or scope; environment detection and generic requests do not provide it.
5. If the core will route meaningful stage close-out to organizedProj, check whether `skills/organized-proj` is already installed globally. If absent, explain the behavior and ask once whether to install it globally. If declined, omit the Skill reference and use a generic instruction to update existing project records. Do not configure this again per project.
6. Show the exact merged diff, selected modules and parameters, and every proposed removal; explain any change in authority. Obtain confirmation through the supported approval mechanism, back up, then apply. Verify the final file and any authorized Skill installation.

Do not modify project repositories or remote hosts. Install organizedProj only if I select it above; other Skills require separate authorization.
```

### Progressive project records

No per-project setup is required. After a meaningful stage, the global rule loads `organized-proj`, which inspects the project and updates only existing relevant records. Domain references under `templates/workspace/` are read only when the task needs them.

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
Install organizedProj globally from https://github.com/Killow1998/OnlyCodexCanDo.git using skills/organized-proj (display name organizedProj, invocation $organized-proj). Compare existing copies and preserve local edits, then run its scripts/check.py. Do not scan or rewrite project docs as part of installation. Report discovery checks separately from behavioral validation.
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
