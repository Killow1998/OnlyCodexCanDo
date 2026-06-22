# TaskWatch 使用说明

TaskWatch 有两种部署方式，二者解决的问题不同：

- 全局 goal 终态邮件 hook：在 Codex goal 进入 `complete`、`blocked` 或 `usageLimited` 时发送邮件。Windows 和 Linux 都可用。
- workspace-local monitor：为 Linux 长任务生成 `.codex_monitor`、按小时巡检报告、最终总结邮件和可选 `systemd --user` timer。只支持 Linux。

Windows 下只使用全局 goal 终态邮件 hook，不部署 workspace-local training 或长任务 monitor。

## 全局 Goal 邮件 Hook

### Codex Desktop App 当前限制

截至 2026-06-12，Windows 上已验证：

- 手动调用 `~/.codex/skills/taskwatch/scripts/taskwatch_stop_hook.py` 可以识别 `update_goal` 终态，并通过 `~/.codex/taskwatch.env` 成功发送邮件；
- `~/.codex/config.toml` 中的 `hooks = true` 和 `[[hooks.Stop]]` 配置已存在；
- 在 Codex CLI 中 trust 新 hook 后，Codex Desktop app 内 goal 完成仍没有在 `~/.codex/taskwatch-state/taskwatch-hook-audit.log` 产生新的 `hook_started` 记录；
- 因此，当前不能把 Codex Desktop app 的 goal 完成邮件依赖在 `[[hooks.Stop]]` 自动触发上。

Desktop app 下需要 goal 完成邮件时，优先继续验证或改接 Desktop 实际会触发的机制，例如 `notify = [..., "turn-ended"]` 或外部 transcript/state watcher。`Stop` hook 仍可保留给 CLI 或手动 smoke test。

安装或刷新全局 hook：

```bash
python skills/taskwatch/scripts/install_global_hook.py \
  --sender-email sender@example.com \
  --recipient-email receiver@example.com \
  --sender-password 'smtp-app-password'
```

已有 `~/.codex/taskwatch.env` 时，可以只刷新 hook，不覆盖邮件配置：

```bash
python skills/taskwatch/scripts/install_global_hook.py --hook-only
```

安装后会写入：

- `~/.codex/config.toml`：托管的 `Stop` hook block；
- `~/.codex/taskwatch.env`：SMTP 配置；
- `~/.codex/taskwatch-state/`：发送去重状态。
- `~/.codex/taskwatch-state/taskwatch-hook-audit.log`：hook 调起、终态识别、去重和发送结果审计日志。

邮件触发条件：

- Codex 正常触发 `Stop` hook；
- transcript 中能识别 goal 终态；
- `~/.codex/taskwatch.env` 存在且 SMTP 配置有效；
- 同一个 `session_id + status + updated_at + turn_id + source` 没有发送过。

目前识别两类 goal 终态来源：

- `thread_goal_updated` 事件；
- `update_goal` 工具输出中的 `goal.status`。

`usageLimited` 还会通过末次消息或 transcript 尾部的额度提示做兜底识别。

## 邮件内容

邮件主题格式：

```text
[TW:DONE][<duration>] <任务名>
[TW:BLOCKED][NEEDS-ACTION] <任务名>
[TW:LIMITED] <任务名>
```

正文包含：

- 一眼结论：状态、任务、结果、是否需要介入；
- 本次产出：git 分支、最新提交、未提交文件数、diff stat、测试/构建信号、归档状态、耗时；
- Codex 最后结论：清洗后的最后 assistant digest，优先来自 hook payload，其次来自 transcript；
- 后续处理：complete / blocked / usageLimited 的简短处理建议；
- Debug：session_id、turn_id、cwd、transcript、事件来源和时间戳。

hook 只做确定性、快速、只读的信息抽取，不调用 LLM 二次总结。git 信息使用短超时命令读取；不是 git 仓库或读取失败时静默跳过。digest 会过滤代码块、JSON、命令参数和明显日志噪声。

`duration` / `耗时` 的计算优先级：

1. `update_goal` 或 goal event 中的 `timeUsedSeconds`；
2. goal 的 `createdAt` 到 `updatedAt`；
3. transcript 开始时间到 goal 结束时间。

第三种只是兜底，可能包含当前线程中早于本 goal 的时间。

## Linux Workspace-Local Monitor

workspace-local monitor 用于训练、评测、批处理等真正长时间运行的 Linux 任务。安装前应先确认真实任务命令、日志、artifact 目录和可选 user service。

示例：

```bash
python skills/taskwatch/scripts/install.py /abs/workspace \
  --label "Run Label" \
  --systemd-basename codex-long-job-monitor \
  --job-service optional.service \
  --primary-log outputs/run.log \
  --progress-log outputs/hourly_monitor.log \
  --artifact-dir logs \
  --artifact-dir outputs \
  --process-grep 'train.py|torchrun|python -m yourpkg|codex exec' \
  --goal-mode \
  --run-command 'python3 -B scripts/run.py --arg value'
```

启动任务：

```bash
./run_with_monitor.sh
```

手动生成一次巡检报告：

```bash
CODEX_MONITOR_SKIP_EMAIL=1 .codex_monitor/scripts/hourly_check.sh
```

安装或移除 timer：

```bash
.codex_monitor/scripts/install_systemd_timer.sh
.codex_monitor/scripts/uninstall_systemd_timer.sh
```

## 验证

仓库内检查：

```bash
python -B skills/taskwatch/scripts/check.py
```

只检查源码，不比较全局安装副本：

```bash
python -B skills/taskwatch/scripts/check.py --skip-global
```

全局 hook smoke test 应使用一个包含终态事件的临时 transcript，并把 payload 通过 stdin 传给：

```bash
python -B ~/.codex/skills/taskwatch/scripts/taskwatch_stop_hook.py
```

测试真实 SMTP 时，确认 `~/.codex/taskwatch-state/` 出现新的 state JSON，且 stderr 没有 `taskwatch: failed to send goal email`。

## 故障排查

- 没收到邮件：检查 `~/.codex/config.toml` 是否有 TaskWatch managed `Stop` hook block，并确认 `hooks = true`。
- hook 是否被 Codex 调起：检查 `~/.codex/taskwatch-state/taskwatch-hook-audit.log` 是否出现新的 `hook_started` 记录。
- hook 调起但没发送：根据审计日志里的 `no_transcript`、`no_terminal_event`、`dedup_skip`、`config_error`、`send_failure` 或 `send_success` 定位。
- 没收到邮件但 hook 已安装：检查 transcript 中是否有 `thread_goal_updated` 或 `update_goal` 输出。
- 重复运行不再发：这是去重状态生效；删除对应 `~/.codex/taskwatch-state/*.json` 后才会重发同一终态。
- SMTP 失败：检查 `SMTP_HOST`、`SMTP_PORT`、`SMTP_SECURITY`、授权码和发件邮箱是否匹配。
- Windows 下 workspace-local installer 报错：这是预期行为；Windows 只安装全局 goal hook。
- Linux 下没有 hourly report：检查 `systemd --user`、timer 状态、`CODEX_MONITOR_CODEX_BIN` 和任务日志路径。

## 维护规则

- 不要把 `taskwatch.env`、SMTP 密码、运行报告、state 文件提交到 Git。
- 修改 repo 内 `skills/taskwatch` 后，要同步全局安装副本 `~/.codex/skills/taskwatch`。
- 修改邮件模板或 hook 触发逻辑时，必须补充 `tests/test_taskwatch_hook.py` 或 `tests/test_install.py`。
