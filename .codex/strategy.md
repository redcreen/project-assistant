# Strategy

## Current Strategic Direction

- Direction: `strategic evaluation layer`
- Status: `done`
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

1. 在准备激活 M11 之前，先评审第一版 `program-board` 的 durable 结构和边界。
2. 当 roadmap 调整建议、治理专项或架构专项再次出现时，继续要求战略判断引用 durable repo 证据。
3. 继续确认 `M8 / M9` 是否保持在 supporting backlog，而不是被无计划地拉回主线。

## Strategy Evidence Contract
- 战略建议必须引用 roadmap、development plan、当前 `.codex/status.md` 和 `.codex/plan.md`，不能只凭聊天直觉。
- 如果建议插入治理专项或架构专项，必须说明触发它的 durable repo 证据，而不是只说“感觉应该做”。
- 如果建议调整 milestone 顺序，必须指出当前顺序哪里已经和真实执行不一致，以及调整后会减少什么长期风险。
- 如果问题跨到业务方向、兼容性承诺、外部定位或显著成本 / 时间边界，必须升级给人类裁决。
- 重要战略判断应落成 devlog，避免下一次回来时只剩结论没有推理链。

## Future Program-Board Boundary
- M10 owns strategic judgment, evidence-backed suggestions, and the human review boundary.
- M11 should own sequencing, orchestration, parallel-safe slices, and durable program-board state.
- Do not let M10 silently grow into full orchestration before the program-board contract exists.
