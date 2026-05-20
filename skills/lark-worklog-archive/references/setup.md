# lark-worklog-archive 安装与使用

> **一句话：**这份文件给 Codex/Agent 看，用于完成 `lark-worklog-archive` 的安装、授权、初始化、日常归档、团队共享和故障恢复。普通用户通常只需要把安装 prompt 交给 Codex，然后在浏览器里完成一次飞书授权。

# 是什么

`lark-worklog-archive` 是一个 Codex Skill，用来把每天通过 Codex/Agent 完成的开发工作归档到飞书月度工作记录文档。

| 规则 | 说明 |
|-|-|
| 月度文档 | 每月一个文档，标题为 `MM-YYYY 工作记录`。 |
| 每日结构 | 每天一个一级标题，格式为 `# MM-DD-YYYY`，新日期在上方。 |
| 分类方式 | 日期下面只用无序列表。一级 bullet 是工作域，例如飞书 CLI / 工作记录、Ubuntu 环境、n3mapping、RL 环境；下面再按工作内容、代码与仓库、开发环境、验证与测试、问题与风险分类。 |
| 链接能力 | 条目可以使用 Markdown 链接，例如 `编写 [使用说明](https://example.com/docx/xxx)，用于团队查看。`，写入飞书后可点击跳转。 |
| 团队署名 | 团队文档中，同一工作域下的 `工作内容` 会保留在同一个分类里，但具体事项写成 `作者：事项`。 |
| 私有边界 | 真实飞书文档 URL、OpenID、App ID、token、secret 和本机 registry 不进入 Git。 |

# 为什么要用

## 不用它的问题

- 多个 Codex 对话同时写飞书时，直接 overwrite 容易丢内容。
- 用户手动整理工作记录成本高，分类、顺序和日期格式容易漂移。
- 跨 PC 使用时，如果每台机器各自创建月度文档，会造成记录分叉。
- 团队共享工作记录时，如果没有署名，同一工作域里的贡献难以区分。

## 使用后的效果

- Codex 只归档已完成并验证过的工作、关键命令/文件、测试结果和遗留问题。
- 同日追加会合并到已有日期 section，按分类追加到自然顺序之后。
- 脚本使用本机月度锁、最新 revision、revision-id、重试、去重、失败队列和写后验证，降低覆盖和丢写风险。
- 普通用户不需要每天复制命令；说“今日归档”即可。

# 怎么用

## 用户怎么触发

正常情况下，用户只需要在 Codex 里说：

- 今日归档。
- 记录今天工作。
- 把这次完成的内容同步到飞书工作记录。
- 安装并配置飞书工作记录 Skill。

Codex/Agent 应读取本 Skill，整理当天实际完成的工作，并调用脚本写入飞书。不要要求普通用户每天手动输入下面的脚本命令。

## 首次安装与授权

给普通用户的推荐 prompt：

```text
请帮我安装并配置 lark-worklog-archive Skill，用于把每天通过 Codex/Agent 完成的开发工作归档到飞书工作记录。请使用公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 通过 HTTPS 安装；安装或检查 lark-cli；发起一次性飞书用户授权，权限需要覆盖 docs、drive、markdown 和 search:docs:read；我只在网页上完成授权确认。授权后请初始化当前月工作记录文档，运行 doctor 检查，并告诉我以后可以直接说“今日归档”。不要把任何飞书文档 URL、OpenID、App ID、token 或 registry 提交到 Git。
```

Codex/Agent 执行路径：

```bash
git clone https://github.com/Killow1998/OnlyCodexCanDo.git
cd OnlyCodexCanDo
python3 skills/lark-worklog-archive/scripts/install.py
npx @larksuite/cli@latest install
lark-cli --version
```

如果本机还没有 `lark-cli` 应用配置：

```bash
lark-cli config init --new
```

`config init` 会输出浏览器链接或二维码。把链接给用户，让用户在网页里完成配置确认；不要要求用户手动复制后续命令。

发起一次性用户授权：

```bash
env LARK_CLI_NO_PROXY=1 lark-cli auth login \
  --recommend \
  --domain docs,drive,markdown \
  --scope "search:docs:read"
```

授权应一次性覆盖文档相关权限，避免后续归档过程中反复要求用户补授权。

授权后初始化和检查：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --init
python3 skills/lark-worklog-archive/scripts/archive_worklog.py --doctor
```

## Agent 日常执行路径

归档前先把用户请求和本轮实际完成内容整理成短条目，不要 invent 未验证工作。

预览分类：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --preview \
  --item "飞书 CLI / 工作记录::工作内容::完成 X，并通过 Y 验证。"
```

