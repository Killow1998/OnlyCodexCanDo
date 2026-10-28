# OnlyCodexCanDo

[English](README.md) | 中文

这是我的 Agent 工作流记录库：记录实际开发中采用的协作原则、项目流程、可复用 Skills，以及改进这些工作方式的经验。

可复用的规则、模板和工具在这里维护，按需部署到不同主机与项目。项目自己的进度和工作记录留在项目里；有跨项目价值的经验，再提炼回来。

## 从哪里开始

| 你想做什么 | 看这里 |
| --- | --- |
| 了解判断、执行、验证与协作原则 | [Agent 工作流](docs/agent-workflow.zh-CN.md) |
| 配置一台主机的全局 `AGENTS.md` | [规则解读与可选项](docs/global-agents.zh-CN.md)、[最小核心模板](templates/AGENTS.global.md) |
| 按需读取后端、前端或 Git 规范 | [规范与读取入口](docs/global-agents.zh-CN.md#按需开发规范) |
| 在重要阶段后保留项目上下文 | [渐进式项目记录](docs/workspace-continuous-documentation.zh-CN.md)、[`organized-proj`](skills/organized-proj/SKILL.md) |
| 选择需要的 Skill，控制触发范围 | [Skill 选择与多主机使用](docs/skill-management.zh-CN.md)、下方的 Skills 清单 |

重要阶段结束后，由 `organized-proj` 按需更新项目现有记录。不要求每个仓库安装工作流或采用固定目录；小改动不记录。飞书等云端归档仍是独立操作。

## 部署工作流

通常只需配置一个主机全局入口：

| 路径 | 作用范围 | 来源 |
| --- | --- | --- |
| 主机级全局行为 | 一台 Agent 主机上的所有 workspace | [核心与选项解读](docs/global-agents.zh-CN.md)、[最小核心](templates/AGENTS.global.md)、选定的可选模块，以及启用阶段记录时全局安装的 `organized-proj` |
| 领域参考 | 仅在任务需要时加载 | [Workspace 参考](templates/workspace/)中的实验、Robotics、UI 与可选 worklog 格式 |

项目事实和记录仍留在项目里，但不再要求单独安装工作流。只有项目存在无法从现有文件发现的稳定约定时，才增加项目级规则。

### 配置一台 PC 的全局 AGENTS.md

把下面这段 Prompt 交给那台 PC 上运行的 Codex Agent：

```text
请根据公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 配置这台 PC 的全局 Codex AGENTS.md。

1. 读取 templates/AGENTS.global.md 和 docs/global-agents.zh-CN.md。检查本机环境与现有全局 AGENTS.md，识别应保留、移到渐进加载层或删除的规则，以及冲突和过时内容。
2. 复用我已确认的偏好。说明相关选项，将未确定的选择集中询问一次；推荐不等于同意。称呼、语言、时区等选项互相独立；填写已选参数，不公开私有值。
3. 按含义整合核心与已选偏好。合并重复、压缩措辞，保留授权边界和读取条件。默认采用简短开头和紧凑列表，省略模块标题、解释和示例；尊重我明确的格式偏好。
4. 按 docs/global-agents.zh-CN.md 只复制已选规范与语言版本，AGENTS.md 中只留一条读取入口。若未安装 organized-proj，集中询问一次是否全局安装；拒绝时改用“更新项目现有记录”，不引用 Skill。无需逐项目配置。
5. 展示准确的 diff、已选项和拟删除内容，说明授权变化。获准后备份、应用，读回核对文件和获准安装的内容。

不要修改项目仓库或远端主机。子 Agent 需要针对任务或范围的明确授权。仅安装获准的 Skill。
```

### 渐进式项目记录

不需要逐项目配置。重要阶段完成后，全局规则加载 `organized-proj`；它检查项目，只更新已有且相关的记录。`templates/workspace/` 下的领域参考只在当前任务需要时读取。

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
请从 https://github.com/Killow1998/OnlyCodexCanDo.git 全局安装 organizedProj，来源为 skills/organized-proj（显示名 organizedProj，调用名 $organized-proj）。先比较已有副本并保留本地修改，然后运行 scripts/check.py。本次安装不扫描或重写项目文档。分别报告实际发现检查和行为验证状态。
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
