# OnlyCodexCanDo

[English](README.md) | 中文

这是我的 Agent 工作流记录库：记录实际开发中采用的协作原则、项目流程、可复用 Skills，以及改进这些工作方式的经验。

可复用的规则、模板和工具在这里维护，按需部署到不同主机与项目。项目自己的进度和工作记录留在项目里；有跨项目价值的经验，再提炼回来。

## 从哪里开始

| 你想做什么 | 看这里 |
| --- | --- |
| 了解判断、执行、验证与协作原则 | [Agent 工作流](docs/agent-workflow.zh-CN.md) |
| 配置一台主机的全局 `AGENTS.md` | [规则解读与可选项](docs/global-agents.zh-CN.md)、[最小核心模板](templates/AGENTS.global.md) |
| 让项目中断后仍能继续开发 | [Workspace 持续文档](docs/workspace-continuous-documentation.zh-CN.md)、[项目规则片段](templates/workspace/AGENTS.docs-workflow.md) |
| 选择需要的 Skill，控制触发范围 | [Skill 选择与多主机使用](docs/skill-management.zh-CN.md)、下方的 Skills 清单 |

本地文档随开发及时更新：`active/` 记录当前计划，`design/` 保存稳定设计，`worklog/` 记录阶段结果、证据和经验。只在内容有实质变化时更新，不要求每次小修改都新建文档。飞书等云端归档是独立的按需操作，不影响本地开发。

## 部署工作流

这里提供两条互相独立的部署路径：

| 路径 | 作用范围 | 来源 |
| --- | --- | --- |
| 主机级全局行为 | 一台 Agent 主机上的所有 workspace | [核心与选项解读](docs/global-agents.zh-CN.md)、[最小核心](templates/AGENTS.global.md)和用户选择的可选或平台模块 |
| Workspace 工作流 | 一个仓库，跨 Agent、跨主机生效 | [三目录工作流说明](docs/workspace-continuous-documentation.zh-CN.md)、独立选择的 [Workspace 模块](templates/workspace/)和该仓库已有的 `AGENTS.md` 与 `docs/` |

全局配置统一 Agent 的工作方式，Workspace 配置维护项目的计划、设计和工作记录。推荐搭配使用，也可以按需单独部署。

### 配置一台 PC 的全局 AGENTS.md

把下面这段 Prompt 交给那台 PC 上运行的 Codex Agent：

```text
请根据公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 配置这台 PC 的全局 Codex AGENTS.md。

1. 读取 templates/AGENTS.global.md，把它作为唯一自动推荐的跨平台核心；同时阅读 docs/global-agents.zh-CN.md，了解有哪些可选项。
2. 提议修改前，先检查 Agent 的实际运行环境和现有全局 AGENTS.md。把现有规则分成保留、移到渐进加载层、建议删除三类并指出冲突；可发现、易漂移或一次性的细节不能仅因为“不冲突”就永久保留。不要盲目覆盖整个文件。
3. 只考虑当前主机相关模块，解释行为、收益和代价。复用我已经明确的偏好，其余用当前可用的交互选项工具集中询问，允许自由填写；不要每个模块问一轮，也不要把推荐或预选当作同意。没有选项工具时用一次简短询问。语言、称呼、会话标题、委派与上下文策略、worktree、RTK、时区及其他主机策略均为独立选择。
4. 选称呼时询问用户称呼和 Agent 昵称，仅保存在私有主机配置；选记录或标题时区时确认 IANA 时区并替换相应占位符。选会话标题时先验证元数据和改名能力，不把指令模板宣传为已安装 Hook。RTK、资源限制和平台模块也先核对实际环境；检测到工具或平台不等于批准。
5. 主机全局文件不加入项目工作流和领域规则。持续文档、实验记录和 Robotics 验证应在各个 Workspace 中另行选择。
6. 写入前展示准确的合并 diff、已选模块及参数，以及每条拟删除或迁移规则；说明是否改变授权范围。通过支持的批准方式获得确认后，先备份再应用，不重复询问已批准且未改变的决定。验证核心和已选模块各出现一次、参数已填写、经批准保留的本机规则仍在；功能模块还要验证实际行为。偏好选项不是文件权限提权。

不要修改项目仓库、远端主机，也不要安装任何 Skill，除非我另行明确授权。
```

### 在一个 Workspace 中配置可选 Agent 工作流

在目标 Workspace 中运行下面的 Prompt；它可以配置持续文档、实验记录、Robotics 验证或其中任意相关组合，并且不会修改主机全局 `AGENTS.md`：

