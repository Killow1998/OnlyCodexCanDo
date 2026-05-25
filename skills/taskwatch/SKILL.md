---
name: taskwatch
description: Scaffold or update a reusable read-only Codex monitor for long-running Linux tasks. Use when the user wants hourly Codex summaries, final email delivery, a systemd user timer, a global Codex Stop hook for goal-terminal email alerts, or a workspace-local `.codex_monitor` setup for training, goal-mode runs, evaluation, or other long tasks with meaningful logs and artifacts.
---

# TaskWatch

Turn an existing long-running Linux workflow into a reusable Codex monitor skill and workspace scaffold.

This skill is for long-running jobs that already have a real entrypoint, log path or artifact trail, and a meaningful completion condition. Typical targets include training, evaluation, batch goal-mode runs, and offline processing. It does not design the job logic itself.

This skill has two deployment modes:

- workspace-local monitor mode for long-running Linux jobs;
- global Codex hook mode for goal terminal email alerts on `complete`, `blocked`, and `usageLimited`.

## Workflow

1. Inspect the target workspace first:
   - job entrypoint or wrapper;
   - main log path if one exists;
   - artifact directories that should be watched;
   - process pattern or user systemd service if one exists;
   - current `.codex_monitor` files if this is an upgrade.
2. Keep deployment user-facing and minimal. The user should normally only need to provide:
   - sender email;
   - recipient email;
   - sender password or SMTP authorization code.
3. For workspace-local monitoring, generate or refresh the monitor with the installer:

   ```bash
   python skills/taskwatch/scripts/install.py /abs/workspace \
     --label "Run Label" \
     --systemd-basename codex-long-job-monitor \
     --job-service optional.service \
     --primary-log outputs/run.log \
     --progress-log outputs/hourly_monitor.log \
     --artifact-dir logs \
     --artifact-dir outputs \
     --process-grep 'train.py|torchrun|python -m yourpkg|codex exec' \
     --goal-mode \
     --run-command 'python3 -B scripts/run.py --arg value' \
     --sender-email sender@example.com \
     --recipient-email receiver@example.com \
     --sender-password 'smtp-app-password'
   ```

4. For global goal-terminal mail, install the Codex `Stop` hook:

   ```bash
   python skills/taskwatch/scripts/install_global_hook.py \
     --sender-email sender@example.com \
     --recipient-email receiver@example.com \
     --sender-password 'smtp-app-password'
   ```

5. `SMTP_HOST`, `SMTP_PORT`, and security mode are inferred automatically from common sender domains. Use overrides only if the sender domain is unusual or the provider uses a nonstandard endpoint.
6. Use `--force` only when intentionally replacing managed monitor files in an existing workspace.
7. Preserve runtime-only files such as `.codex_monitor/email.env`, reports, snapshots, and state outputs.
8. Verify after generation:

   ```bash
   python skills/taskwatch/scripts/check.py
   CODEX_MONITOR_SKIP_EMAIL=1 /abs/workspace/.codex_monitor/scripts/hourly_check.sh
   ```

## Generated Files

- `.codex_monitor/monitor.env`: monitor configuration
- `.codex_monitor/run_command.sh`: real long-running command wrapper
- `.codex_monitor/scripts/*.sh` and `send_mail.py`
- `.codex_monitor/email.env.example`
- `.codex_monitor/README.md`
- `run_with_monitor.sh`
- `run_train_with_monitor.sh` compatibility wrapper
- `~/.codex/taskwatch.env` for global hook mail settings
- `~/.codex/config.toml` managed `Stop` hook block for goal-terminal alerts

## Notes

- Linux only for deployment. The generated timer targets `systemd --user`.
- The generated hourly monitor is read-only from Codex's perspective.
- The generated systemd user timer installs without sudo.
- Final email is optional. If `.codex_monitor/email.env` is missing, reports are still generated locally.
- For Codex goal-mode runs, use `--goal-mode` so the final email can distinguish `complete`, `blocked`, and `usageLimited`.
- The global Codex hook watches goal terminal states only. It does not replace the workspace-local hourly monitor for training logs and artifacts.
- Codex should infer the real job command, logs, and artifact directories from the workspace whenever possible instead of asking the user to fill them manually.
- Treat the real job exit code as the default completion signal. Existing `TRAIN_DONE` or `TRAIN_FAILED` markers are still read for backward compatibility.
- After updating this skill in the repo, sync the installed copy under `~/.codex/skills/taskwatch`.
