# Agent Instructions

This is a public repository of reusable agent skills. Keep it free of private runtime data and project-specific workflow rules.

## Repository Rules

- Never commit secrets, tokens, SMTP passwords, Feishu/Lark document URLs, OpenID values, app IDs, or local registry values.
- After changing a skill, run its release checks: `python -B skills/<skill>/scripts/check.py`.
- After changing a skill, sync the installed global copy under `~/.codex/skills/<skill>` so `check.py` global consistency passes.
- When changing installer flags, email templates, or hook trigger logic, extend the skill's tests in the same change.

## Worklog Archiving

- Treat `skills/lark-worklog-archive/references/worklog-writing-guide.md` as the canonical worklog style guide.
- After each meaningful project phase is completed, archive the worklog before context is likely to be compacted or lost. Do not wait until the user asks at the end of a long session.
- Use `skills/lark-worklog-archive/scripts/archive_worklog.py` for Feishu/Lark worklog writes, and run `--preview` first for non-trivial entries.
- Keep the record as project progress, not a command log. Group by objective and explain why the work mattered.
- Choose first-level domains from the actual work context; the four default second-level sections are `背景与目标`, `工作内容`, `结果`, and `问题与下一步`.
- Preserve exact dates. Do not attribute work to a day unless the source worklog, conversation, or command evidence supports that date.
