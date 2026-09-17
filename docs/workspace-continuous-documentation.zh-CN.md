# 渐进式项目记录

[English](workspace-continuous-documentation.md) | 中文

项目不再需要单独安装文档工作流。主机全局 `AGENTS.md` 可以在重要阶段完成时转入全局安装的 [`organized-proj`](../skills/organized-proj/SKILL.md) Skill。只有此时才加载完整流程；Skill 复用项目现有记录，小改动直接跳过。

## 什么是重要阶段

工作产生了可独立检阅的结果、改变了长期设计，或留下了必须跨越当前对话保存的下一步，才进行阶段收尾。命令结束或回复结束本身不算。

## Skill 记录什么

先检查受影响的项目，只更新内容确实变化的权威文档：

- 当前计划或进度记录；
- 稳定设计或接口文档；
- 阶段工作记录或项目已有的等价记录；
- 受影响的用户使用说明。

不要为了匹配本仓库而新建 `docs/active`、`docs/design`、`docs/worklog`、项目 `AGENTS.md` 片段或另一套文档体系。项目已经采用这些路径时继续沿用。按目标记录结果与证据，不复制命令流水和对话原文。

Git 提交、云端归档、发布、远程写入和删除文档仍需要各自对应的授权。本地项目记录已经足以完成阶段收尾。

## 全局部署

配置主机全局 `AGENTS.md` 时，先检查 `organized-proj` 是否已全局安装。未安装时，说明它只负责阶段收尾，并集中询问一次是否从 `skills/organized-proj/` 安装。用户拒绝时，不在 `AGENTS.md` 留下失效的 Skill 引用，改用“按项目现有方式留记录”的通用规则。以后不再逐项目询问。

## 领域参考仍按需读取

[`templates/workspace/`](../templates/workspace/) 下的文件是参考，不再是项目安装项：

- [`experiments.md`](../templates/workspace/experiments.md)：真实实验；
- [`robotics-validation.md`](../templates/workspace/robotics-validation.md)：仿真或真机证据；
- [`ui-conventions.md`](../templates/workspace/ui-conventions.md)：界面工作；
- 项目没有既定记录格式时才参考 worklog 模板。

只读取当前任务相关的参考。只有项目存在无法从现有文件发现的稳定约定时，才新增项目级规则。
