# Plan

## Current Phase

`locale-aware internal control-surface output`

## Current Execution Line
- Objective: 评估哪些内部控制面输出应该按用户语言做单通道展示，减少中文工作流里的冗余英文，同时不削弱公开文档双语和 AI 恢复精度
- Plan Link: evaluate-locale-aware-internal-output
- Runway: one active-slice checkpoint covering implementation, validation, and state refresh
- Progress: 0 / 9 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment
- Validation: representative Chinese-first repo 的 internal snapshots 更短但不失恢复点；公开文档双语门禁不受影响；`deep` 继续通过

## Architecture Supervision
- Signal: `green`
- Signal Basis: no blocker or escalation trigger is currently forcing a higher-level decision
- Problem Class: default-on model 已经成立，当前问题转成 internal output 的语言策略，而不是核心执行模型缺失
- Root Cause Hypothesis: 公开文档双语与内部恢复输出共享了太多 raw wording，导致中文优先工作流里仍然带着大量不必要的英文
- Correct Layer: internal progress / continue / handoff presentation rules, validation policy, and wording boundaries between public and internal surfaces
- Rejected Shortcut: 直接把所有 internal output 全量中文化，却不先定义哪些 surfaces 必须保留 raw truth 或 bilingual behavior
- Automatic Review Trigger: no automatic trigger is currently active
- Escalation Gate: continue automatically

## Escalation Model

- Continue Automatically: 当前工作只是在既定方向内补齐脚手架、门禁、输出和文档，不改变业务含义
- Raise But Continue: 出现监督信号偏黄、但仍能在既定方向内收敛时，先记录风险再继续
- Require User Decision: 需要改变产品行为、兼容性边界、性能/成本取舍或用户体验方向时，必须停下来等用户裁决

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
- Auto-Capture When:
  - the root-cause hypothesis changes
  - a reusable mechanism replaces repeated local fixes
  - a retrofit changes governance, architecture, or release policy
  - a tradeoff or rejected shortcut is likely to matter in future work
- Skip When:
  - the change is mechanical or formatting-only
  - no durable reasoning changed
  - the work simply followed an already-approved path
  - the change stayed local and introduced no durable tradeoff

## Slices

- Slice: redefine the operating model
  - Objective: 把 `project-assistant` 从“命令驱动 skill”重新定位成“默认内嵌的 AI 工程系统”
  - Dependencies: 当前 `SKILL.md`、`usage.md`、`governance.md`
  - Risks: 新定位只停留在文案层，没有进入默认执行语义
  - Validation: 规则文档明确区分业务裁决、人类干预窗口、默认自动职责
  - Exit Condition: skill 自己能清楚表达“用户给方向，系统默认推进”的工作模型

- Slice: embed architecture supervision by default
  - Objective: 把架构监督从手工命令升级为 `plan / execute / retrofit / closeout` 的默认内嵌能力
  - Dependencies: 架构模式定义、控制面更新策略、命令窗口保留策略
  - Risks: 监督逻辑过重，影响节奏；或者过轻，仍然放任局部修补
  - Validation: 明确同步轻审查、异步重审查、升级给用户的裁决点
  - Exit Condition: 架构监督默认自动运行，`项目助手 架构 xxx` 退化为人工覆盖入口

- Slice: embed development-log capture by default
  - Objective: 把开发日志从“可选记录动作”变成“出现持久推理链路时自动沉淀”
  - Dependencies: `write_development_log.py`、`validate_development_log.py`、devlog 触发规则
  - Risks: 写成流水账，或者触发条件太松导致噪声过多
  - Validation: 规则文档明确自动触发条件、跳过条件和人工补记入口
  - Exit Condition: `devlog` 成为默认自动能力，手工命令只保留为补记和强制记录窗口

- Slice: simplify the human surface
  - Objective: 让命令从主工作流降级成“观察/干预窗口”，只保留少量高价值入口
  - Dependencies: help menu、usage、README、handoff 规则
  - Risks: 命令太多依然让用户记不住；命令太少又无法人工覆盖
  - Validation: 能清楚给出默认自动行为 + 手工干预窗口的边界
  - Exit Condition: 常态下用户只需要提需求与业务方向，命令主要用于查看、纠偏和覆盖

- Slice: define the escalation and gate model
  - Objective: 明确哪些情况自动推进，哪些情况必须升级给用户裁决
  - Dependencies: control-surface rules、validation gates、release rules
  - Risks: 自动化越界，或者仍然频繁把技术判断抛回给用户
  - Validation: 形成明确的“自动推进 / 强制提醒 / 必须人工裁决”分层
  - Exit Condition: 项目助手的自主性边界可解释、可验证、可持续维护

