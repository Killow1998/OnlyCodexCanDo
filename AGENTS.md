# Agent Instructions

This is a public repository of reusable agent skills and workflow guidance. Keep it free of private runtime data and project-specific workflow rules.

## Repository Rules

- Never commit secrets, tokens, SMTP passwords, Feishu/Lark document URLs, OpenID values, app IDs, or local registry values.
- After changing a skill, run its release checks: `python -B skills/<skill>/scripts/check.py`.
- Treat skill source changes and host deployment separately. Sync only explicitly authorized installations; use a checker's `--skip-global` option for source-only validation when available, and report deployment drift rather than overwriting installed copies to make a check pass.
- When changing installer flags, email templates, or hook trigger logic, extend the skill's tests in the same change.

## Workflow Documentation

- Before changing shared agent workflow guidance, read `docs/agent-workflow.md` and keep `docs/agent-workflow.zh-CN.md` semantically aligned.
- Before changing host-global deployment guidance, read `docs/global-agents.md`; before changing workspace continuity guidance, read `docs/workspace-continuous-documentation.md`. Keep each English document aligned with its `.zh-CN.md` counterpart.
- Keep `templates/AGENTS.global.md` platform-neutral. Put operating-system-specific rules in `templates/platform/` and load them only after the target environment is verified.
- Keep `templates/AGENTS.global.md` limited to broadly applicable behavior. Put language, tool, host, Git-policy, data-policy, and personal workflow preferences in `templates/optional/`; deployment guidance must explain relevant choices and obtain user confirmation instead of silently merging every module.
- Keep host-global setup and workspace setup independently deployable. Broadly applicable behavior belongs in the minimal core, selected host behavior in optional modules, and project workflows in `templates/workspace/` and the target repository.
- Keep experiment and domain modules independently selectable within `templates/workspace/`. Do not make continuous documentation, experiment discipline, or robotics validation imply one another.
- Keep stable cross-project policy in the workflow guide. Never copy chat transcripts, session indexes, host names, private paths, or machine-specific state into this public repository.
- Do not package a workflow as a Skill merely because it can be packaged. First confirm that its trigger and output are stable and that scripts, references, assets, or automated checks provide real value.

## Work Records

- Treat `skills/lark-worklog-archive/references/worklog-writing-guide.md` as the canonical worklog style guide.
- After a meaningful phase, preserve reusable conclusions and remaining work in the relevant project documentation. Keep private host and session evidence out of this public repository; small edits do not need a separate worklog.
- Feishu/Lark archiving is a separately selected integration, not a prerequisite for completing repository work. When that write is authorized, use `skills/lark-worklog-archive/scripts/archive_worklog.py` and run `--preview` first for non-trivial entries.
- Keep the record as project progress, not a command log. Group by objective and explain why the work mattered.
- Choose first-level domains from the actual work context; the four default second-level sections are `背景与目标`, `工作内容`, `结果`, and `问题与下一步`.
- Preserve exact dates. Do not attribute work to a day unless the source worklog, conversation, or command evidence supports that date.
