# Architecture Retrofit

## Trigger

- Tier: `medium`
- Active Slice: `automate supervision, release protection, and human windows`
- Current Execution Line: 把自动架构信号、更严格发布保护，以及更收敛的人类窗口一起落到执行层
- Architecture Signal: `green`
- Escalation Gate: `continue automatically`

## Primary Symptoms

- architecture direction is viable, but the repo still benefits from an explicit retrofit plan before structural changes

## Root-Cause Drivers

- Root Cause Hypothesis: 如果这些能力分散在文档、脚本和输出层里而不共享同一判断逻辑，系统很快又会回到局部 patch 驱动
- Signal Basis: no blocker or escalation trigger is currently forcing a higher-level decision
- Correct Layer: shared control-surface logic, release gates, and human-facing reporting
- Rejected Shortcut: 只在 README 或帮助菜单里描述新模型，而不把它编码进脚本、门禁和控制面

## Affected Boundaries

- control surface (`.codex/plan.md`, `.codex/status.md`, `.codex/brief.md`)
- canonical architecture ownership (`docs/architecture*.md` and doc-governance question owners)
- execution slices and architecture supervision state
- tests and validation gates that enforce the intended architecture
- CI and release workflows that should enforce the corrected architecture path

## Current Architecture Sources

- Canonical Owners:
- docs/architecture.md
- docs/architecture.zh-CN.md
- Additional Architecture-Like Docs:
- none

## Current Risks / Open Decisions

- none

## Target Architecture

- Keep one canonical architecture owner set and make all other architecture-like docs either reference, workstream, or archive material.
- Ensure execution, validation, and reporting all reflect the same root-cause hypothesis and correct layer.
- When the repo has first-class modules, keep the module layer aligned with the target architecture instead of letting module docs drift away from the source of truth.
- Treat architecture retrofit as a boundary correction exercise, not a chain of local bug fixes.

## Retrofit Scope

- move the architectural source of truth to one canonical owner set and demote duplicates to reference or archive
- replace local-only fixes with a reusable mechanism in the correct layer
- align execution slices, documentation, tests, and gates with the corrected architecture direction
- refresh progress and handoff outputs so the corrected architecture remains visible during execution
- align CI and release protection with the corrected architecture assumptions

## Execution Strategy

- audit the current architecture signal, canonical owner docs, and duplicate architecture-like documents
- write down the target boundaries, correct layer, and rejected shortcuts before editing implementation details
- slice the retrofit so each slice changes one meaningful boundary and has explicit validation
- run `deep` gates during convergence and `release` gates before any architecture-sensitive release

## Validation

- `python3 scripts/validate_gate_set.py /path/to/repo --profile deep` passes
- architecture signal is green or explicitly justified before closing the retrofit
- release-sensitive changes also pass `python3 scripts/validate_gate_set.py /path/to/repo --profile release`
- progress and handoff reflect the corrected architecture signal and active execution line

## Exit Conditions

- one canonical architecture owner set answers the main architecture question
- duplicate or conflicting architecture docs no longer compete as active owners
- execution slices and control-surface artifacts reflect the corrected layer and root cause
- the retrofit leaves behind fewer local-only fixes and clearer boundaries than it started with

## Usable Now

- 恢复当前状态与下一步
- 长任务执行线与可见任务板
- 默认架构监督与升级 gate
- 自动架构信号更新
- 架构整改审计与工作底稿
- 文档整改与 Markdown 治理
- 开发日志索引与自动沉淀
- 公开文档中英文切换
- CI deep 门禁
- CI release readiness 门禁
- CI 更严格发布保护门禁
- 版本发布与 tag 安装地址