写入月度文档：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --item "飞书 CLI / 工作记录::工作内容::完成 X，并通过 Y 验证。" \
  --item "飞书 CLI / 工作记录::验证与测试::运行 Z 测试通过。"
```

如果工作产出了可分享文档或公开提交，在条目里放 Markdown 链接：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --item "飞书 CLI / 工作记录::工作内容::编写 [使用说明](https://example.com/docx/xxx)，用于团队查看。"
```

真实飞书文档链接只能出现在运行时归档内容或本机私有配置中；不要提交到 Git。

## 分类规则

默认工作域：

- 飞书 CLI / 工作记录
- Ubuntu 环境
- n3mapping
- RL 环境
- 其他

默认子类：

- 工作内容
- 代码与仓库
- 开发环境
- 验证与测试
- 问题与风险
- 其他

私有分类规则可放在：

```text
skills/lark-worklog-archive/references/category-rules.local.json
$HOME/.config/lark-worklog-archive/category-rules.json
```

分类检查：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --classify-only \
  --item "验证 n3mapping Humble launch smoke。"
```

## 共享给团队

团队共享文档适合多人共同开发同一类工作，例如多人一起完善飞书 CLI 或同一个项目。团队模式必须显式启用，避免误写个人文档。

推荐让用户提供：

```text
请把 lark-worklog-archive 配置为团队共享工作记录。团队名是 <team-name>，文档标题前缀是 <team-title>。以后团队归档时，请用我的署名 <display-name> 写入工作内容，格式应能区分不同成员完成的事项。
```

Codex/Agent 初始化团队 registry：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --init \
  --team \
  --team-id "<team-name>" \
  --title-prefix "<team-title>"
```

团队写入必须显式 `--team`，并通过 `--author` 或 `LARK_WORKLOG_AUTHOR` 写入署名：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --team \
  --author "Alice" \
  --item "飞书 CLI / 工作记录::工作内容::完善授权向导。"
```

## 并发与恢复

- 同机多对话使用每月文件锁。
- 写入前 fetch 最新 revision，更新时带 revision-id。
- 同日追加优先替换当天 section，新日期优先插入到文档顶部。
- 同一条目重复执行会去重。
- 写入后会重新 fetch 验证提交条目是否存在。
- 失败后可以用 `--queue-failed` 保存到本机失败队列，后续同日期归档自动重放并去重。

修复某一天：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --normalize-only \
  --date 05-20-2026
```

修复整月：

```bash
python3 skills/lark-worklog-archive/scripts/archive_worklog.py \
  --normalize-only \
  --all-dates
```

缓存和失败队列路径：

```text
$HOME/.cache/lark-worklog-archive/cache.json
$HOME/.local/state/lark-worklog-archive/failed-queue.jsonl
```

## Token 消耗

- 正常归档：最低输出，只打印标题、日期和新增条目数。
- `--preview`：低输出，不读写飞书，适合日常检查分类。
- `--doctor`：低输出，检查安装、授权、registry 和当前月份。
- `--dry-run`：高输出，会打印完整 Markdown，只在调试结构时使用。
- 手动 `docs +fetch`：高输出，只在审计或排障时使用。
- `--print-doc`：可能把文档 locator 打到对话里，默认不要使用。

## 发布检查

提交或分发前运行：

```bash
python3 skills/lark-worklog-archive/scripts/check.py
```

它会运行单元测试、语法检查、敏感信息扫描、安装 dry-run、Skill validation 和全局安装副本一致性检查。

## 故障排除

| 问题 | 处理方式 |
|-|-|
| `lark-cli` 不存在 | 运行 `npx @larksuite/cli@latest install`，再检查 `lark-cli --version`。 |
| 应用配置不存在 | 运行 `lark-cli config init --new`，让用户在浏览器里完成配置。 |
| 权限不足或授权过期 | 重新发起一次性授权，覆盖 docs、drive、markdown 和 `search:docs:read`。 |
| registry owner mismatch | 使用个人 registry 路径，或确认后显式传 `--allow-foreign-registry`。 |
| 分类不准 | 先 `--preview` 或 `--classify-only`，再调整本机私有分类规则。 |
| 文档结构混乱 | 使用 `--normalize-only --date` 修复单日，必要时 `--normalize-only --all-dates`。 |
| 团队文档无法写入 | 确认已传 `--team`，并带 `--author` 或 `LARK_WORKLOG_AUTHOR`。 |
| 代理警告 | 默认使用 `LARK_CLI_NO_PROXY=1`，除非用户明确要求走代理。 |
