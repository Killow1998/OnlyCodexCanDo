---
name: lark-worklog-archive
description: Archive daily Codex or agent work into the user's Feishu/Lark worklog document. Use when the user says "今日归档", "今天归档", "记录今天工作", "同步到飞书工作记录", or asks Codex to summarize today's completed development work and update the Feishu worklog.
---

# Lark Worklog Archive

Archive verified daily Codex/Agent work into the user's monthly Feishu/Lark worklog.

Real Feishu document URLs, OpenID values, app IDs, tokens, secrets, and local registry values are runtime/private data only. Do not commit them to Git.

## Output Rules

- Keep one worklog document per month, titled `MM-YYYY 工作记录`.
- Date headings are H1s in `MM-DD-YYYY`, newest date first.
- Under each date, use unordered lists only; do not add prose, tables, or subheadings.
- First-level bullets are work domains, for example `飞书 CLI / 工作记录`, `Go2-W 实机开发`, `n3mapping`, or `其他`.
- Put `工作内容`, `代码与仓库`, `开发环境`, `验证与测试`, and `问题与风险` under the relevant work domain.
- Archive verified work only: changed files, commands run, documents updated, tests/builds, pushes, and remaining blockers.
- Keep bullets concrete and short. State uncertainty or unverified work explicitly.
- Append same-day additions after existing sibling items in natural execution order.
- Include Markdown links for shareable docs, commits, issues, or PRs when useful.
- Use Asia/Shanghai date by default unless the user requests another date.

## Workflow

1. Collect actual work from the conversation, tool outputs, git diff, command history, or user summary. Do not invent work.
2. Preview classification for non-trivial entries:

   ```bash
   python skills/lark-worklog-archive/scripts/archive_worklog.py \
     --preview \
     --item "飞书 CLI / 工作记录::验证与测试::运行 check.py 通过。"
   ```

3. Archive through the helper:

   ```bash
   python skills/lark-worklog-archive/scripts/archive_worklog.py \
     --item "飞书 CLI / 工作记录::工作内容::完成 X。" \
     --item "飞书 CLI / 工作记录::验证与测试::运行 Y 通过。"
   ```

The helper uses a per-month lock, latest Feishu revision, retry, dedupe, and post-write verification. Same-day writes first try guarded section replace, then fall back to full-document rewrite if replace or verification fails.

## Checks

Run doctor when setup, auth, registry, or document access may be stale:

```bash
python skills/lark-worklog-archive/scripts/archive_worklog.py --doctor
```

Run release checks before sharing changes:

```bash
python skills/lark-worklog-archive/scripts/check.py
```

## References

- Setup, install, auth, reinstall, repair, team mode, and troubleshooting: [references/setup.md](references/setup.md)
- Category rule template: [references/category-rules.example.json](references/category-rules.example.json)
- Completed changes: [references/CHANGELOG.md](references/CHANGELOG.md)
- Future plans: [references/todo.md](references/todo.md)
