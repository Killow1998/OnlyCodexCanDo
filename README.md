# OnlyCodexCanDo

English | [中文](README.zh-CN.md)

Public repository for reusable Codex skills.

This repo is not a memory store and is not tied to one single workflow. It should contain only skill source files, public examples, scripts, and documentation. Private runtime data such as Feishu/Lark document URLs, OpenID values, app IDs, tokens, secrets, and local registries must stay out of Git.

## Skills

### `lark-worklog-archive`

Archives daily Codex/Agent work into a monthly Feishu/Lark worklog document.

It is designed for prompts such as:

- "Archive today's work."
- "Record today's work."
- "Sync this work to the Feishu worklog."

Main behavior:

- one Feishu/Lark worklog document per month;
- one heading per day, using `MM-DD-YYYY`;
- work items grouped by domain and subcategory;
- safe same-day appends through the helper script instead of direct document overwrite;
- optional Markdown links in worklog items for related docs or commits;
- private document mappings kept in local ignored config.

### `TaskWatch`

Scaffolds a reusable read-only Codex monitor for long-running Linux workspaces and jobs.

It is designed for prompts such as:

- "Create a Codex monitor for this long-running run."
- "Set up hourly read-only job reports."
- "Add a systemd user timer and final completion email for this workspace."

Main behavior:

- generates a workspace-local `.codex_monitor` scaffold;
- writes a configurable `run_command.sh` and `monitor.env`;
- installs hourly report and final summary scripts;
- supports Codex goal-mode terminal emails for `complete`, `blocked`, and `usageLimited`;
- can also install a global Codex `Stop` hook for terminal goal alerts without a workspace-local monitor;
- supports a systemd user timer without sudo;
- keeps SMTP secrets and runtime reports out of Git;
- can infer SMTP host, port, and security from the sender email for common providers, so the user usually only needs sender email, recipient email, and sender password.

## Install A Skill

For `lark-worklog-archive`, users should ask Codex to install and configure it instead of running every command manually:

```text
Please install and configure the lark-worklog-archive Skill so Codex/Agent can archive my daily development work into a Feishu/Lark worklog. Use the public repository https://github.com/Killow1998/OnlyCodexCanDo.git over HTTPS; install or check lark-cli; reuse an existing lark-cli app/config if one is already present; otherwise start one-time Feishu/Lark user authorization with docs, drive, markdown, and search:docs:read permissions. I will only confirm authorization in the browser. After authorization, run doctor checks, search/register the existing current monthly worklog document first, and create a new monthly document only if no existing document is found and I explicitly approve it. Tell me that I can use "archive today's work" later. Do not commit any Feishu/Lark document URL, OpenID, app ID, token, secret, or registry value to Git.
```

Detailed agent-facing setup notes are in [skills/lark-worklog-archive/references/setup.md](skills/lark-worklog-archive/references/setup.md).

For `TaskWatch`, Codex should inspect the target workspace first, infer the real job command, logs, and artifact roots, then run the skill installer. For goal-terminal email only, install the global hook instead. The agent-facing instructions live in [skills/taskwatch/SKILL.md](skills/taskwatch/SKILL.md).

## Repository Rules

- Keep this repository focused on reusable skills, not project memories or chat history.
- Use HTTPS clone instructions for public users.
- Keep real user configuration in ignored local files or user config directories.
- Do not commit secrets, tokens, Feishu/Lark document URLs, OpenID values, app IDs, private API endpoints, or real registry values.

Development notes for `lark-worklog-archive` are tracked in [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md).
