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

## 安装 Skill

对于 `lark-worklog-archive`，普通用户不需要自己逐条执行安装命令。把下面这段 prompt 交给 Codex 即可：

```text
请帮我安装并配置 lark-worklog-archive Skill，用于把每天通过 Codex/Agent 完成的开发工作归档到飞书工作记录。请使用公开仓库 https://github.com/Killow1998/OnlyCodexCanDo.git 通过 HTTPS 安装；安装或检查 lark-cli；发起一次性飞书用户授权，权限需要覆盖 docs、drive、markdown 和 search:docs:read；我只在网页上完成授权确认。授权后请初始化当前月工作记录文档，运行 doctor 检查，并告诉我以后可以直接说“今日归档”。不要把任何飞书文档 URL、OpenID、App ID、token、secret 或 registry 提交到 Git。
```

给 Codex/Agent 看的安装细节在 [skills/lark-worklog-archive/references/setup.md](skills/lark-worklog-archive/references/setup.md)。

## 仓库规则

- 这个仓库只放可复用 skills，不放项目记忆或对话历史。
- 面向公开用户时使用 HTTPS clone。
- 真实用户配置放在本机 ignored 文件或用户配置目录。
- 不提交 secrets、tokens、飞书/Lark 文档 URL、OpenID、App ID、私有 API endpoint 或真实 registry。

`lark-worklog-archive` 的开发 TODO 在 [skills/lark-worklog-archive/references/todo.md](skills/lark-worklog-archive/references/todo.md)。
