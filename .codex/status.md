# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-12`

## Current Phase

`PTL supervision and worker handoff layers closed; M15 evidence collection queued`

## Active Slice
`close-m13-and-m14-and-queue-m15-evidence`

## Current Execution Line
- Objective: 收口 M13 PTL 监督环与 M14 worker 接续层，把 PTL supervision 和 worker handoff / re-entry 都沉淀成 durable 控制面、门禁与维护者展示，并把下一步切到“是否真的需要 M15”的证据采集，而不是直接承诺多执行器
- Plan Link: close-m13-and-m14-and-queue-m15-evidence
- Runway: one checkpoint covering M13 closeout, M14 closeout, validation, and post-M14 evidence queueing
- Progress: 9 / 9 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment

## Execution Tasks
- [x] EL-1 confirm the closeout objective for `close-m13-and-m14-and-queue-m15-evidence`: 让 M13 / M14 从“路线图方向”升级成“PTL supervision、worker handoff、门禁、展示、文档都成立”
- [x] EL-2 verify dependencies and affected boundaries: PTL supervision sync / validate, worker handoff sync / validate, progress / continue / handoff, roadmap / development-plan / README, control truth
- [x] EL-3 confirm architecture signal, root-cause hypothesis, and correct layer still hold
- [x] EL-4 add a reusable PTL supervision sync path and a PTL supervision validator
- [x] EL-5 add a reusable worker handoff sync path and a worker handoff validator
- [x] EL-6 把 PTL supervision / worker handoff 摘要接入 `progress / continue / handoff`
- [x] EL-7 close M13 and M14 across README, roadmap, development plan, strategy docs, orchestration docs, and control truth
- [x] EL-8 运行验证：`deep` 与 `release` 在 M13 / M14 收口后继续通过
- [x] EL-9 capture a devlog entry because M13 / M14 are now complete and M15 remains evidence-gated

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Last Entry: docs/devlog/2026-04-12-close-m13-and-m14-ptl-supervision-and-worker-handoff.md

## Architecture Supervision
- Signal: `green`
- Signal Basis: no blocker or escalation trigger is currently forcing a higher-level decision
- Root Cause Hypothesis: 现在最大的缺口不再是“有没有 post-M12 方向”，而是 PTL 能不能在 worker 停下后真正接住项目，并把 handoff / re-entry 也写成 durable 真相
- Correct Layer: durable PTL supervision、worker handoff / re-entry、post-M14 evidence collection、future milestone selection
- Automatic Review Trigger: no automatic trigger is currently active
- Escalation Gate: continue automatically

## Current Escalation State
- Current Gate: continue automatically
- Reason: M13 / M14 已经关闭；后续仅剩“是否真的需要 M15”的证据采集，仍在既定方向内，可以继续推进而不需要新的用户级取舍
- Next Review Trigger: review again when post-M14 evidence suggests M15 is justified, a supporting backlog topic re-enters the mainline, or a business-direction tradeoff appears

## Done

- M6 `embedded architect-assistant operating model` 已关闭：
  - 规划、执行、架构监督和开发日志都已成为默认自动能力
  - 代表性整改流 `整改 / 文档整改 / 架构整改` 已在真实仓库上跑通
  - `progress`、`handoff`、控制面、README 和门禁已经能表达同一套基本真相
- M7 `narrative quality and automated architecture triggers` 已关闭：
  - representative medium / large repo 的第一屏输出已经更接近维护者恢复面板，而不是 AI-only status dump
  - `progress / continue / handoff` 的 maintainer-facing wording contract 已落到脚本和代表性仓库验证里
  - 至少一条 ownership / boundary / repeated-fix drift 路径已经可以自动升级成 architecture-review trigger
- M10 `strategic evaluation layer` 已关闭：
  - `.codex/strategy.md` 已从手工文档变成 durable 战略控制面
  - `sync_strategy_surface.py` 与 `validate_strategy_surface.py` 已建立
  - `progress / continue / handoff` 现在都能直接显示战略视角
  - README、roadmap、development plan、控制面和文档导航都把 M10 视为已完成里程碑
  - `M8 / M9` 仍保留为 supporting backlog，不再继续占据主线
- M11 `program orchestration` 已关闭：
  - `.codex/program-board.md` 已成为 durable 程序编排控制面
  - `sync_program_board.py` 与 `validate_program_board.py` 已建立
  - `progress / continue / handoff` 现在都能直接显示程序编排视角
  - README、roadmap、development plan、控制面和文档导航都把 M11 视为已完成里程碑
  - `M8 / M9` 继续保持在 supporting backlog，不会无计划回流主线
- M12 `supervised long-run delivery` 已关闭：
  - `.codex/delivery-supervision.md` 已成为 durable 长期监督交付控制面
  - `sync_delivery_supervision.py` 与 `validate_delivery_supervision.py` 已建立
  - `progress / continue / handoff` 现在都能直接显示长期交付视角
  - README、roadmap、development plan、控制面和文档导航都把 M12 视为已完成里程碑
  - 后续状态已切到 rollout / 摩擦采集，而不是继续停在内部主线里程碑
- M13 `PTL supervision loop` 已关闭：
  - `.codex/ptl-supervision.md` 已成为 durable 的 PTL 监督控制面
  - `sync_ptl_supervision.py` 与 `validate_ptl_supervision.py` 已建立
  - `progress / continue / handoff` 现在都能直接显示 PTL 监督视角
  - README、roadmap、development plan、战略文档、编排模型和控制面都把 M13 视为已完成里程碑
- M14 `worker handoff and re-entry` 已关闭：
  - `.codex/worker-handoff.md` 已成为 durable 的 worker 接续与回流控制面
  - `sync_worker_handoff.py` 与 `validate_worker_handoff.py` 已建立
  - `progress / continue / handoff` 现在都能直接显示 handoff / re-entry 视角
  - README、roadmap、development plan、战略文档、编排模型和控制面都把 M14 视为已完成里程碑
  - M15 明确保持为 evidence-gated later 层，而不是被提前当成当前能力

## In Progress

- post-M14 evidence collection 已排队：下一步是把完整的 PTL supervision + worker handoff 模型带到更多 repo 上，并记录是否真的需要 M15
- supporting backlog 再吸收判断仍在后续：`M8 / M9` 何时回主线，继续以跨 repo 证据为准

## Blockers / Open Decisions

- None currently.
- Follow-up: `项目助手 继续` 当前仍偏重，继续评估如何在不丢恢复信息的前提下压缩输出体量和重复内容
- Follow-up: 只有当 post-M14 证据证明单 Codex PTL 模式已经成为瓶颈时，才考虑打开 M15

## Next 3 Actions

1. 在更多 medium / large 仓库上使用完整的 PTL supervision + worker handoff 模型，并记录 worker 停下后的真实接续摩擦
2. 根据真实跨 repo 证据决定 `M8 / M9` 是否继续保持在 supporting backlog
3. 当证据显示单 Codex PTL 模式真的成为瓶颈时，再决定是否需要 M15 选择性多执行器调度
