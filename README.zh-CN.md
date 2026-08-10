# OnlyCodexCanDo

[English](README.md) | 中文

这是一个公开的 Codex Skills 与 Agent 工作流说明仓库。

这里发布可复用的 skill 源码、跨项目工作流、配置模板、公开示例、脚本和说明文档，并作为多个 Agent 终端共享稳定规则与提炼知识的公开来源。

## Agent 工作流

跨项目工作方式见[可组合 Agent 工作流](docs/agent-workflow.zh-CN.md)，English version 见 [Composable Agent Workflow](docs/agent-workflow.md)。

这里把小而通用的跨平台核心，与语言、工具、主机、平台和 Workspace 选项分开。可复用核心位于 [templates/AGENTS.global.md](templates/AGENTS.global.md)，可选主机模块位于 [templates/optional/](templates/optional/)，平台模块位于 [templates/platform/](templates/platform/)，互相独立的 Workspace 工作流位于 [templates/workspace/](templates/workspace/)。这样，无关偏好和领域规则不会占用每个 Agent 的上下文。

这里提供两条互相独立的部署路径：

| 路径 | 作用范围 | 来源 |
| --- | --- | --- |
| 主机级全局行为 | 一台 Agent 主机上的所有 workspace | [核心与选项解读](docs/global-agents.zh-CN.md)、[最小核心](templates/AGENTS.global.md)和用户选择的可选或平台模块 |
| Workspace 工作流 | 一个仓库，跨 Agent、跨主机生效 | [三目录工作流说明](docs/workspace-continuous-documentation.zh-CN.md)、独立选择的 [Workspace 模块](templates/workspace/)和该仓库已有的 `AGENTS.md` 与 `docs/` |

两条路径都可以单独使用，但推荐组合部署：主机层统一 Agent“怎么工作”，workspace 层保存项目“知道什么”。这是推荐绑定，不是技术强绑定；两份 diff 应分别审阅和批准，同一规则不要在两层重复维护。

### 配置一台 PC 的全局 AGENTS.md

把下面这段 Prompt 交给那台 PC 上运行的 Codex Agent：

```text
请根据公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 配置这台 PC 的全局 Codex AGENTS.md。

1. 读取 templates/AGENTS.global.md，把它作为唯一自动推荐的跨平台核心；同时阅读 docs/global-agents.zh-CN.md，了解有哪些可选项。
2. 提议修改前，先检查 Agent 的实际运行环境和现有全局 AGENTS.md。保留不冲突的本机规则并指出冲突，不要盲目覆盖整个文件。
3. 只考虑当前主机可能需要的模块。对于 templates/optional/ 或 templates/platform/ 下每个相关选项，用通俗语言说明它会增加什么行为、代价或限制，以及是否推荐，再让我选择；不要擅自加入中文优先、单 Agent、禁用 worktree、RTK、时区、仓库/数据策略、资源限制或平台模块。明显不相关的模块不要拿来逐项提问。
4. 选择时区模块时，询问 IANA 时区并替换占位符；选择 RTK 或资源限制模块时，先验证目标主机确实具备对应工具或运行环境。检测到 Windows 只代表 windows-shell.md 相关，不代表用户已经批准。
5. 主机全局文件不加入项目工作流和领域规则。持续文档、实验记录和 Robotics 验证应在各个 Workspace 中另行选择。
6. 写入前展示准确的合并 diff 和已选模块清单。只有我确认后才应用，并先创建可恢复备份；应用后验证公共核心和每个已选模块各出现一次，没有未选模块或未替换占位符，原有本机规则仍然存在。

不要修改项目仓库、远端主机，也不要安装任何 Skill，除非我另行明确授权。
```

### 在一个 Workspace 中配置可选 Agent 工作流

在目标 Workspace 中运行下面的 Prompt；它可以配置持续文档、实验记录、Robotics 验证或其中任意相关组合，并且不会修改主机全局 `AGENTS.md`：

