# project-assistant 开发计划

[English](development-plan.md) | [中文](development-plan.zh-CN.md)

## 目的

这份文档是给维护者看的 durable 详细执行计划，位置在 `docs/roadmap` 之下、`.codex/plan.md` 之上。

它回答的是：

`接下来先做什么、从哪里恢复、每个里程碑下面到底落什么细节。`

## 相关文档

- [../../roadmap.zh-CN.md](../../roadmap.zh-CN.md)
- [../../architecture.zh-CN.md](../../architecture.zh-CN.md)
- [../../test-plan.zh-CN.md](../../test-plan.zh-CN.md)

## 怎么使用这份计划

1. 先看 roadmap，理解整体路线和当前里程碑。
2. 再看这里的“当前位置”和“顺序执行队列”，理解今天该从哪里恢复。
3. 需要具体约束时，再回到 `.codex/plan.md` 看实时执行控制面。

## 当前位置

| 项目 | 当前值 | 说明 |
| --- | --- | --- |
| 当前阶段 | `post-M21 daemon-host baseline active` | `M17-M21` 已经一口气完成；当前不再停留在规划顺序，而是进入 daemon-host baseline 稳定化与 dogfooding |
| 当前切片 | `stabilize-daemon-host-baseline-for-dogfooding` | 当前主线从“怎么做”切到“怎么把这条 baseline 稳成默认快路径” |
| 当前执行线 | 把 daemon runtime、VS Code host、continue bridge、legacy rollout、文档与门禁继续收成同一条默认快路径，并开始更广泛采证 | 当前真正要回答的是“这条 baseline 能不能稳定承接日常使用与后续 release” |
| 当前验证 | `validate_daemon_runtime.py`、`validate_vscode_host_extension.py`、`validate_daemon_host_mvp.py`、`validate_daemon_legacy_rollout.py` 已通过 | 当前实现已 durable 化，接下来主要是稳定化、包装和更广范围 dogfooding |

## 阶段总览

| 里程碑 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |
| M1 | done | 建立 `.codex` 控制面与项目分级 | core skill routing | 当前状态可恢复 |
| M2 | done | 建立收敛式 retrofit | control-surface scripts | 整改不再停在中间态 |
| M3 | done | 建立进展与交接工作流 | module layer + snapshot scripts | 进展和交接稳定可用 |
| M4 | done | 建立 durable 文档标准与文档校验 | document standards + docs scripts | durable 文档通过结构门禁 |
| M5 | done | 建立公开文档双语切换与验收 | i18n rules + i18n validator | 公开文档可在中英文之间稳定切换 |
| M6 | done | 收敛成内嵌式架构师助手工作模型 | previous milestones | 规划、执行、架构监督和开发日志成为默认自动能力 |
| M7 | done | 提升叙事质量与自动架构触发能力 | M6 | 整改后的手工清理更少，方向纠偏提示更少 |
| M8 | deferred | 按语言优化内部控制面输出 | handoff + command templates + validation policy | 转成 supporting backlog，而不是继续占据主线 |
| M9 | deferred | 自动压缩上下文与 continue / resume / handoff 快照体量而不损失可恢复性 | continue snapshot + handoff + validation policy | 转成 supporting backlog，而不是继续占据主线 |
| M10 | done | 增加由项目技术负责人（PTL）驱动的战略评估层 | M7 + 已批准的战略方向 | roadmap / 治理 / 架构调整建议成为 durable、可 review 的战略输出 |
| M11 | done | 增加由项目技术负责人（PTL）驱动的程序编排层 | M10 + durable program board | 系统能协调多个相关切片，而不是持续依赖人工输入“继续” |
| M12 | done | 增加由项目技术负责人（PTL）驱动的受监督长期自动交付层 | M11 + 稳定升级策略 | 长期交付能持续推进到真正的业务裁决点 |
| M13 | done | 增加由项目技术负责人（PTL）驱动的监督环 | M12 + durable delivery supervision | PTL 能周期性 / 事件驱动地巡检、继续、重排或升级 |
| M14 | done | 增加 worker 接续与回流 | M13 + durable handoff / supervision truth | `worker 停了，项目不能跟着停` 成为 durable 能力 |
| M15 | later | 增加选择性多执行器调度 | M14 + 不相交写入边界 + 冲突控制 | 只有安全并行任务才进入多执行器；高耦合任务继续保持单主写入线 |
| M16 | done | 增加统一硬入口与工具前门 | M14 + 版本化控制面 + entry scripts | 旧项目会先自动升级到当前控制面代际，且 `continue / progress / handoff` 第一屏不再绕回自由 prose |
| M17 | done | 建立 PTL daemon runtime core 与 write-safe 快升级基线 | M16 + daemon-first 架构 + runtime contract | daemon runtime、queue/event contract、runtime store 与最小 CLI 控制面可用 |
| M18 | done | 建立 VS Code 宿主前端壳与 live status 面 | M17 + daemon 事件契约 | 用户已能在 VS Code 中看到队列、状态、当前切片与最近事件 |
| M19 | done | 建立宿主 continue 恢复桥，把 `resume-ready` 接成宿主动作 | M18 + Codex runner / 命令契约 | `manual continue` 与保守的 `one-click continue` 可用；不依赖聊天框注入 |
| M20 | done | 在 daemon-host 基线上完成本地工作区验证与旧功能逐项回归 | M19 + 代表性本地 workspace | daemon-host 基线稳定，且旧能力在新基线上持续重新通过 |
| M21 | done | 在 daemon-host 基线上恢复 post-M16 rollout verification | M20 | 代表性旧代际仓库继续先升级再输出结构化面板，且体验不再被可避免的同步工作主导 |

