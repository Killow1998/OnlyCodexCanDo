# Lark Worklog Archive TODO

目标：把 `lark-worklog-archive` 从可用版推进到可分享、可安装、可配置、低 token 消耗的稳定版。所有改动必须继续遵守：公开仓库不保存真实飞书文档 URL、OpenID、App ID、token、secret 或私有 API 地址。

## 2026-05-20 跨平台与重装兼容

- [x] 修复 Windows 下 `archive_worklog.py` 顶层 `fcntl` 导入失败。
  - POSIX 继续用 `fcntl.flock`。
  - Windows 使用 `msvcrt.locking`。
  - 锁文件位置从硬编码 `/tmp` 改为 `tempfile.gettempdir()`。

- [x] 修复 Windows 下 `lark-cli.ps1` 被 PowerShell 执行策略拦截的问题。
  - 主脚本和安装脚本优先解析 `lark-cli.cmd` / `lark-cli.exe`。
  - 支持 `LARK_CLI` 环境变量手动指定 CLI 路径。
  - `run_lark()` 显式用 UTF-8 解码，避免 GBK 默认代码页导致中文 JSON 解码失败。

- [x] 修复已有文档搜索命中但仍创建新文档的问题。
  - 飞书搜索结果可能把标题放在外层 `title_highlighted`，URL 放在内层 `result_meta.url`。
  - `find_url()` 现在递归查找嵌套 URL/token。
  - `find_doc_by_title()` 增加多种搜索 query fallback。

- [x] 增加重装保护模式。
  - 新增 `--existing-only`，用于重装/恢复场景，只注册已有月度文档，不创建新文档。
  - `--init --existing-only --doc <existing-doc>` 可显式注册用户提供的旧文档。
  - 日常归档也可传 `--existing-only`，找不到已有文档时失败而不是创建。

- [x] 修复 Windows 下 release check 固定 `python3` 失败的问题。
  - `scripts/check.py` 改用 `sys.executable` 调用单测、语法检查、install dry-run 和 skill validate。
  - 子进程设置 `PYTHONUTF8=1`，避免外部 validate 脚本在 Windows 默认 GBK 下读取中文 `SKILL.md` 失败。
  - release check 使用 `python -B` 和内存编译语法检查，避免自身生成 `__pycache__`。

- [x] 修复坏 category config 让脚本 import 阶段崩溃的问题。
  - 移除 import 阶段加载本机 category config 的行为。
  - `--doctor` 可以诊断坏 JSON 或不可读的 category rules 文件。
  - 归档、预览、分类等正常命令仍在解析参数后加载并应用 category rules。
  - 读取 category rules 时兼容 UTF-8 BOM，避免 Windows PowerShell 写出的 JSON 无法解析。

- [x] 增加发布包缓存目录检查。
  - `scripts/check.py` 现在检查 skill 目录下是否存在 `__pycache__`。
  - 发布/分享前必须保持 skill 目录无缓存目录。

- [x] 修复真实归档后验证过严的问题。
  - `verify_items()` 现在验证去掉显式 `域::子类::` 后的正文。
  - Windows 路径反斜杠 round-trip 可能不同，验证时会归一化连续反斜杠。
  - 缺失报错输出正文而不是带分类前缀的原始参数，方便定位。

- [x] 记录飞书长文档更新的安全方式。
  - Windows PowerShell 下长 Markdown 不要直接塞进命令行参数。
  - 使用当前 workspace 内的相对 `@file`，更新后立即 fetch 验证。
  - 标题敏感文档优先用包含 `<title>...</title>` 的 XML 更新；仅正文里的 `# 标题` 不能证明飞书文档标题已更新。
  - 如果出现 `partial_success` 或 tokenization warning，必须检查文档是否完整。

- [x] 修复 `--normalize-only --date` 真实文档修复风险。
  - 现场验证发现 Markdown `str_replace` 修复某一天时可能破坏日期标题或文档标题。
  - 指定日期修复改为先重组目标日期，再用带 `<title>` 的结构化全文 rewrite 写回。
  - 单测改为要求 `overwrite` 路径并验证目标日期和相邻日期标题仍存在。
  - 修复写回后飞书 Markdown 转义反斜杠和下划线导致 verification 误报失败的问题，改用 section 语义签名比较。

- [x] 增加 Node 版本提示。
  - 现场安装发现 Node `v20.8.0` 会让 `npx @larksuite/cli@latest install` 触发依赖版本和 ESM 加载错误。
  - `scripts/install.py` 会提示低于 `20.12.0` 的 Node 可能需要先升级。

