# Strategy

## Current Strategic Direction

- Direction: `strategic evaluation layer`
- Status: `active`
- Why Now: 执行层、整改层、文档治理层和恢复层已经基本成形，当前最大的缺口转成“项目后续怎么走、何时插专项、何时调整路线”的更高层判断

## What This Layer Owns

| Topic | Strategic Layer Owns? | Notes |
| --- | --- | --- |
| roadmap 调整建议 | yes | 但只提建议，不自动改业务方向 |
| 是否插入治理 / 架构专项 | yes | 需要基于 repo 证据和长期风险 |
| 项目定位是否需要提升 | yes | 作为建议输出，仍需人类审批 |
| 多个切片 / 多个执行器编排 | not yet | 留给 M11 |
| 长时间自动交付 | not yet | 留给 M12 |

## Carryover Backlog

| Topic | Current Position | Why It Is Not Mainline |
| --- | --- | --- |
| M8 locale-aware internal output | supporting backlog | 这是表现层优化，不再是当前最大缺口 |
| M9 slimmer continue snapshot | supporting backlog | 这是恢复体量优化，不再是当前最大缺口 |

## Human Review Boundary

- Human Approves:
  - business direction changes
  - compatibility promises
  - external positioning changes
  - significant cost or timeline tradeoffs
- System May Propose:
  - roadmap reshaping
  - governance / architecture side-tracks
  - milestone reorder suggestions
  - strategic carryover decisions for M8 / M9

## Next Strategic Checks

1. 定义战略判断必须引用哪些 durable repo 证据
2. 定义什么情况下战略层可以建议插入治理 / 架构专项
3. 先设计 M11 所需的 `program-board`，但不提前激活程序编排
