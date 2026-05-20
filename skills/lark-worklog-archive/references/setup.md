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

If `npx @larksuite/cli@latest install` fails with an `ERR_REQUIRE_ESM` or dependency engine warning, check Node.js. The current installer may require Node.js `20.12.0` or newer.

On Windows Terminal / PowerShell, use the `.cmd` wrapper if `lark-cli.ps1` is blocked by execution policy:

```powershell
& "$env:APPDATA\npm\lark-cli.cmd" --version
```

Check existing CLI app/config before initializing:

```bash
lark-cli auth status
lark-cli config show
```

```powershell
& "$env:APPDATA\npm\lark-cli.cmd" auth status
& "$env:APPDATA\npm\lark-cli.cmd" config show
```

Only initialize a new CLI app/config when no existing config is present. Reinstalling this skill should not create a new Feishu app. If the user already has a Feishu CLI app, tell them to choose or reuse it instead of creating a parallel app.

```bash
lark-cli config init --new
```

Start one-time user authorization:

```bash
LARK_CLI_NO_PROXY=1 lark-cli auth login \
  --recommend \
  --domain docs,drive,markdown \
  --scope "search:docs:read"
```

Windows PowerShell:

```powershell
$env:LARK_CLI_NO_PROXY='1'
& "$env:APPDATA\npm\lark-cli.cmd" auth login `
  --recommend `
  --domain docs,drive,markdown `
  --scope "search:docs:read"
```

After the user finishes browser authorization, run doctor before writing anything:

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
  --item "飞书 CLI / 工作记录::结果::编写 [使用说明](https://example.com/docx/xxx)，用于团队查看。"
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
  --item "飞书 CLI / 工作记录::工作内容::完善授权向导。"
```

Team items under `工作内容` are stored as `作者：事项`.

## Repair And Checks

Refer to the Checks section in [SKILL.md](../SKILL.md) for `--doctor` and release check commands.

Preview classification:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py \
  --classify-only \
  --item "验证 n3mapping Humble launch smoke。"
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
- Same-day writes first try a guarded same-day section replace, then fall back to full-document rewrite if replace or verification fails.
- Structural repair, abnormal documents, `--force-overwrite`, and all-dates repair may use full-document rewrite.
- Normal archive output is intentionally short to reduce token use.
- Avoid `--dry-run`, manual full `docs +fetch`, or `--print-doc` unless debugging.
- Keep `monthly-docs.local.json`, category overrides, OpenID values, tokens, app IDs, secrets, and real document URLs out of Git.
