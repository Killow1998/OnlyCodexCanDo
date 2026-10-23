# 后端与算法

后端服务、编译型工程或算法开发时读取。

## 快速迭代

- 把修改到看见结果的耗时作为开发指标。复用或补齐能独立运行的短验证入口。
- 编译型工程启用项目支持的并行构建与编译缓存。沿用实际构建入口，选择其支持的生成器与 ccache 等缓存工具。
- 保留构建目录和缓存，增量构建受影响目标及依赖。全量清理重建用于构建故障诊断或项目要求的发布验证。
- 区分开发与发布配置，把一次性环境准备移出日常构建。修正意外覆盖开发配置的优化参数。
- 拆分构建目标，减少公共头文件引起的无关重编。切换 CMake 生成器使用独立构建目录。
- 将频繁调整的参数和实验编排移出编译过程。为算法实验提供离线回放或独立入口，跳过无关界面与服务启动。
- 用脚本或现有接口加速策略实验，正式算法保留一套权威实现。原型与正式核心用相同输入对照结果。
- 专门的构建或性能提速改造，用代表性任务对比前后耗时与结果一致性。

### CMake 与 ROS 构建入口

| 项目入口 | 定向构建 | 依赖处理 |
| --- | --- | --- |
| 普通 CMake | `cmake --build <build-dir> --target <target>` | 使用该构建树内的目标依赖关系。 |
| ROS 1 的 catkin_tools | `catkin build <pkg>` | 默认构建指定包及其工作区依赖；依赖已构建且未受影响时可加 `--no-deps`。 |
| ROS 2 的 colcon | `colcon build --symlink-install --packages-up-to <pkg>` | 包含指定包及其工作区依赖；依赖已就绪且未受影响时用 `colcon build --symlink-install --packages-select <pkg>`。 |

- ROS 工作区使用原有的 catkin 或 colcon 入口，保留 profile、构建与 devel/install 布局。用构建工具的 CMake 参数入口配置编译缓存；Ninja 按该工具的支持情况选用。
- 公共头文件、消息、服务或包接口变化时，把受影响的下游包纳入构建与验证。
- 构建前确认底层 ROS 环境（underlay）；运行验证时加载本次构建生成的工作区 setup，确认使用的是目标工作区产物。
- colcon 默认启用 `--symlink-install`，减少文件复制与部分脚本修改后的重复安装；C++ 源码修改仍需编译。

## 日志先行

- 设计核心行为时同步设计日志，记录关键状态、失败上下文、耗时与关联标识。
- 采用现有或成熟日志库。凭据不进日志，高频原始载荷改记摘要。
- 高频路径使用有界异步缓冲、批量写入和聚合采样。重要错误及时刷新，缓冲溢出记录丢弃数量。
- 按事件或适当间隔读取日志。
- 每个服务实例的本地日志默认总限额 **100 MB（100,000,000 字节）**，包含当前及轮转文件。通过可配置的轮转与保留策略跨重启约束总量。

## 接口与模块

- 前后端仅通过明确接口交互，各自管理内部实现与状态。权限、校验和业务规则由后端负责。
- 优先深模块：用小接口封装复杂行为，让修改集中在所属模块；外部依赖通过适配器接入，以便独立运行和验证。
- 明确请求、响应、错误与兼容约定。共享契约或生成客户端，不让调用方依赖内部实现或直接访问后端数据库。

参考：[CMake 按目标构建](https://cmake.org/cmake/help/latest/manual/cmake.1.html#build-a-project)、[catkin build](https://catkin-tools.readthedocs.io/en/stable/verbs/catkin_build.html)、[colcon 包选择](https://colcon.readthedocs.io/en/released/reference/package-selection-arguments.html)、[colcon 构建参数](https://colcon.readthedocs.io/en/main/reference/verb/build.html)、[工作区环境](https://colcon.readthedocs.io/en/main/user/quick-start.html)、[ccache](https://ccache.dev/manual/latest.html)、[深模块](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md)。
