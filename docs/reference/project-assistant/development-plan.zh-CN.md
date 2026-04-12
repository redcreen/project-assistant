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
| 当前阶段 | `narrative quality and automated architecture triggers` | 来自 `.codex/plan.md` 的当前维护阶段 |
| 当前切片 | `tighten-maintainer-facing-narrative-and-architecture-triggers` | 当前执行线绑定的切片 |
| 当前执行线 | 收紧 maintainer-facing narrative，减少 `progress / continue / handoff` 里的 AI-centric 表达，并把至少一条架构升级触发从“手工识别”变成自动信号 | 当前这轮真正要收口的工作 |
| 当前验证 | representative medium + large repo snapshots 可读；`deep` / `release` 继续通过 | 继续前如何证明这条线已收口 |

## 阶段总览

| 阶段 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |
| M1 | done | 建立 `.codex` 控制面与项目分级 | core skill routing | 当前状态可恢复 |
| M2 | done | 建立收敛式 retrofit | control-surface scripts | 整改不再停在中间态 |
| M3 | done | 建立进展与交接工作流 | module layer + snapshot scripts | 进展和交接稳定可用 |
| M4 | done | 建立 durable 文档标准与文档校验 | document standards + docs scripts | durable 文档通过结构门禁 |
| M5 | done | 建立公开文档双语切换与验收 | i18n rules + i18n validator | 公开文档可在中英文之间稳定切换 |
| M6 | done | 收敛成内嵌式架构师助手工作模型 | previous milestones | 规划、执行、架构监督和开发日志成为默认自动能力 |
| M7 | active | 提升叙事质量与自动架构触发能力 | M6 | 整改后的手工清理更少，方向纠偏提示更少 |
| M8 | later | 评估按语言裁剪内部控制面的可能性 | handoff + command templates + validation policy | 中文工作流能减少冗余英文而不削弱公开文档双语 |
| M9 | later | 压缩 continue / resume 快照体量而不损失可恢复性 | continue snapshot + handoff + validation policy | `项目助手 继续` 只保留最小恢复信息，不再重复 progress 内容 |

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
| 10 | `tighten-maintainer-facing-narrative-and-architecture-triggers` | 当前 | n/a | n/a |

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
| 当前状态 | active |
| 目标 | 提升叙事质量与自动架构触发能力 |
| 依赖 | M6 |
| 退出条件 | 整改后的手工清理更少，方向纠偏提示更少 |

### M8

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | later |
| 目标 | 评估按语言裁剪内部控制面的可能性 |
| 依赖 | handoff + command templates + validation policy |
| 退出条件 | 中文工作流能减少冗余英文而不削弱公开文档双语 |

### M9

| 项目 | 当前值 |
| --- | --- |
| 当前状态 | later |
| 目标 | 压缩 continue / resume 快照体量而不损失可恢复性 |
| 依赖 | continue snapshot + handoff + validation policy |
| 退出条件 | `项目助手 继续` 只保留最小恢复信息，不再重复 progress 内容 |

## 当前下一步

| 下一步 | 为什么做 |
| --- | --- |
| 继续从 `tighten-maintainer-facing-narrative-and-architecture-triggers` 之后恢复 | 当前执行线已经把真实恢复点固定在 `.codex/plan.md` 里 |
