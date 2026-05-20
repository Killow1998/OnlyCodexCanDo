---
name: lark-worklog-archive
description: Archive daily Codex or agent work into the user's Feishu/Lark worklog document. Use when the user says "今日归档", "今天归档", "记录今天工作", "同步到飞书工作记录", or asks Codex to summarize today's completed development work and update the Feishu worklog.
---

# Lark Worklog Archive

Use this skill to append a concise daily work archive into the user's monthly Feishu/Lark worklog document.

Current monthly registry:

```text
references/monthly-docs.local.json
```

## Output Rules

- Keep one Feishu document per month.
- Monthly document title template: `MM-YYYY 工作记录`, for example `05-2026 工作记录`.
- Date headings use US style: `MM-DD-YYYY`.
- Newer dates must appear before older dates.
- Each day is one H1 heading: `# MM-DD-YYYY`.
- Content under each date must be grouped as unordered lists. Multiple nesting levels are allowed.
- First-level bullets are work domains, such as `飞书 CLI / 工作记录`, `Ubuntu 环境`, `n3mapping`, `RL 环境`, and `其他`.
- Subcategories such as `工作内容`, `验证与测试`, `问题与风险`, `代码与仓库`, and `开发环境` belong under the relevant work domain; do not promote them to first-level bullets when the actual work is about a specific domain.
- Within each level, keep a natural execution order. Same-day additions should be appended after existing sibling items, not prepended ahead of earlier prerequisite work.
- Do not add subheadings, tables, or prose paragraphs under a date.
- Summarize verified work only: changed files, commands run, documents created, tests/builds, pushes, and remaining blockers.
- Keep each bullet concrete and short. Mention uncertainty or unverified work explicitly.
- Use the machine date in timezone `Asia/Shanghai` by default. Only pass `--date` when the user explicitly wants another archive date.

## Workflow

1. Collect today's actual work from the conversation, tool outputs, git diff, command history, or user-provided summary.
2. Convert it to bullet items. Do not invent work.
3. Confirm `lark-cli` is installed and authorized:

   ```bash
   command -v lark-cli
   env LARK_CLI_NO_PROXY=1 lark-cli auth status
   ```

4. Run the archive helper:

   ```bash
   python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
     --item "完成 X，并通过 Y 验证。" \
     --item "修改 Z，遗留问题是 W。"
   ```

   Or pass a prepared bullet list through stdin:

   ```bash
   printf '%s\n' \
     '- 完成 X。' \
     '- 通过 Y 验证。' |
   python3 skills/lark-worklog-archive/scripts/archive_worklog.py
   ```

   The helper handles concurrent local conversations with a per-month lock, uses Feishu revision IDs for optimistic retry, and verifies that the submitted bullets exist after the update. If today's date is already the active top section, it replaces only that day's section so category buckets stay coherent without rewriting unrelated dates.

5. Fetch the current monthly document after updating and verify the newest date is at the top:

   ```bash
   env LARK_CLI_NO_PROXY=1 lark-cli docs +fetch \
     --api-version v2 \
     --as user \
     --doc "<doc-url-printed-by-archive_worklog.py>" \
     --doc-format markdown
   ```

## Updating Behavior

The helper chooses a document from the local monthly registry by the archive month. If the month is unknown, it first tries to search Feishu for an existing exact monthly title, then creates a new monthly document named `MM-YYYY 工作记录` if no match is available. The previous month's document remains unchanged as the archive.

Inside a monthly document, the helper fetches the current Markdown, inserts `# MM-DD-YYYY` at the top when the date is new, or updates the existing same-date section. Items are normalized into domain buckets with nested subcategories, and older dated sections stay below the newer dates.

For multiple Codex conversations, always use the helper instead of hand-running `docs +update overwrite`. Direct overwrite can lose another conversation's new bullets.

Same-day additions replace only the matching day section when possible, so multiple conversations can add bullets to the same day without rewriting unrelated sections. New dates are inserted after the document title when the document structure allows it. Structural changes and fallback migrations still use a guarded full rewrite.

The helper is idempotent for repeated bullets: rerunning the same archive command should not duplicate identical list items.

If passing `--doc` manually, the helper will not save that override into the local monthly registry unless `--register-doc` is also passed. This avoids corrupting the registry with temporary test documents.

The registry is owned by one Feishu `userOpenId`. If a different person uses this skill, they must set their own registry path instead of reusing another user's local registry.

Use `--dry-run` before writing if the bullet list is long or the current document looks unusual.

Do not commit private registries, document addresses, OpenID values, app IDs, tokens, or API endpoints. The repository contains only `monthly-docs.example.json`; each user keeps real mappings in an ignored local registry or a private config path.

## Category Rules

Default domain and subcategory rules are built in. To customize them, copy `references/category-rules.example.json` to an ignored local path:

```bash
cp skills/lark-worklog-archive/references/category-rules.example.json \
  skills/lark-worklog-archive/references/category-rules.local.json
```

The helper also accepts `$HOME/.config/lark-worklog-archive/category-rules.json`, `LARK_WORKLOG_CATEGORY_RULES`, or `--category-rules <path>`.

Check classification without touching Feishu:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --classify-only \
  --item "验证 n3mapping Humble launch smoke。"
```

## Sharing With Friends

Friends can use the skill and the same script, but they must use their own local registry.

For another person, set a personal registry path:

```bash
export LARK_WORKLOG_REGISTRY="$HOME/.config/lark-worklog-archive/monthly-docs.json"
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --item "初始化我的工作记录。"
```

They still need their own `lark-cli` app config and user authorization. See [references/setup.md](references/setup.md).

## Token Use

Normal archive runs print only a short success message. The script parses `lark-cli` JSON internally and does not dump full document content unless `--dry-run` or explicit fetch commands are used. Prefer the helper over manual fetch/update commands for token efficiency.

## Setup On A New PC

Read [references/setup.md](references/setup.md) when `lark-cli` is missing, auth is invalid, or the user asks how to install/authorize Feishu CLI.