```text
请使用 https://github.com/Killow1998/OnlyCodexCanDo.git，在当前 Workspace 中配置选定的 Agent 工作流。

1. 读取 docs/workspace-continuous-documentation.zh-CN.md，并先检查当前 workspace 的分支、工作树、AGENTS.md 或其他 Agent 指令、README 和已有 docs。保护无关工作，优先复用等价文档，不要创建重复体系。
2. 把每个 Workspace 模块当作独立选项。分别说明持续文档（templates/workspace/AGENTS.docs-workflow.md 与 worklog 模板）、显式实验记录（templates/workspace/experiments.md）和 Robotics 证据分层（templates/workspace/robotics-validation.md）的实际收益与维护成本。只推荐有项目证据支持的模块，但不要仅凭仓库名或技术栈推定用户已经同意。
3. 询问我要加入哪些相关模块。持续文档、实验纪律和 Robotics 验证互不自动绑定。
4. 如果选择持续文档，展示现有文档如何对应三个用途：当前 spec/plan -> docs/active/，稳定算法与技术设计 -> docs/design/，完成阶段记录 -> docs/worklog/。已有等价路径就沿用，不为统一目录名复制内容。
5. 只创建已选模块缺少的结构。持续文档模块把模板放到 docs/worklog/worklog-template.md，并只将稳定的文档入口规则合并进作用范围最近的项目 AGENTS.md；小改动不强制创建 plan 或 worklog。
6. 写入前展示仅限当前 workspace 的 diff 和已选模块清单。只有我确认后才应用；应用后验证引用路径、规则和模板，确认没有平行工作流或任务临时文件。

不要修改主机全局 AGENTS.md、其他 workspace、远端主机，也不要安装任何 Skill，除非我另行明确授权。
```

推荐组合部署方式：每台主机只选择一次最小全局配置，再只在确有收益的仓库中选择 Workspace 模块。两部分始终分别批准、分别验证；推荐组合不代表任何一部分必须部署。

## Skills

### `CodexLFE`

让 Codex Orchestration 使用受约束的 GPT-5.6 Luna Max Fast 自定义 Executor。

主要行为：

- 只安装或验证 canonical Codex Orchestration marketplace 来源；
- 创建本机 `codex_lfe_executor` custom agent，不复制或 vendor Orchestration；
- 必要的 Luna v2 兼容 catalog 只从目标机器自己的模型缓存生成；
- 只有显式、preview-first 的 `setup` 和 `disable` 才会修改全局状态；
- setup 后必须完全重启 Codex，`verify` 才会做静态检查并请求一次真实 routed spawn；
- 配置冲突、agent 归属冲突、依赖来源异常或 managed state drift 时全部 fail closed。

### `lark-worklog-archive`

把每天通过 Codex/Agent 完成的工作归档到飞书/Lark 月度工作记录文档。

适合这些触发方式：

- 今日归档。
- 记录今天工作。
- 把这次完成的内容同步到飞书工作记录。

主要行为：

- 每月一个飞书/Lark 工作记录文档；
- 每天一个 `MM-DD-YYYY` 标题；
- 工作内容按工作域和子类归档；
- 通过 helper 脚本安全追加同一天内容，避免直接 overwrite；
- 工作条目可以带 Markdown 链接，用于跳转到相关文档或 commit；
- 真实文档映射只保存在本机忽略配置中。
- 当前匹配 `lark-cli 1.0.51`；本机 CLI 过旧时先更新，不保留旧版授权输出兼容逻辑。

### `TaskWatch`

为任何长时间运行的 Linux 任务生成可复用的只读 Codex monitor。

适合这些触发方式：

- 给这个长时间运行任务加一个 Codex monitor。
- 生成按小时巡检的只读任务报告。
- 给当前 workspace 增加 systemd 用户定时器和任务完成邮件通知。

主要行为：

- 生成 `.codex_monitor` 脚手架：默认在 workspace 内，加 `--central` 时整体放到 `~/.codex/taskwatch/jobs/<name>/`，工程目录不新增任何文件；
- 写入可配置的 `run_command.sh` 和 `monitor.env`；
- 安装小时报告和最终总结脚本；
- 支持 Codex goal-mode 在最终邮件里区分 `complete`、`blocked` 和 `usageLimited`；
- 也可以只安装全局 Codex `Stop` hook，用于 goal 终态邮件告警，不依赖 workspace 本地 monitor；
- 支持无 sudo 的 systemd user timer；
- SMTP secret 和运行期报告保持不入 Git；
- 对常见邮箱域名自动推断 SMTP host、port 和安全模式，所以通常只需要用户提供发件邮箱、收件邮箱和发件邮箱密钥；
- 支持干净卸载：脚手架用 `install.py --uninstall`，全局 hook 用 `install_global_hook.py --remove`。

当前局限性：

- workspace-local monitor 只支持 Linux，timer 默认走 `systemd --user`。
- Windows 下只安装全局 goal 终态 `Stop` hook，不部署 workspace 本地 training 或长任务 monitor。
- 全局 goal 终态邮件依赖 Codex `Stop` hook。如果是断电、宿主机崩溃、或者外部直接 kill 导致 Codex 没有正常收尾，这条链路不会触发。
- goal 归档状态属于 best-effort 检测。它依赖 Codex transcript 和本地 state 推断，特殊流程下可能显示为“未检测到”。
- workspace-local monitor 假设任务本身已经有真实可运行的命令、日志或 artifact 目录；它不会替你发明任务逻辑。
- SMTP 仍然依赖邮箱服务商的有效 app password / 授权码。
- 全局 hook 和 workspace-local monitor 是互补关系：前者负责 goal 终态告警，后者负责按小时的日志和产物巡检。

