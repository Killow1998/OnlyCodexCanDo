---
name: taskwatch
description: Scaffold or update a reusable read-only Codex monitor for long-running Linux tasks. Use when the user wants hourly Codex summaries, final email delivery, a systemd user timer, a global Codex Stop hook for goal-terminal email alerts, or a workspace-local `.codex_monitor` setup for training, goal-mode runs, evaluation, or other long tasks with meaningful logs and artifacts.
---

# TaskWatch

Turn an existing long-running Linux workflow into a reusable Codex monitor skill and workspace scaffold.

This skill is for long-running jobs that already have a real entrypoint, log path or artifact trail, and a meaningful completion condition. Typical targets include training, evaluation, batch goal-mode runs, and offline processing. It does not design the job logic itself.

## Choose A Mode First

- Workspace-local monitor: hourly read-only reports, final summary email, optional `systemd --user` timer for one long-running Linux job. Linux only.
- Global Codex Stop hook: goal-terminal email on `complete`, `blocked`, and `usageLimited`. Cross-platform when Codex hooks and the current Python runtime are available.

On Windows, install only the global hook. On Linux, the two modes are complementary: the hook covers goal terminal alerts, the local monitor covers hourly log and artifact summaries; goal-mode runs usually want both.

Command examples assume a repo checkout. When running from the installed copy, replace `skills/taskwatch` with `~/.codex/skills/taskwatch`.

## Workspace-Local Monitor (Linux)

1. Inspect the target workspace first, and infer values from it instead of asking the user to fill flags manually:
   - job entrypoint or wrapper;
   - main log path if one exists;
   - artifact directories that should be watched;
   - process pattern or user systemd service if one exists;
   - current `.codex_monitor` files if this is an upgrade.
2. Keep deployment user-facing and minimal. The user should normally only need to provide:
   - sender email;
   - recipient email;
   - sender password or SMTP authorization code.
3. Generate or refresh the monitor with the installer:

   ```bash
   export TASKWATCH_SENDER_PASSWORD='smtp-app-password'
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
     --recipient-email receiver@example.com
   ```

   Prefer `TASKWATCH_SENDER_PASSWORD` over the `--sender-password` flag so the secret stays out of shell history and process listings. The flag still works and wins when both are set.

   Add `--central` to keep the workspace clean: the whole scaffold, including `run_with_monitor.sh`, is created under `~/.codex/taskwatch/jobs/<systemd-basename>/` and no files are written into the workspace. The scaffold records the target workspace through `CODEX_MONITOR_WORKSPACE` in `monitor.env`; start the job with `~/.codex/taskwatch/jobs/<systemd-basename>/run_with_monitor.sh`. Use `--job-dir` for a custom scaffold location.

4. `SMTP_HOST`, `SMTP_PORT`, and security mode are inferred automatically from common sender domains. Use overrides only if the sender domain is unusual or the provider uses a nonstandard endpoint.
5. Use `--dry-run` to preview managed file paths without writing. Use `--force` only when intentionally replacing managed monitor files in an existing workspace.
6. Preserve runtime-only files such as `.codex_monitor/email.env`, reports, snapshots, and state outputs.
7. Verify after generation:

   ```bash
   python skills/taskwatch/scripts/check.py
   CODEX_MONITOR_SKIP_EMAIL=1 /abs/workspace/.codex_monitor/scripts/hourly_check.sh
   ```

## Global Goal-Terminal Hook

Install or refresh the Codex `Stop` hook:

```bash
export TASKWATCH_SENDER_PASSWORD='smtp-app-password'
python skills/taskwatch/scripts/install_global_hook.py \
  --sender-email sender@example.com \
  --recipient-email receiver@example.com
```

When `~/.codex/taskwatch.env` already exists, refresh the hook without touching mail settings:

```bash
python skills/taskwatch/scripts/install_global_hook.py --hook-only
```

## Uninstall

Remove a workspace-local monitor (preserves `email.env`, reports, snapshots, and state unless `--purge` is added; runs the systemd timer uninstall first when `systemctl` is available):

```bash
python skills/taskwatch/scripts/install.py /abs/workspace --uninstall
```

For a central scaffold, pass the same layout flags used at install time:

```bash
python skills/taskwatch/scripts/install.py /abs/workspace --central --systemd-basename codex-long-job-monitor --uninstall
```

Remove the global Stop hook block from `~/.codex/config.toml` (keeps `taskwatch.env` and state unless `--purge`):

```bash
python skills/taskwatch/scripts/install_global_hook.py --remove
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

With `--central`, the same scaffold lives under `~/.codex/taskwatch/jobs/<systemd-basename>/` instead of the workspace.

## Constraints

- Workspace-local monitor deployment is Linux only. The generated timer targets `systemd --user` and installs without sudo.
- The generated hourly monitor is read-only from Codex's perspective.
- Final email is optional. If `.codex_monitor/email.env` is missing, reports are still generated locally.
- For Codex goal-mode runs, use `--goal-mode` so the final email can distinguish `complete`, `blocked`, and `usageLimited`.
- On Windows Codex Desktop app, `[[hooks.Stop]]` did not auto-trigger after CLI trust in the 2026-06-12 verification; see [references/usage.md](references/usage.md) before relying on Desktop app goal emails.
- Treat the real job exit code as the default completion signal. Existing `TRAIN_DONE` or `TRAIN_FAILED` markers are still read for backward compatibility.

## Maintenance

- After updating this skill in the repo, sync the installed copy under `~/.codex/skills/taskwatch` and re-run `check.py` (it compares the two).
- When changing email templates, installer flags, or hook trigger logic, extend `tests/test_taskwatch_hook.py` or `tests/test_install.py`.
- Never commit `taskwatch.env`, SMTP secrets, reports, or state files.

## References

- Usage guide, email content, verification, and troubleshooting: [references/usage.md](references/usage.md)
