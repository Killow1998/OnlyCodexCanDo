# TaskWatch 使用说明

新部署先看 [Agent Mail 配置与验收](agent-mail.zh-CN.md)。TaskWatch 支持 Agent Mail 和 SMTP。`run_with_alert.py` 为选定命令发送退出通知；全局 Hook 处理 goal 终态，Linux 巡检保留按小时报告。

TaskWatch 有两种部署方式，二者解决的问题不同：

- 全局 goal 终态邮件 hook：在实际客户端触发 Hook、且能识别 Codex goal 的 `complete`、`blocked` 或 `usageLimited` 状态时发送邮件。须在目标客户端验证，不能仅凭操作系统推断可用。
- workspace-local monitor：为 Linux 长任务生成 `.codex_monitor`、按小时巡检报告、最终总结邮件和可选 `systemd --user` timer。只支持 Linux。

Windows 下只使用全局 goal 终态邮件 hook，不部署 workspace-local training 或长任务 monitor。

## 全局 Goal 邮件 Hook

### Codex Desktop App 历史验证记录

截至 2026-06-12，Windows 上已验证：

- 手动调用 `~/.codex/skills/taskwatch/scripts/taskwatch_stop_hook.py` 可以识别 `update_goal` 终态，并通过 `~/.codex/taskwatch.env` 成功发送邮件；
- `~/.codex/config.toml` 中的 `hooks = true` 和 `[[hooks.Stop]]` 配置已存在；
- 在 Codex CLI 中 trust 新 hook 后，Codex Desktop app 内 goal 完成仍没有在 `~/.codex/taskwatch-state/taskwatch-hook-audit.log` 产生新的 `hook_started` 记录；
- 因此，这次测试没有证明 Codex Desktop app 的 `[[hooks.Stop]]` 自动触发可用；它不是对后续版本的结论。

重新部署时先核对[当前官方 Hooks 文档](https://learn.chatgpt.com/docs/hooks)、实际客户端版本和 Hook 信任状态，再验证一次真实终态。普通 `Stop` 只说明一轮结束，不说明 goal 完成。若该客户端没有可靠触发，再评估绑定特定任务的外部监控；不直接编辑内部数据库，不把旧配置示例当作当前能力证明。

安装或刷新全局 hook：

```bash
export TASKWATCH_SENDER_PASSWORD='smtp-app-password'
python skills/taskwatch/scripts/install_global_hook.py \
  --sender-email sender@example.com \
  --recipient-email receiver@example.com
```

优先用 `TASKWATCH_SENDER_PASSWORD` 环境变量传授权码，避免密码进入 shell history 和进程列表；`--sender-password` 仍然可用，且显式传入时优先。

已有 `~/.codex/taskwatch.env` 时，可以只刷新 hook，不覆盖邮件配置：

```bash
python skills/taskwatch/scripts/install_global_hook.py --hook-only
```

`--hook-only` 要求该配置文件已经存在；干净环境必须先提供完整 SMTP 参数。安装器会把 `taskwatch.env` 收紧为 `0600`，把私有 state 目录收紧为 `0700`。

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

默认脚手架写入 workspace 内（`.codex_monitor/` 和 `run_with_monitor.sh`）。如果不希望工程目录出现任何监控文件，加 `--central`：整套脚手架会生成到 `~/.codex/taskwatch/jobs/<systemd-basename>/`，workspace 保持干净，目标目录通过 `monitor.env` 里的 `CODEX_MONITOR_WORKSPACE` 记录。自定义位置用 `--job-dir`。

Goal mode 会同时识别 `thread_goal_updated` 和 `update_goal` 终态。自动发现只有一个候选 transcript 时才采用；多个并发候选会保持 unknown。已知目标 transcript 或 session 时，在 `monitor.env` 设置 `CODEX_MONITOR_GOAL_TRANSCRIPT` 或 `CODEX_MONITOR_SESSION_ID`。

`--primary-log`、`--progress-log` 和 `--artifact-dir` 必须是无空白、无单引号且不含 `..` 的相对路径；这是生成 shell 命令的安全边界。每次 `run_with_monitor.sh` 启动都会清除上一次运行生成的 goal 终态和自动绑定 state，但保留 `monitor.env` 中的显式绑定。

启动任务（central 模式下换成 `~/.codex/taskwatch/jobs/<name>/run_with_monitor.sh`）：

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

## 卸载

卸载 workspace-local monitor（默认保留 `email.env`、reports、snapshots、state；加 `--purge` 一并删除；`systemctl` 可用时会先执行 timer 卸载）：

```bash
python skills/taskwatch/scripts/install.py /abs/workspace --uninstall
```

central 模式的任务用安装时相同的布局参数：

```bash
python skills/taskwatch/scripts/install.py /abs/workspace --central --systemd-basename codex-long-job-monitor --uninstall
```

移除全局 Stop hook（只删 `~/.codex/config.toml` 里的托管 block，保留 `taskwatch.env` 与去重状态；加 `--purge` 一并删除）：

```bash
python skills/taskwatch/scripts/install_global_hook.py --remove
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
- 修改源码后运行 `check.py --skip-global`；同步全局副本、部署 Hook/服务和修改邮件配置分别获得对应授权，保留本机修改。
- 修改邮件模板或 hook 触发逻辑时，必须补充 `tests/test_taskwatch_hook.py` 或 `tests/test_install.py`。