- Slice: operationalize reporting and release governance
  - Objective: 把更长任务板自动生成、可用能力快照、更严格的开发日志触发强度，以及 release readiness gate 收口成一个可执行面
  - Dependencies: `sync_execution_line.py`、`capability_snapshot.py`、`validate_release_readiness.py`、CI workflows
  - Risks: 用户仍然不知道当前哪些能力可用；开发日志噪声过高；本地发布门禁和 CI readiness 脱节
  - Validation: `progress` 显示 usable-now 快照；`sync_execution_line.py` 能从该 slice 自动生成长任务板；CI 能运行更严格的 readiness gate
  - Exit Condition: 当前状态、当前可用能力、下一执行线和发布就绪度都能被自动表达和校验

- Slice: automate supervision, release protection, and human windows
  - Objective: 把自动架构信号、更严格发布保护，以及更收敛的人类窗口一起落到执行层
  - Dependencies: `sync_architecture_supervision.py`、`validate_gate_set.py --profile release`、`progress_snapshot.py`、`context_handoff.py`
  - Risks: 架构信号仍然依赖静态文案；发布保护只停在 tag 场景；用户仍然看到过多手工命令
  - Validation: `progress` / `handoff` 使用自动架构信号；release profile 可用；COMMANDS/README/help-menu 收敛成主窗口 + 后台流程
  - Exit Condition: 自动架构信号、CI release protection 和主窗口压缩均已落地，并通过门禁

- Slice: make architecture retrofit a first-class flow
  - Objective: 把“架构整改”做成一等能力，补齐命令、脚本、工作底稿和门禁
  - Dependencies: `sync_architecture_retrofit.py`、`validate_architecture_retrofit.py`、architecture submenu、retrofit rules
  - Risks: 普通整改与架构整改继续混在一起；只有命令没有 working note；只有审计没有门禁
  - Validation: 架构整改工作底稿可生成且可校验；命令、模板和控制面都能识别该模式
  - Exit Condition: `项目助手 架构 整改` 已成为可执行、可验证、可恢复的一等流程

- Slice: prepare project-assistant for broader repo adoption
  - Objective: 从更高层复核 `project-assistant` 本身，把控制面、README、可用能力快照和推广姿态收口到一致状态
  - Dependencies: representative repo validations、capability snapshot、progress/handoff outputs、README narrative
  - Risks: gates 虽然通过，但用户仍然不知道什么已经能用、下一步是什么；README 仍像开发者视角而不够 rollout-ready
  - Validation: status/plan/progress/handoff 对齐；README / README.zh-CN 能明确回答“现在能直接用什么、何时用哪个入口”；`deep` / `release` 继续通过
  - Exit Condition: 这套 skill 已适合拿去处理其他真实项目，而不是还停留在“能力已经写出来但 operator truth 不够清晰”的状态

- Slice: tighten-maintainer-facing-narrative-and-architecture-triggers
  - Objective: 让维护者回来接手时更容易看懂当前阶段、当前切片和下一步，并把至少一条架构升级逻辑从手工识别变成自动信号
  - Dependencies: representative repo friction、progress/continue/handoff 输出、architecture supervision signals、README/roadmap wording
  - Risks: 输出仍然像给 AI 自己看；自动触发太吵或太弱；README / roadmap / progress 又开始各说各话
  - Validation: representative medium / large repo 的 progress / continue / handoff 更接近“维护者恢复面板”；至少一条 architecture-review trigger 自动触发；`deep` / `release` 继续通过
  - Exit Condition: 维护者视角叙事更稳定，自动架构触发不再主要依赖人工判断

- Slice: evaluate-locale-aware-internal-output
  - Objective: 评估哪些内部控制面输出应该按用户语言做单通道展示，减少中文工作流里的冗余英文，同时不削弱公开文档双语和 AI 恢复精度
  - Dependencies: progress / continue / handoff wording contract、public-doc i18n rules、validation policy、command templates
  - Risks: 内部输出与公开文档规则串线；为了省 token 丢失恢复点；人类解释层和 AI 真相层再次分裂
  - Validation: representative Chinese-first repo 的 internal snapshots 更短但不失恢复点；公开文档双语门禁不受影响；`deep` 继续通过
  - Exit Condition: 已明确哪些 internal surfaces 应该 locale-aware、哪些必须保持 bilingual / raw truth，并且这套规则可被脚本稳定执行
