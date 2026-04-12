# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-12`

## Current Phase

`embedded architect-assistant redesign`

## Active Slice
`make architecture retrofit a first-class flow`

## Current Execution Line
- Objective: 把“架构整改”做成一等能力，补齐命令、脚本、工作底稿和门禁
- Plan Link: make architecture retrofit a first-class flow
- Runway: 完成架构整改审计脚本、工作底稿、门禁、菜单入口和控制面收口
- Progress: 8 / 8 tasks complete
- Stop Conditions:
  - `项目助手 架构 整改` / `project assistant architecture retrofit` 已成为正式入口
  - `.codex/architecture-retrofit.md` 能由脚本生成并通过门禁
  - `deep` 门禁与能力快照都能识别架构整改能力

## Execution Tasks
- [x] EL-1 增加 `项目助手 架构 整改` / `project assistant architecture retrofit` 入口
- [x] EL-2 新增 `sync_architecture_retrofit.py` 生成 `.codex/architecture-retrofit.md`
- [x] EL-3 新增 `validate_architecture_retrofit.py`，禁止工作底稿停在模板态
- [x] EL-4 把架构整改接入 `deep` 门禁和能力快照
- [x] EL-5 更新 `SKILL.md`、retrofit/usage/help-menu/README/模板
- [x] EL-6 更新控制面模板和命令速查，接入架构整改入口
- [x] EL-7 在 skill 自己身上生成真实的架构整改工作底稿
- [x] EL-8 写入 durable devlog 并跑通 `deep` / `release`

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Last Entry: docs/devlog/2026-04-12-make-architecture-retrofit-a-first-class-project-assistant-flow.md

## Architecture Supervision
- Signal: `green`
- Signal Basis: 架构整改已经有命令入口、脚本工作底稿和校验门禁，当前方向可以继续自动推进
- Root Cause Hypothesis: 如果没有一条 architecture-first 的整改流，assistant 只会做普通整改或局部 review，难以系统性修正边界和错误层级
- Correct Layer: architecture retrofit working note, control surface, validation gates, and command surface
- Escalation Gate: continue automatically

## Current Escalation State
- Current Gate: continue automatically
- Reason: current execution can proceed inside the existing direction without a user-level tradeoff
- Next Review Trigger: review again when blockers change, the active slice rolls forward, or release-facing work begins

## Done

- `project-assistant` 已支持：
  - 控制面整改
  - 模块层进展面板
  - 上下文恢复包
  - 文档系统规范
  - 开发日志索引、写入脚本和门禁
  - 开发日志触发强度控制面
  - `项目助手 架构` 统一父命令与子命令入口
  - 架构审查默认先看高层包，再按需下钻代码证据
  - 规划/执行语义已引入“当前执行线（execution line）”
  - `sync_execution_line.py` 自动生成更长的执行线任务板
  - `sync_architecture_supervision.py` 自动刷新架构信号与升级 gate
  - `sync_architecture_retrofit.py` 生成架构整改工作底稿
  - `capability_snapshot.py` 输出“现在可用能力”快照
  - `validate_release_readiness.py` 发布就绪门禁
  - `validate_architecture_retrofit.py` 校验架构整改工作底稿
  - `.github/workflows/deep-gate.yml` CI deep 门禁
  - `.github/workflows/release-readiness.yml` CI release readiness 门禁
  - `.github/workflows/release-protection.yml` CI 更严格发布保护门禁
  - `validate_gate_set.py --profile release` 更严格发布保护口径
  - 人工命令面已收敛成四个主窗口：菜单 / 进展 / 架构 / 开发日志
- `validate_docs_system.py` 与 `sync_docs_system.py` 已落地
- 文档规范已固化到：
  - `references/document-standards.md`
  - `references/templates.md`
  - `SKILL.md`
- `项目助手 整改` 已默认包含文档整改
- `项目助手 文档整改` 已作为独立短指令加入
- `deep` 门禁当前包含：
  - 文档结构
  - 文档质量
  - 控制面质量
  - 开发日志质量

## In Progress

- 把 `project-assistant` 从“命令驱动 skill”继续收敛成“默认自动推进的 AI 工程系统”
- 继续把自动架构监督从控制面同步推进到更多执行触发点
- 继续收紧人工命令面与自动开发日志边界

## Blockers / Open Decisions

- None currently.

## Next 3 Actions

1. 把自动架构信号继续接到更多整改与执行入口，减少“写了规则但没刷新状态”的窗口
2. 在代表性项目上试跑 `项目助手 架构 整改`，验证 working note 和实际整改节奏是否匹配
3. 把“现在可用能力”快照进一步做成周期性状态汇报的一部分