```text
请使用 https://github.com/Killow1998/OnlyCodexCanDo.git，在当前 Workspace 中配置选定的 Agent 工作流。

1. 读取 docs/workspace-continuous-documentation.zh-CN.md，并先检查当前 workspace 的分支、工作树、AGENTS.md 或其他 Agent 指令、README 和已有 docs。保护无关工作，优先复用等价文档，不要创建重复体系。
2. 把每个 Workspace 模块当作独立选项。分别说明持续文档（templates/workspace/AGENTS.docs-workflow.md 与 worklog 模板）、显式实验记录（templates/workspace/experiments.md）和 Robotics 证据分层（templates/workspace/robotics-validation.md）的实际收益与维护成本。只推荐有项目证据支持的模块，但不要仅凭仓库名或技术栈推定用户已经同意。
3. 复用已明确的选择，其余相关模块通过可用的交互选项集中询问；持续文档、实验纪律、Robotics 验证和界面约定（templates/workspace/ui-conventions.md）互不自动绑定。
4. 如果选择持续文档，展示现有文档如何对应三个用途：当前 spec/plan -> docs/active/，稳定算法与技术设计 -> docs/design/，完成阶段记录 -> docs/worklog/。已有等价路径就沿用，不为统一目录名复制内容。
5. 只创建已选模块缺少的结构。持续文档模块把模板放到 docs/worklog/worklog-template.md，并只将稳定的文档入口规则合并进作用范围最近的项目 AGENTS.md；小改动不强制创建 plan 或 worklog。
6. 写入前展示仅限当前 workspace 的 diff 和已选模块清单。只有我确认后才应用；应用后验证引用路径、规则和模板，确认没有平行工作流或任务临时文件。

不要修改主机全局 AGENTS.md、其他 workspace、远端主机，也不要安装任何 Skill，除非我另行明确授权。
```

## Skills

按任务选择，不需要全部安装。详细流程和限制放在各自入口中。

| Skill / 插件 | 用途 | 使用建议与说明 |
| --- | --- | --- |
| `codex-home-audit` | 诊断 Codex 状态目录占用与启动问题 | 按需只读检查；清理另行批准。[入口](skills/codex-home-audit/SKILL.md) |
| `lark-worklog-archive` | 把选定的开发成果归档到飞书 | 主动要求时使用；日常以项目 docs 为主。[入口](skills/lark-worklog-archive/SKILL.md) · [安装、授权与验证状态](skills/lark-worklog-archive/references/setup.md) |
| `organizedProj` | 整理本次影响的项目文档，保留已验证经验 | 有范围的阶段收尾，复用现有文档。[入口](skills/organized-proj/SKILL.md) |
| `TaskWatch` | 长任务失败与完成通知 | 支持 Agent Mail 和 SMTP。[Agent Mail 配置](skills/taskwatch/references/agent-mail.zh-CN.md) · [使用说明](skills/taskwatch/references/usage.md) |

## 安装 Skill

### `organizedProj`

把下面的 Prompt 交给目标主机或 workspace 中的 Agent：

```text
请从 https://github.com/Killow1998/OnlyCodexCanDo.git 安装 organizedProj，来源为 skills/organized-proj（显示名 organizedProj，调用名 $organized-proj）。先比较已有副本、保留本地修改；询问是全局可用还是仅当前 workspace 可用，只部署选定范围，然后运行 scripts/check.py。本次安装不扫描或重写项目文档。分别报告实际发现检查和行为验证状态。
```

### `codex-home-audit`

把下面的 Prompt 交给目标主机上的 Codex：

```text
请从 https://github.com/Killow1998/OnlyCodexCanDo.git 安装 codex-home-audit，只部署 skills/codex-home-audit，保留其他 Skills。先比较已有副本与源码，保留本地修改并展示冲突；安装后运行该 Skill 的 scripts/check.py，报告检查结果，不为消除差异而盲目覆盖。现在不要扫描或清理真实 CODEX_HOME。告诉我是否需要重开任务才能发现更新后的 Skill。
```

### `lark-worklog-archive`

先配置本地能力，云端授权和归档留到实际需要时：

```text
请从 https://github.com/Killow1998/OnlyCodexCanDo.git 安装 lark-worklog-archive Skill，并使用官方最新稳定版 lark-cli。先检查本机已有安装、app/config 和自定义文件；升级 CLI 时使用官方 update，保留现有配置与凭据。不要覆盖未审阅的本地 Skill 修改。本次只安装和验证本地能力，不发起登录、不创建飞书应用或月度文档、不上传工作记录，也不设置定时上传或授权保活。日常记录以项目 docs 为主，等我明确要求归档到飞书时，再检查授权与目标文档，只在确有需要时让我完成浏览器授权。最后分别报告本地检查和云端验证状态；私有配置与凭据不得进入 Git。
```

具体命令、授权排查和已验证版本见[安装说明](skills/lark-worklog-archive/references/setup.md)。

### `TaskWatch`

按 [Agent Mail 配置](skills/taskwatch/references/agent-mail.zh-CN.md)启用命令退出或 goal 终态通知；SMTP 和 Linux 进度报告见[使用说明](skills/taskwatch/references/usage.md)。启用前确定收件人和通知内容。

部署后验证实际事件触发和邮件送达，凭据保存在本机私有配置中。

## 怎样持续改进

1. 在实际项目中尝试，用项目 worklog 记录结果、问题和证据。
2. 有复用价值后，再更新 OCCD 中对应的规则、模板、Skill 或已有说明，保留必要的适用场景和选择理由。
3. 一项事实只维护一个主要出处，README 提供入口；经验也可以促成删除或合并旧规则。
4. 改好源码与说明后，按授权更新选定主机或项目，并验证实际行为。仓库更新不等于所有安装副本都已更新。

## 仓库规则

- 只发布经过提炼、适合跨项目复用的知识；原始 session、主机清单、凭据和私有运行状态由独立的私有层管理。
- 面向公开用户时使用 HTTPS clone。
- 真实用户配置放在本机 ignored 文件或用户配置目录。
- 不提交 secrets、tokens、飞书/Lark 文档 URL、OpenID、App ID、私有 API endpoint 或真实 registry。

`lark-worklog-archive` 的开发 TODO 在 [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md)。