## 安装 Skill

### `CodexLFE`

把本仓库添加为 Codex plugin marketplace，并安装 CodexLFE：

```text
codex plugin marketplace add https://github.com/Killow1998/OnlyCodexCanDo.git --json
codex plugin add codex-lfe@only-codex-can-do --json
```

然后在 Codex 中显式运行 setup：

```text
$codex-lfe:codex-lfe setup
```

setup 返回 `RESTART_REQUIRED` 后，完全退出并重开 Codex，创建新任务，再运行：

```text
$codex-lfe:codex-lfe verify
```

### `lark-worklog-archive`

普通用户不需要自己逐条执行安装命令。把下面这段 prompt 交给 Codex 即可：

```text
请帮我安装并配置 lark-worklog-archive Skill，用于把每天通过 Codex/Agent 完成的开发工作归档到飞书工作记录。请使用公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 通过 HTTPS 安装；安装或检查 lark-cli；如果已有 lark-cli app/config 就复用，不要重新创建飞书 app；否则发起一次性飞书用户授权，权限需要覆盖 docs、drive、markdown 和 search:docs:read；我只在网页上完成授权确认。授权后先运行 doctor 检查，优先搜索/注册已有的当前月工作记录文档；只有找不到已有文档且我明确同意时，才创建新的月度文档。最后告诉我以后可以直接说“今日归档”。不要把任何飞书文档 URL、OpenID、App ID、token、secret 或 registry 提交到 Git。
```

给 Codex/Agent 看的安装细节在 [skills/lark-worklog-archive/references/setup.md](skills/lark-worklog-archive/references/setup.md)。

### `TaskWatch`

对于 workspace 本地 monitor，Codex 应该先检查目标 workspace，尽量自己推断真实任务命令、日志路径、artifact 目录、进程匹配规则和已有 service 名称，再运行 installer：

```text
请从 https://github.com/Killow1998/OnlyCodexCanDo.git 安装并配置 TaskWatch skill。先检查目标 workspace，尽量自己推断真实的长任务启动命令、主日志、artifact 目录、进程匹配规则，以及是否已有 user systemd service，而不是让我手动把每个 flag 都填一遍。只在 Linux 下部署。对于 workspace 本地 monitor，请生成 .codex_monitor、run_with_monitor.sh、按小时的只读巡检报告、最终完成邮件，以及可选的 systemd --user timer。对于 goal-mode 任务，还要确保最终邮件能区分 complete、blocked 和 usageLimited。只有在确实需要邮件配置时，才向我索取三项信息：发件邮箱、收件邮箱、发件邮箱的 SMTP 密码或授权码。所有 secret、报告和本地运行期状态都不要提交到 Git。安装完成后运行 skill 检查；如果本机已经安装了全局 skill，也要验证全局副本一致性；最后把启动监控任务的准确命令告诉我。
```

如果只是要全局 goal 终态邮件，不需要 workspace 本地 monitor：

```text
请从 https://github.com/Killow1998/OnlyCodexCanDo.git 只安装 TaskWatch 的全局 goal 终态邮件 hook。在 ~/.codex 下配置 Codex Stop hook，让 goal 任务在 complete、blocked 和 usageLimited 时发送终态邮件。如果本机已经有现成配置就复用。只有在尚未配置邮件时，才向我索取发件邮箱、收件邮箱和发件邮箱的 SMTP 密码或授权码。所有 secret 只能保存在本机忽略文件里，并在安装后做一次安全的 smoke test。
```

Windows 下使用这条“只安装全局 hook”的路径。Linux 主机才使用 workspace 本地 monitor 来监控 training、evaluation 或其他长时间任务，并通过 `systemd --user` 定时巡检。

技能入口说明在 [skills/taskwatch/SKILL.md](skills/taskwatch/SKILL.md)。使用说明在 [skills/taskwatch/references/usage.md](skills/taskwatch/references/usage.md)。

## 仓库规则

- 只发布经过提炼、适合跨项目复用的知识；原始 session、主机清单、凭据和私有运行状态由独立的私有层管理。
- 面向公开用户时使用 HTTPS clone。
- 真实用户配置放在本机 ignored 文件或用户配置目录。
- 不提交 secrets、tokens、飞书/Lark 文档 URL、OpenID、App ID、私有 API endpoint 或真实 registry。

`lark-worklog-archive` 的开发 TODO 在 [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md)。
