# OnlyCodexCanDo

Public Codex skills repository.

This repository stores reusable skills only. It is not a memory store and should not contain project history, chat summaries, credentials, Feishu document URLs, API endpoints, OpenID values, app IDs, tokens, or other private runtime configuration.

## Install

Clone with HTTPS:

```bash
git clone https://github.com/Killow1998/OnlyCodexCanDo.git
```

Then install a skill from this repository with your Codex skills installer, or copy the target folder under `skills/` into your local Codex skills directory.

Maintainers who have write access may use SSH for pushing, but public users should use HTTPS for installation.

## Skills

### `lark-worklog-archive`

Archive "今日归档" style daily Codex/Agent work into a monthly Feishu/Lark worklog document.

Main behavior:

- one Feishu/Lark document per month, titled `MM-YYYY 工作记录`;
- each day is an H1 heading using `MM-DD-YYYY`;
- newest days are kept above older days;
- same-day items are grouped as nested unordered lists: first-level bullets are work domains, with subcategories and concrete work nested below;
- normal use goes through the helper script so multiple conversations append safely and duplicate bullets are avoided;
- private Feishu document mappings stay in a local ignored registry, not in Git.

Setup and authorization details are in [skills/lark-worklog-archive/references/setup.md](skills/lark-worklog-archive/references/setup.md).

## Repository Rules

- Keep only skill source, scripts, examples, and public setup references here.
- Do not commit local registries such as `monthly-docs.local.json`.
- Do not commit secrets, access tokens, Feishu document URLs, OpenID values, app IDs, or private API endpoints.
- If a skill needs user-specific values, store examples in Git and keep real values in ignored local files or user config paths.
