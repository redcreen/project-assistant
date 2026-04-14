# 路线图

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## 范围

这个路线图只描述 `project-assistant` skill 自身的演进，不替代 `.codex/status.md` 中的当前执行状态。

详细执行队列看这里：

- [project-assistant/development-plan.zh-CN.md](reference/project-assistant/development-plan.zh-CN.md)

## 当前 / 下一步 / 更后面

| 时间层级 | 重点 | 退出信号 |
| --- | --- | --- |
| 当前 | 稳住刚完成的 daemon-host baseline，把它变成真实可用的默认快路径：runtime、queue、VS Code host、continue bridge、legacy rollout 与文档/门禁都保持一致 | broader dogfooding 不再暴露高频 runtime/host 回归，daemon-host baseline 可被默认采用 |
| 下一步 | 决定 daemon-host baseline 的 release 叙事、安装入口和更广的 dogfooding 范围，同时继续收集宿主恢复桥证据 | operator docs、release-facing docs 和 install path 对齐，且更广泛 workspace 仍能稳定通过 |
| 更后面 | 只在证据充分时才扩大宿主表面、评估 web / remote 宿主，或重新讨论 `M15 选择性多执行器调度` | 不把 baseline 稳定化、宿主扩张和多执行器讨论混成一个 release |

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
| [M8](reference/project-assistant/development-plan.zh-CN.md#m8) | deferred | 按语言优化内部控制面输出 | handoff + command templates + validation policy | 继续作为 bounded supporting backlog |
| [M9](reference/project-assistant/development-plan.zh-CN.md#m9) | deferred | 自动压缩上下文与 continue / resume / handoff 快照体量而不损失可恢复性 | continue snapshot + handoff + validation policy | 继续作为 bounded supporting backlog |
| [M10](reference/project-assistant/development-plan.zh-CN.md#m10) | done | 增加位于执行层之上的战略评估层 | [M7](reference/project-assistant/development-plan.zh-CN.md#m7) + 已批准的战略方向 | 系统能产出 durable 战略判断，并把方向变化继续交给人类审批 |
| [M11](reference/project-assistant/development-plan.zh-CN.md#m11) | done | 增加跨多个切片或执行器的程序编排层 | [M10](reference/project-assistant/development-plan.zh-CN.md#m10) + durable program board | 系统能协调多个相关切片，而不是持续依赖人工输入“继续” |
| [M12](reference/project-assistant/development-plan.zh-CN.md#m12) | done | 增加受监督的长期自动交付层 | [M11](reference/project-assistant/development-plan.zh-CN.md#m11) + 稳定升级策略 | 长期交付能持续推进到真正的业务裁决点 |
| [M13](reference/project-assistant/development-plan.zh-CN.md#m13) | done | 增加由 PTL 驱动的监督环 | [M12](reference/project-assistant/development-plan.zh-CN.md#m12) + durable delivery supervision | PTL 能周期性 / 事件驱动地巡检、继续、重排或升级 |
| [M14](reference/project-assistant/development-plan.zh-CN.md#m14) | done | 增加 worker 接续与回流 | [M13](reference/project-assistant/development-plan.zh-CN.md#m13) + durable handoff / supervision truth | `worker 停了，项目不能跟着停` 成为 durable 能力 |
| [M15](reference/project-assistant/development-plan.zh-CN.md#m15) | later | 增加选择性多执行器调度，只对安全并行任务开放 | [M14](reference/project-assistant/development-plan.zh-CN.md#m14) + 不相交写入边界 + 冲突控制 | 只有 write scope 清楚、回收口明确、冲突门禁成立时，才允许真正多执行器并行 |
| [M16](reference/project-assistant/development-plan.zh-CN.md#m16) | done | 增加统一硬入口与工具前门 | [M14](reference/project-assistant/development-plan.zh-CN.md#m14) + 版本化控制面 + entry scripts | 旧项目会先自动升级到当前控制面代际，且 `continue / progress / handoff` 第一屏不再绕回自由 prose |
| [M17](reference/project-assistant/development-plan.zh-CN.md#m17) | done | 建立 PTL daemon runtime core 与 write-safe 快升级基线 | [M16](reference/project-assistant/development-plan.zh-CN.md#m16) + daemon-first 架构 + runtime contract | daemon runtime、queue/event contract、runtime store 与最小 CLI 控制面可用 |
| [M18](reference/project-assistant/development-plan.zh-CN.md#m18) | done | 建立 VS Code 宿主前端壳与 live status 面 | [M17](reference/project-assistant/development-plan.zh-CN.md#m17) + daemon 事件契约 | 用户已能在 VS Code 中看到队列、状态、当前切片与最近事件 |
| [M19](reference/project-assistant/development-plan.zh-CN.md#m19) | done | 建立宿主 continue 恢复桥，把 `resume-ready` 接成宿主动作 | [M18](reference/project-assistant/development-plan.zh-CN.md#m18) + Codex runner / 命令契约 | `manual continue` 与保守的 `one-click continue` 可用；不依赖聊天框注入 |
| [M20](reference/project-assistant/development-plan.zh-CN.md#m20) | done | 在 daemon-host 基线上完成本地工作区验证与旧功能逐项回归 | [M19](reference/project-assistant/development-plan.zh-CN.md#m19) + 代表性本地 workspace | daemon-host 基线稳定，且旧能力在新基线上持续重新通过 |
| [M21](reference/project-assistant/development-plan.zh-CN.md#m21) | done | 在 daemon-host 基线上恢复 post-M16 rollout verification | [M20](reference/project-assistant/development-plan.zh-CN.md#m20) | 代表性旧代际仓库继续先升级再输出结构化面板，且体验不再被可避免的同步工作主导 |

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
    M16 --> M17["M17 daemon runtime core"]
    M17 --> M18["M18 VS Code 宿主壳"]
    M18 --> M19["M19 host resume bridge"]
    M19 --> M20["M20 daemon-host 验证 + 旧功能回归"]
    M20 --> M21["M21 恢复 post-M16 rollout"]
    M21 --> M15["M15 选择性多执行器调度"]
```

## 风险与依赖

- daemon-host baseline 已交付，但 release 包装、版本入口和更广范围 dogfooding 仍需继续完成
- 宿主恢复桥首版已默认选定 VS Code 扩展前端；不应把“往内置聊天框里自动写继续”当成主架构
- `M15` 只面向安全并行任务；如果多个任务会改同一批文件、同一控制面或同一抽象边界，就不应进入多执行器层
- `M8 / M9` 仍然重要，但现在都作为 bounded supporting backlog 管理，而不是继续占据主线
- 如果未来要支持 web / remote 宿主，仍需要新的 runtime / transport / trust boundary 设计，而不应直接复用本地桌面假设

## 行为型 Backlog

| 主题 | 为什么要做 | 当前定位 |
| --- | --- | --- |
| daemon-host baseline 稳定化与 dogfooding | `M17-M21` 已完成，但真正决定留存的是 baseline 能否稳定成为默认快路径 | active / current mainline |
| 问题驱动收口环 | 当 durable 问题被识别后，skill 未来应自动触发“日志 -> 架构 -> 路线图 / 开发计划 -> 长任务实现”的闭环 | supporting backlog / todo |
| 控制面真相同步确定性 | 当用户执行 `项目助手 继续` 时，`.codex/status.md`、`.codex/plan.md`、`strategy / program-board / delivery / PTL / handoff` 以及 `continue / progress / handoff` 输出之间不应再出现刷新顺序不一致 | supporting backlog / todo |
| 同仓多宿主前台单写者保护 | 现在 daemon 已有 foreground lease，但 VS Code 宿主还没有把它真正接成“同一仓库只能有一个前台写代码 owner”，是否值得做要继续看真实使用证据 | supporting backlog / todo |
| 更强宿主表面 | Webview dashboard、chat participant、web / remote host 等增强入口应建立在 daemon-host baseline 稳定后 | later / supporting backlog |

## 战略方向

| 主题 | 为什么重要 | 当前位置 |
| --- | --- | --- |
| daemon-first 异步执行、宿主恢复桥与时延治理 | 当前用户痛点已经落实成 working baseline：daemon runtime、宿主状态面和 continue bridge 已交付，下一步是把它变成稳定、可 adopt 的默认路径 | active in roadmap and development plan |
| 业务规划与程序编排层 | `project-assistant` 已完成以项目技术负责人（PTL）为核心的 `M10 / M11 / M12 / M13 / M14 / M16`；`M15` 继续保持为证据驱动 later 层 | active in roadmap and development plan |
| 问题驱动收口环 | 当 durable 问题被识别后，skill 未来应自动触发“日志 -> 架构 -> 路线图 / 开发计划 -> 长任务实现”的闭环，而不是依赖用户重复下指令 | supporting backlog / todo |

方向文档：

- [业务规划与程序编排方向](reference/project-assistant/strategic-planning-and-program-orchestration.zh-CN.md)
- [宿主恢复桥与 VS Code 扩展可行性](reference/project-assistant/host-resume-bridge.zh-CN.md)
