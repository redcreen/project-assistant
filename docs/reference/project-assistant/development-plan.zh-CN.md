# project-assistant 开发计划

[English](development-plan.md) | [中文](development-plan.zh-CN.md)

## 目的

这份文档是给维护者看的 durable 详细执行计划，位置在 `docs/roadmap` 之下、AI 控制面之上。

它回答的不是“今天聊天里说了什么”，而是：

`接下来先做什么、从哪里恢复、每个里程碑下面到底落什么细节。`

## 相关文档

- [../../roadmap.zh-CN.md](../../roadmap.zh-CN.md)
- [../../architecture.zh-CN.md](../../architecture.zh-CN.md)
- [../../test-plan.zh-CN.md](../../test-plan.zh-CN.md)

## 怎么使用这份计划

1. 先看 roadmap，理解总体进展与下一阶段。
2. 再看这里的“总体进展”“执行任务进度”和“顺序执行队列”，理解今天该从哪里恢复。
3. 只有在维护自动化本身时，才需要继续下钻到内部控制文档。

## 总体进展

| 项目 | 当前值 |
| --- | --- |
| 总体进度 | 3 / 4 execution tasks 完成 |
| 当前阶段 | `post-M21 daemon-host baseline active` |
| 当前切片 | `stabilize-daemon-host-baseline-for-dogfooding` |
| 当前目标 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins |
| 当前切片退出条件 | daemon-host baseline 可被更广泛使用，且没有高频 runtime/host 回归 |
| 明确下一步动作 | EL-4 keep “single foreground writer per repo” as evidence-gated backlog until real adoption proves it should move from follow-up into a formal slice |
| 下一候选切片 | `package-daemon-host-baseline-for-release` |

## 当前位置

