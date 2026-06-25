# Agent Instructions

## Worklog Archiving

- Treat `skills/lark-worklog-archive/references/worklog-writing-guide.md` as the canonical worklog style guide.
- After each meaningful project phase is completed, archive the worklog before context is likely to be compacted or lost. Do not wait until the user asks at the end of a long session.
- Use `skills/lark-worklog-archive/scripts/archive_worklog.py` for Feishu/Lark worklog writes, and run `--preview` first for non-trivial entries.
- Keep the record as project progress, not a command log. Group by objective and explain why the work mattered.
- Default second-level sections are:
  - `背景与目标`
  - `工作内容`
  - `结果`
  - `问题与下一步`
- Choose first-level domains from the actual work context, such as `Go2-W / TGW 路径规划`, `Go2-W / N3Mapping 定位`, `Agent 工具 / 自动化`, or `开发环境 / 系统配置`.
- Commands, file paths, commits, tests, and links are evidence inside the four sections, not the main structure.
- Preserve exact dates. Do not attribute work to a day unless the source worklog, conversation, or command evidence supports that date.
- If the user says not to write Feishu yet, prepare the `.archive_items_YYYY-MM-DD.txt` draft locally and wait for approval before writing.
- After a successful Feishu write and verification, move only local uploaded worklog source files into `worklog/uploaded_to_feishu/YYYY-MM/`; do not move or delete remote Go2-W source drafts.
