# lark-worklog-archive Setup

This file is for Codex/Agent. Normal users should not need to run these commands manually.

## User-Facing Install Prompt

Give this prompt to Codex when installing the skill on a new machine:

```text
请帮我安装并配置 lark-worklog-archive Skill，用于把每天通过 Codex/Agent 完成的开发工作归档到飞书工作记录。请使用公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 通过 HTTPS 安装；安装或检查 lark-cli；发起一次性飞书用户授权，权限需要覆盖 docs、drive、markdown 和 search:docs:read；我只在网页上完成授权确认。授权后请初始化当前月工作记录文档，运行 doctor 检查，并告诉我以后可以直接说“今日归档”。不要把任何飞书文档 URL、OpenID、App ID、token、secret 或 registry 提交到 Git。
```

Codex should perform the setup and only ask the user to confirm the Feishu/Lark authorization in the browser.

## What Codex Should Do

Install the repo and local skill:

```bash
git clone https://github.com/Killow1998/OnlyCodexCanDo.git
cd OnlyCodexCanDo
python3 skills/lark-worklog-archive/scripts/install.py
```

Install or check `lark-cli`:

```bash
npx @larksuite/cli@latest install
lark-cli --version
```

Initialize `lark-cli` app config only if missing:

```bash
lark-cli config init --new
```

Start one-time user authorization:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth login \
  --recommend \
  --domain docs,drive,markdown \
  --scope "search:docs:read"
```

After the user finishes browser authorization:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --init
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --doctor
```

## Daily Use

The user should be able to say:

- 今日归档
- 记录今天工作
- sync this work to the Feishu worklog

Codex should summarize verified work only, preview non-trivial classification, then write through the helper:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --preview \
  --item "飞书 CLI / 工作记录::工作内容::完成 X，并通过 Y 验证。"

python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --item "飞书 CLI / 工作记录::工作内容::完成 X，并通过 Y 验证。" \
  --item "飞书 CLI / 工作记录::验证与测试::运行 Z 测试通过。"
```

If the work produced a document, issue, PR, or commit that should be easy to open later, include a Markdown link in the item:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --item "飞书 CLI / 工作记录::工作内容::编写 [使用说明](https://example.com/docx/xxx)，用于团队查看。"
```

Real Feishu/Lark document links are allowed only in runtime worklog items or local private config. Do not commit them to Git.

## Team Worklog

Team mode must be explicit:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --init \
  --team \
  --team-id "<team-name>" \
  --title-prefix "<team-title>"
```

Team writes must include an author:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --team \
  --author "Alice" \
  --item "飞书 CLI / 工作记录::工作内容::完善授权向导。"
```

Items under `工作内容` are stored as `作者：事项`.

## Repair And Checks

Preview classification:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --classify-only \
  --item "验证 n3mapping Humble launch smoke。"
```

Repair one day:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --normalize-only \
  --date 05-20-2026
```

Repair the current month:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --normalize-only \
  --all-dates
```

Run release checks:

```bash
python3 skills/lark-worklog-archive/scripts/check.py
```

## Notes

- The monthly title is `MM-YYYY 工作记录`.
- Daily headings use `MM-DD-YYYY`.
- Use the helper instead of manual `docs +update overwrite`.
- The helper uses local month locks, latest revision fetch, revision-id writes, retries, dedupe, and post-write verification.
- Normal archive output is intentionally short to reduce token use.
- Avoid `--dry-run`, manual full `docs +fetch`, or `--print-doc` unless debugging.
- Keep `monthly-docs.local.json`, category overrides, OpenID values, tokens, app IDs, secrets, and real document URLs out of Git.
