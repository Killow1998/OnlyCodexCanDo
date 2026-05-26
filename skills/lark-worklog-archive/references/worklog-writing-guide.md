# Worklog Writing Guide

The worklog is for weekly reports, retrospectives, and future context recovery. It is not a raw command log.

## Default Shape

Group work by meaningful objective. Under each work domain, use these second-level bullets:

- `背景与目标`: why this work mattered and what problem it was meant to solve.
- `工作内容`: the main approach and actions taken.
- `结果`: current outcome, completed state, commits, tests, documents, or environment status.
- `问题与下一步`: unfinished work, risks, blockers, and next actions.

Commands, file paths, test names, commits, and document links are evidence. Include them only when they make the result easier to verify or reopen later.

Choose domains and decide whether items should be merged in the agent summary, not in the helper script. Domain names should come from the actual work context. Examples include `工作记录 / 知识管理`, `Agent 工具 / 自动化`, `开发环境 / 系统配置`, `仿真 / 训练`, and `实机 / 硬件部署`, but these are examples rather than a closed taxonomy. The helper preserves the structured domains it receives and does not infer domains from keywords.

## Avoid

- Listing every command, file, and small fix as separate work items.
- Splitting one objective into `代码与仓库`, `验证与测试`, `开发环境`, and `问题与风险`.
- Using `其他` when a real project or environment domain is known.
- Appending duplicate old-style fragments to a day that already needs summarization.

## Migrating Old Entries

When touching an old-style daily section, prefer rewriting that day into the new shape instead of appending more fragments.

Map old sections like this:

- `代码与仓库` -> `结果`, unless the content describes an active implementation step.
- `验证与测试` -> `结果`.
- `开发环境` -> `工作内容` or `结果`, depending on whether it describes setup work or completed environment state.
- `问题与风险` -> `问题与下一步`.

Preserve useful evidence, but compress repeated commands and file lists into concise result bullets.

## Examples

```markdown
- 工作记录 / 知识管理
  - 背景与目标
    - 希望让 Codex 总结每日工作，后续可直接汇总成周报；旧记录过于零散，难以回看动机和进度。
  - 工作内容
    - 将 lark-worklog-archive 的默认记录方式调整为按事项总结，补充写作指南和迁移说明。
  - 结果
    - 新结构改为“背景与目标 / 工作内容 / 结果 / 问题与下一步”，并通过 check.py 验证。
  - 问题与下一步
    - 需要按新指南重写已有旧风格工作内容，减少同日重复碎片。

- 开发环境 / 系统配置
  - 背景与目标
    - 为了在 CLI 中稳定使用 Codex 开发，减少代理缺失导致的 reconnect。
  - 工作内容
    - 整理 Ubuntu 终端和代理相关配置。
  - 结果
    - 环境已基本可用，可继续用真实开发任务验证稳定性。

- Agent 工具 / 自动化
  - 背景与目标
    - 为了减少长任务盯守成本，需要把监控和通知流程做成可复用 agent skill。
  - 工作内容
    - 调整 skill 安装、检查和全局同步流程，统一终态邮件字段。
  - 结果
    - 本地和全局 skill 副本一致，check.py 通过。

- 仿真 / 训练
  - 背景与目标
    - 为推进实验，需要复现仿真训练流程；之前环境混乱，不利于训练和排错。
  - 工作内容
    - 重新整理 RL 依赖和工作区。
  - 结果
    - 当前只完成环境搭建，还没有开始正式复现训练。
  - 问题与下一步
    - 下一步验证数据、训练脚本和 baseline。

- 实机 / 硬件部署
  - 背景与目标
    - 希望在目标设备上也能使用 agent 辅助开发，从而直接推进实机任务。
  - 工作内容
    - 配置远程开发和 Codex 使用条件。
  - 结果
    - 初步部署完成，为后续硬件联调打基础。
  - 问题与下一步
    - 需要用真实任务验证构建、部署和运行链路。
```