| 项目 | 当前值 | 说明 |
| --- | --- | --- |
| 当前阶段 | `post-M21 daemon-host baseline active` | 当前维护阶段 |
| 当前切片 | `stabilize-daemon-host-baseline-for-dogfooding` | 当前执行线绑定的切片 |
| 当前执行线 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins | 当前真正要收口的工作 |
| 当前验证 | validate_daemon_runtime.py`、`validate_vscode_host_extension.py`、`validate_daemon_host_mvp.py`、`validate_daemon_legacy_rollout.py` 已通过，M17-M21 baseline 已具备可持续回归的自动化入口 | 这条线继续前需要保持为真的验证入口 |

## 执行任务进度

| 顺序 | 任务 | 状态 |
| --- | --- | --- |
| 1 | EL-1 harden daemon runtime edges exposed by concurrent startup, shutdown, or status polling in real workspaces | 已完成 |
| 2 | EL-2 keep README / architecture / usage / test plan / entry routing aligned with daemon-host as the new default fast path | 已完成 |
| 3 | EL-3 collect broader dogfooding evidence before opening the next host surface or any M15 discussion | 已完成 |
| 4 | EL-4 keep “single foreground writer per repo” as evidence-gated backlog until real adoption proves it should move from follow-up into a formal slice | 下一步 |

## 阶段总览

| 阶段 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |
| M1 | done | 建立 `.codex` 控制面与项目分级 | core skill routing | 当前状态可恢复 |
| M2 | done | 建立收敛式 retrofit | control-surface scripts | 整改不再停在中间态 |
| M3 | done | 建立进展与交接工作流 | module layer + snapshot scripts | 进展和交接稳定可用 |
| M4 | done | 建立 durable 文档标准与文档校验 | document standards + docs scripts | durable 文档通过结构门禁 |
| M5 | done | 建立公开文档双语切换与验收 | i18n rules + i18n validator | 公开文档可在中英文之间稳定切换 |
| M6 | done | 收敛成内嵌式架构师助手工作模型 | previous milestones | 规划、执行、架构监督和开发日志成为默认自动能力 |
| M7 | done | 提升叙事质量与自动架构触发能力 | M6 | 整改后的手工清理更少，方向纠偏提示更少 |
| M8 | deferred | 按语言优化内部控制面输出 | handoff + command templates + validation policy | 继续作为 bounded supporting backlog |
| M9 | deferred | 自动压缩上下文与 continue / resume / handoff 快照体量而不损失可恢复性 | continue snapshot + handoff + validation policy | 继续作为 bounded supporting backlog |
| M10 | done | 增加位于执行层之上的战略评估层 | [M7](#m7) + 已批准的战略方向 | 系统能产出 durable 战略判断，并把方向变化继续交给人类审批 |
| M11 | done | 增加跨多个切片或执行器的程序编排层 | [M10](#m10) + durable program board | 系统能协调多个相关切片，而不是持续依赖人工输入“继续” |
| M12 | done | 增加受监督的长期自动交付层 | [M11](#m11) + 稳定升级策略 | 长期交付能持续推进到真正的业务裁决点 |
| M13 | done | 增加由 PTL 驱动的监督环 | [M12](#m12) + durable delivery supervision | PTL 能周期性 / 事件驱动地巡检、继续、重排或升级 |
| M14 | done | 增加 worker 接续与回流 | [M13](#m13) + durable handoff / supervision truth | `worker 停了，项目不能跟着停` 成为 durable 能力 |
| M15 | later | 增加选择性多执行器调度，只对安全并行任务开放 | [M14](#m14) + 不相交写入边界 + 冲突控制 | 只有 write scope 清楚、回收口明确、冲突门禁成立时，才允许真正多执行器并行 |
| M16 | done | 增加统一硬入口与工具前门 | [M14](#m14) + 版本化控制面 + entry scripts | 旧项目会先自动升级到当前控制面代际，且 `continue / progress / handoff` 第一屏不再绕回自由 prose |
| M17 | done | 建立 PTL daemon runtime core 与 write-safe 快升级基线 | [M16](#m16) + daemon-first 架构 + runtime contract | daemon runtime、queue/event contract、runtime store 与最小 CLI 控制面可用 |
| M18 | done | 建立 VS Code 宿主前端壳与 live status 面 | [M17](#m17) + daemon 事件契约 | 用户已能在 VS Code 中看到队列、状态、当前切片与最近事件 |
| M19 | done | 建立宿主 continue 恢复桥，把 `resume-ready` 接成宿主动作 | [M18](#m18) + Codex runner / 命令契约 | `manual continue` 与保守的 `one-click continue` 可用；不依赖聊天框注入 |
| M20 | done | 在 daemon-host 基线上完成本地工作区验证与旧功能逐项回归 | [M19](#m19) + 代表性本地 workspace | daemon-host 基线稳定，且旧能力在新基线上持续重新通过 |
| M21 | done | 在 daemon-host 基线上恢复 post-M16 rollout verification | M20 | 代表性旧代际仓库继续先升级再输出结构化面板，且体验不再被可避免的同步工作主导 |

## 顺序执行队列

| 顺序 | 切片 | 当前状态 | 目标 | 验证 |
| --- | --- | --- | --- | --- |
| 1 | `close-m17-through-m21-daemon-host-baseline` | 较早切片 | 把 daemon runtime、VS Code host shell、continue bridge、本地验证、旧功能回归和 post-M16 rollout 恢复一口气收口成可用 baseline | validate_daemon_runtime.py`、`validate_vscode_host_extension.py`、`validate_daemon_host_mvp.py`、`validate_daemon_legacy_rollout.py |
| 2 | `stabilize-daemon-host-baseline-for-dogfooding` | 当前 | 把刚完成的 daemon-host baseline 稳定成默认快路径，并为更广泛 dogfooding 准备好 operator docs 与采证入口 | validate_gate_set.py --profile deep`、runtime/host smoke、broader workspace dogfooding |
| 3 | `package-daemon-host-baseline-for-release` | 下一步 / 已排队 | 决定 daemon-host baseline 的 release 叙事、安装说明和版本落点 | release-facing docs、gate outputs 和 install path 对齐 |
| 4 | `future-host-expansion-and-m15-evidence` | 下一步 / 已排队 | 只在 daemon-host baseline 已稳定、dogfooding 证据充分后，再判断是否扩大到更强宿主表面或重新讨论 `M15 | real adoption evidence + clear write-scope boundaries |
| 5 | `M17 / build-ptl-daemon-runtime-core` | 下一步 / 已排队 | 建立 daemon runtime、runtime store、queue/event contract，以及最小的 `start/status/stop/queue` 控制面 | validate_daemon_runtime.py |
| 6 | `M18 / build-vscode-host-shell-and-live-status` | 下一步 / 已排队 | 建立 VS Code 宿主前端壳，至少包含 Tree View、Status Bar、Output channel，以及与 daemon 的连接 | validate_vscode_host_extension.py |
| 7 | `M19 / wire-manual-and-one-click-continue` | 下一步 / 已排队 | 把 `resume-ready` 事件接成 `manual continue`，并补上保守的 `one-click continue | validate_vscode_host_extension.py` + host continue smoke |
| 8 | `M20 / validate-daemon-host-mvp-on-local-workspaces` | 下一步 / 已排队 | 在代表性的本地 workspace 上验证 daemon + VS Code host MVP 的状态展示、恢复路径和稳定性 | validate_daemon_host_mvp.py |
| 9 | `M20 / validate-legacy-feature-set-on-daemon-host-baseline` | 下一步 / 已排队 | 在 daemon-host 基线上按家族逐项回归旧功能，而不是等所有能力都迁完再统一验收 | validate_daemon_host_mvp.py` + `validate_gate_set.py --profile deep |
| 10 | `M21 / resume-post-m16-rollout-on-daemon-host-baseline` | 下一步 / 已排队 | 在 daemon-host 基线稳定后，恢复 post-M16 rollout verification，并重新评估 host-bridge 证据 | validate_daemon_legacy_rollout.py |

## 里程碑细节

### M1

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立 `.codex` 控制面与项目分级 |
| 依赖 | core skill routing |
| 退出条件 | 当前状态可恢复 |

### M2

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立收敛式 retrofit |
| 依赖 | control-surface scripts |
| 退出条件 | 整改不再停在中间态 |

### M3

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立进展与交接工作流 |
| 依赖 | module layer + snapshot scripts |
| 退出条件 | 进展和交接稳定可用 |

### M4

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立 durable 文档标准与文档校验 |
| 依赖 | document standards + docs scripts |
| 退出条件 | durable 文档通过结构门禁 |

### M5

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立公开文档双语切换与验收 |
| 依赖 | i18n rules + i18n validator |
| 退出条件 | 公开文档可在中英文之间稳定切换 |

### M6

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 收敛成内嵌式架构师助手工作模型 |
| 依赖 | previous milestones |
| 退出条件 | 规划、执行、架构监督和开发日志成为默认自动能力 |

### M7

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 提升叙事质量与自动架构触发能力 |
| 依赖 | M6 |
| 退出条件 | 整改后的手工清理更少，方向纠偏提示更少 |

### M8

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | deferred |
| 目标 | 按语言优化内部控制面输出 |
| 依赖 | handoff + command templates + validation policy |
| 退出条件 | 继续作为 bounded supporting backlog |

### M9

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | deferred |
| 目标 | 自动压缩上下文与 continue / resume / handoff 快照体量而不损失可恢复性 |
| 依赖 | continue snapshot + handoff + validation policy |
| 退出条件 | 继续作为 bounded supporting backlog |

### M10

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加位于执行层之上的战略评估层 |
| 依赖 | [M7](#m7) + 已批准的战略方向 |
| 退出条件 | 系统能产出 durable 战略判断，并把方向变化继续交给人类审批 |

### M11

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加跨多个切片或执行器的程序编排层 |
| 依赖 | [M10](#m10) + durable program board |
| 退出条件 | 系统能协调多个相关切片，而不是持续依赖人工输入“继续” |

### M12

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加受监督的长期自动交付层 |
| 依赖 | [M11](#m11) + 稳定升级策略 |
| 退出条件 | 长期交付能持续推进到真正的业务裁决点 |

### M13

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加由 PTL 驱动的监督环 |
| 依赖 | [M12](#m12) + durable delivery supervision |
| 退出条件 | PTL 能周期性 / 事件驱动地巡检、继续、重排或升级 |

### M14

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加 worker 接续与回流 |
| 依赖 | [M13](#m13) + durable handoff / supervision truth |
| 退出条件 | `worker 停了，项目不能跟着停` 成为 durable 能力 |

### M15

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | later |
| 目标 | 增加选择性多执行器调度，只对安全并行任务开放 |
| 依赖 | [M14](#m14) + 不相交写入边界 + 冲突控制 |
| 退出条件 | 只有 write scope 清楚、回收口明确、冲突门禁成立时，才允许真正多执行器并行 |

### M16

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加统一硬入口与工具前门 |
| 依赖 | [M14](#m14) + 版本化控制面 + entry scripts |
| 退出条件 | 旧项目会先自动升级到当前控制面代际，且 `continue / progress / handoff` 第一屏不再绕回自由 prose |

### M17

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立 PTL daemon runtime core 与 write-safe 快升级基线 |
| 依赖 | [M16](#m16) + daemon-first 架构 + runtime contract |
| 退出条件 | daemon runtime、queue/event contract、runtime store 与最小 CLI 控制面可用 |

### M18

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立 VS Code 宿主前端壳与 live status 面 |
| 依赖 | [M17](#m17) + daemon 事件契约 |
| 退出条件 | 用户已能在 VS Code 中看到队列、状态、当前切片与最近事件 |

### M19

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立宿主 continue 恢复桥，把 `resume-ready` 接成宿主动作 |
| 依赖 | [M18](#m18) + Codex runner / 命令契约 |
| 退出条件 | `manual continue` 与保守的 `one-click continue` 可用；不依赖聊天框注入 |

### M20

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 在 daemon-host 基线上完成本地工作区验证与旧功能逐项回归 |
| 依赖 | [M19](#m19) + 代表性本地 workspace |
| 退出条件 | daemon-host 基线稳定，且旧能力在新基线上持续重新通过 |

### M21

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 在 daemon-host 基线上恢复 post-M16 rollout verification |
| 依赖 | M20 |
| 退出条件 | 代表性旧代际仓库继续先升级再输出结构化面板，且体验不再被可避免的同步工作主导 |

## 当前下一步

| 下一步 | 为什么做 |
| --- | --- |
| EL-4 keep “single foreground writer per repo” as evidence-gated backlog until real adoption proves it should move from follow-up into a formal slice | 这是当前第一条未完成 execution task；roadmap 与 development plan 都应把人带到同一个恢复点。 |
