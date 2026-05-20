# Lark Worklog Archive Changelog

## 2026-05-20

### Cross-platform and Windows hardening

- Added POSIX/Windows file locking support with `fcntl` / `msvcrt` and system temp lock files.
- Preferred `lark-cli.cmd` / `lark-cli.exe` on Windows to avoid PowerShell `lark-cli.ps1` policy failures.
- Replaced hardcoded `python3` release checks with `sys.executable` and UTF-8 subprocess environments.
- Added timezone fallback for Windows environments without IANA tzdata.
- Supported UTF-8 BOM in category rules, registries, caches, and failed queues.
- Fixed bare filename paths for registry, cache, and failed queue files.
- Prevented Windows drive paths such as `C:\...` from being treated as team author signatures.

### Feishu/Lark document safety

- Added existing-document search fallback and `--existing-only` reinstall protection.
- Added long `--content` handling through ignored relative `@file` temp files.
- Added guarded same-day section replace with fallback full rewrite.
- Avoided risky Markdown section replace for Windows paths, Markdown emphasis markers, and long section patterns.
- Verified repair writes after `--normalize-only --date` and `--normalize-only --all-dates`.
- Improved post-write verification for explicit category prefixes, Windows backslashes, and Markdown escaping.
- Added repair notes for excessive escaping and old category structures.

### User-facing workflow

- Added install, doctor, init, preview, normalize-only, cache, failed queue, and team registry flows.
- Added configurable category rules with a public template and local override paths.
- Added team worklog mode with explicit `--team` and author attribution.
- Added compact default output, `--print-doc` for explicit document locator output, and local lookup cache.
- Added setup documentation for Windows PowerShell, lark-cli auth, reinstall, repair, team use, and troubleshooting.

### Quality and release checks

- Added unit tests with a fake lark-cli runner.
- Added release `check.py` for unit tests, syntax checks, sensitive scans, cache scans, install dry-run, skill validation, and global skill consistency.
- Added sensitive value redaction for document URLs, OpenID values, app IDs, tokens, secrets, and bearer tokens.
- Added `.gitignore` coverage for private registries, category overrides, Python caches, and lark worklog temp files.

### Sharing

- Created a shareable Feishu usage document for the skill.
- Added Markdown link rendering for worklog entries that reference docs, commits, issues, or PRs.
