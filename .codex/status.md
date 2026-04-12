# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-12`

## Current Phase

`narrative quality and automated architecture triggers`

## Active Slice
`tighten-maintainer-facing-narrative-and-architecture-triggers`

## Current Execution Line
- Objective: 收紧 maintainer-facing narrative，减少 `progress / continue / handoff` 的 AI-centric 表达，并把至少一条架构升级触发从“手工识别”变成自动信号
- Plan Link: tighten-maintainer-facing-narrative-and-architecture-triggers
- Runway: 用 representative repo 的真实摩擦点来收口第一屏叙事，然后把自动 architecture-review trigger 接到 supervision signal 上
- Progress: 0 / 6 tasks complete
- Stop Conditions:
  - representative repo 的 progress / continue / handoff 不再需要大量人工翻译
  - 至少一条自动 architecture-review trigger 已由 signal 驱动
  - README / roadmap / status / plan / progress / handoff 对当前阶段的叙述保持一致

## Execution Tasks
- [ ] EL-1 盘点 representative medium / large repo 的叙事摩擦点
- [ ] EL-2 定义 maintainer-facing wording contract
- [ ] EL-3 接入至少一条自动 architecture-review trigger
- [ ] EL-4 在 representative repo 上验证新的叙事和自动触发
- [ ] EL-5 更新 README / roadmap / development-plan / progress-reporting
- [ ] EL-6 重跑 `capability_snapshot`、`progress_snapshot`、`context_handoff`、`deep`、`release`

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Last Entry: docs/devlog/2026-04-12-close-m6-embedded-architect-assistant-milestone.md

## Architecture Supervision
- Signal: `yellow`
- Signal Basis: open blockers or architectural risks are still recorded
- Root Cause Hypothesis: 默认自动推进模型已经成立，剩余摩擦点主要来自叙事层和自动触发层，而不是缺失核心能力
- Correct Layer: progress / continue / handoff narration, architecture supervision triggers, and outward-facing docs
- Escalation Gate: raise but continue

## Current Escalation State
- Current Gate: raise but continue
- Reason: the current direction can continue, but the supervision state should stay visible
- Next Review Trigger: review again when blockers change, the active slice rolls forward, or release-facing work begins

## Done

- M6 `embedded architect-assistant operating model` 已关闭：
  - 规划、执行、架构监督和开发日志都已成为默认自动能力
  - 代表性整改流 `整改 / 文档整改 / 架构整改` 已在真实仓库上跑通
  - `progress`、`handoff`、控制面、README 和门禁已经能表达同一套基本真相
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

- 收紧 maintainer-facing progress / continue / handoff 叙事，减少“更像给 AI 自己看”的输出
- 把至少一条 architecture drift / repeated-fix 信号升级成自动 architecture-review trigger
- 继续观察跨项目使用时的误报、漏报和需要人工裁决的真实频率

## Blockers / Open Decisions

- None currently.
- Follow-up: `项目助手 继续` 当前仍偏重，继续评估如何在不丢恢复信息的前提下压缩输出体量和重复内容

## Next 3 Actions

1. 收集 representative medium / large repo 里最常见的 progress / continue / handoff 叙事摩擦点
2. 把 maintainer-facing wording contract 收进 `progress` / `continue` / `handoff`
3. 接入第一条自动 architecture-review trigger，并在 representative repo 上验证
