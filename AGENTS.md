# Agent Instructions

These instructions govern changes and releases in this public skills and workflow repository.

## Repository Rules

- Keep credentials, Feishu/Lark document URLs, identities, app IDs, local registry values, private host/session data, and project-specific policy out of published files.
- After changing a skill, run `python -B skills/<skill>/scripts/check.py` from source. After authorized deployment, add `--check-global` or `--global-skill <path>` to compare the installation; report drift instead of overwriting local edits to pass.
- For release-check CLI changes, run `ruff check`, `ruff format --check`, and `python -B tests/check_release_cli.py`; the CLI scenarios include each Skill's release checks.
- When changing installer flags, email templates, or hook trigger logic, extend the skill's tests in the same change.

## Workflow Documentation

- For shared workflow edits, read `docs/agent-workflow.md`; for global deployment, `docs/global-agents.md`; for project continuity, `docs/workspace-continuous-documentation.md`. Keep each English document aligned with its `.zh-CN.md` counterpart.
- Keep `templates/AGENTS.global.md` platform-neutral and broadly applicable. Put selected personal/tool/Git/data preferences in `templates/optional/` and domain references in `templates/workspace/`; deployment includes only user-selected options. OS procedures belong to the project that needs them.
- Create a Skill only for a stable, recurring workflow whose packaged instructions or resources justify its installation and upkeep.

## Work Records

- For an authorized Feishu/Lark archive, read `skills/lark-worklog-archive/SKILL.md`; follow its helper procedure and canonical `references/worklog-writing-guide.md`. Preserve dates supported by the evidence.
