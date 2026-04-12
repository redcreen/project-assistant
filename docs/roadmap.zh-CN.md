# 路线图

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## 范围

这个路线图只描述 `project-assistant` skill 自身的演进，不替代 `.codex/status.md` 中的当前执行状态。


详细执行队列看这里：

- [project-assistant/development-plan.zh-CN.md](reference/project-assistant/development-plan.zh-CN.md)

## 当前 / 下一步 / 更后面

| 时间层级 | 重点 | 退出信号 |
| --- | --- | --- |
| 当前 | 把完整分层模型带到更多仓库上试跑，收集 rollout 摩擦，并保持 strategy / program / delivery 三层控制面一致 | M12 已关闭，rollout 证据开始替代内部拍脑袋命名下一里程碑 |
| 下一步 | 根据 rollout 证据决定是否需要新的 post-M12 里程碑、是否让 supporting backlog 局部回流，或是否要进入多执行器调度层 | 下一条命名里程碑只来自重复出现的 rollout 摩擦，而不是内部猜测 |
| 更后面 | 只在 rollout 证据足够时，再把 M8/M9 这类 supporting backlog 议题按受控方式并入主线 | 在真实 adoption 证据出现前，supporting backlog 不会无计划回流主线 |

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
| [M9](reference/project-assistant/development-plan.zh-CN.md#m9) | deferred | 压缩 continue / resume 快照体量而不损失可恢复性 | continue snapshot + handoff + validation policy | 转成 M10 下的 supporting backlog，而不是继续占据主线 |

## 战略层里程碑

| 里程碑 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |
| [M10](reference/project-assistant/development-plan.zh-CN.md#m10) | done | 增加位于执行层之上的战略评估层 | [M7](reference/project-assistant/development-plan.zh-CN.md#m7) + 已批准的战略方向 | 系统能产出 durable 战略判断、识别何时应插入治理/架构专项，并把业务方向变更继续交给人类审批 |
| [M11](reference/project-assistant/development-plan.zh-CN.md#m11) | done | 增加跨多个切片或执行器的程序编排层 | [M10](reference/project-assistant/development-plan.zh-CN.md#m10) + durable program board | 系统能协调多个相关切片，而不是持续依赖人工输入“继续” |
| [M12](reference/project-assistant/development-plan.zh-CN.md#m12) | done | 增加受监督的长期自动交付层 | [M11](reference/project-assistant/development-plan.zh-CN.md#m11) + 稳定升级策略 | 长期交付能持续推进到真正的业务裁决点，而不是在日常调度上不断停下来 |

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
```

## 风险与依赖

- 文档同步脚本更擅长快速补齐结构，不一定能一次重写出最好的叙事质量
- 默认自动架构监督如果被过多实现细节污染，就会失去高层纠偏能力
- 长任务执行线必须停在真实检查点，不能变成不可见的后台黑箱
- 公开文档双语质量仍然依赖内容生成，不仅是文件对和切换链接
- 如果未来要支持精确 context 门禁，仍然需要运行时暴露对应指标
- `M8 / M9` 提到的问题仍然重要，但现在作为 `M10` 下的 supporting backlog 管理，而不是继续占据主线
- 战略层必须持续基于 repo 证据给出判断，不能越权自动改变业务方向
- 程序编排层必须等战略层的 review 合约稳定后再落地
- `M11` 当前先收口“单 Codex 编排真相层”；如果未来要扩到多桌面 Codex / 多执行器自动调度，必须以 rollout 证据单独立项
- 任何 post-M12 里程碑都应来自重复的 rollout 摩擦，而不是在没有证据时重开已关闭层

## 战略方向

| 主题 | 为什么重要 | 当前位置 |
| --- | --- | --- |
| 业务规划与程序编排层 | `project-assistant` 已经完成 `M10` 战略评估层、`M11` 程序编排层和 `M12` 长期受监督交付层；当前重点转为 rollout / 摩擦采集，`M8 / M9` 继续作为 supporting backlog 等待被受控吸收 | 已进入 roadmap 和 development plan |

方向文档：

- [业务规划与程序编排方向](reference/project-assistant/strategic-planning-and-program-orchestration.zh-CN.md)
