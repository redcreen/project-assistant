# Plan

## Current Phase

`strategic evaluation layer foundation`

## Current Execution Line
- Objective: 把战略规划层从“待讨论提案”升级成正式方向，建立第一份 durable strategy surface 和 review contract，并把 M8/M9 收进 supporting backlog 而不是继续占据主线
- Plan Link: establish-strategy-surface-and-review-contract
- Runway: one checkpoint covering strategy-surface creation, docs alignment, validation, and state refresh
- Progress: 9 / 9 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment
- Validation: 战略方向文档、README、roadmap、development plan 与控制面一致；`.codex/strategy.md` 已存在；`deep` 继续通过

## Architecture Supervision
- Signal: `green`
- Signal Basis: no blocker or escalation trigger is currently forcing a higher-level decision
- Problem Class: 执行层和治理层已经较完整，但缺少更高层的战略判断面来决定项目后续怎么走、何时插专项、何时改 roadmap
- Root Cause Hypothesis: 现在最大的缺口不再是单个执行功能，而是没有 durable 的战略层把“项目接下来怎么走”沉淀成 repo 真相
- Correct Layer: durable strategy surface、roadmap / development-plan / README narrative、review contract、future program board entry
- Rejected Shortcut: 继续把战略问题塞进 status 的 follow-up 或聊天讨论，而不建立一等的战略控制面
- Automatic Review Trigger: no automatic trigger is currently active
- Escalation Gate: continue automatically

## Escalation Model

- Continue Automatically: 当前工作是在已批准的战略方向内补齐控制面、文档和 review 边界，不改变业务方向
- Raise But Continue: 出现监督信号偏黄、但仍能在既定战略方向内收敛时，先记录风险再继续
- Require User Decision: 需要改变业务方向、兼容性承诺、外部定位或显著成本 / 时间边界时，必须停下来等用户裁决

## Execution Tasks
- [x] EL-1 confirm the checkpoint and objective for `establish-strategy-surface-and-review-contract`: 把战略规划层升级成正式方向，并让 repo 真相能承载这个方向
- [x] EL-2 verify dependencies and affected boundaries: roadmap / development-plan / README / `.codex/status.md` / `.codex/plan.md` / future strategy surface
- [x] EL-3 confirm architecture signal, root-cause hypothesis, and correct layer still hold
- [x] EL-4 create the first durable strategy surface and define what it owns
- [x] EL-5 define how M8 and M9 survive as supporting backlog topics under M10 instead of remaining mainline milestones
- [x] EL-6 update docs, control-surface notes, and strategic direction links
- [x] EL-7 run validation: strategic docs and control truth align; `deep` continues to pass
- [x] EL-8 refresh progress, next checkpoint, and next 3 actions for M10
- [x] EL-9 capture a devlog entry because the roadmap and current direction changed

## Development Log Capture
- Trigger Level: high
- Auto-Capture When:
  - the root-cause hypothesis changes
  - a reusable mechanism replaces repeated local fixes
  - a retrofit changes governance, architecture, release policy, or strategic direction
  - a tradeoff or rejected shortcut is likely to matter in future work
- Skip When:
  - the change is mechanical or formatting-only
  - no durable reasoning changed
  - the work simply followed an already-approved path
  - the change stayed local and introduced no durable tradeoff

## Slices

- Slice: activate-m10-strategic-evaluation-layer
  - Objective: 把战略规划与程序编排从“后续提案”提升成正式方向，并让 roadmap / README / development-plan / control truth 指向同一个当前主线
  - Dependencies: 战略方向文档、roadmap、development plan、README、status / plan
  - Risks: 文档和控制面继续各说各话；M8/M9 看起来像被放弃，而不是被纳入 supporting backlog
  - Validation: 文档入口统一；M10 active；M8/M9 deferred；`deep` 通过
  - Exit Condition: 所有 maintainer-facing 入口都把 M10 视为当前主线

- Slice: establish-strategy-surface-and-review-contract
  - Objective: 创建第一份 durable strategy surface，定义战略层拥有的边界，以及哪些问题必须继续升级给人类
  - Dependencies: `.codex/strategy.md`、roadmap、development plan、README
  - Risks: 战略层越权；program orchestration 过早上场；M8/M9 supporting backlog 重新漂回主线
  - Validation: `.codex/strategy.md` 存在且可读；docs 与 control truth 对齐；`deep` 通过
  - Exit Condition: repo 里已经有一份一等的战略控制面，而不是继续靠聊天或 follow-up 维持方向

- Slice: define-strategy-evidence-and-review-contract
  - Objective: 定义战略建议必须引用哪些 durable repo 证据，以及什么情况下战略层可以建议插入治理 / 架构专项
  - Dependencies: `.codex/strategy.md`、devlog、roadmap、current repo evidence
  - Risks: 战略建议再次变成空泛直觉；没有 review 合约就直接过渡到程序编排
  - Validation: 有明确 evidence contract；有明确 human approval boundary；M11 仍保持未激活
  - Exit Condition: M10 的战略判断机制可复用、可审阅、可恢复
