# 主机全局 AGENTS 指南

[English](global-agents.md) | 中文

[最小核心](../templates/AGENTS.global.md)简短保留跨任务的判断、主动执行、授权边界与阶段记录。

## 渐进式项目记录

全局文件将项目重要阶段及明确的文档整理、交接请求转入 [`organized-proj`](../skills/organized-proj/SKILL.md)，需要时才加载完整流程。

配置全局文件时：

1. 检查 `organized-proj` 是否已全局安装。
2. 未安装时说明行为，并集中询问一次是否从本仓库安装。
3. 用户拒绝时不写入 Skill 引用，改用更新项目现有记录的通用规则。
4. 以后不再逐项目询问，也不自动安装项目文档目录。

详见[渐进式项目记录](workspace-continuous-documentation.zh-CN.md)。

## 可选主机偏好

只添加用户实际选择的偏好：

| 模块 | 行为 |
| --- | --- |
| [中文优先](../templates/optional/chinese-first.md) | 中文交流和说明，技术标识保留原文。 |
| [协作称呼](../templates/optional/collaboration-names.md) | 设置私有称呼，以协作开头鼓励独立判断。 |
| [仅在明确要求时使用子 Agent](../templates/optional/subagent-context.md) | 用户未授权当前任务或范围时不委派。 |
| [默认不使用 Git worktree](../templates/optional/no-worktrees.md) | 除非用户要求，否则留在当前 checkout。 |
| [记录时区](../templates/optional/timezone.md) | Agent 创建的记录使用选定 IANA 时区。 |
| [仓库安全](../templates/optional/repository-safety.md) | 增加 Git 与无关工作保护。 |
| [UI 验证](../templates/optional/ui-verification.md) | 不写 UI 单元测试，视觉验收交给用户。 |

选用后，按用户选定的语言，将称呼说明放在首句，协作开头紧随其后。称呼是对话偏好，不作为项目署名。个人称呼和已填写的主机参数不进入公共模板。

## 按需开发规范

以下可选规范使用普通 Markdown 文件；配置全局入口时选择一次，无需逐项目安装，也不新增 Skill。

| 规范 | 读取时机 | 内容 |
| --- | --- | --- |
| [编码与 lint](../templates/optional/lint-toolchains.zh-CN.md) | 编写或修改代码 | 单一职责、可检索命名、禁止代码注释与项目 lint；默认使用 clang-tidy/clang-format、Ruff、Clippy/rustfmt。 |
| [后端](../templates/optional/guides/backend.zh-CN.md) | 后端或编译型算法开发 | CMake/catkin/colcon 快速迭代、诊断日志限额、接口独立。 |
| [前端](../templates/optional/guides/frontend.zh-CN.md) | 设计或修改界面 | 信息层级、克制表达、交互与人的视觉验收。 |
| [审阅、提交与推送](../templates/optional/guides/git.zh-CN.md) | 代码收尾、审阅、提交或推送 | “收尾推送”先执行完整代码简化再发布；普通 Git 操作跳过简化。 |

只把选定语言的所选规范复制到实际全局 `AGENTS.md` 同目录下的 `guides/`，统一命名为 `code.md`、`backend.md`、`frontend.md`、`git.md`。选定的 `lint-toolchains.md` 或 `lint-toolchains.zh-CN.md` 安装为 `code.md`；其他中文规范同样改为上述统一名称。更新时保留本地修改。采用规范时先检查项目现有约定。

全局文件只需一条入口，列出已选规范：

```markdown
- 按任务读取本文件同目录规范：编码→`guides/code.md`；后端或算法→`guides/backend.md`；界面→`guides/frontend.md`；审阅、简化或 Git→`guides/git.md`。
```

只保留指向已安装规范的引用。这是要求 Agent 按条件主动读文件，不应假定 `@file.md` 自带条件加载功能；规范正文不复制进常驻核心。`templates/workspace/` 下的领域参考仍按需选用，避免重复安装内容重叠的 UI 规则。

选用 `simplify-codebase` 时，若尚未安装，集中提供一次安装选项。Git 规范优先使用已安装的 Skill，未安装时也能直接执行。详见[安装提示词](../README.zh-CN.md#simplify-codebase)。

采用 `code.md` 后，将选定的编码和 lint 规则移出常驻全局文件；代码任务仍会读取，普通查询无需加载。

## 简洁、坦诚地表达

选择此偏好时，替换原有报告规则，不另加同义条目：

> 自然直接、术语一致，结论先行，按需保留依据与明细；事实与未知直说，推论标注“推测”并简述依据；仅说明影响判断的限制，避免重复；即时消息句末不加句号

公共模板使用通用的推论标记；个人配置可使用用户选定的助手昵称。句末标点偏好独立选择，仅用于即时消息。

[ASD-STE100](https://www.asd-ste100.org/STE_faq.html) 可作为术语一致、主体明确和句意清楚的参考。

## 部署

按含义整合核心与已选偏好：合并重复内容，保留授权边界和读取条件。默认采用简短开头和紧凑列表，用户另有格式偏好时从其选择。省略模块标题、解释和示例；时区与规范入口各用一句。条件性流程留在链接指向的规范或 Skill 中。

先检查现有全局文件，删除过时或重复规则，写入前展示最终文本。只询问尚未决定的选项。备份旧文件后，一次写入选定核心与选项并读回验证。主机部署不授权修改项目、远程写入、提交或发布。

多主机比较时，分别比较核心和已选选项。无法访问的主机保持“未核实”；主机清单和私有路径不进入本仓库。
