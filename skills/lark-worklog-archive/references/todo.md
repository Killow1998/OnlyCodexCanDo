# Lark Worklog Archive TODO

目标：把 `lark-worklog-archive` 从可用版推进到可分享、可安装、可配置、低 token 消耗的稳定版。所有改动必须继续遵守：公开仓库不保存真实飞书文档 URL、OpenID、App ID、token、secret 或私有 API 地址。

## P0 - 明天优先

- [ ] 做一个正式安装入口。
  - 提供 `scripts/install.py` 或等价安装脚本。
  - 支持从 public GitHub HTTPS 安装 Skill。
  - 检查 `lark-cli`、Node/npm、Python 版本、Codex skills 目录。
  - 安装后提示用户重启 Codex。
  - 不把本机 registry 或任何私有配置写入仓库。

- [ ] 做首次授权向导。
  - 增加 `scripts/doctor.py` 或 `scripts/setup_worklog.py`。
  - 检查 `lark-cli auth status`、缺失 scopes、当前身份是否为 user。
  - 给出最小授权命令和 device-code/no-wait 流程。
  - 自动解释常见错误：权限不足、token 过期、用户未授权、doc 不存在、registry 未配置。
  - 输出必须短，不打印 access token 或完整文档内容。

- [ ] 把分类规则改成可配置。
  - 增加公开模板：`references/category-rules.example.json`。
  - 支持本机私有配置：`references/category-rules.local.json` 或 `$HOME/.config/lark-worklog-archive/category-rules.json`。
  - 支持 work domains、subcategories、keyword priority、fallback domain。
  - 当前默认域保留：`飞书 CLI / 工作记录`、`Ubuntu 环境`、`n3mapping`、`RL 环境`、`其他`。
  - 提供命令检查某条 bullet 会被归到哪里。

- [ ] 写自动测试，而不是只靠脚本级手工验证。
  - 建 `tests/`，覆盖日期解析、section split、旧结构迁移、多级列表解析、分类、去重、XML 输出。
  - 为飞书 CLI 调用做 fake runner，不依赖真实飞书网络。
  - 覆盖 normalize-only、same-day update、new-day insert、registry owner guard。
  - 加一条敏感信息扫描测试，确保 example/config/docs 不含真实 URL、OpenID、App ID、token。

- [ ] 设计团队共享 worklog 模式。
  - 明确个人 worklog、团队共享 worklog 两种模式。
  - 团队模式要显式 opt-in，不能误写个人文档。
  - 设计 registry schema：owner、team_id、doc title prefix、allowed users、share policy。
  - 设计跨用户并发策略：revision retry、失败重放、冲突提示、可选操作日志。

## P1 - 可用性完善

- [ ] 增加 `doctor` 命令。
  - 检查 lark-cli 是否安装。
  - 检查 auth 是否有效。
  - 检查 registry 是否存在、是否能解析当前月文档。
  - 检查当前月文档是否可读写。
  - 检查分类规则是否能加载。
  - 给出最短修复命令。

- [ ] 增加 `init` 命令。
  - 为新用户创建本机 registry。
  - 搜索或创建当前月文档。
  - 写入一条可选初始化记录。
  - 生成不会进入 Git 的本机配置。

- [ ] 增加 `preview` 命令。
  - 只输出本次新增 bullet 的分类结果和目标文档标题。
  - 默认不打印整篇飞书文档。
  - 需要全文 diff 时显式传 `--verbose` 或 `--full-diff`。

- [ ] 增加文档修复命令。
  - `normalize-only` 继续保留。
  - 增加 `--date` 指定只修某一天。
  - 增加 `--all-dates` 修整个文档。
  - 增加旧格式迁移报告：哪些顶层分类被移动、哪些条目无法识别。

- [ ] 改善安装文档。
  - README 只保留最短安装路径。
  - `setup.md` 拆成首次安装、授权、手动更新、故障排除几个短节。
  - 避免长命令重复，减少 Agent 加载后的上下文成本。

## P2 - Token 消耗控制

- [ ] 默认输出继续保持短结果。
  - 成功时只输出文档标题、日期、新增条目数。
  - 不打印完整 doc URL，除非 `--verbose`。
  - 不打印完整文档内容，除非 `--dry-run --full`.

- [ ] 减少 fetch 内容进入 Agent 上下文。
  - 正常归档尽量只让脚本内部处理 JSON。
  - 给 Agent 的最终输出只保留摘要。
  - 对调试输出做截断和脱敏。

- [ ] 优化同日追加路径。
  - 能局部更新当天 section 时不整篇 overwrite。
  - 新日期优先 block insert。
  - 只有结构迁移或冲突恢复时才走全文 rewrite。

- [ ] 增加本地轻量缓存。
  - 缓存当前月 doc id/title/revision 摘要。
  - 缓存只用于减少搜索，不作为覆盖依据。
  - 每次写入前仍 fetch 最新 revision。

- [ ] 输出 token 预算说明。
  - README 或 setup 中说明普通归档、dry-run、debug 的 token 影响。
  - 明确建议：日常用 helper，不手动 fetch 整篇文档。

## P3 - 质量与安全

- [ ] 定义 registry schema version。
  - 为 `monthly-docs.example.json` 增加 `schema_version`。
  - 兼容旧 registry。
  - 提供迁移函数。

- [ ] 增强隐私保护。
  - 所有日志中脱敏 doc URL、OpenID、App ID。
  - 添加 `--print-doc` 才输出完整文档定位信息。
  - 默认错误提示中只输出 action 和原因，不输出 token。

- [ ] 增强冲突恢复。
  - 冲突后重新 fetch/merge/retry。
  - 多次失败时输出可重放命令。
  - 可选写入本机 failed queue，下一次归档自动重放。

- [ ] 增加 release/check 脚本。
  - 一键运行测试、Skill validate、敏感信息扫描。
  - 检查全局安装版本是否与仓库一致。
  - 检查 README 中 public 安装命令是否可用。

## P4 - 分享与推广

- [ ] 等 Skill 基本完善后，写一篇飞书文档用于分享给朋友。
  - 说明这个 Skill 解决什么问题。
  - 说明安装 public GitHub repo 的方式。
  - 说明 lark-cli 安装和用户授权流程。
  - 说明如何创建个人 worklog、如何触发“今日归档”。
  - 说明月度归档、分类规则、多会话/多 PC 行为。
  - 说明隐私边界：公开仓库不保存个人文档 URL 或 token。
  - 说明故障排除：权限不足、找不到文档、分类不对、重复条目、冲突重试。
  - 这篇飞书文档可以作为后续对外介绍页，但不要在 Git 中保存真实文档 URL。

## 明天建议顺序

1. 先补测试框架和 fake lark runner，防止继续改坏归档逻辑。
2. 再做可配置分类规则，把今天硬编码的领域分类迁出脚本。
3. 然后做 `doctor/init/preview` 三个用户入口。
4. 最后整理 README/setup，减少默认加载内容和 token 消耗。
