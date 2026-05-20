# OnlyCodexCanDo

> **一句话：**这是一个公开 Codex Skills 仓库。目前主要提供 `lark-worklog-archive`，让 Codex/Agent 把每天完成的开发工作自动归档到飞书月度工作记录。用户只需要让 Codex 安装、授权或“今日归档”，具体命令由 Codex 根据 Skill 执行。

This repository stores reusable skills only. It is not a memory store and must not contain project history, chat summaries, credentials, Feishu document URLs, API endpoints, OpenID values, app IDs, tokens, or other private runtime configuration.

# 是什么

`lark-worklog-archive` 是一个 Codex Skill，用来把每天通过 Codex/Agent 完成的开发、调试、环境配置和仓库维护工作写入飞书工作记录。

| 规则 | 说明 |
|-|-|
| 月度文档 | 每月一个飞书文档，标题为 `MM-YYYY 工作记录`。 |
| 每日结构 | 每天一个一级标题，格式为 `# MM-DD-YYYY`，新日期在上方。 |
| 分类方式 | 日期下面只用无序列表。一级 bullet 是工作域，例如飞书 CLI / 工作记录、Ubuntu 环境、n3mapping、RL 环境；下面再按工作内容、代码与仓库、开发环境、验证与测试、问题与风险分类。 |
| 文档链接 | 工作记录条目可以包含 Markdown 链接，产出的飞书文档、GitHub commit 或说明文档可以直接跳转查看。 |
| 团队署名 | 团队模式下，同一工作域里的 `工作内容` 会写成 `作者：事项`，用于区分不同成员完成的内容。 |
| 私有配置 | 真实飞书文档映射、OpenID、App ID、token 和 registry 只保存在本机私有配置中，不进入 Git。 |

# 为什么要用

## 不用它的问题

- 多个 Codex 对话容易重复写、互相覆盖，或者把计划误写成已完成工作。
- 用户手动整理每日工作记录成本高，分类和顺序容易混乱。
- 跨 PC 或跨对话更新飞书文档时，直接 overwrite 风险很高。
- 给朋友或团队复用时，如果安装、授权和 registry 规则不清楚，很容易把私有 URL 或账号信息提交到公开仓库。

## 使用后的效果

- Codex 只归档已验证的工作结果、关键命令/文件、测试结果和遗留问题。
- 同一天内容会按工作域和子类合并，后追加内容保留自然执行顺序。
- 脚本使用本机锁、revision、局部替换、去重、失败队列和最终验证降低丢写风险。
- 普通用户不需要每天复制命令；说“今日归档”即可让 Codex 自动整理并写入飞书。

# 怎么用

## 用户怎么触发

常用触发方式：

- 今日归档。
- 记录今天工作。
- 把这次完成的内容同步到飞书工作记录。
- 安装并配置飞书工作记录 Skill。

Codex 会读取 Skill，整理当天实际完成的工作，并调用脚本写入飞书。用户不需要每天手动维护 Markdown。

## 首次安装与授权

首次使用时，把下面这段 prompt 交给 Codex：

```text
请帮我安装并配置 lark-worklog-archive Skill，用于把每天通过 Codex/Agent 完成的开发工作归档到飞书工作记录。请使用公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 通过 HTTPS 安装；安装或检查 lark-cli；发起一次性飞书用户授权，权限需要覆盖 docs、drive、markdown 和 search:docs:read；我只在网页上完成授权确认。授权后请初始化当前月工作记录文档，运行 doctor 检查，并告诉我以后可以直接说“今日归档”。不要把任何飞书文档 URL、OpenID、App ID、token 或 registry 提交到 Git。
```

安装和授权细节见 [skills/lark-worklog-archive/references/setup.md](skills/lark-worklog-archive/references/setup.md)。这份文件主要给 Codex/Agent 看，普通用户通常只需要使用上面的 prompt。

## 共享给团队

团队共享文档适合多人共同开发同一类工作，例如多人一起完善飞书 CLI 或同一个项目。配置时让 Codex 明确启用团队模式，并给每个成员设置署名：

```text
请把 lark-worklog-archive 配置为团队共享工作记录。团队名是 <team-name>，文档标题前缀是 <team-title>。以后团队归档时，请用我的署名 <display-name> 写入工作内容，格式应能区分不同成员完成的事项。
```

## 并发与恢复

- 同机多对话使用每月文件锁。
- 写入前 fetch 最新 revision，更新时带 revision-id。
- 同日追加优先替换当天 section，新日期优先插入到文档顶部。
- 失败后可以写入本机失败队列，后续同日期归档自动重放并去重。

## 故障排除

| 问题 | 处理方式 |
|-|-|
| `lark-cli` 不存在 | 让 Codex 安装或重新检查 `@larksuite/cli`。 |
| 权限不足或授权过期 | 让 Codex 重新发起一次性授权，用户只在网页上确认。 |
| 分类不准 | 让 Codex 预览分类，再调整本机分类规则。 |
| 文档结构混乱 | 让 Codex 修复某一天或修复整月结构。 |
| 团队文档无法写入 | 确认团队模式已启用，并且 Codex 写入时带成员署名。 |

# Repository Rules

- Keep only skill source, scripts, examples, and public setup references here.
- Do not commit local registries such as `monthly-docs.local.json`.
- Do not commit secrets, access tokens, Feishu document URLs, OpenID values, app IDs, private API endpoints, or real registry values.
- If a skill needs user-specific values, store examples in Git and keep real values in ignored local files or user config paths.

Development TODO is tracked in [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md).
