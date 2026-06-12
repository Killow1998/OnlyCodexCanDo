# OnlyCodexCanDo

[English](README.md) | 中文

这是一个公开的 Codex Skills 仓库。

这个仓库不是记忆仓库，也不是只为某一个 workflow 服务。这里应该只保存可复用的 skill 源码、公开示例、脚本和说明文档。真实飞书文档 URL、OpenID、App ID、token、secret、本机 registry 等运行时私有信息不能进入 Git。

## Skills

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

- 生成 workspace 本地的 `.codex_monitor` 脚手架；
- 写入可配置的 `run_command.sh` 和 `monitor.env`；
- 安装小时报告和最终总结脚本；
- 支持 Codex goal-mode 在最终邮件里区分 `complete`、`blocked` 和 `usageLimited`；
- 也可以只安装全局 Codex `Stop` hook，用于 goal 终态邮件告警，不依赖 workspace 本地 monitor；
- 支持无 sudo 的 systemd user timer；
- SMTP secret 和运行期报告保持不入 Git；
- 对常见邮箱域名自动推断 SMTP host、port 和安全模式，所以通常只需要用户提供发件邮箱、收件邮箱和发件邮箱密钥。

当前局限性：

- workspace-local monitor 只支持 Linux，timer 默认走 `systemd --user`。
- Windows 下只安装全局 goal 终态 `Stop` hook，不部署 workspace 本地 training 或长任务 monitor。
- 全局 goal 终态邮件依赖 Codex `Stop` hook。如果是断电、宿主机崩溃、或者外部直接 kill 导致 Codex 没有正常收尾，这条链路不会触发。
- goal 归档状态属于 best-effort 检测。它依赖 Codex transcript 和本地 state 推断，特殊流程下可能显示为“未检测到”。
- workspace-local monitor 假设任务本身已经有真实可运行的命令、日志或 artifact 目录；它不会替你发明任务逻辑。
- SMTP 仍然依赖邮箱服务商的有效 app password / 授权码。
- 全局 hook 和 workspace-local monitor 是互补关系：前者负责 goal 终态告警，后者负责按小时的日志和产物巡检。

## 安装 Skill

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

- 这个仓库只放可复用 skills，不放项目记忆或对话历史。
- 面向公开用户时使用 HTTPS clone。
- 真实用户配置放在本机 ignored 文件或用户配置目录。
- 不提交 secrets、tokens、飞书/Lark 文档 URL、OpenID、App ID、私有 API endpoint 或真实 registry。

`lark-worklog-archive` 的开发 TODO 在 [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md)。
