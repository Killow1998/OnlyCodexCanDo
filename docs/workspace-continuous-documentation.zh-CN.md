# Workspace 持续文档规则逐条解读

[English](workspace-continuous-documentation.md) | 中文

本文解释 [项目 AGENTS 片段](../templates/workspace/AGENTS.docs-workflow.md) 的六条规则，以及 [project-state 模板](../templates/workspace/project-state.md) 中每个字段为什么存在、会怎样影响持续开发。规则编号 `D1` 至 `D6` 与 AGENTS 片段中的 bullet 顺序一一对应。

## 核心概念

### 规范来源（canonical source）

规范来源是某类信息被认可的唯一当前版本。例如接口设计以 `docs/architecture.md` 为准，当前可恢复状态以 `docs/project-state.md` 为准。唯一来源减少多个 `final`、`v2`、handoff 文件互相冲突；其他文档应链接它，而不是复制内容。

### Living project-state

Living project-state 是一个持续原地更新的“项目重启入口”。它只保存当前目标、已验证状态、下一安全动作和未决风险，不承担完整历史。完成内容归档后从 living state 精简出去，因此它始终短而当前。

### 耐久知识

耐久知识是在会话结束后仍值得保留的内容，例如架构决策、失败边界、兼容契约、可靠验证方法和用户纠正的规则。命令流水、临时日志和已经失效的中间猜测通常不是耐久知识。

### Verified state

Verified state 是最近一次由代码、测试、构建、真实界面、硬件或其他直接证据确认的项目状态。它必须注明验证方法和时间，避免下一次会话把旧结论误当作当前事实。

### Next safe action

Next safe action 是在当前证据和风险边界下，下一个可以安全执行的具体动作，同时包含前置条件和执行后的验证方法。它让下一个 Agent 能继续推进，而不是重新探索或盲目重跑危险命令。

### Worklog、changelog 与 handoff

- Worklog 记录完成阶段的目标、决策、结果和问题，服务人类回顾。
- Changelog 记录面向版本或用户的变化。
- Handoff 是交给明确接收者的临时交接物，不是永久知识库。

Handoff 中有长期价值的信息应并入 project-state、架构、决策或 worklog，然后关闭任务创建的临时文件。

## AGENTS 规则：D1-D6

| ID | 规则含义 | 对开发的影响 |
| --- | --- | --- |
| D1 | 非平凡工作前读取 project-state 以及它指向的架构、决策、验证和 worklog。 | Agent 从项目已知事实继续，减少重复探索、冲突实现和忘记历史失败；小任务不强制加载所有文档。 |
| D2 | 项目 `AGENTS.md` 只保存稳定规则和文档路由，不保存任务状态、命令流水或主机状态。 | 指令文件保持小而长期有效，启动上下文不会被过期进度和机器噪声污染。 |
| D3 | 完成有意义阶段或上下文可能丢失前，更新耐久决策、verified state、验收证据、next safe action 和风险。 | 中断后能从可信状态恢复；只在状态跃迁时记录，避免每个小改动都拖慢敏捷开发。 |
| D4 | 优先一个 living project-state；临时 handoff 必须有接收者和关闭计划，吸收后合并并清理。 | 防止 handoff 无限堆积和多个状态文件互相矛盾，同时保留真实交接能力。 |
| D5 | 复用项目已有 worklog、changelog、架构记录和命名，不创建平行体系。 | 降低维护成本和信息分叉；模板会适配项目，而不是让项目适配模板。 |
| D6 | 结束前检查引用路径、整理任务笔记、保护用户文档并保持 workspace 整洁。 | 避免死链接、临时草稿和无主文件进入长期代码库，但不会借“整洁”删除未知价值资料。 |

## Project State 字段：S1-S7

| ID | 字段 | 概念与开发影响 |
| --- | --- | --- |
| S1 | `Last verified` | 记录状态最后被直接证据确认的日期，而不是最后编辑日期。过旧时提醒 Agent 重新验证。 |
| S2 | `Scope and Current Goal` | 定义项目范围、当前目标和真实验收信号，防止下一会话把局部任务扩展成整个项目重构。 |
| S3 | `Verified State` | 记录已确认事实、工作路径、相关分支/版本/环境和验证方法，让恢复基于证据而非会话记忆。 |
| S4 | `Decisions` | 保存决定、理由、被拒方案及兼容边界，减少后来重复争论或无意推翻已有架构。 |
| S5 | `Next Safe Action` | 给出下一动作、前置条件和事后验证，使交接可以直接推进且不会盲目重放可能有副作用的操作。 |
| S6 | `Open Risks and Unknowns` | 明确未验证假设、影响和解决方法，防止不确定性被隐藏成“已完成”。 |
| S7 | `Durable History` | 指向已有 worklog、changelog 或决策记录，并从 living state 移走已完成细节，保持当前入口简洁。 |

## 对开发节奏的影响

持续文档不是每次保存代码都写报告。推荐触发点是：架构或兼容决策形成、真实验收结果改变、发现重要失败边界、完成一个有意义阶段，或者上下文即将压缩/交接。低风险小改动只需保证现有状态没有被文档错误描述。

它可以独立于主机全局 AGENTS 部署。与全局规则同时使用时，全局层决定 Agent 的通用行为，workspace 规则提供当前项目知识；关键项目规则必须留在仓库中，不能假设所有协作者拥有相同的全局文件。

主机规则逐条解读见[主机全局 AGENTS 逐条解读](global-agents.zh-CN.md)。
