# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-12`

## Current Phase

`post-M16 rollout verification active`

## Active Slice
`verify-unified-front-door-rollout-on-legacy-repos`

## Current Execution Line
- Objective: 在代表性旧代际仓库上继续验证统一前门：`continue / progress / handoff` 会先升级到当前控制面代际，再输出结构化第一屏，并把剩余摩擦明确区分为 repo 层问题还是宿主桥接问题
- Plan Link: verify-unified-front-door-rollout-on-legacy-repos
- Runway: one checkpoint covering legacy-repo rollout evidence, host-bridge gap isolation, and next-step routing
- Progress: 4 / 6 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment

## Execution Tasks
- [x] EL-1 confirm the rollout objective for `verify-unified-front-door-rollout-on-legacy-repos`: 证明旧代际仓库会先升级再输出结构化第一屏
- [x] EL-2 verify dependencies and affected boundaries: `project_assistant_entry.py`、`sync_resume_readiness.py`、`continue / progress / handoff` entry、README、architecture、roadmap、development plan、`.codex/entry-routing.md`
- [x] EL-3 confirm architecture signal, host-bridge boundary, and correct layer still hold
- [x] EL-4 validate representative medium / large legacy repos through the unified front door
- [ ] EL-5 isolate the remaining host-bridge gap and decide the next concrete bridge step
- [ ] EL-6 keep rollout evidence and next-step routing aligned across control truth and docs

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Last Entry: docs/devlog/2026-04-12-close-m16-tool-first-front-door-and-entry-routing.md

## Architecture Supervision
- Signal: `yellow`
- Signal Basis: repo 层统一前门已收口，但真实桌面 task / 新 session 仍可能绕过这条前门，所以当前还需要保持 rollout / bridge 摩擦可见
- Root Cause Hypothesis: 当前剩余问题已经从 repo 脚本能力转成宿主 / 工具桥接问题；继续用 repo 内文案修补已经不能单独解决桌面真实入口绕过前门的问题
- Correct Layer: `.codex/entry-routing.md`、architecture、rollout evidence、宿主 / 插件桥接设计，而不是继续只改 snapshot 文案
- Automatic Review Trigger: 当真实 task / 新 session 再次绕过统一前门时自动触发
- Escalation Gate: raise but continue

## Current Escalation State
- Current Gate: raise but continue
- Reason: repo 层统一前门已完成，但真实桌面桥接仍需继续采证和隔离问题
- Next Review Trigger: review again when blockers change, the active slice rolls forward, or release-facing work begins

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
- M16 `tool-first front door and hard-entry bridge` 已关闭：
  - `project_assistant_entry.py`、`bin/project-assistant` 与 `.codex/entry-routing.md` 已成为 durable 的统一前门
  - `sync_entry_routing.py` 与 `validate_entry_routing.py` 已建立
  - `continue / progress / handoff` 现在共享前门、版本 preflight 与结构化第一屏契约
  - README、architecture、roadmap、development plan、usage 和控制面都把 M16 视为已完成里程碑

## In Progress

- post-M16 rollout verification 已激活：当前主线是在更多旧代际仓库上验证统一前门是否总是先升级再输出结构化面板
- supporting backlog 再吸收判断仍在后续：`M8 / M9` 何时回主线，继续以跨 repo 证据为准

## Blockers / Open Decisions

- None currently.
- Follow-up: 自动压缩上下文仍是后续专题，目标是在不丢 durable 恢复信息的前提下，分层压缩 `continue / progress / handoff` 的输出体量与重复内容
- Follow-up: 只有当 post-M16 证据证明单 Codex PTL 模式已经成为瓶颈时，才考虑打开 M15
- Follow-up: 把“当前问题 -> 解决思路 -> 方案 -> devlog -> architecture -> roadmap / development plan -> 一口气长任务实现”固化成默认行为；当 durable 问题被识别后，`project-assistant` 不应再依赖用户逐条提醒这套收口顺序

## Next 3 Actions

1. 把真实桌面 task / 新 session 仍可能绕过统一前门的行为正式收成 host-bridge evidence
2. 基于 rollout 证据设计下一步宿主 / 插件桥接方案，而不是继续只改 repo 文案
3. 继续把 `M8 / M9` 保持在 supporting backlog，并只在真正需要时再评估 `M15`
