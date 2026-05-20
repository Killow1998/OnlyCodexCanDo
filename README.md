# OnlyCodexCanDo

English | [中文](README.zh-CN.md)

Public repository for reusable Codex skills.

This repo is not a memory store and is not tied to one single workflow. It should contain only skill source files, public examples, scripts, and documentation. Private runtime data such as Feishu/Lark document URLs, OpenID values, app IDs, tokens, secrets, and local registries must stay out of Git.

## Skills

### `lark-worklog-archive`

Archives daily Codex/Agent work into a monthly Feishu/Lark worklog document.

It is designed for prompts such as:

- "Archive today's work."
- "Record today's work."
- "Sync this work to the Feishu worklog."

Main behavior:

- one Feishu/Lark worklog document per month;
- one heading per day, using `MM-DD-YYYY`;
- work items grouped by domain and subcategory;
- safe same-day appends through the helper script instead of direct document overwrite;
- optional Markdown links in worklog items for related docs or commits;
- private document mappings kept in local ignored config.

## Install A Skill

For `lark-worklog-archive`, users should ask Codex to install and configure it instead of running every command manually:

```text
Please install and configure the lark-worklog-archive Skill so Codex/Agent can archive my daily development work into a Feishu/Lark worklog. Use the public repository https://github.com/Killow1998/OnlyCodexCanDo.git over HTTPS; install or check lark-cli; start one-time Feishu/Lark user authorization with docs, drive, markdown, and search:docs:read permissions; I will only confirm authorization in the browser. After authorization, initialize the current monthly worklog document, run doctor checks, and tell me that I can use "archive today's work" later. Do not commit any Feishu/Lark document URL, OpenID, app ID, token, secret, or registry value to Git.
```

Detailed agent-facing setup notes are in [skills/lark-worklog-archive/references/setup.md](skills/lark-worklog-archive/references/setup.md).

## Repository Rules

- Keep this repository focused on reusable skills, not project memories or chat history.
- Use HTTPS clone instructions for public users.
- Keep real user configuration in ignored local files or user config directories.
- Do not commit secrets, tokens, Feishu/Lark document URLs, OpenID values, app IDs, private API endpoints, or real registry values.

Development notes for `lark-worklog-archive` are tracked in [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md).
