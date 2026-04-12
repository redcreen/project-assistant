# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-12`

## Current Phase

`embedded architect-assistant redesign`

## Active Slice
`prepare project-assistant for broader repo adoption`

## Current Execution Line
- Objective: 从更高层自审 `project-assistant`，把控制面真相、README 对外表述和 rollout-ready 信号收口到一致状态
- Plan Link: prepare project-assistant for broader repo adoption
- Runway: 收口自审发现的 stale control truth，明确“现在能直接用什么”，并把 README 调整成更适合推广到其他项目的入口
- Progress: 5 / 5 tasks complete
- Stop Conditions:
  - `.codex/status.md`、`.codex/plan.md`、`progress`、`handoff` 不再停留在上一条已完成 slice
  - README 已能明确表达“什么已经稳定可用”与“何时用 retrofit / architecture retrofit”
  - `deep`、`release`、能力快照和 progress/handoff 都反映同一套 readiness truth

## Execution Tasks
- [x] EL-1 复核 control surface、README、docs 入口和门禁输出，定位真实剩余问题
- [x] EL-2 把 `.codex/status.md` 和 `.codex/plan.md` 从旧 slice 切到 broader-repo adoption readiness
- [x] EL-3 更新 README / README.zh-CN，明确 stable workflows 与 rollout guidance
- [x] EL-4 写入 durable devlog，记录这次自审为什么重点收口 control truth 而不是继续加功能
- [x] EL-5 重跑 `capability_snapshot`、`progress_snapshot`、`context_handoff`、`deep`、`release`

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Last Entry: docs/devlog/2026-04-12-self-review-and-broader-repo-readiness-for-project-assistant.md

## Architecture Supervision
- Signal: `green`
- Signal Basis: 关键 workflow 已在代表性仓库上跑通，当前主要问题是把“可用能力”和“当前真相”对齐，而不是再补结构性能力
- Root Cause Hypothesis: 这类助手最容易在功能变多后失去 operator clarity；真正的问题不是缺功能，而是控制面和 README 没及时反映已完成的真实状态
- Correct Layer: control truth, outward-facing README narrative, capability snapshot, and rollout guidance
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
  - 在代表性仓库上已跑通：
    - `项目助手 整改`
    - `项目助手 文档整改`
    - `项目助手 架构 整改`
  - 当前自审已把 README、能力快照、progress、handoff、status、plan 对齐到同一 readiness truth
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
- 继续观察跨项目使用时的误报、漏报和需要人工裁决的真实频率
- 继续把 readiness / progress / handoff 做成更低摩擦的默认体验

## Blockers / Open Decisions

- None currently.
- Follow-up: `项目助手 继续` 当前仍偏重，继续评估如何在不丢恢复信息的前提下压缩输出体量和重复内容

## Next 3 Actions

1. 用这版 `project-assistant` 在下一个真实项目上执行一次完整整改，观察首轮跨项目摩擦点
2. 收集第一批“架构整改 / 文档整改 / 普通整改”边界不清的案例，决定是否还要收紧自动升级规则
3. 如果接下来 1-2 个项目都稳定收敛，再切下一次 release，更新对外安装 tag