- [x] 更新安装文档。
  - 重装时先检查/复用已有 lark-cli app/config，不要重复 `config init --new`。
  - 授权后先 `--doctor`，再 `--init --existing-only` 注册已有月度文档。
  - Windows 下推荐使用 Windows Terminal 的 PowerShell profile。
  - 增加 Windows PowerShell 的 `lark-cli.cmd`、`$env:LARK_CLI_NO_PROXY` 和 `python` 示例。

## P0 - 明天优先

- [x] 做一个正式安装入口。
  - 提供 `scripts/install.py` 或等价安装脚本。
  - 支持从 public GitHub HTTPS 安装 Skill。
  - 检查 `lark-cli`、Node/npm、Python 版本、Codex skills 目录。
  - 安装后提示用户重启 Codex。
  - 不把本机 registry 或任何私有配置写入仓库。
  - 初版入口：`python skills/lark-worklog-archive/scripts/install.py`。

- [x] 做首次授权向导。
  - 增加 `scripts/doctor.py` 或 `scripts/setup_worklog.py`。
  - 检查 `lark-cli auth status`、缺失 scopes、当前身份是否为 user。
  - 给出最小授权命令和 device-code/no-wait 流程。
  - 自动解释常见错误：权限不足、token 过期、用户未授权、doc 不存在、registry 未配置。
  - 输出必须短，不打印 access token 或完整文档内容。
  - 初版入口：`archive_worklog.py --doctor` 和 `archive_worklog.py --init`；授权命令保留在 `setup.md`。

- [x] 把分类规则改成可配置。
  - 增加公开模板：`references/category-rules.example.json`。
  - 支持本机私有配置：`references/category-rules.local.json` 或 `$HOME/.config/lark-worklog-archive/category-rules.json`。
  - 支持 work domains、subcategories、keyword priority、fallback domain。
  - 当前默认域保留：`飞书 CLI / 工作记录`、`Ubuntu 环境`、`n3mapping`、`RL 环境`、`其他`。
  - 提供命令检查某条 bullet 会被归到哪里。
  - 初版命令：`archive_worklog.py --classify-only --item "..."`，可配 `--category-rules <path>`。

- [x] 写自动测试，而不是只靠脚本级手工验证。
  - 建 `tests/`，覆盖日期解析、section split、旧结构迁移、多级列表解析、分类、去重、XML 输出。
  - 为飞书 CLI 调用做 fake runner，不依赖真实飞书网络。
  - 覆盖 normalize-only、same-day update、new-day insert、registry owner guard。
  - 加一条敏感信息扫描测试，确保 example/config/docs 不含真实 URL、OpenID、App ID、token。
  - 初版测试入口：`python -m unittest discover -s skills/lark-worklog-archive/tests`。

- [x] 设计团队共享 worklog 模式。
  - 明确个人 worklog、团队共享 worklog 两种模式。
  - 团队模式要显式 opt-in，不能误写个人文档。
  - 设计 registry schema：owner、team_id、doc title prefix、allowed users、share policy。
  - 设计跨用户并发策略：revision retry、失败重放、冲突提示、可选操作日志。
  - 初版支持 `mode: team`、`--team`、`--team-id`、`--title-prefix`、`--allow-user-open-id`；团队写入和修复必须显式传 `--team`。

## P1 - 可用性完善

- [x] 增加 `doctor` 命令。
  - 检查 lark-cli 是否安装。
  - 检查 auth 是否有效。
  - 检查 registry 是否存在、是否能解析当前月文档。
  - 检查当前月文档是否可读写。
  - 检查分类规则是否能加载。
  - 给出最短修复命令。
  - 初版只做读取校验；写权限在实际归档时通过 revision update 和最终 verification 校验。

- [x] 增加 `init` 命令。
  - 为新用户创建本机 registry。
  - 搜索或创建当前月文档。
  - 写入一条可选初始化记录。
  - 生成不会进入 Git 的本机配置。

- [x] 增加 `preview` 命令。
  - 只输出本次新增 bullet 的分类结果和目标文档标题。
  - 默认不打印整篇飞书文档。
  - 需要全文 diff 时显式传 `--verbose` 或 `--full-diff`。
  - 初版入口：`archive_worklog.py --preview --item "..."`；全文仍走 `--dry-run`。

- [x] 增加文档修复命令。
  - `normalize-only` 继续保留。
  - 增加 `--date` 指定只修某一天。
  - 增加 `--all-dates` 修整个文档。
  - 增加旧格式迁移报告：哪些顶层分类被移动、哪些条目无法识别。
  - 初版 `--normalize-only --date MM-DD-YYYY` 使用 section replace；`--normalize-only --all-dates` 走全文修复并输出迁移报告。