## 顺序执行队列

| 顺序 | 切片 | 当前状态 | 目标 | 验证 |
| --- | --- | --- | --- | --- |
| 1 | `redefine the operating model` | 较早切片 | n/a | n/a |
| 2 | `embed architecture supervision by default` | 较早切片 | n/a | n/a |
| 3 | `embed development-log capture by default` | 较早切片 | n/a | n/a |
| 4 | `simplify the human surface` | 较早切片 | n/a | n/a |
| 5 | `define the escalation and gate model` | 较早切片 | n/a | n/a |
| 6 | `operationalize reporting and release governance` | 较早切片 | n/a | n/a |
| 7 | `automate supervision, release protection, and human windows` | 较早切片 | n/a | n/a |
| 8 | `make architecture retrofit a first-class flow` | 较早切片 | n/a | n/a |
| 9 | `prepare project-assistant for broader repo adoption` | 较早切片 | n/a | n/a |
| 10 | `tighten-maintainer-facing-narrative-and-architecture-triggers` | 已完成的里程碑切片 | representative medium / large repo 的第一屏更接近维护者恢复面板；至少一条架构触发已能自动升级 | representative repo snapshots 改善且自动触发可见 |
| 11 | `activate-m10-strategic-evaluation-layer` | 已完成 | 把战略层从“提案”提升成 active roadmap 方向，并让 roadmap / README / 控制面指向同一个当前主线 | 文档、路线图、开发计划和控制面都指向 M10 |
| 12 | `establish-strategy-surface-and-review-contract` | 已完成 | 创建第一份 durable strategy surface，定义 review 边界，并明确 M8/M9 怎样并入 supporting backlog | `.codex/strategy.md` 存在；文档与控制面一致；`deep` 通过 |
| 13 | `close-m10-and-queue-m11` | 已完成 | 让 M10 从“方向成立”变成“脚本、门禁、展示、文档都成立” | `deep` 与 `release` 通过 |
| 14 | `close-m11-and-queue-m12` | 已完成 | 让 M11 从“program direction”变成“program board、门禁、展示、文档都成立” | `deep` 与 `release` 通过 |
| 15 | `close-m12-and-open-rollout` | 已完成 | 让 M12 从“方向已批准”变成“delivery-supervision、门禁、展示、文档都成立” | `deep` 与 `release` 通过 |
| 16 | `define-m13-m14-m15-post-m12-mainline` | 已完成 | 把 post-M12 正式写成 `M13 / M14 / M15`，并明确 `worker 接续与回流` 的人话定义 | roadmap、README、development plan、战略文档与编排模型都对齐 |
| 17 | `close-m13-and-m14-and-queue-m15-evidence` | 已完成 | 把 `M13 / M14` 真正收口成 PTL supervision / worker handoff 的 durable 控制面、门禁、进展与交接 | `deep` 与 `release` 通过；控制面、README、roadmap、development plan 与进展输出都显示 `M13 / M14 done` |
| 18 | `close-m16-tool-first-front-door-and-queue-rollout-verification` | 已完成 | 把真实入口问题收口成统一前门、版本 preflight、结构化第一屏、CLI 前门与 durable `entry-routing` 控制面 | `project_assistant_entry.py`、`sync_resume_readiness.py`、`validate_entry_routing.py`、`deep` 与 `release` 通过；代表性旧仓库可先升级再输出面板 |
| 19 | `close-m17-through-m21-daemon-host-baseline` | 已完成 | 把 daemon runtime、VS Code host shell、continue bridge、本地验证、旧功能回归和 post-M16 rollout 恢复一口气收口成可用 baseline | `validate_daemon_runtime.py`、`validate_vscode_host_extension.py`、`validate_daemon_host_mvp.py`、`validate_daemon_legacy_rollout.py` 通过 |
| 20 | `stabilize-daemon-host-baseline-for-dogfooding` | 当前主线 | 把 daemon-host baseline 稳定成默认快路径，并为更广泛 dogfooding 准备 operator docs 与采证入口 | `deep` 门禁、runtime/host smoke 和更广范围 workspace dogfooding 保持稳定 |
| 21 | `package-daemon-host-baseline-for-release` | next | 决定 daemon-host baseline 的 release 叙事、安装入口和版本落点 | release-facing docs、install path 与 gate outputs 对齐 |
| 22 | `future-host-expansion-and-m15-evidence` | later / evidence-gated | 只有 baseline 稳定、采证充分后，才评估更强宿主表面或重新讨论 `M15` | real adoption evidence + clear write-scope boundaries |
| 23 | `formalize-issue-driven-closure-loop` | supporting backlog / todo | 把“当前问题 -> 解决思路 -> 方案 -> devlog -> architecture -> roadmap / development plan -> 一口气长任务实现”固化成默认行为，而不是依赖用户逐条提醒 | 后续实现时，能够在 durable 问题被识别后自动触发这条收口链路 |
| 24 | `formalize-control-truth-sync-determinism` | supporting backlog / todo | 把 `.codex/status.md`、`.codex/plan.md`、`strategy / program-board / delivery / PTL / handoff` 以及 `continue / progress / handoff` 的刷新顺序收口成一次确定性的同步事务，避免用户执行 `项目助手 继续` 时看到“部分已更新、部分落后”的滞后感 | 后续实现时，旧项目升级、控制面刷新、结构化第一屏和持久真相能在同一轮 checkpoint 里稳定对齐 |

