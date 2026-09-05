# lark-worklog-archive Setup

This file is for Codex/Agent. Normal users should not need to run these commands manually.

## User-Facing Install Prompt

Use the install prompt in the [English README](../../../README.md#lark-worklog-archive) or [中文 README](../../../README.zh-CN.md#lark-worklog-archive). Keep the user-facing prompt there; this guide owns the detailed commands and troubleshooting.

Local installation does not require browser consent or a cloud write. Check authorization when a cloud archive is explicitly requested, and ask for browser consent only when the diagnosed state requires it.

## What Codex Should Do

On Windows, use Windows Terminal with a PowerShell profile. Use `python` there, and call `lark-cli.cmd` if PowerShell blocks `lark-cli.ps1`. On Unix systems where `python` is not Python 3, use `python3` for the same commands.

The helper supports Python 3.8 and newer. Python 3.9+ provides `zoneinfo`; on Python 3.8 the optional `backports.zoneinfo` package enables arbitrary IANA zones, while the default `Asia/Shanghai` and explicit `UTC` modes work without that dependency.

Install the repo and local skill:

```bash
git clone https://github.com/Killow1998/OnlyCodexCanDo.git
cd OnlyCodexCanDo
python skills/lark-worklog-archive/scripts/install.py
```

Install or check `lark-cli`:

```bash
npx @larksuite/cli@latest install
lark-cli --version
```

Use the current stable CLI and record the version actually checked. `lark-cli 1.0.93` passed Windows version/passthrough checks, local auth-metadata parsing, the auth and document command-help checks, and the helper's offline release checks. Its official Skills were also confirmed in sync. Authenticated cloud read/write acceptance has not been rerun on this version; the last live auth/doctor baseline remains `lark-cli 1.0.87`. Do not treat an upgrade as restored authorization or prompt for consent merely to complete an offline check.

The helper expects the `auth status --json --verify` identity/token shape and bypasses the npm `.cmd` shim internally so URL arguments containing `&` remain intact. Record the installed version before diagnosing auth; do not use an upgrade or reinstall as the first repair. For a requested upgrade, use `lark-cli update`; it also syncs official Skills. Preserve customized files before updating and keep existing app/config and credentials. Recheck the helper's commands and release checks, and verify authenticated document access when a cloud archive is next requested.

If `npx @larksuite/cli@latest install` fails with an `ERR_REQUIRE_ESM` or dependency engine warning, check Node.js. The current installer may require Node.js `20.12.0` or newer.

On Windows Terminal / PowerShell, use the `.cmd` wrapper if `lark-cli.ps1` is blocked by execution policy:

```powershell
& "$env:APPDATA\npm\lark-cli.cmd" --version
```

Check existing CLI app/config before initializing (always through the passthrough so the managed store is used):

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli auth status
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli config show
```

The helper retains its existing configuration under `~/.codex/memories/runtime/lark-cli/config/`. On first use it may copy pre-existing config and Linux-style data directories into that runtime root. This is a compatibility behavior, not a purely read-only probe. Use its `--lark-cli` passthrough to keep app/profile selection consistent while troubleshooting:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli auth status
```

Configuration location is not necessarily credential location. In `lark-cli 1.0.87`, [Windows uses DPAPI-encrypted HKCU registry values](https://github.com/larksuite/cli/blob/v1.0.87/internal/keychain/keychain_windows.go); [macOS uses Keychain and Linux encrypted files](https://github.com/larksuite/cli/blob/v1.0.87/internal/keychain/keychain.go). The old claim that native and managed Windows commands necessarily rotate two separate file-token copies was incorrect. Verify the actual account and backend before attributing failure to split stores.

`--doctor` compares config content, not modification times of unrelated caches/logs. A difference is a prompt to inspect app/user/profile selection, not an instruction to log in again. Overrides remain available through `LARK_WORKLOG_LARK_RUNTIME_ROOT`, `LARKSUITE_CLI_CONFIG_DIR`, and `LARKSUITE_CLI_DATA_DIR`. Do not silently migrate existing installations or copy encrypted credentials across machines.

## Authorization troubleshooting

Start with `--lark-cli auth status --json` to inspect local metadata; redact identifiers and never print token values. Use `auth status --json --verify` only when a network verification is relevant. It may refresh credentials as part of CLI operation; neither a local status check nor a successful browser page alone proves document access.

| Evidence | Interpretation and next action |
| --- | --- |
| `tokenStatus: needs_refresh` | The access token needs renewal but the stored refresh deadline has not passed. The CLI can attempt refresh on a user API call; do not immediately request browser login. |
| `tokenStatus: expired`, past `refreshExpiresAt` | The refresh window has ended. Browser authorization is needed; reinstalling or copying files cannot extend it. |
| `no_token` or keychain access failure | Check selected app/user/config and OS-store access, including an approved outside-sandbox comparison, before concluding credentials are lost. |
| Timeout, DNS, proxy, TLS, or connection failure | Repair connectivity and retry the same identity. Do not reset authorization. |
| Missing scope or resource access | Distinguish incremental user consent, bot app permissions, and a specific document ACL. Do not switch to bot to bypass an error. |
| Verification explicitly failed | Keep the failure visible even if local metadata says `ready` or `available`. Preserve the original error; do not guess that login will fix it. |

These expiry states and automatic-renewal behavior are defined in the CLI's [token status implementation](https://github.com/larksuite/cli/blob/v1.0.87/internal/auth/token_store.go) and [auth status command](https://github.com/larksuite/cli/blob/v1.0.87/cmd/auth/status.go). Use the returned timestamps rather than assuming a universal permanent login or fixed lifetime.

### Occasional cloud archiving

Keep frequently updated work in project docs; authenticate only when the user requests a cloud archive. Long inactivity can outlast the refresh window and require consent again. Do not add a background keepalive, change account identity, or broaden scopes merely to hide this tradeoff. A future always-on or bot-based workflow needs its own permission and maintenance decision. This helper's user-owned registry and document access cannot be made bot-compatible merely by appending `--as bot`.

## Initial authorization and recovery

Only initialize a new CLI app/config when no existing config is present. Reinstalling this skill should not create a new Feishu app. If the user already has a Feishu CLI app, tell them to choose or reuse it instead of creating a parallel app.

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli config init --new
```

When initial consent or confirmed expiry/revocation requires it, start user authorization (same command on Linux, macOS, and Windows PowerShell). This grants a renewable but not permanent session:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli auth login \
  --recommend \
  --domain docs,drive,markdown \
  --scope "search:docs:read" \
  --no-wait \
  --json
```

Generate and display a QR code from the returned `verification_url`, then stop and let the user finish browser authorization. After the user confirms, complete the same device flow yourself and verify the live token before writing anything:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli auth qrcode \
  "<verification_url>" \
  --output "lark-auth.png"
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli auth login \
  --device-code "<device_code>"
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli auth status \
  --json \
  --verify
```

Remove the task-created QR image after authorization. Then run doctor before writing anything:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --doctor
```

For reinstall/recovery when the user already has a worklog, register the existing current-month document only. This must not create a new monthly document:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --init --existing-only
```

If search cannot find the old document but the user provides a known document URL/token, register it explicitly:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --init --existing-only --doc "<existing-doc-url-or-token>"
```

Only for first setup with no existing worklog, and only after the user confirms creating a new monthly document:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --init
```

Then run doctor again:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --doctor
```

Windows PowerShell uses the same Python entry point:

```powershell
python skills/lark-worklog-archive/scripts/archive_worklog.py --doctor
python skills/lark-worklog-archive/scripts/archive_worklog.py --init --existing-only
```

## Daily Use

Refer to the Workflow section in [SKILL.md](../SKILL.md) for the daily archive workflow. The user triggers archiving by saying "今日归档", "记录今天工作", or similar.

Daily writing style is defined in [worklog-writing-guide.md](worklog-writing-guide.md). Existing old-style daily sections should be rewritten according to that guide when touched.

If the work produced a document, issue, PR, or commit that should be easy to open later, include a Markdown link in the item:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py \
  --item "工作记录 / 知识管理::结果::编写 [使用说明](https://example.com/docx/xxx)，用于团队查看。"
```

Real Feishu/Lark document links are allowed only in runtime worklog items or local private config. Do not commit them to Git.

## Team Worklog

Team mode must be explicit:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py \
  --init \
  --team \
  --team-id "<team-name>" \
  --title-prefix "<team-title>"
```

Team writes must include an author:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py \
  --team \
  --author "Alice" \
  --item "工作记录 / 知识管理::工作内容::完善授权向导。"
```

Team items under `工作内容` are stored as `作者：事项`.

## Repair And Checks

Refer to the Checks section in [SKILL.md](../SKILL.md) for `--doctor` and release check commands.

Preview parsed structure:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py \
  --structure-only \
  --item "ROS / SLAM::结果::验证 Humble launch smoke。"
```

Repair one day:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py \
  --normalize-only \
  --date 05-20-2026
```

Repair the current month:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py \
  --normalize-only \
  --all-dates
```

## Updating Documentation Safely

When Codex updates a Feishu document with long Markdown on Windows, prefer a relative `@file` path from the current workspace instead of passing a long multi-line string directly through PowerShell. Remove the temporary file after the update.

For title-sensitive documentation updates, prefer XML content with an explicit `<title>...</title>` block, or fetch immediately afterward and verify `data.document.content` contains the intended title tag. Do not rely on a visible `# Heading` in the body as proof that the Feishu document title was updated.

Avoid mixing raw Lark XML blocks with Markdown unless the target document has already been tested with that format. If the CLI reports `partial_success` or tokenization warnings, fetch the document immediately and verify the expected sections are still present.

## Notes

- The monthly title is `MM-YYYY 工作记录`.
- Daily headings use `MM-DD-YYYY`.
- Use the helper instead of manual `docs +update overwrite`.
- The helper uses local month locks, latest revision fetch, revision-id writes, retries, dedupe, and post-write verification.
- Same-day writes first try a guarded section replace. Full-document fallback proceeds automatically only when fetched XML contains supported title/date/list/link blocks.
- Images, tables, embeds, attachments, and other unsupported blocks stop automatic archive before overwrite. Use `--force-overwrite` only after reviewing and accepting removal of those blocks.
- Structural repair and all-dates repair are explicit full-document rewrite operations.
- Normal archive output is intentionally short to reduce token use.
- Avoid `--dry-run`, manual full `docs +fetch`, or `--print-doc` unless debugging.
- Keep `monthly-docs.local.json`, OpenID values, tokens, app IDs, secrets, and real document URLs out of Git.
