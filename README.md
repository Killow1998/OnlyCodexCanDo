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
- matched to `lark-cli 1.0.51`; update older CLI installs instead of relying on legacy auth-output compatibility.

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

Current limitations:

- Workspace-local monitoring is Linux only. Its timer path assumes `systemd --user`.
- On Windows, install only the global goal-terminal `Stop` hook. Do not deploy the workspace-local training or long-job monitor there.
- The global goal-terminal mail path depends on the Codex `Stop` hook. It will not fire for power loss, host crash, or an external kill that bypasses Codex shutdown.
- Goal archive detection is best-effort. It infers archive status from Codex transcripts and local state, so unusual flows may show `未检测到` / `not detected`.
- Workspace-local monitoring assumes the job already has a real command, meaningful logs, or artifact directories. It does not invent task logic.
- SMTP still depends on a valid provider app password or authorization code.
- The global hook and the workspace-local monitor are complementary: the hook handles goal terminal alerts, while the local monitor handles hourly artifact/log summaries.

## Install A Skill

### `lark-worklog-archive`

Users should ask Codex to install and configure it instead of running every command manually:

```text
Please install and configure the lark-worklog-archive Skill so Codex/Agent can archive my daily development work into a Feishu/Lark worklog. Use the public repository https://github.com/Killow1998/OnlyCodexCanDo.git over HTTPS; install or check lark-cli; reuse an existing lark-cli app/config if one is already present; otherwise start one-time Feishu/Lark user authorization with docs, drive, markdown, and search:docs:read permissions. I will only confirm authorization in the browser. After authorization, run doctor checks, search/register the existing current monthly worklog document first, and create a new monthly document only if no existing document is found and I explicitly approve it. Tell me that I can use "archive today's work" later. Do not commit any Feishu/Lark document URL, OpenID, app ID, token, secret, or registry value to Git.
```

Detailed agent-facing setup notes are in [skills/lark-worklog-archive/references/setup.md](skills/lark-worklog-archive/references/setup.md).

### `TaskWatch`

For a workspace-local monitor, Codex should inspect the target workspace first, infer the real job command, logs, artifact roots, process pattern, and any existing user systemd service, then run the skill installer:

```text
Please install and configure the TaskWatch skill from https://github.com/Killow1998/OnlyCodexCanDo.git. Inspect the target workspace first and infer the real long-running command, main logs, artifact directories, process pattern, and any existing user systemd service instead of asking me to fill every flag manually. Deploy it in Linux only. For a workspace-local monitor, generate .codex_monitor, run_with_monitor.sh, hourly read-only reports, final completion email, and an optional systemd --user timer. For goal-mode runs, also make sure final emails can distinguish complete, blocked, and usageLimited. Only ask me for three mail inputs when needed: sender email, recipient email, and the sender SMTP password or authorization code. Keep secrets, reports, and local runtime state out of Git. After installation, run the skill checks, verify the global skill copy if one is installed, and give me the exact command I should use to start the monitored run.
```

For global goal-terminal email only, install the hook without a workspace-local monitor:

```text
Please install only the global TaskWatch goal-terminal email hook from https://github.com/Killow1998/OnlyCodexCanDo.git. Configure the Codex Stop hook under ~/.codex so goal runs send terminal emails for complete, blocked, and usageLimited. Reuse existing settings if they are already present. Only ask me for sender email, recipient email, and the sender SMTP password or authorization code if mail is not configured yet. Keep all secrets in local ignored files and verify the hook with a safe smoke test.
```

On Windows, use this global-hook-only path. Linux hosts can use the workspace-local monitor for training, evaluation, or other long-running jobs with `systemd --user`.

The agent-facing instructions live in [skills/taskwatch/SKILL.md](skills/taskwatch/SKILL.md).

## Repository Rules

- Keep this repository focused on reusable skills, not project memories or chat history.
- Use HTTPS clone instructions for public users.
- Keep real user configuration in ignored local files or user config directories.
- Do not commit secrets, tokens, Feishu/Lark document URLs, OpenID values, app IDs, private API endpoints, or real registry values.

Development notes for `lark-worklog-archive` are tracked in [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md).