## 里程碑细节

### M10

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加由项目技术负责人（PTL）驱动的战略评估层 |
| 依赖 | M7 + 已批准的战略方向 |
| 退出条件 | roadmap / 治理 / 架构调整建议成为 durable、可 review 的战略输出 |

### M11

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加由项目技术负责人（PTL）驱动的程序编排层 |
| 依赖 | M10 + durable program board |
| 退出条件 | 系统能协调多个相关切片，而不是持续依赖人工输入“继续” |

### M12

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加由项目技术负责人（PTL）驱动的受监督长期自动交付层 |
| 依赖 | M11 + 稳定升级策略 |
| 退出条件 | 长期交付能持续推进到真正的业务裁决点 |

### M13

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加由项目技术负责人（PTL）驱动的监督环 |
| 依赖 | M12 + durable delivery supervision |
| 退出条件 | PTL 能周期性 / 事件驱动地巡检、继续、重排或升级，而不是只在聊天里偶尔出现 |

### M14

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加 worker 接续与回流 |
| 人话解释 | `worker 停了，项目不能跟着停` |
| 依赖 | M13 + durable handoff / supervision truth |
| 退出条件 | worker 停下后，剩余工作仍能被 PTL 恢复、转交、回流或升级 |

### M15

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | later |
| 目标 | 增加选择性多执行器调度 |
| 依赖 | M14 + 不相交写入边界 + 冲突控制 |
| 退出条件 | 只有 write scope 清楚、回收口明确、冲突可控的任务才进入多执行器 |

