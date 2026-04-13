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
| 当前阶段 | `daemon-first fast-upgrade planning ready` | 当前讨论已从“是否要 daemon”推进到“按什么顺序实现 daemon core、宿主前端和恢复桥”，目的是让你可以直接按文档点名开发 |
| 当前切片 | `plan-daemon-fast-upgrade-and-vscode-host-mvp` | 当前这轮把首版默认开发顺序正式固定为 `daemon core -> VS Code host shell -> resume bridge -> local validation -> old-feature re-validation` |
| 当前执行线 | 先把默认实现顺序和首版宿主范围写清楚，让开发能按切片推进，而不是在 daemon、host UI 和聊天集成之间反复跳转 | 当前真正要回答的是“第一刀先砍哪里，后面每一刀按什么顺序接上” |
| 当前验证 | `docs/reference/project-assistant/async-execution-and-latency-governance.md`、`ptl-daemon-mvp.md`、`host-resume-bridge.md` 与控制面都一致表达“先 daemon core，再 VS Code 宿主，再恢复桥” | 当前实现规划已经 durable 化，可直接作为开发排序依据 |

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
| 19 | `plan-daemon-fast-upgrade-and-vscode-host-mvp` | 当前主线 | 把首版快升级版正式拆成可按顺序实现的切片，并明确首个宿主默认是 VS Code 扩展前端 | roadmap、development plan、status、plan 和宿主桥文档能读出同一套默认开发顺序 |
| 20 | `build-ptl-daemon-runtime-core` | next | 建立 daemon runtime、queue/event contract、runtime store 和最小 CLI 控制面 | daemon 可启动 / 停止 / 展示队列状态，并产出宿主可消费的事件 |
| 21 | `build-vscode-host-shell-and-live-status` | next | 建立 VS Code 宿主前端壳，至少收 Tree View、Status Bar、Output channel 和 daemon 连接 | 用户已能在 VS Code 里看到 live 状态、当前切片和最近事件 |
| 22 | `wire-manual-and-one-click-continue` | next | 把 `resume-ready` 接成宿主可见的 continue 动作，先收 `manual continue`，再视范围补保守的 `one-click continue` | 停下来的 worker 能通过宿主恢复继续，不要求聊天框注入 |
| 23 | `validate-daemon-host-mvp-on-local-workspaces` | next | 在代表性本地 workspace 上验证 daemon + VS Code host MVP 的状态、恢复和稳定性 | 本地工作区验证证明宿主 MVP 足够稳定，可以作为下一阶段基线 |
| 24 | `validate-legacy-feature-set-on-daemon-host-baseline` | next | 在 daemon-host 基线上按家族逐项回归旧功能，而不是等一个超大迁移一次性完成 | 旧能力在新基线上持续重新通过，不反噬“先提速、先减负”的主目标 |
| 25 | `resume-post-m16-rollout-on-daemon-host-baseline` | next | 在 daemon-host 基线和旧功能回归稳定后，再恢复 post-M16 rollout verification | 代表性旧仓库继续先升级再输出结构化面板，且体验不再被可避免的同步工作主导 |
| 26 | `formalize-issue-driven-closure-loop` | supporting backlog / todo | 把“当前问题 -> 解决思路 -> 方案 -> devlog -> architecture -> roadmap / development plan -> 一口气长任务实现”固化成默认行为，而不是依赖用户逐条提醒 | 后续实现时，能够在 durable 问题被识别后自动触发这条收口链路 |
| 27 | `formalize-control-truth-sync-determinism` | supporting backlog / todo | 把 `.codex/status.md`、`.codex/plan.md`、`strategy / program-board / delivery / PTL / handoff` 以及 `continue / progress / handoff` 的刷新顺序收口成一次确定性的同步事务，避免用户执行 `项目助手 继续` 时看到“部分已更新、部分落后”的滞后感 | 后续实现时，旧项目升级、控制面刷新、结构化第一屏和持久真相能在同一轮 checkpoint 里稳定对齐 |

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

## 当前下一步

| 下一步 | 为什么做 |
| --- | --- |
| 从 `build-ptl-daemon-runtime-core` 开始 | daemon core 是后面宿主壳、resume bridge 和 live 状态的共同基础；不先收它，宿主开发会空转 |
| 然后进入 `build-vscode-host-shell-and-live-status` | 用户要看到“页面在动、代码在改”，所以首版宿主前端不能再晚于恢复桥之后 |
| 再做 `wire-manual-and-one-click-continue` | continue 恢复动作是宿主桥的关键价值；这一步应该建立在 daemon core 和 live status 都已经存在的基础上 |
| 宿主 MVP 稳住后立刻运行 `validate-daemon-host-mvp-on-local-workspaces` | 先在真实本地工作区证明这条链路稳定，才能拿它去承载旧功能回归 |
| 再进入 `validate-legacy-feature-set-on-daemon-host-baseline` | 当前策略明确是“先把体验做轻，再按顺序回归旧能力”，而不是做一个大而全迁移 |
| 预留 `formalize-issue-driven-closure-loop` | 这类“先写日志、再写架构、再同步 roadmap / development plan、再一口气实现”的请求已经表现出稳定模式，值得升级成 skill 默认行为 |
| 预留 `formalize-control-truth-sync-determinism` | `项目助手 继续` 目前仍可能让维护者感知到 `.codex` 真相刷新不同步，这个问题值得升级成确定性同步专题 |

## 战略方向

| 主题 | 范围 | 当前位置 |
| --- | --- | --- |
| daemon-first 异步执行、宿主恢复桥与时延治理 | 当前产品目标已经转成“尽快恢复编码速度”：先收 daemon core、VS Code 宿主前端和恢复桥，再在新基线上逐项验证旧功能 | active |
| 业务规划、程序编排与硬入口 | `project-assistant` 已完成以 PTL 为核心的 `M10 / M11 / M12 / M13 / M14`，并新增 `M16` 把 `continue / progress / handoff` 收成统一前门；`M15` 仍保持为证据驱动 later 层，`M8 / M9` 继续作为 bounded supporting backlog | active |

方向文档：

- [业务规划与程序编排方向](strategic-planning-and-program-orchestration.zh-CN.md)
- [宿主恢复桥与 VS Code 扩展可行性](host-resume-bridge.zh-CN.md)
