# Feishu/Lark CLI Setup

Use this file only when installing the skill, authorizing `lark-cli`, repairing setup, or explaining the workflow to another user.

## First Install

```bash
git clone https://github.com/Killow1998/OnlyCodexCanDo.git
cd OnlyCodexCanDo
python3 skills/lark-worklog-archive/scripts/install.py
npx @larksuite/cli@latest install
lark-cli --version
```

If this is the first `lark-cli` setup on the machine:

```bash
lark-cli config init --new
```

Open the printed URL or scan the QR code, then finish the Feishu Open Platform app setup in the browser.

## User Authorization

Interactive login:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth login \
  --recommend \
  --domain docs,drive,markdown \
  --scope "search:docs:read"
```

Agent-friendly device flow:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth login \
  --recommend \
  --domain docs,drive,markdown \
  --scope "search:docs:read" \
  --no-wait \
  --json
```

Send `verification_url` to the user. After authorization:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth login --device-code '<device_code>'
```

Check and initialize:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth status
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --init
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --doctor
```

## Daily Use

Archive items:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --item "完成 X，并通过 Y 验证。"
```

If the work produced a shareable Feishu document or public doc, include it as a Markdown link in the bullet:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --item "飞书 CLI / 工作记录::工作内容::编写 [使用说明](https://example.com/docx/xxx)，用于团队查看。"
```

Use real Feishu document links only in runtime archive items or local private config. Do not commit real Feishu URLs to Git.

Preview without writing:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --preview \
  --item "验证 n3mapping Humble launch smoke。"
```

Repair one day:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --normalize-only \
  --date 05-20-2026
```

Repair every day in the current month:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --normalize-only \
  --all-dates
```

## Format Rules

- Monthly title: `MM-YYYY 工作记录`.
- Daily heading: `# MM-DD-YYYY`.
- Newer dates stay above older dates.
- Under each date, use unordered lists only.
- First-level bullets are work domains; nested bullets are categories and concrete work.
- Real registries stay local: `references/monthly-docs.local.json` or `$HOME/.config/lark-worklog-archive/monthly-docs.json`.

## Multi-Conversation Safety

Use the helper instead of manual overwrite. It:

- locks locally per month;
- fetches the latest revision before writing;
- uses `--revision-id` and retries conflicts;
- replaces only the same-day section when possible;
- inserts new dates after the title when possible;
- verifies submitted bullets after writing;
- deduplicates reruns.

Cross-PC races can still happen. If a conflict remains after retries, rerun the same archive command or use `--queue-failed`.

## Cache And Failed Queue

Cache path:

```text
$HOME/.cache/lark-worklog-archive/cache.json
```

The cache only avoids repeated exact-title search. Every write still fetches the latest revision. Disable it with `--no-cache`.

Failed queue path:

```text
$HOME/.local/state/lark-worklog-archive/failed-queue.jsonl
```

Use `--queue-failed` to save failed items locally. Later archive runs replay queued items for the same date and remove them after success. Use `--no-replay-failed` to skip replay once.

## Category Rules

Public template:

```text
skills/lark-worklog-archive/references/category-rules.example.json
```

Private override paths:

```text
skills/lark-worklog-archive/references/category-rules.local.json
$HOME/.config/lark-worklog-archive/category-rules.json
```

Classification-only check:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --classify-only \
  --item "验证 n3mapping Humble launch smoke。"
```

## Sharing

Each person should use their own registry by default:

```bash
export LARK_WORKLOG_REGISTRY="$HOME/.config/lark-worklog-archive/monthly-docs.json"
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --init
```

Dedicated team registry:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --init \
  --team \
  --team-id "<team-name>" \
  --title-prefix "<team-title>"
```

Team registry writes and repairs require `--team` on every command. Archive writes also require `--author "<display-name>"` or `LARK_WORKLOG_AUTHOR`, so `工作内容` entries are written as `作者：事项`. Optional `--allow-user-open-id` values stay local and must not be committed.

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --team \
  --author "Alice" \
  --item "飞书 CLI / 工作记录::工作内容::完善授权向导。"
```

## Token Budget

- Normal archive: lowest output; prints title, date, count.
- `--preview`: low output; no Feishu write.
- `--doctor`: low output; checks readiness and prints short fixes.
- `--dry-run`: high output; prints generated Markdown.
- Manual `docs +fetch`: high output; only use for auditing or debugging.
- `--print-doc`: may expose a document locator in the conversation; avoid unless needed.

## Release Check

```bash
python3 skills/lark-worklog-archive/scripts/check.py
```

This runs tests, syntax checks, sensitive-value scanning, install dry-run, Skill validation when available, and global installed-copy comparison.

## Troubleshooting

- `lark-cli` missing: run `npx @larksuite/cli@latest install`.
- Auth expired or missing: rerun the user authorization command.
- Permission denied: add the missing Feishu scopes and reauthorize.
- Registry owner mismatch: use a personal registry path or intentionally pass `--allow-foreign-registry`.
- Team registry write blocked: pass `--team`.
- Wrong date: pass `--date YYYY-MM-DD` or `--date MM-DD-YYYY`.
- Proxy warning: use `LARK_CLI_NO_PROXY=1` unless a proxy is required.