- [x] 改善安装文档。
  - README 只保留最短安装路径。
  - `setup.md` 拆成首次安装、授权、手动更新、故障排除几个短节。
  - 避免长命令重复，减少 Agent 加载后的上下文成本。
  - 已将 `setup.md` 压缩为安装、授权、日常使用、修复、共享、token 预算、故障排除等短节。

## P2 - Token 消耗控制

- [x] 默认输出继续保持短结果。
  - 成功时只输出文档标题、日期、新增条目数。
  - 不打印完整 doc URL，除非 `--print-doc`。
  - 不打印完整文档内容，除非 `--dry-run`.
  - 当前完整文档定位信息只在显式传 `--print-doc` 时输出。

- [x] 减少 fetch 内容进入 Agent 上下文。
  - 正常归档尽量只让脚本内部处理 JSON。
  - 给 Agent 的最终输出只保留摘要。
  - 对调试输出做截断和脱敏。
  - 当前默认输出不打印全文、doc locator 或原始 JSON；`--doctor`/错误输出会脱敏并截断。

- [x] 优化同日追加路径。
  - 能局部更新当天 section 时不整篇 overwrite。
  - 新日期优先 block insert。
  - 只有结构迁移或冲突恢复时才走全文 rewrite。
  - 已有测试覆盖 same-day `str_replace` 和 new-day `block_insert_after`。

- [x] 增加本地轻量缓存。
  - 缓存当前月 doc id/title/revision 摘要。
  - 缓存只用于减少搜索，不作为覆盖依据。
  - 每次写入前仍 fetch 最新 revision。
  - 初版缓存路径：`$HOME/.cache/lark-worklog-archive/cache.json`，可用 `--no-cache` 禁用。

- [x] 输出 token 预算说明。
  - README 或 setup 中说明普通归档、dry-run、debug 的 token 影响。
  - 明确建议：日常用 helper，不手动 fetch 整篇文档。
  - 已在 `setup.md` 增加 normal archive、preview、doctor、dry-run、manual fetch、print-doc 的 token 影响说明。

## P3 - 质量与安全

- [x] 定义 registry schema version。
  - 为 `monthly-docs.example.json` 增加 `schema_version`。
  - 兼容旧 registry。
  - 提供迁移函数。
  - 当前 `load_registry()` 兼容旧的平铺月度映射，`save_registry()` 写出 `schema_version: 1`。

- [x] 增强隐私保护。
  - 所有日志中脱敏 doc URL、OpenID、App ID。
  - 添加 `--print-doc` 才输出完整文档定位信息。
  - 默认错误提示中只输出 action 和原因，不输出 token。
  - 后续仍可继续扩展更严格的错误分类。

- [x] 增强冲突恢复。
  - 冲突后重新 fetch/merge/retry。
  - 多次失败时输出可重放命令。
  - 可选写入本机 failed queue，下一次归档自动重放。
  - 初版支持 `--queue-failed` 写入 `$HOME/.local/state/lark-worklog-archive/failed-queue.jsonl`；后续同日期归档自动重放，可用 `--no-replay-failed` 跳过。

- [x] 增加 release/check 脚本。
  - 一键运行测试、Skill validate、敏感信息扫描。
  - 检查全局安装版本是否与仓库一致。
  - 检查 README 中 public 安装命令是否可用。
  - 初版入口：`python skills/lark-worklog-archive/scripts/check.py`。

## P4 - 分享与推广

- [x] 等 Skill 基本完善后，写一篇飞书文档用于分享给朋友。
  - 说明这个 Skill 解决什么问题。
  - 说明安装 public GitHub repo 的方式。
  - 说明 lark-cli 安装和用户授权流程。
  - 说明如何创建个人 worklog、如何触发“今日归档”。
  - 说明月度归档、分类规则、多会话/多 PC 行为。
  - 说明隐私边界：公开仓库不保存个人文档 URL 或 token。
  - 说明故障排除：权限不足、找不到文档、分类不对、重复条目、冲突重试。
  - 这篇飞书文档可以作为后续对外介绍页，但不要在 Git 中保存真实文档 URL。
  - 已创建飞书文档：`Codex 飞书工作记录 Skill 使用说明`；真实文档定位信息不写入 Git。

## 明天建议顺序

1. 做最后的 completion audit，确认当前公开仓库、全局安装副本、飞书分享文档和测试状态一致。
