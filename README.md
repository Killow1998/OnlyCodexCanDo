# OnlyCodexCanDo

English | [中文](README.zh-CN.md)

Public repository for reusable Codex skills and agent workflow guidance.

This repository publishes reusable skill source files, cross-project workflow patterns, configuration templates, examples, scripts, and documentation. It serves as a shared public source of stable rules and curated knowledge across multiple agent hosts.

## Agent Workflow

The cross-project operating model is documented in [Composable Agent Workflow](docs/agent-workflow.md). The Chinese source is [可组合 Agent 工作流](docs/agent-workflow.zh-CN.md).

It separates a small cross-platform core from user-selected language, tool, host, platform, and workspace modules. The reusable core is [templates/AGENTS.global.md](templates/AGENTS.global.md); optional host modules live in [templates/optional/](templates/optional/), platform modules in [templates/platform/](templates/platform/), and independently selectable workspace workflows in [templates/workspace/](templates/workspace/). This keeps unrelated preferences and domain rules out of every agent's context.

There are two independent deployment paths:

| Path | Scope | Source |
| --- | --- | --- |
| Host-global behavior | One agent host, across its workspaces | [Core and option explanations](docs/global-agents.md), [minimal core](templates/AGENTS.global.md), and user-selected optional or platform modules |
| Workspace workflows | One repository, across agents and hosts | [Three-directory workflow](docs/workspace-continuous-documentation.md), independently selected [workspace modules](templates/workspace/), and that repository's existing `AGENTS.md` and `docs/` |

Either path can be used alone. Using both is recommended: the host layer standardizes how the agent works, while the workspace layer preserves what the project knows. This is a recommended pairing, not a technical binding; deploy and review each diff independently, and do not duplicate the same rules in both layers.

### Configure a PC's global AGENTS.md

Give the following prompt to the Codex agent running on that PC:

```text
Configure this PC's global Codex AGENTS.md from the public repository https://github.com/Killow1998/OnlyCodexCanDo.git.

1. Read templates/AGENTS.global.md as the only automatically recommended cross-platform core. Also read docs/global-agents.md to understand the available choices.
2. Inspect the actual runtime environment and the existing global AGENTS.md before proposing anything. Preserve non-conflicting local rules and identify conflicts; do not overwrite the whole file blindly.
3. Consider only modules that could matter on this host. For each relevant item under templates/optional/ or templates/platform/, explain in plain language what behavior it adds, its cost or tradeoff, and whether you recommend it. Ask me to select modules; do not silently add Chinese, single-agent mode, no-worktree mode, RTK, a time zone, repository/data policy, resource limits, or a platform module. Do not ask about clearly irrelevant modules.
4. If a time-zone module is selected, ask for the IANA time zone and replace its placeholder. If RTK or a resource-limit module is selected, verify that the required tool or runtime actually exists. Detecting Windows makes windows-shell.md relevant, not automatically approved.
5. Keep project workflows and domain rules out of the host-global file. Workspace documentation, experiments, and robotics validation are selected separately inside each workspace.
6. Show the exact merged diff and selected-module list before writing. Apply only after I confirm; create a recoverable backup first, then verify the core and every selected module appear exactly once, no unselected module or unresolved placeholder remains, and preserved local rules still exist.

Do not modify project repositories, remote hosts, or install any Skill unless I separately authorize it.
```

### Configure optional agent workflows in a workspace

Run this prompt from the target workspace. It can configure continuous documentation, experiment records, robotics validation, or any relevant subset, and it does not modify the host's global `AGENTS.md`:

```text
Configure selected agent workflows in this workspace using https://github.com/Killow1998/OnlyCodexCanDo.git.

1. Read docs/workspace-continuous-documentation.md and inspect this workspace's branch, working tree, AGENTS.md or equivalent instructions, README, and existing docs before proposing changes. Preserve unrelated work and reuse equivalent documents instead of creating duplicates.
2. Treat each workspace module as an independent choice. Explain the relevant benefit and maintenance cost of continuous documentation (templates/workspace/AGENTS.docs-workflow.md plus the worklog template), explicit experiment records (templates/workspace/experiments.md), and robotics evidence levels (templates/workspace/robotics-validation.md). Recommend only modules supported by the actual project, but do not infer approval from a repository name or technology alone.
3. Ask me which relevant modules to add. Do not make continuous documentation, experiment discipline, or robotics validation imply one another.
4. If continuous documentation is selected, show how existing documents map to three roles: current specs/plans -> docs/active/, stable algorithm and technical design -> docs/design/, and completed-stage records -> docs/worklog/. Reuse equivalent paths instead of copying content merely to match directory names.
5. Create only missing structures required by selected modules. For continuous documentation, place the template at docs/worklog/worklog-template.md and merge only stable routing rules into the nearest applicable project AGENTS.md; do not require a plan or worklog for every small edit.
6. Show the workspace-only diff and selected-module list before writing. Apply only after I confirm, then verify referenced paths, rules, and templates, and confirm there is no duplicate workflow or task-created scratch left behind.

Do not modify the host's global AGENTS.md, other workspaces, remote hosts, or install any Skill unless I separately authorize it.
```

Recommended combined deployment: select a minimal host-global profile once on each host, then select workspace modules only inside repositories that benefit from them. Keep the approvals and diffs separate; the recommendation does not make either deployment mandatory.

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
