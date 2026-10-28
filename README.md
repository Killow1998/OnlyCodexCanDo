# OnlyCodexCanDo

English | [中文](README.zh-CN.md)

This is my agent workflow repository: a record of the collaboration principles, project workflows, reusable Skills, and lessons I use and refine through real development.

Reusable rules, templates, and tools are maintained here and deployed to selected hosts and projects. Project progress and work records stay with their projects; lessons useful across projects are distilled back into this repository.

## Where to Start

| What you want to do | Start here |
| --- | --- |
| Understand judgment, execution, verification, and collaboration | [Agent workflow](docs/agent-workflow.md) |
| Configure a host's global `AGENTS.md` | [Rule explanations and options](docs/global-agents.md), [minimal core template](templates/AGENTS.global.md) |
| Load backend, frontend, or Git guidance when needed | [On-demand guides and routing](docs/global-agents.md#on-demand-development-guides) |
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

1. Read templates/AGENTS.global.md and docs/global-agents.md. Inspect this host and its existing global AGENTS.md; identify rules to keep, move behind progressive disclosure, or remove, including conflicts and obsolete details.
2. Reuse my confirmed preferences. Explain relevant options and batch unresolved choices in one question; recommendations are not consent. Names, language, time zone, and other options are independent; resolve selected placeholders without publishing private values.
3. Compose the core and selected preferences by meaning. Merge overlaps and shorten wording while preserving authorization and read triggers. Default to a short opening and compact list; omit module headings, explanations, and examples. Respect my explicit format preferences.
4. Copy only selected guides in the selected language as described in docs/global-agents.md; keep one routing line in AGENTS.md. If organized-proj is absent, ask once whether to install it globally; if declined, use “update existing project records” without a Skill reference. No per-project setup is needed.
5. Show the exact diff, selected options, and proposed removals, including any authorization changes. After approval, back up, apply, and read back to verify the file and any authorized installation.

Do not modify project repositories or remote hosts. Subagents require explicit task or scope authorization. Install only authorized Skills.
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
