# Simplify Codebase 评测

[English](simplify-codebase-evaluation.md) | 中文

## 样本与边界

- 样本：[`devxsameer/blog-api`](https://github.com/devxsameer/blog-api)，固定在 `72f22d3ee2be`（2026-01-20）。
- 选择原因：仓库明确自称“有意过度工程化”，同时又包含真实的认证、授权、数据库、事务和 API 边界。
- 规模：排除 lockfile 与生成的 Drizzle metadata 后，共 109 个文件、5,154 行维护文本；生产 TypeScript 为 85 个文件、3,814 行。
- 行为边界：保留 API 行为、token 长度与 SHA-256 digest、错误到状态码的映射、数据库事务、认证安全措施和公开路由契约。未授权依赖、schema 或产品行为变化。

修改后的副本只留在本机，没有 commit 或发布到样本仓库。

## 一轮有边界的精简

Skill 只实施了高置信度候选：

- 复用已有随机 token 与 SHA-256 实现，并显式传入字节长度，删除一份重复的邮件 token 工具模块；
- 让 tag 查询绕过只做转发的 service 函数，同时保留承担真实业务逻辑的 tag 归一化；
- 合并重复的 API error 响应分支；
- 删除未使用的 error 状态、数据库错误字段、path 初始化、import 和 callback 名称；
- controller/service/repository 仍承担授权、事务、聚合或持久化责任时予以保留。

没有删除认证 hash。密码 hash 保护存储凭据；refresh/email token hash 能降低数据库泄露后被直接重放的风险。类型、Git 和普通测试不能提供这些安全属性。

## 量化结果

| 指标 | 精简前 | 精简后 | 变化 |
| --- | ---: | ---: | ---: |
| TypeScript 文件 | 85 | 84 | -1 |
| TypeScript 物理行 | 3,814 | 3,768 | -46（-1.2%） |
| TypeScript 非空行 | 3,259 | 3,218 | -41 |
| 分支关键词（`if`、`else`、`switch`、`case`、`catch`、`for`、`while`） | 98 | 97 | -1 |
| 依赖 | 不变 | 不变 | 0 |

压缩比例不大本身就是结果：Skill 删除了能证明的重复与间接层后及时停止，没有为了更好看的比例而压平安全和持久化边界。

## 验证与限制

已通过：

- TypeScript build 与 `--noUnusedLocals --noUnusedParameters`；
- 编译后行为检查：refresh token 为 128 个十六进制字符、email token 为 64 个字符、SHA-256 输出不变；
- 编译后边界检查：validation、已知 API error、PostgreSQL uniqueness 和未知错误分别保持 400/404/409/500；
- `git diff --check` 与最终 diff 审查。

仓库的 12 个 Vitest 集成测试只有在沙箱外才能启动，随后都因为没有 PostgreSQL 测试数据库而停在 database setup。因此本评测不声称全量集成测试通过。后续应在一次性 PostgreSQL 实例上复跑同一 patch，并增加一个确实含无意义 hash 或 gate 的独立样本；本轮证明的是 Skill 会在真实安全边界保留 hash，而不是已经证明它删掉了无意义 hash。

## 由评测得到的规则调整

- 代码长度和圈复杂度是筛选信号，不是全局硬 gate。
- 单一路径上的 interface、factory、adapter、provider、registry、strategy 和 manager，需要真实的第二个消费者或明确边界才能成立。
- 只实现要求的行为；不要顺手增加相邻功能，也不要在代码或 PR 文案中保留对无关省略项的解释。
- 只汇报真正影响决策的拒绝候选；清理报告不应变成“本来就没要求做什么”的清单。
