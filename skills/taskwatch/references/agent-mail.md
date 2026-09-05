# Agent Mail notifications

English | [中文](agent-mail.zh-CN.md)

TaskWatch supports Tencent Agent Mail (`agently-cli`) and existing SMTP configurations. The CLI package is `@tencent-qqmail/agently-cli`; use its [official setup guide](https://agent.qq.com/doc/cli-setup.md). Keep its OAuth identity and credentials private on the sending host.

## Configure delivery

Confirm the selected job or goals, sender identity, recipient, event types, and allowed content once. Reuse that authorization for matching future alerts. Unchanged progress stays quiet; scheduled digests remain optional.

```bash
python3 skills/taskwatch/scripts/agent_mail.py \
  --config ~/.codex/taskwatch.env \
  --recipient receiver@example.com \
  --cli /absolute/path/to/agently-cli --workspace codex
python3 skills/taskwatch/scripts/install_global_hook.py --hook-only
```

Existing configuration is preserved by default. Use `--force` only when intentionally replacing a backed-up mail configuration. `AGENTLY_WORKSPACE` selects the existing identity; the adapter adds the CLI directory to the service PATH, without copying tokens. Verify that the configured CLI and its sibling Node runtime work in the actual background environment. The generated Linux monitor's `email.env` supports the same configuration command.

The default `MAIL_CONTENT=brief` sends status and evidence locations without transcript or log bodies. `--confirmed` is used only for the standing authorization above. Installing the CLI alone does not authorize arbitrary messages.

## Goal alerts

The Stop hook detects `complete`, `blocked`, and `usageLimited` from supported terminal evidence. A normal turn ending is not goal completion. Review the exact hook using Codex `/hooks`, as required by the [official Hooks documentation](https://learn.chatgpt.com/docs/hooks). Do not alter internal trust records or claim that a configured hook has fired before observing it on the target client.

## Command exit alerts

From the selected workspace, launch the actual training or evaluation through:

```bash
python3 /path/to/taskwatch/scripts/run_with_alert.py \
  --label "Selected training" --state-dir /private/path/taskwatch-runs \
  -- python3 train.py --config experiment.yaml
```

Arguments go directly to the child process without shell interpolation. The supervisor waits for its real exit code and sends a brief notification without an LLM or periodic polling. Mail failures preserve the job's exit code. A zero code means successful process exit, not verified result quality. No already-running job is implicitly attached. User cancellation is not classified as an unexpected failure.

The observer must remain alive: killing the supervisor itself, shutting down the host, or killing its entire cgroup requires an independently authorized external observer. A stopped host cannot reliably alert about its own outage.

## Verification and recovery

Validate a controlled success, failure, and duplicate event before relying on notifications. Verify the real client hook separately from direct script invocation. Check actual receipt separately from the mail service accepting a request.

A `*.delivery.json` receipt is created exclusively before sending to suppress duplicate/concurrent attempts. An accepted CLI response records `accepted`; this does not prove inbox delivery. Failure, timeout, or an uncertain response leaves `pending` and prevents automatic retries. Inspect the sender's sent folder; remove only that event's receipt and retry after confirming that no mail was sent. This avoids duplicate alerts when a server accepted mail but its response was lost.

Keep run state and delivery receipts in private locations. Public examples must not contain real recipients, aliases, task identities, host inventories, or credentials. Source-only checks validate packaging and offline behavior; installation, identity, event detection, send acceptance, and actual receipt are separate acceptance signals.
