# 主机全局 AGENTS 指南

[English](global-agents.md) | 中文

[最小核心](../templates/AGENTS.global.md)刻意保持简短，只保留能阻止范围漂移、未经授权的损失、重复犯错、凭空猜测、过度验证或阶段结果丢失的规则。

## 核心行为

- 用第一性原理、奥卡姆剃刀和苏格拉底提问判断。
- 只修改授权范围，判断前先检查项目现状。
- 大改前说明范围，被纠正后检查同类问题；改变外部状态或难以撤销的动作需要对应授权。
- 测试可观察行为，证据足够即止。
- 重要阶段完成后，只在获准时提交，否则把结果保存在项目现有记录中。

核心不规定 Shell、操作系统、目录结构或固定测试仪式。

## 渐进式项目记录

阶段记录通过 [`organized-proj`](../skills/organized-proj/SKILL.md) 渐进加载。全局文件只保存触发条件；完整收尾流程留在 Skill 中，只有重要阶段完成时才读取。Skill 复用项目现有文档，小改动直接跳过。

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
| [协作称呼](../templates/optional/collaboration-names.md) | 使用私有的用户称呼和 Agent 昵称。 |
| [仅在明确要求时使用子 Agent](../templates/optional/subagent-context.md) | 用户未授权当前任务或范围时不委派。 |
| [默认不使用 Git worktree](../templates/optional/no-worktrees.md) | 除非用户要求，否则留在当前 checkout。 |
| [记录时区](../templates/optional/timezone.md) | Agent 创建的记录使用选定 IANA 时区。 |
| [仓库安全](../templates/optional/repository-safety.md) | 增加 Git 与无关工作保护。 |
| [UI 验证](../templates/optional/ui-verification.md) | 不写 UI 单元测试，视觉验收交给用户。 |

个人称呼和已填写的主机参数不进入公共模板。

## 部署

先检查现有全局文件，删除过时或重复规则，写入前展示最终文本。只询问尚未决定的选项。备份旧文件后，一次写入选定核心与选项并读回验证。主机部署不授权修改项目、远程写入、提交或发布。

多主机比较时，分别比较核心和已选选项。无法访问的主机保持“未核实”；主机清单和私有路径不进入本仓库。
