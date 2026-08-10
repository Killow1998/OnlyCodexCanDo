# OnlyCodexCanDo

English | [中文](README.zh-CN.md)

Public repository for reusable Codex skills and agent workflow guidance.

This repository publishes reusable skill source files, cross-project workflow patterns, configuration templates, examples, scripts, and documentation. It serves as a shared public source of stable rules and curated knowledge across multiple agent hosts.

## Agent Workflow

The cross-project operating model is documented in [Personal Agent Workflow](docs/agent-workflow.md). The Chinese source is [个人 Agent 工作流](docs/agent-workflow.zh-CN.md).

It covers independent judgment, instruction layering, compatibility decisions, optional subagents and RTK, risk-proportional three-angle verification, and the `active/design/worklog` documentation flow. The reusable cross-platform core is [templates/AGENTS.global.md](templates/AGENTS.global.md). Platform rules are separate overlays so irrelevant instructions do not occupy every host's context.

There are two independent deployment paths:

| Path | Scope | Source |
| --- | --- | --- |
| Host-global behavior | One agent host, across its workspaces | [Rule-by-rule explanation](docs/global-agents.md), [global template](templates/AGENTS.global.md), and an applicable platform overlay |
| Workspace continuity | One repository, across agents and hosts | [Three-directory workflow](docs/workspace-continuous-documentation.md), [workspace templates](templates/workspace/), and that repository's existing `AGENTS.md` and `docs/` |

Either path can be used alone. Using both is recommended: the host layer standardizes how the agent works, while the workspace layer preserves what the project knows. This is a recommended pairing, not a technical binding; deploy and review each diff independently, and do not duplicate the same rules in both layers.

### Configure a PC's global AGENTS.md

Give the following prompt to the Codex agent running on that PC:

```text
Configure this PC's global Codex AGENTS.md from the public repository https://github.com/Killow1998/OnlyCodexCanDo.git.

1. Read templates/AGENTS.global.md as the cross-platform core.
2. Detect the agent's actual runtime environment before choosing an overlay. If it is Windows native, also read and merge templates/platform/windows-shell.md. If it is Linux, macOS, or WSL acting as a Linux environment, do not load or copy the Windows overlay.
3. Inspect the existing global AGENTS.md first. Preserve non-conflicting local rules, identify conflicts, and show me the proposed diff before writing. Do not overwrite the whole file blindly.
4. Keep machine-specific paths, host names, credentials, session data, and project-only rules out of the shared core.
5. Apply the change only after I confirm the diff. Before writing, create a recoverable local backup of the existing file. Then verify that the resulting file contains the cross-platform core exactly once and only the applicable platform overlay.

Do not modify project repositories, remote hosts, or install any Skill unless I separately authorize it.
```

### Configure continuous documentation in a workspace

Run this prompt from the target workspace. It does not modify the host's global `AGENTS.md`:

```text
Configure a continuous project-documentation workflow in this workspace using https://github.com/Killow1998/OnlyCodexCanDo.git.

1. Read docs/workspace-continuous-documentation.md, templates/workspace/AGENTS.docs-workflow.md, and templates/workspace/worklog-template.md from that public repository.
2. Inspect this workspace's branch, working tree, AGENTS.md or equivalent agent instructions, README, and existing docs before proposing changes. Preserve unrelated work and reuse equivalent documents instead of creating duplicates.
3. Show how existing documents map to three roles: current specs/plans -> docs/active/, stable algorithm and technical design -> docs/design/, and completed-stage records -> docs/worklog/. Reuse equivalent paths instead of copying content merely to match directory names.
4. When a role is missing, create only the necessary active, design, or worklog directory and place the template at docs/worklog/worklog-template.md. Do not add a separate global-state file or a transfer document for every session.
5. Merge only the required read, update, and closeout rules for the three directories into the nearest applicable project AGENTS.md. Do not require a plan or worklog for every small edit.
6. Show the workspace-only diff before writing. Apply it only after I confirm, then verify referenced paths, the template location, and AGENTS routing, and confirm there is no duplicate documentation system or task-created scratch left behind.

Do not modify the host's global AGENTS.md, other workspaces, remote hosts, or install any Skill unless I separately authorize it.
```

