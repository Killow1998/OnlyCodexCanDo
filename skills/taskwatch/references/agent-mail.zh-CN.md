# Agent Mail 主动通知

[English](agent-mail.md) | 中文

TaskWatch 支持腾讯 Agent Mail（`agently-cli`）和已有 SMTP 配置。CLI 包名为 `@tencent-qqmail/agently-cli`，安装参考[官方说明](https://agent.qq.com/doc/cli-setup.md)。OAuth 身份和凭据仅保存在发件主机的私有配置中。

## 配置投递

一次确认具体任务或 goals、发件身份、收件人、事件类型及允许发送的内容，后续符合范围的通知复用该授权。进度无变化时保持安静，定时摘要独立选择。

```bash
python3 skills/taskwatch/scripts/agent_mail.py \
  --config ~/.codex/taskwatch.env \
  --recipient receiver@example.com \
  --cli /absolute/path/to/agently-cli --workspace codex
python3 skills/taskwatch/scripts/install_global_hook.py --hook-only
```

默认保留已有配置；只有明确切换且已备份时才使用 `--force`。`AGENTLY_WORKSPACE` 选择已有身份，适配器为后台 PATH 加入 CLI 所在目录，不复制 token。应在真实后台环境验证 CLI 及其同目录 Node 可运行。生成的 Linux monitor 的 `email.env` 也可使用同一配置命令。

默认 `MAIL_CONTENT=brief` 只发送状态和证据位置，不附会话或日志正文。`--confirmed` 仅用于上述持续通知授权；安装 CLI 不意味着允许任意发信。

## Goal 通知

Stop hook 根据明确终态证据识别 `complete`、`blocked` 和 `usageLimited`。普通一轮结束不代表 goal 完成。按照[官方 Hooks 文档](https://learn.chatgpt.com/docs/hooks)，在 Codex `/hooks` 审查并信任准确的定义。不要修改内部信任记录；只有观察到目标客户端实际触发后，才能称为已生效。

## 命令退出通知

从选定 workspace 启动实际训练或评测：

```bash
python3 /path/to/taskwatch/scripts/run_with_alert.py \
  --label "Selected training" --state-dir /private/path/taskwatch-runs \
  -- python3 train.py --config experiment.yaml
```

参数直接交给子进程，不经 shell 拼接。监督进程等待真实退出码，再发简短通知，不调用 LLM 或定时轮询。邮件失败不改变任务退出码；零退出码只说明进程正常退出，产物质量仍按任务标准验收。已有运行中的任务不会自动接入；用户主动取消不归类为意外失败。

观察者必须保持运行：监督进程自身被杀、主机关机或整个 cgroup 被终止，需要另行授权的独立观察者。已经停机的主机无法可靠地通知自己的故障。

## 验收与恢复

先验证一次可控成功、失败及重复事件。真实客户端 Hook 触发与直接调用脚本分别验证；邮件服务接受请求与收件箱实际收到也分别确认。

投递前独占创建 `*.delivery.json`，抑制重复或并发发送。CLI 确认后记录 `accepted`，不等于收件箱已收到。发送失败、超时或响应不确定时保留 `pending`，停止自动重试。先核对发件箱，只有确认尚未发送时，才删除该事件的回执并重试，避免服务端已发出但响应丢失时重复告警。

运行状态和回执保存在私有位置。公开示例不包含真实收件人、别名、任务标识、主机清单或凭据。源码检查覆盖打包与离线行为；安装、身份、事件检测、发送接受和实际收信分别验收。
