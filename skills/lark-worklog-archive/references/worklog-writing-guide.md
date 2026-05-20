# Worklog Writing Guide

The worklog is for weekly reports, retrospectives, and future context recovery. It is not a raw command log.

## Default Shape

Group work by meaningful objective. Under each work domain, use these second-level bullets:

- `背景与目标`: why this work mattered and what problem it was meant to solve.
- `工作内容`: the main approach and actions taken.
- `结果`: current outcome, completed state, commits, tests, documents, or environment status.
- `问题与下一步`: unfinished work, risks, blockers, and next actions.

Commands, file paths, test names, commits, and document links are evidence. Include them only when they make the result easier to verify or reopen later.

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
- 飞书 CLI / 工作记录
  - 背景与目标
    - 希望让 Codex 总结每日工作，后续可直接汇总成周报；旧记录过于零散，难以回看动机和进度。
  - 工作内容
    - 将 lark-worklog-archive 的默认记录方式调整为按事项总结，补充写作指南和迁移说明。
  - 结果
    - 新结构改为“背景与目标 / 工作内容 / 结果 / 问题与下一步”，并通过 check.py 验证。
  - 问题与下一步
    - 需要按新指南重写已有旧风格工作内容，减少同日重复碎片。

- Ubuntu 环境
  - 背景与目标
    - 为了在 CLI 中稳定使用 Codex 开发，减少代理缺失导致的 reconnect。
  - 工作内容
    - 整理 Ubuntu 终端和代理相关配置。
  - 结果
    - 环境已基本可用，可继续用真实开发任务验证稳定性。

- RL 环境
  - 背景与目标
    - 为推进科研，需要复现 SeaNav；之前环境混乱，不利于训练和排错。
  - 工作内容
    - 重新整理 RL 依赖和工作区。
  - 结果
    - 当前只完成环境搭建，还没有开始正式复现训练。
  - 问题与下一步
    - 下一步验证数据、训练脚本和 baseline。

- Go2-W 实机开发
  - 背景与目标
    - 希望在 Go2-W 主机上也能使用 Codex 开发，从而直接推进实机任务。
  - 工作内容
    - 配置远程开发和 Codex 使用条件。
  - 结果
    - 初步部署完成，为后续实机开发打基础。
  - 问题与下一步
    - 需要用真实任务验证构建、部署和运行链路。
```
