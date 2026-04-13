# 路线图

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## 范围

这个路线图只描述 `project-assistant` skill 自身的演进，不替代 `.codex/status.md` 中的当前执行状态。

详细执行队列看这里：

- [project-assistant/development-plan.zh-CN.md](reference/project-assistant/development-plan.zh-CN.md)

## 当前 / 下一步 / 更后面

| 时间层级 | 重点 | 退出信号 |
| --- | --- | --- |
| 当前 | 收口首版快升级版的默认开发顺序：`daemon core -> VS Code host shell -> resume bridge -> local workspace validation`，让你可以直接按 roadmap / plan 点名开工 | 首版宿主、实现顺序、resume 能力级别和本地验证边界已经清楚到可以逐刀实现 |
| 下一步 | 按顺序实现 daemon core、VS Code 宿主前端、continue 恢复桥，并在代表性本地工作区上完成 MVP 验证 | 用户已能在 VS Code 中看到 live 状态、通过宿主接住 continue，并确认写代码体验明显变轻 |
| 更后面 | 在 daemon-host 基线上逐项回归旧功能家族，恢复 post-M16 rollout verification，再视证据决定是否扩到 chat surfaces、web/remote 宿主或更激进的 auto-resume | 不把 daemon 核心、宿主桥接、旧功能回归和更远的聊天集成混成一个 release |

## 里程碑

