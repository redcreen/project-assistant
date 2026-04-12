# project-assistant 开发计划

[English](development-plan.md) | [中文](development-plan.zh-CN.md)

## 目的

这份文档是给维护者看的 durable 详细执行计划，位置在 `docs/roadmap` 之下、`.codex/plan.md` 之上。

它回答的不是“今天聊天里说了什么”，而是：

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
| 当前阶段 | `supervised long-run delivery layer closed; rollout queued` | 来自 `.codex/plan.md` 的当前维护阶段 |
| 当前切片 | `close-m12-and-open-rollout` | 当前执行线绑定的切片 |
| 当前执行线 | 收口 M12 长期受监督交付层，把 delivery-supervision、checkpoint rhythm、自动继续边界与升级时机都切到 durable 真相，并把后续状态切到 rollout / 摩擦采集 | 当前这轮真正收口的工作 |
| 当前验证 | delivery-supervision 脚本、校验、`progress / continue / handoff`、README、roadmap、development plan 与控制面一致；`deep` 和 `release` 继续通过 | 继续前如何证明这条线已收口 |

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
| M8 | deferred | 按语言优化内部控制面输出 | handoff + command templates + validation policy | 转成 M10 下的 supporting backlog，而不是继续占据主线 |
| M9 | deferred | 压缩 continue / resume 快照体量而不损失可恢复性 | continue snapshot + handoff + validation policy | 转成 M10 下的 supporting backlog，而不是继续占据主线 |
| M10 | done | 增加由项目技术负责人（PTL）驱动的战略评估层 | M7 + 已批准的战略方向 | roadmap / 治理 / 架构调整建议成为 durable、可 review 的战略输出，而不是零散直觉 |
| M11 | done | 增加由项目技术负责人（PTL）驱动的程序编排层 | M10 + durable program board | 先把单 Codex 的 durable 编排真相层稳定下来；如果未来需要多执行器调度，再单独立项 |
| M12 | done | 增加由项目技术负责人（PTL）驱动的受监督长期交付层 | M11 + 稳定升级策略 | 长期交付能持续推进到真正的业务裁决点 |

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
| 11 | `activate-m10-strategic-evaluation-layer` | 已完成的切换切片 | 把战略层从“提案”提升成 active roadmap 方向，并让 roadmap / README / 控制面指向同一个当前主线 | 文档、路线图、开发计划和控制面都指向 M10 |
| 12 | `establish-strategy-surface-and-review-contract` | 已完成 | 创建第一份 durable strategy surface，定义 review 边界，并明确 M8/M9 怎样并入 supporting backlog | `.codex/strategy.md` 存在；文档与控制面一致；`deep` 通过 |
| 13 | `close-m10-and-queue-m11` | 已完成 | 把 M10 从“方向成立”收口成“脚本、门禁、展示、文档都成立”，并明确把 M11 排成下一条主线 | `validate_strategy_surface.py`、`progress / continue / handoff`、README、roadmap、development plan 和控制面都对齐；`deep` 与 `release` 通过 |
| 14 | `close-m11-and-queue-m12` | 已完成 | 把 M11 从“有方向和草图”收口成“program-board、门禁、展示、文档都成立”，并明确把 M12 排成下一条主线 | `validate_program_board.py`、`progress / continue / handoff`、README、roadmap、development plan 和控制面都对齐；`deep` 与 `release` 通过 |
| 15 | `close-m12-and-open-rollout` | 当前 | 把 M12 从“方向已批准”收口成“delivery-supervision、门禁、展示、文档都成立”，并把后续状态切到 rollout / 摩擦采集 | `validate_delivery_supervision.py`、`progress / continue / handoff`、README、roadmap、development plan 和控制面都对齐；`deep` 与 `release` 通过 |

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
| 退出条件 | 这条线继续作为 M10 下的 supporting backlog，而不是主线里程碑 |

### M9

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | deferred |
| 目标 | 压缩 continue / resume 快照体量而不损失可恢复性 |
| 依赖 | continue snapshot + handoff + validation policy |
| 退出条件 | 这条线继续作为 M10 下的 supporting backlog，而不是主线里程碑 |

### M10

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加由项目技术负责人（PTL）驱动的战略评估层 |
| 依赖 | M7 + 已批准的战略方向 |
| 退出条件 | roadmap / 治理 / 架构调整建议成为由 durable 控制面和 review 规则支撑的战略输出 |

### M11

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加由项目技术负责人（PTL）驱动的程序编排层 |
| 依赖 | M10 + durable program board |
| 退出条件 | 系统能协调多个相关切片，而不是持续依赖人工输入“继续”；当前先成立单 Codex 编排真相层，多执行器调度留待后续证据驱动 |

### M12

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | done |
| 目标 | 增加由项目技术负责人（PTL）驱动的受监督长期自动交付层 |
| 依赖 | M11 + 稳定升级策略 |
| 退出条件 | 长期交付能持续推进到真正的业务裁决点 |

## 当前下一步

| 下一步 | 为什么做 |
| --- | --- |
| 继续从 `close-m12-and-open-rollout` 之后恢复 | M12 已经完成；下一个 durable 问题是怎样让 rollout / 摩擦证据决定 post-M12 里程碑或 supporting backlog 回流 |

## 战略方向

| 主题 | 范围 | 当前位置 |
| --- | --- | --- |
| 业务规划与程序编排层 | `project-assistant` 已完成以项目技术负责人（PTL）为核心的战略评估层、程序编排层和长期受监督交付层；当前进入 rollout / 摩擦采集阶段；M8/M9 继续作为 supporting backlog 挂在这条主线之下 | active |

方向文档：

- [业务规划与程序编排方向](strategic-planning-and-program-orchestration.zh-CN.md)
