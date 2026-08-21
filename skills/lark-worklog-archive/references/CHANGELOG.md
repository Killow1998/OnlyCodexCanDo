# Lark Worklog Archive Changelog

## 2026-08-15

### lark-cli 1.0.87 compatibility

- Updated the validated compatibility baseline to `lark-cli 1.0.87` after a live managed-store device authorization, verified user/token status, and `--doctor` check on Windows.
- Changed auth inspection to `auth status --json --verify` so doctor verifies the live token instead of accepting local credential metadata alone.
- Bypassed the npm `lark-cli.cmd` shim internally when its Node entrypoint is available; the shim split QR authorization URLs at `&`, producing a truncated QR argument even though the CLI process appeared to run.
- Documented the non-blocking device flow, QR display, follow-up completion, and temporary QR cleanup sequence.
- Restored Python 3.8 runtime compatibility: use `backports.zoneinfo` when available and retain dependency-free `Asia/Shanghai` / `UTC` date handling when neither timezone module exists; release tests also avoid Python 3.10-only parenthesized context managers.

## 2026-07-07

### Single persistent lark-cli credential store

- The helper now always points `lark-cli` at the managed store `~/.codex/memories/runtime/lark-cli/`, inside and outside Codex, instead of only when `CODEX_THREAD_ID` is set. Diverging legacy/managed stores rotated Feishu refresh tokens independently and kept invalidating each other, which looked like auth randomly dropping.
- Added the `--lark-cli` passthrough so `auth login`, `auth status`, and `config` commands run inside the managed environment; setup docs now route all raw CLI calls through it.
- `--doctor` warns when the legacy store (`~/.lark-cli`, `~/.local/share/lark-cli`) is newer than the managed store.

### SKILL.md failure path and check.py bytecode fix

- Documented the daily-archive failure path in `SKILL.md`: archive with `--queue-failed`, run `--doctor` on failure, and rely on same-date automatic replay of queued items.
- Documented `--date` backfill, team-mode pointer, and the installed-copy path convention in `SKILL.md`.
- Fixed `check.py` writing `__pycache__` into the skill during its own subprocess runs, which made the next `cache directory scan` fail; subprocesses now run with `PYTHONDONTWRITEBYTECODE=1` and `-B`.

## 2026-06-11

### lark-cli 1.0.51 auth status handling

- Matched `--doctor` authorization parsing to `lark-cli 1.0.51`.
- Treated `identity: none`, unavailable user identities, and `tokenStatus: no_token` as failed authorization in `--doctor`.
- Reject unavailable user identities even if an `openId` or stale `ready` status is still present in the auth payload.
- Removed compatibility with older `auth status` output shapes; update `lark-cli` instead of carrying fallback parsing.

## 2026-05-26

### Agent-led worklog shaping

- Removed helper-side keyword classification and local category rule loading from the release package.
- Kept the helper focused on structural parsing, locking, revision-safe writes, dedupe, repair, and verification.
- Added `--structure-only` for parsing previews; the old `--classify-only` flag remains as a hidden compatibility alias.
- Clarified that agents should decide work domains and item merging before calling the helper.

## 2026-05-20

### Breaking: summary-style worklog structure

- Changed the default daily structure from old log-like sections such as `工作内容`, `代码与仓库`, `开发环境`, `验证与测试`, and `问题与风险` to `背景与目标`, `工作内容`, `结果`, and `问题与下一步`.
- Added [worklog-writing-guide.md](worklog-writing-guide.md) so Agent writes for weekly reports, retrospectives, and context recovery instead of command-by-command logging.
- Old section names are migration inputs only: `代码与仓库` and `验证与测试` move to `结果`, `开发环境` moves to `工作内容`, and `问题与风险` moves to `问题与下一步`.
- If anyone uses an older version, update the skill as soon as possible and ask Agent to rewrite existing daily or weekly entries according to the new guide instead of appending more old-format fragments.

### Cross-platform and Windows hardening

- Added POSIX/Windows file locking support with `fcntl` / `msvcrt` and system temp lock files.
- Preferred `lark-cli.cmd` / `lark-cli.exe` on Windows to avoid PowerShell `lark-cli.ps1` policy failures.
- Replaced hardcoded `python3` release checks with `sys.executable` and UTF-8 subprocess environments.
- Added timezone fallback for Windows environments without IANA tzdata.
- Supported UTF-8 BOM in registries, caches, and failed queues.
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
- Added team worklog mode with explicit `--team` and author attribution.
- Added compact default output, `--print-doc` for explicit document locator output, and local lookup cache.
- Added setup documentation for Windows PowerShell, lark-cli auth, reinstall, repair, team use, and troubleshooting.

### Quality and release checks

- Added unit tests with a fake lark-cli runner.
- Added release `check.py` for unit tests, syntax checks, sensitive scans, cache scans, install dry-run, skill validation, and global skill consistency.
- Added sensitive value redaction for document URLs, OpenID values, app IDs, tokens, secrets, and bearer tokens.
- Added `.gitignore` coverage for private registries, Python caches, and lark worklog temp files.

### Sharing

- Created a shareable Feishu usage document for the skill.
- Added Markdown link rendering for worklog entries that reference docs, commits, issues, or PRs.
