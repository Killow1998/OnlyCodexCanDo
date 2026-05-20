# Feishu/Lark CLI Setup

Use the official `lark-cli`.

## Install

```bash
npx @larksuite/cli@latest install
lark-cli --version
```

## Create Or Bind App Config

For first setup on a machine:

```bash
lark-cli config init --new
```

Open the URL or scan the QR code printed by the CLI, then finish the Feishu Open Platform app setup in the browser.

Check config:

```bash
lark-cli config show
```

## Authorize User Access

For this worklog skill, request document and drive access:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth login \
  --recommend \
  --domain docs,drive,markdown \
  --scope "search:docs:read"
```

In agent contexts, prefer the non-blocking flow:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth login \
  --recommend \
  --domain docs,drive,markdown \
  --scope "search:docs:read" \
  --no-wait \
  --json
```

Send the exact `verification_url` to the user. After the user confirms authorization, complete polling with:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth login --device-code '<device_code>'
```

Check auth:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth status
```

## Update The Worklog Manually

Monthly documents use this title template:

```text
MM-YYYY 工作记录
```

Daily headings use US date format:

```text
MM-DD-YYYY
```

Fetch:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli docs +fetch \
  --api-version v2 \
  --as user \
  --doc "<monthly-document>" \
  --doc-format markdown
```

Overwrite with prepared Markdown:

```bash
env LARK_CLI_NO_PROXY=1 lark-cli docs +update \
  --api-version v2 \
  --as user \
  --doc "<monthly-document>" \
  --command overwrite \
  --doc-format markdown \
  --content @worklog.md
```

The content format must be:

```markdown
# 05-19-2026

- 飞书 CLI / 工作记录
  - 工作内容
    - Newest day goes first.
  - 验证与测试
    - Related Feishu CLI checks stay under the Feishu CLI domain.

# 05-18-2026

- n3mapping
  - 工作内容
    - Older day moves down.
```

## Monthly Rollover

This skill stores month-to-document mappings in a local registry. The repository only includes a safe template:

```text
skills/lark-worklog-archive/references/monthly-docs.example.json
```

Real registries must stay local and untracked. Recommended paths:

```text
skills/lark-worklog-archive/references/monthly-docs.local.json
$HOME/.config/lark-worklog-archive/monthly-docs.json
```

When `archive_worklog.py` sees a new month that is not in the registry, it creates a new Feishu document named `MM-YYYY 工作记录`, writes the new daily section, and updates the local registry.

If `search:docs:read` is authorized, the helper searches by exact monthly title before creating a new document. This reduces duplicate monthly documents when another PC already created the new month but the local registry is stale. Without that scope, the helper falls back to the local registry and may create a duplicate on month rollover if the repo was not pulled first.

## Multi-Conversation Safety

Prefer the helper script over manual overwrite:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --item "完成 X。" \
  --item "通过 Y 验证。"
```

The helper:

- uses a per-month file lock under `/tmp` so multiple local Codex conversations do not write at the same time;
- replaces only the same-day section when possible, so grouped multi-level appends do not rewrite unrelated dates;
- fetches the newest Feishu revision immediately before writing;
- updates with `--revision-id` and retries on conflicts;
- fetches again after writing and verifies the submitted bullets are present.
- normalizes older date sections to `MM-DD-YYYY` and bullet-only content;
- deduplicates identical bullets so rerunning the same archive command is safe.

Cross-PC edits can still race if two machines update at exactly the same time. The revision retry reduces that risk, and the final verification catches obvious lost writes. If a conflict remains, rerun the same archive command.

## Category Rules

The public template is:

```text
skills/lark-worklog-archive/references/category-rules.example.json
```

Real custom rules should stay local and untracked:

```text
skills/lark-worklog-archive/references/category-rules.local.json
$HOME/.config/lark-worklog-archive/category-rules.json
```

Preview classification without writing to Feishu:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --classify-only \
  --item "验证 n3mapping Humble launch smoke。"
```

## Sharing With Other People

The local registry has an `owner_open_id` to prevent another Feishu account from accidentally writing into the original user's worklog document.

For another person, use a separate registry:

```bash
mkdir -p "$HOME/.config/lark-worklog-archive"
export LARK_WORKLOG_REGISTRY="$HOME/.config/lark-worklog-archive/monthly-docs.json"
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --item "初始化我的工作记录。"
```

If a team intentionally shares one worklog document, the document must be shared in Feishu and users must pass `--allow-foreign-registry` intentionally.

## Cloud Repository Safety

Do not commit real document addresses, user OpenID values, app IDs, tokens, or API endpoints. Keep those only in the local registry or in the local `lark-cli` configuration.

## Token-Friendly Use

Use the helper for normal archiving. It prints a short result and keeps full document JSON inside the script process. Avoid `--dry-run` and manual `docs +fetch` unless debugging, because those print document content into the agent context.

## Time Handling

The helper defaults to the current date in `Asia/Shanghai`:

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --item "今日工作。"
```

Use `--date` only for backfill or correction. Both formats are accepted:

```bash
--date 2026-05-19
--date 05-19-2026
```

## Proxy Note

If shell proxy variables are set, `lark-cli` warns that credentials may transit through the proxy. Use `LARK_CLI_NO_PROXY=1` for auth and document operations unless the user explicitly needs the proxy.