### M16

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加统一硬入口与工具前门 |
| 依赖 | M14 + 版本化控制面 + entry scripts |
| 退出条件 | `continue / progress / handoff` 共享同一条前门、先跑同一条 preflight、先输出结构化第一屏；repo 还额外拥有 durable `entry-routing` contract 与 CLI 前门 |

### M17

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立 PTL daemon runtime core 与 write-safe 快升级基线 |
| 依赖 | M16 + daemon-first 架构 + runtime contract |
| 退出条件 | daemon runtime、queue/event contract、runtime store 与最小 CLI 控制面可用 |

### M18

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立 VS Code 宿主前端壳与 live status 面 |
| 依赖 | M17 + daemon 事件契约 |
| 退出条件 | 用户已能在 VS Code 中看到队列、状态、当前切片与最近事件 |

### M19

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 建立宿主 continue 恢复桥，把 `resume-ready` 接成宿主动作 |
| 依赖 | M18 + Codex runner / 命令契约 |
| 退出条件 | `manual continue` 可用，并在范围允许时补上保守的 `one-click continue`；不依赖聊天框注入 |

### M20

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 在 daemon-host 基线上完成本地工作区验证与旧功能逐项回归 |
| 依赖 | M19 + 代表性本地 workspace |
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
| 从 `stabilize-daemon-host-baseline-for-dogfooding` 开始 | `M17-M21` 已经完成，当前优先级转成“把这条 baseline 稳成默认快路径”，而不是重新讨论实现顺序 |
| 然后进入 `package-daemon-host-baseline-for-release` | 只有把 release 叙事、安装入口和 operator docs 讲清楚，这条 baseline 才真正可 adopt |
| 保持 `future-host-expansion-and-m15-evidence` 为证据驱动 later 层 | 先稳住 baseline，再考虑更强宿主表面、web / remote host 或 `M15`，避免重新把主线拖重 |
| 预留 `formalize-issue-driven-closure-loop` | 这类“先写日志、再写架构、再同步 roadmap / development plan、再一口气实现”的请求已经表现出稳定模式，值得升级成 skill 默认行为 |
| 预留 `formalize-control-truth-sync-determinism` | `项目助手 继续` 目前仍可能让维护者感知到 `.codex` 真相刷新不同步，这个问题值得升级成确定性同步专题 |

## 战略方向

| 主题 | 范围 | 当前位置 |
| --- | --- | --- |
| daemon-first 异步执行、宿主恢复桥与时延治理 | 当前产品目标已经从“先定义方向”转成“先把 daemon-host baseline 稳成默认快路径”，daemon runtime、VS Code 宿主前端和恢复桥都已落地 | active |
| 业务规划、程序编排与硬入口 | `project-assistant` 已完成以 PTL 为核心的 `M10 / M11 / M12 / M13 / M14`，并新增 `M16` 把 `continue / progress / handoff` 收成统一前门；`M15` 仍保持为证据驱动 later 层，`M8 / M9` 继续作为 bounded supporting backlog | active |

方向文档：

- [业务规划与程序编排方向](strategic-planning-and-program-orchestration.zh-CN.md)
- [宿主恢复桥与 VS Code 扩展可行性](host-resume-bridge.zh-CN.md)
