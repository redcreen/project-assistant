# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-12`

## Current Phase

`locale-aware internal control-surface output`

## Active Slice
`evaluate-locale-aware-internal-output`

## Current Execution Line
- Objective: 评估哪些内部控制面输出应该按用户语言做单通道展示，减少中文工作流里的冗余英文，同时不削弱公开文档双语和 AI 恢复精度
- Plan Link: evaluate-locale-aware-internal-output
- Runway: one active-slice checkpoint covering implementation, validation, and state refresh
- Progress: 0 / 9 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment

## Execution Tasks
- [ ] EL-1 confirm the checkpoint and objective for `evaluate-locale-aware-internal-output`: 评估哪些内部控制面输出应该按用户语言做单通道展示，减少中文工作流里的冗余英文，同时不削弱公开文档双语和 AI 恢复精度
- [ ] EL-2 verify dependencies and affected boundaries: progress / continue / handoff wording contract、public-doc i18n rules、validation policy、command templates
- [ ] EL-3 confirm architecture signal, root-cause hypothesis, and correct layer still hold
- [ ] EL-4 implement the highest-value change for `evaluate-locale-aware-internal-output`
- [ ] EL-5 address the main execution risk: 内部输出与公开文档规则串线；为了省 token 丢失恢复点；人类解释层和 AI 真相层再次分裂
- [ ] EL-6 update docs, control-surface notes, or contracts touched by this slice
- [ ] EL-7 run validation: representative Chinese-first repo 的 internal snapshots 更短但不失恢复点；公开文档双语门禁不受影响；`deep` 继续通过
- [ ] EL-8 refresh progress, capabilities, next checkpoint, and next 3 actions
- [ ] EL-9 capture a devlog entry if the root cause, tradeoff, or rejected shortcut changed

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Last Entry: docs/devlog/2026-04-12-close-m7-narrative-quality-and-automated-architecture-triggers.md

## Architecture Supervision
- Signal: `green`
- Signal Basis: no blocker or escalation trigger is currently forcing a higher-level decision
- Root Cause Hypothesis: 公开文档双语与内部恢复输出仍共享过多 raw wording，导致中文优先工作流里有不必要的英文噪声
- Correct Layer: internal progress / continue / handoff presentation rules, validation policy, and the boundary between internal and public wording
- Automatic Review Trigger: no automatic trigger is currently active
- Escalation Gate: continue automatically

## Current Escalation State
- Current Gate: continue automatically
- Reason: current execution can proceed inside the existing direction without a user-level tradeoff
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
  - 相关 README、roadmap、development plan、progress-reporting 和验证脚本已同步
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

- 评估哪些 internal control-surface outputs 适合按语言单通道展示，减少中文工作流里的冗余英文
- 保持公开文档双语、内部输出 locale-aware、AI 恢复精度三者之间的边界清楚
- 继续观察跨项目使用时的误报、漏报和需要人工裁决的真实频率

## Blockers / Open Decisions

- None currently.
- Follow-up: `项目助手 继续` 当前仍偏重，继续评估如何在不丢恢复信息的前提下压缩输出体量和重复内容
- Strategic Follow-Up: 等 M8 / M9 收口后，评估是否需要一层更高阶的业务规划与程序编排能力，用来判断项目后续怎么走、何时应插入治理/架构专项、何时需要提升项目抽象与定位，并探索是否需要一个总的 AI 监督角色来管理更长时间的多 Codex 交付流程

## Next 3 Actions

1. 盘点哪些 internal surfaces 对中文工作流最冗余，并明确哪些应该 locale-aware
2. 先收口 `continue` 的最小恢复信息，避免再次变成第二个 mini-dashboard
3. 验证 locale-aware internal output 不会削弱公开文档双语和 AI 恢复精度