| 里程碑 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |
| [M1](reference/project-assistant/development-plan.zh-CN.md#m1) | done | 建立 `.codex` 控制面与项目分级 | core skill routing | 当前状态可恢复 |
| [M2](reference/project-assistant/development-plan.zh-CN.md#m2) | done | 建立收敛式 retrofit | control-surface scripts | 整改不再停在中间态 |
| [M3](reference/project-assistant/development-plan.zh-CN.md#m3) | done | 建立进展与交接工作流 | module layer + snapshot scripts | 进展和交接稳定可用 |
| [M4](reference/project-assistant/development-plan.zh-CN.md#m4) | done | 建立 durable 文档标准与文档校验 | document standards + docs scripts | durable 文档通过结构门禁 |
| [M5](reference/project-assistant/development-plan.zh-CN.md#m5) | done | 建立公开文档双语切换与验收 | i18n rules + i18n validator | 公开文档可在中英文之间稳定切换 |
| [M6](reference/project-assistant/development-plan.zh-CN.md#m6) | done | 收敛成内嵌式架构师助手工作模型 | previous milestones | 规划、执行、架构监督和开发日志成为默认自动能力 |
| [M7](reference/project-assistant/development-plan.zh-CN.md#m7) | done | 提升叙事质量与自动架构触发能力 | [M6](reference/project-assistant/development-plan.zh-CN.md#m6) | 整改后的手工清理更少，方向纠偏提示更少 |
| [M8](reference/project-assistant/development-plan.zh-CN.md#m8) | deferred | 按语言优化内部控制面输出 | handoff + command templates + validation policy | 转成 M10 下的 supporting backlog，而不是继续占据主线 |
| [M9](reference/project-assistant/development-plan.zh-CN.md#m9) | deferred | 自动压缩上下文与 continue / resume / handoff 快照体量而不损失可恢复性 | continue snapshot + handoff + validation policy | 转成 M10 下的 supporting backlog，而不是继续占据主线 |

## 战略层里程碑

| 里程碑 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |
| [M10](reference/project-assistant/development-plan.zh-CN.md#m10) | done | 增加位于执行层之上的战略评估层 | [M7](reference/project-assistant/development-plan.zh-CN.md#m7) + 已批准的战略方向 | 系统能产出 durable 战略判断、识别何时应插入治理/架构专项，并把业务方向变更继续交给人类审批 |
| [M11](reference/project-assistant/development-plan.zh-CN.md#m11) | done | 增加跨多个切片或执行器的程序编排层 | [M10](reference/project-assistant/development-plan.zh-CN.md#m10) + durable program board | 系统能协调多个相关切片，而不是持续依赖人工输入“继续” |
| [M12](reference/project-assistant/development-plan.zh-CN.md#m12) | done | 增加受监督的长期自动交付层 | [M11](reference/project-assistant/development-plan.zh-CN.md#m11) + 稳定升级策略 | 长期交付能持续推进到真正的业务裁决点，而不是在日常调度上不断停下来 |
| [M13](reference/project-assistant/development-plan.zh-CN.md#m13) | done | 增加由 PTL 驱动的监督环，让项目在 worker 停下后仍有常驻技术主责人继续盯进度、方向和升级 | [M12](reference/project-assistant/development-plan.zh-CN.md#m12) + durable delivery supervision | PTL 能周期性 / 事件驱动地巡检、决定继续 / 重排 / 升级，而不是依赖人类反复输入“继续” |
| [M14](reference/project-assistant/development-plan.zh-CN.md#m14) | done | 增加 worker 接续与回流，让未完成工作可以被 PTL 恢复、转交、回队列，而不是在 worker 停下时一起丢掉 | [M13](reference/project-assistant/development-plan.zh-CN.md#m13) + durable handoff / supervision truth | worker 在 checkpoint、超时、失败或交接后，剩余工作仍能继续推进或被明确升级 |
| [M15](reference/project-assistant/development-plan.zh-CN.md#m15) | later | 增加选择性多执行器调度，只对安全并行任务开放 | [M14](reference/project-assistant/development-plan.zh-CN.md#m14) + 不相交写入边界 + 冲突控制 | 只有 write scope 清楚、回收口明确、冲突门禁成立时，才允许真正多执行器并行 |
| [M16](reference/project-assistant/development-plan.zh-CN.md#m16) | done | 增加统一硬入口与工具前门，让 `继续 / 进展 / 交接` 必须先走同一条前门、版本 preflight 和结构化输出 | [M14](reference/project-assistant/development-plan.zh-CN.md#m14) + 版本化控制面 + entry scripts | 旧项目会先自动升级到当前控制面代际，且 `continue / progress / handoff` 的第一屏不再绕回自由 prose |

## 里程碑流转

```mermaid
flowchart LR
    M1["M1 控制面"] --> M2["M2 收敛式整改"]
    M2 --> M3["M3 进展 + 交接"]
    M3 --> M4["M4 文档标准"]
    M4 --> M5["M5 公开文档双语"]
    M5 --> M6["M6 内嵌式架构师助手"]
    M6 --> M7["M7 更强叙事 + 自动触发"]
    M7 --> M10["M10 战略评估层"]
    M10 --> M11["M11 程序编排层"]
    M11 --> M12["M12 长期受监督交付层"]
    M12 --> M13["M13 PTL 监督环"]
    M13 --> M14["M14 worker 接续与回流"]
    M14 --> M16["M16 统一硬入口与工具前门"]
    M16 --> M15["M15 选择性多执行器调度"]
```

## 风险与依赖

- 文档同步脚本更擅长快速补齐结构，不一定能一次重写出最好的叙事质量
- 默认自动架构监督如果被过多实现细节污染，就会失去高层纠偏能力
- 长任务执行线必须停在真实检查点，不能变成不可见的后台黑箱
- 公开文档双语质量仍然依赖内容生成，不仅是文件对和切换链接
- 如果未来要支持精确 context 门禁，仍然需要运行时暴露对应指标
- `M8 / M9` 仍然重要，但现在都作为 supporting backlog 管理，而不是继续占据主线
- `M15` 只面向安全并行任务；如果多个任务会改同一批文件、同一控制面或同一抽象边界，就不应进入多执行器层
- `M16` 的重点不是再加一个 CLI，而是让 `continue / progress / handoff` 的真实入口不再依赖模型自己“记得先跑脚本”
- `M16` 必须继续明确边界：repo 现在拥有统一前门和 script backend，但不应谎称桌面宿主已经完全硬绑定
- 宿主恢复桥首版已默认选定 VS Code 扩展前端；不应把“往内置聊天框里自动写继续”当成主架构

## 行为型 Backlog

| 主题 | 为什么要做 | 当前定位 |
| --- | --- | --- |
| daemon-first 异步执行、宿主恢复桥与时延治理 | 用户已经明确表示：如果 skill 继续这么慢，使用意愿会直接掉到卸载。当前主线不仅要做 daemon-first 运行时，还要补上宿主恢复桥和 live 状态展示，首版默认以 VS Code 扩展宿主前端为实现目标。 | active / current mainline |
| 问题驱动收口环 | 这类请求会反复出现：先把当前问题、解决思路和方案写进 devlog，再把关键结论同步到 architecture、roadmap、development plan，然后直接进入一口气长任务实现。未来这不应再依赖用户逐条提醒。 | supporting backlog / todo |
| 控制面真相同步确定性 | 当用户执行 `项目助手 继续` 时，`.codex/status.md`、`.codex/plan.md`、`strategy / program-board / delivery / PTL / handoff` 以及 `continue / progress / handoff` 输出之间不应再出现刷新顺序不一致、局部落后或“看起来没同步”的滞后感。 | supporting backlog / todo |
| VS Code chat surfaces 作为增强入口 | VS Code 扩展可以后续再接 `@project-assistant` participant、slash commands 或 tools，但不应阻塞首版宿主前端和恢复桥。 | later / supporting backlog |

## 战略方向

| 主题 | 为什么重要 | 当前位置 |
| --- | --- | --- |
| daemon-first 异步执行、宿主恢复桥与时延治理 | 当前用户反馈已经升级到产品留存级别：需要的不只是后台优先规则，而是 daemon 运行时、宿主恢复桥和 live UI 一起把“写代码被过程控制拖慢”这个问题打掉。 | active in roadmap and development plan |
| 业务规划与程序编排层 | `project-assistant` 已完成以项目技术负责人（PTL）为核心的 `M10 / M11 / M12 / M13 / M14`，并新增 `M16` 把 `continue / progress / handoff` 收成统一硬入口；`M15` 继续保持为证据驱动的 later 层，`M8 / M9` 仍作为 bounded supporting backlog | active in roadmap and development plan |
| 问题驱动收口环 | 当 durable 问题被识别后，skill 未来应自动触发“日志 -> 架构 -> 路线图 / 开发计划 -> 长任务实现”的闭环，而不是依赖用户重复下指令 | supporting backlog / todo |

方向文档：

- [业务规划与程序编排方向](reference/project-assistant/strategic-planning-and-program-orchestration.zh-CN.md)
- [宿主恢复桥与 VS Code 扩展可行性](reference/project-assistant/host-resume-bridge.zh-CN.md)
