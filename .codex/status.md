# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-13`

## Current Phase

`M17-M21 daemon-host mainline planning ready`

## Active Slice
`define-m17-through-m21-daemon-host-mainline`

## Current Execution Line
- Objective: 把首版快升级版正式抬成 `M17-M21` 里程碑主线：`M17 daemon core -> M18 VS Code host -> M19 resume bridge -> M20 validation -> M21 rollout resume`
- Plan Link: define-m17-through-m21-daemon-host-mainline
- Runway: one checkpoint covering implementation order, first host choice, resume capability level, and local-workspace validation boundary
- Progress: 4 / 4 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - first implementation slice, first host boundary, or resume level needs user judgment

## Execution Tasks
- [x] EL-1 record the latency problem, user pain, and hard requirements in a durable markdown note
- [x] EL-2 promote the issue into a named initiative with a dedicated design note and control-truth entry
- [x] EL-3 discuss options with the user and choose `daemon-first, write-safe, async-by-default` as the target architecture
- [x] EL-4 define the `M17-M21` milestone order for the daemon-host mainline and sync it into roadmap / plan

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Last Entry: docs/devlog/2026-04-13-daemon-first.md

## Architecture Supervision
- Signal: `yellow`
- Signal Basis: 用户已经明确要求先看 roadmap / plan 再按切片下实现指令。当前方向已经从“抽象讨论 daemon 是否值得做”收口到“围绕 daemon core + VS Code host MVP 的明确实现顺序”。同时，`host resume bridge` 已确认应以 VS Code 扩展宿主前端为首选，而不是去赌聊天框注入。
- Root Cause Hypothesis: 当前最伤体验的不是单点脚本时延，而是缺少常驻调度层和宿主恢复桥，导致支撑任务、恢复动作和 live 状态展示都还和主写入线耦合在一起。
- Correct Layer: daemon runtime、queue/event schema、foreground gate、VS Code host shell、resume bridge、live status surfaces，以及之后的本地工作区验证与旧功能回归。
- Automatic Review Trigger: 当首版宿主选择、resume 能力级别、daemon/host 边界或旧功能回归顺序发生变化时自动触发
- Escalation Gate: raise but continue

## Current Escalation State
- Current Gate: require user decision
- Reason: 规划已收口到可开发切片；下一步应由用户点名先开哪一刀，而不是默认同时展开 daemon core、宿主前端和恢复桥
- Next Review Trigger: review again when the user selects the first implementation slice or changes the default build order

## Done

- bootstrap / retrofit latency 快修已完成一轮：
  - `sync_docs_system.py` 与 `sync_markdown_governance.py` 不再无条件重复 bootstrap control surface
  - `sync_control_surface.py` 现在会一次性补齐 `entry-routing`
  - `project_assistant_entry.py` 已覆盖 `bootstrap / retrofit / docs-retrofit`，并把这几条入口收成统一前门
  - `scripts/benchmark_latency.py` 现在能同时量 baseline 与 front-door path，并显示宿主调用轮次
- daemon-first 方向已确认：
  - `docs/reference/project-assistant/async-execution-and-latency-governance*.md` 已改成 daemon-first 主方案
  - `docs/reference/project-assistant/ptl-daemon-mvp*.md` 已定义快升级版边界
  - 当前策略已明确为：先发一版让编码速度快起来，再在 daemon 基线上逐项验证旧功能
- host resume bridge 方向已确认：
  - `docs/reference/project-assistant/host-resume-bridge*.md` 已把 `daemon -> host -> Codex -> UI` 的边界、恢复能力分级和 VS Code 扩展可行性写清楚
  - 当前推荐路径已明确为：先做 VS Code 扩展宿主前端，不把“往聊天框里自动写继续”当主架构
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

- daemon-first 快升级规划已收口：当前已把首版实现顺序拆成 `daemon core -> VS Code host shell -> resume bridge -> local validation -> old-feature re-validation`
- post-M16 rollout verification 暂时继续停在下一条恢复线：等异步治理方向确认后再恢复 host-bridge 证据采集

## Blockers / Open Decisions

- None currently.
- Follow-up: `M17 / build-ptl-daemon-runtime-core` 是否只先收 CLI + socket + queue store，还是连第一批 worker 也一起带上
- Follow-up: `M18 / build-vscode-host-shell-and-live-status` 首版是否只收 Tree View + Status Bar + Output channel，还是连 Webview dashboard 一起带上
- Follow-up: `M19 / wire-manual-and-one-click-continue` 首版是否默认只收 `manual continue`，还是把保守的 `one-click continue` 也一起收进第一批
- Follow-up: 自动压缩上下文仍是后续专题，目标是在不丢 durable 恢复信息的前提下，分层压缩 `continue / progress / handoff` 的输出体量与重复内容
- Follow-up: 只有当 post-M16 证据证明单 Codex PTL 模式已经成为瓶颈时，才考虑打开 M15
- Follow-up: 把“当前问题 -> 解决思路 -> 方案 -> devlog -> architecture -> roadmap / development plan -> 一口气长任务实现”固化成默认行为；当 durable 问题被识别后，`project-assistant` 不应再依赖用户逐条提醒这套收口顺序
- Follow-up: 控制面真相同步确定性仍需专题收口；当用户执行 `项目助手 继续` 时，`status / plan / strategy / program-board / delivery / PTL / handoff / progress / continue` 之间不应再出现刷新先后不一致或“部分已更新、部分仍落后”的滞后感

## Next 3 Actions

1. `M17 / build-ptl-daemon-runtime-core`
2. `M18 / build-vscode-host-shell-and-live-status`
3. `M19 / wire-manual-and-one-click-continue`
