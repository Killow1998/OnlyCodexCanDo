# lark-worklog-archive Setup

This file is for Codex/Agent. Normal users should not need to run these commands manually.

## User-Facing Install Prompt

Give this prompt to Codex when installing the skill on a new machine:

```text
请帮我安装并配置 lark-worklog-archive Skill，用于把每天通过 Codex/Agent 完成的开发工作归档到飞书工作记录。请使用公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 通过 HTTPS 安装；安装或检查 lark-cli；如果已有 lark-cli app/config 就复用，不要重新创建飞书 app；否则发起一次性飞书用户授权，权限需要覆盖 docs、drive、markdown 和 search:docs:read；我只在网页上完成授权确认。授权后先运行 doctor 检查，优先搜索/注册已有的当前月工作记录文档；只有找不到已有文档且我明确同意时，才创建新的月度文档。最后告诉我以后可以直接说“今日归档”。不要把任何飞书文档 URL、OpenID、App ID、token、secret 或 registry 提交到 Git。
```

Codex should perform the setup and only ask the user to confirm the Feishu/Lark authorization in the browser.

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

Validated compatibility baseline: `lark-cli 1.0.87` on Windows. The helper expects its `auth status --json --verify` identity/token shape and bypasses the npm `.cmd` shim internally so URL arguments containing `&` remain intact. Update older installations with `lark-cli update` before debugging authorization; re-run live auth verification, doctor, and the skill release checks before recording a newer CLI version.

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

The helper always points `lark-cli` at one persistent managed credential store: `~/.codex/memories/runtime/lark-cli/` (config under `config/`, encrypted credentials under `data/lark-cli/`), both inside and outside Codex. On first use it migrates existing legacy state from `~/.lark-cli` and `~/.local/share/lark-cli`. Do not run bare `lark-cli auth login` afterwards: that writes credentials to the legacy location, the two stores then rotate refresh tokens independently and invalidate each other, and auth appears to "randomly drop". Run every `lark-cli` command through the helper's `--lark-cli` passthrough instead, which injects the managed environment:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli auth status
```

`--doctor` warns when the legacy store is newer than the managed store (the usual sign that a bare `lark-cli auth login` happened). Override the store location with `LARK_WORKLOG_LARK_RUNTIME_ROOT`, `LARKSUITE_CLI_CONFIG_DIR`, or `LARKSUITE_CLI_DATA_DIR` only when you need a different persistent location.

Only initialize a new CLI app/config when no existing config is present. Reinstalling this skill should not create a new Feishu app. If the user already has a Feishu CLI app, tell them to choose or reuse it instead of creating a parallel app.

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --lark-cli config init --new
```

Start one-time user authorization (same command on Linux, macOS, and Windows PowerShell):

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
