# Workspace 持续文档工作流

[English](workspace-continuous-documentation.md) | 中文

这是一套可选工作流，只解决一个问题：让人或 Agent 中断一段时间后，回到 workspace 仍然知道当前在做什么、设计为什么这样做、之前实际完成了什么。Workspace 所有者必须明确选择它；主机全局部署不会自动安装。

它不是一套复杂的知识管理系统。最小结构只有三个目录：

```text
docs/
├── active/    # 当前正在推进的 spec 和 plan
├── design/    # 稳定的算法、接口和架构设计
└── worklog/   # 已完成阶段的工作记录和 worklog 模板
```

其中最重要的是 `worklog/`。它保存真实完成的工作、验证证据、失败根因和以后还能复用的经验。某条经验如果会长期影响算法、接口或架构，再把它提炼到 `design/`；不需要另外创建一套“经验库”。

项目已有其他目录时可以继续使用，但 `archive/`、`backlog/`、`reviews/`、`runbook/`、`handoff/` 等都不是这套工作流的必选部分。

## 三个目录分别放什么

### `docs/active/`：现在正在做什么

这里只放当前仍在推进的 spec 或 plan。新 Agent 开始较大的任务前，先读这里，就能知道目标、范围、限制、完成标准、当前进度和下一步。

一份实用的 active 文档通常包括：

- 这项工作要解决什么问题；
- 哪些内容在范围内，哪些不在；
- 已经确认的事实和仍需验证的假设；
- 实施步骤或阶段；
- 每个阶段如何验收；
- 当前完成到哪里，下一步是什么。

不要把已经结束的计划长期留在 `active/`。任务完成后，把长期有效的算法和接口设计更新到 `design/`，把实际结果写入 `worklog/`，再按项目原有方式归档或清理这份计划。不要未经授权删除用户原有文档。

### `docs/design/`：系统为什么这样设计

这里保存会长期影响开发的设计，例如：

- 算法原理和状态转换；
- 模块职责与边界；
- 接口、数据格式和错误处理；
- 安全条件和必须保持的约束；
- 重要方案的选择理由。

`design/` 不是每日进度表。只有算法、接口或架构真的发生变化时才更新。当前任务进行到哪一步，仍然写在 `active/`。

### `docs/worklog/`：这次实际做了什么

完成一个有意义的阶段后，新增一份带日期或时间的 worklog。它用于复盘、恢复上下文和沉淀经验，但不是命令流水账。

每份 worklog 按工作目标组织，使用四段：

1. `背景与目标`：为什么做；
2. `工作内容`：采用了什么主要做法；
3. `结果`：完成了什么、如何验证，以及有哪些值得保留的失败根因或经验；
4. `问题与下一步`：还有什么未完成、未验证或有风险。

命令、文件、commit、测试和日志路径可以作为证据，但不要成为正文结构。没有验证的事情必须明确写成“未验证”。模板见 [worklog-template.zh-CN.md](../templates/workspace/worklog-template.zh-CN.md)。部署到项目时，建议保存为 `docs/worklog/worklog-template.md`。

## 一次开发任务怎样走完

```text
开始任务
  -> 读取项目 AGENTS.md
  -> 读取 docs/active/ 中相关的当前计划
  -> 按需读取 docs/design/ 中相关设计
  -> 实施和验证
  -> 必要时更新 active 计划和 design 设计
  -> 完成一个阶段后写入 docs/worklog/
  -> 任务完成后清出不再活跃的 active 计划
```

具体操作：

1. **开始前**：先确认当前任务是否已有 active 文档。没有且任务较大时，创建一份 spec 或 plan；小改动不必为了流程强行建文件。
2. **开发中**：只有范围、方案、进度或下一步发生实质变化时才更新 active 文档，不要求每改一行代码就写文档。
3. **设计改变时**：把长期有效的算法、接口和架构变化写入 design 文档，不要只留在对话或 worklog 中。
4. **阶段完成时**：更新 active 中的完成状态，并按模板写一份 worklog，记录结果、证据和剩余问题。
5. **任务结束时**：确认 design 和 worklog 已接住需要保留的信息，再把已完成计划移出 active。项目已有 archive 就沿用；没有时不要为了这套工作流额外创建 archive 体系。

## 项目 `AGENTS.md` 只负责提醒怎么用

项目 `AGENTS.md` 不复制 spec、design 或 worklog 的内容，只保存稳定规则和入口，例如：

- 较大任务前读取 `docs/active/`；
- 改算法或接口前读取相关 `docs/design/`；
- 阶段结束后按模板写 `docs/worklog/`；
- 不把当前进度和命令日志塞进 `AGENTS.md`。

可合并的规则片段见 [AGENTS.docs-workflow.md](../templates/workspace/AGENTS.docs-workflow.md)。

## 部署到已有 Workspace

不要直接覆盖现有文档。先检查项目已有结构，再做最小映射：

| 需要的功能 | 优先复用 | 没有时建议创建 |
| --- | --- | --- |
| 当前 spec / plan | 现有计划、roadmap、milestone 文档 | `docs/active/` |
| 算法与技术设计 | 现有 architecture、design、spec 文档 | `docs/design/` |
| 阶段工作记录 | 现有 worklog、devlog、progress archive | `docs/worklog/` |

如果现有目录已经承担同样职责，可以继续沿用原路径，只需让项目 `AGENTS.md` 清楚指向它们。不要为了目录名一致而复制一套平行文档。

## 可选 Workspace 模块

持续文档只是一个 Workspace 模块，不是其他模块的前置条件。部署时应先检查项目，只解释相关选项，再让 Workspace 所有者逐项独立选择：

| 模块 | 增加的行为 | 成本或边界 |
| --- | --- | --- |
| [持续文档规则](../templates/workspace/AGENTS.docs-workflow.md)与 [worklog 模板](../templates/workspace/worklog-template.zh-CN.md) | 增加 `active/`、`design/` 和 `worklog/` 的稳定入口。 | 需要维护有意义的计划、设计变化和完成阶段记录；小改动仍不强制写文档。 |
| [实验工作流](../templates/workspace/experiments.md) | 为真实实验记录目标、准确配置、验收或停止条件、结果和经验，并阻止只凭噪声中间信号盲目调参。 | 增加运行前和运行后的记录；可以复用已有实验目录，不依赖三目录流程。 |
| [Robotics 验证](../templates/workspace/robotics-validation.md) | 区分算法、smoke test、仿真和真机证据，并明确坐标系、状态来源、职责和安全边界。 | 只在这些证据层级和系统边界确实适用时加入；仿真不能替代真机证据，也不强制采用实验记录。 |

选择一个模块不会自动选择另一个。Robotics 仓库可以只选 Robotics 验证，不选持续文档；机器学习仓库可以只选实验记录；长期维护的普通应用也可以只选三目录工作流。仓库名和技术检测只能支持推荐，不能代替用户批准。

## 这套工作流刻意不做什么

- 不另建全局状态文件；当前状态直接写在对应的 active spec/plan 中。
- 不要求每个 session 创建交接文件。
- 不要求每次小改动写 worklog。
- 不把 session 原文、命令流水或主机私有信息放进仓库。
- 不强制项目采用 `archive/`、`backlog/`、`reviews/` 或 `runbook/`。
- 不允许以“保持整洁”为理由删除未经确认的用户文档。

这就是完整的持续文档模块：**当前工作看 `active/`，长期设计看 `design/`，实际结果和经验看 `worklog/`。** 实验和 Robotics 模块仍然是分别选择的附加项。
