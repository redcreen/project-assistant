# 路线图

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## 范围

这个路线图只描述 `project-assistant` skill 自身的演进，不替代 `.codex/status.md` 中的当前执行状态。


详细执行队列看这里：

- [project-assistant/development-plan.zh-CN.md](reference/project-assistant/development-plan.zh-CN.md)

## 当前 / 下一步 / 更后面

| 时间层级 | 重点 | 退出信号 |
| --- | --- | --- |
| 当前 | 按语言优化内部控制面输出 | 中文优先工作流减少冗余英文，同时不削弱公开文档双语和 AI 恢复精度 |
| 下一步 | 压缩 continue / resume 快照体量而不损失可恢复性 | `项目助手 继续` 更接近最小恢复包，不再重复 progress 内容 |
| 更后面 | 更丰富的验收规则、更好的恢复自动化、更多可视化 | 新仓库更少需要额外提示和人工覆盖命令 |

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
| [M8](reference/project-assistant/development-plan.zh-CN.md#m8) | active | 评估按语言裁剪内部控制面的可能性 | handoff + command templates + validation policy | 中文工作流能减少冗余英文而不削弱公开文档双语 |
| [M9](reference/project-assistant/development-plan.zh-CN.md#m9) | later | 压缩 continue / resume 快照体量而不损失可恢复性 | continue snapshot + handoff + validation policy | `项目助手 继续` 只保留最小恢复信息，不再重复 progress 内容 |

## 下一层提案里程碑

| 里程碑 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |
| [M10](reference/project-assistant/development-plan.zh-CN.md#m10) | proposed | 增加位于执行层之上的战略评估层 | [M8](reference/project-assistant/development-plan.zh-CN.md#m8) + [M9](reference/project-assistant/development-plan.zh-CN.md#m9) + durable 战略提案 | 系统能提出 roadmap / 治理 / 架构调整建议，但不会越权自动改业务方向 |
| [M11](reference/project-assistant/development-plan.zh-CN.md#m11) | proposed | 增加跨多个切片或执行器的程序编排层 | [M10](reference/project-assistant/development-plan.zh-CN.md#m10) + durable program board | 系统能协调多个相关切片，而不是持续依赖人工输入“继续” |
| [M12](reference/project-assistant/development-plan.zh-CN.md#m12) | proposed | 增加受监督的长期自动交付层 | [M11](reference/project-assistant/development-plan.zh-CN.md#m11) + 稳定升级策略 | 长期交付能持续推进到真正的业务裁决点，而不是在日常调度上不断停下来 |

## 里程碑流转

```mermaid
flowchart LR
    M1["M1 控制面"] --> M2["M2 收敛式整改"]
    M2 --> M3["M3 进展 + 交接"]
    M3 --> M4["M4 文档标准"]
    M4 --> M5["M5 公开文档双语"]
    M5 --> M6["M6 内嵌式架构师助手"]
    M6 --> M7["M7 更强叙事 + 自动触发"]
    M7 --> M8["M8 按语言优化内部输出"]
```

## 风险与依赖

- 文档同步脚本更擅长快速补齐结构，不一定能一次重写出最好的叙事质量
- 默认自动架构监督如果被过多实现细节污染，就会失去高层纠偏能力
- 长任务执行线必须停在真实检查点，不能变成不可见的后台黑箱
- 公开文档双语质量仍然依赖内容生成，不仅是文件对和切换链接
- 如果未来要支持精确 context 门禁，仍然需要运行时暴露对应指标
- `继续` 快照现在仍然偏重，后续需要继续收敛成“最小恢复包”，而不是第二个迷你 dashboard

## 战略跟进专题

| 主题 | 为什么重要 | 何时再讨论 |
| --- | --- | --- |
| 业务规划与程序编排层 | 评估 `project-assistant` 是否需要一层更高阶的规划 / 监督角色，用来判断项目后续怎么走、何时插入治理或架构专项、是否需要调整既有里程碑或项目定位，以及如何让人类更多聚焦业务方向而不是持续盯开发过程 | 等 M8 和 M9 收口后再展开；先出方案、经过 review，再决定是否转成正式里程碑或 development-plan 项目 |

提案文档：

- [业务规划与程序编排提案](reference/project-assistant/strategic-planning-and-program-orchestration-proposal.zh-CN.md)