Recommended combined deployment: run the host-global prompt once on each host, then run the workspace prompt only inside repositories that need continuity across sessions. Keep the two approvals and diffs separate.

## Skills

### `CodexLFE`

Configures Codex Orchestration to use a bounded GPT-5.6 Luna Max Fast custom Executor.

Main behavior:

- installs or validates only the canonical Codex Orchestration marketplace source;
- creates a machine-local `codex_lfe_executor` custom agent without vendoring Orchestration;
- derives any required Luna v2 compatibility catalog from the target machine's own model cache;
- applies global changes only through explicit, preview-first `setup` and `disable` commands;
- requires a full Codex restart before `verify` performs static checks and requests one real routed spawn;
- fails closed on conflicting config, agent ownership, dependency provenance, or managed-state drift.

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

- generates a `.codex_monitor` scaffold, either workspace-local or (with `--central`) under `~/.codex/taskwatch/jobs/<name>/` so the workspace stays clean;
- writes a configurable `run_command.sh` and `monitor.env`;
- installs hourly report and final summary scripts;
- supports Codex goal-mode terminal emails for `complete`, `blocked`, and `usageLimited`;
- can also install a global Codex `Stop` hook for terminal goal alerts without a workspace-local monitor;
- supports a systemd user timer without sudo;
- keeps SMTP secrets and runtime reports out of Git;
- can infer SMTP host, port, and security from the sender email for common providers, so the user usually only needs sender email, recipient email, and sender password;
- supports clean removal: `install.py --uninstall` for a scaffold, `install_global_hook.py --remove` for the global hook.

Current limitations:

- Workspace-local monitoring is Linux only. Its timer path assumes `systemd --user`.
- On Windows, install only the global goal-terminal `Stop` hook. Do not deploy the workspace-local training or long-job monitor there.
- The global goal-terminal mail path depends on the Codex `Stop` hook. It will not fire for power loss, host crash, or an external kill that bypasses Codex shutdown.
- Goal archive detection is best-effort. It infers archive status from Codex transcripts and local state, so unusual flows may show `未检测到` / `not detected`.
- Workspace-local monitoring assumes the job already has a real command, meaningful logs, or artifact directories. It does not invent task logic.
- SMTP still depends on a valid provider app password or authorization code.
- The global hook and the workspace-local monitor are complementary: the hook handles goal terminal alerts, while the local monitor handles hourly artifact/log summaries.

## Install A Skill

### `CodexLFE`

Add this repository as a Codex plugin marketplace and install CodexLFE:

```text
codex plugin marketplace add https://github.com/Killow1998/OnlyCodexCanDo.git --json
codex plugin add codex-lfe@only-codex-can-do --json
```

Then explicitly invoke setup in Codex:

```text
$codex-lfe:codex-lfe setup
```

After setup reports `RESTART_REQUIRED`, fully quit and reopen Codex, start a new task, and run:

```text
$codex-lfe:codex-lfe verify
```

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

The agent-facing instructions live in [skills/taskwatch/SKILL.md](skills/taskwatch/SKILL.md). The usage guide is in [skills/taskwatch/references/usage.md](skills/taskwatch/references/usage.md).

## Repository Rules

- Publish only curated knowledge that is safe and useful across projects. Keep raw sessions, host inventories, credentials, and private runtime state in a separately governed private layer.
- Use HTTPS clone instructions for public users.
- Keep real user configuration in ignored local files or user config directories.
- Do not commit secrets, tokens, Feishu/Lark document URLs, OpenID values, app IDs, private API endpoints, or real registry values.

Development notes for `lark-worklog-archive` are tracked in [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md).
