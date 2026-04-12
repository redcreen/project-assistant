# Plan

## Current Phase

`PTL supervision and worker handoff layers closed; M15 evidence collection queued`

## Current Execution Line
- Objective: 收口 M13 PTL 监督环与 M14 worker 接续层，把 PTL supervision 和 worker handoff / re-entry 都沉淀成 durable 控制面、门禁与维护者展示，并把下一步切到“是否真的需要 M15”的证据采集，而不是直接承诺多执行器
- Plan Link: close-m13-and-m14-and-queue-m15-evidence
- Runway: one checkpoint covering M13 closeout, M14 closeout, validation, and post-M14 evidence queueing
- Progress: 9 / 9 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment
- Validation: PTL supervision / worker handoff 脚本、校验、`progress / continue / handoff`、README、roadmap、development plan 与控制面一致；`deep` 和 `release` 继续通过

## Architecture Supervision
- Signal: `green`
- Signal Basis: no blocker or escalation trigger is currently forcing a higher-level decision
- Problem Class: post-M12 已经定了方向，但如果 M13 / M14 只停在 roadmap 和聊天里，PTL 仍然不会成为常驻技术主责人，worker 停下后项目也还会跟着停
- Root Cause Hypothesis: 如果不把 PTL supervision loop 和 worker handoff / re-entry 写成独立 durable 控制面、门禁和维护者展示，那么“长期监督”和“worker 接续”仍然只是方向，不是可恢复能力
- Correct Layer: `.codex/ptl-supervision.md`、`.codex/worker-handoff.md`、对应 sync / validate、`progress / continue / handoff`、README / roadmap / development-plan closeout
- Rejected Shortcut: 只在 roadmap 里宣布有 M13 / M14，却不把 PTL 和 handoff 真正做成 durable 真相
- Automatic Review Trigger: no automatic trigger is currently active
- Escalation Gate: continue automatically

## Escalation Model

- Continue Automatically: 当前工作是在已批准的战略方向内补齐长期监督交付的 durable 面，不改变业务方向
- Raise But Continue: rollout 摩擦或监督信号偏黄，但仍能在既有方向内收敛时，先记录风险再继续
- Require User Decision: 需要改变业务方向、兼容性承诺、外部定位或显著成本 / 时间边界时，必须停下来等用户裁决

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

- Slice: close-m13-and-m14-and-queue-m15-evidence
  - Objective: 关闭 M13 / M14，把 PTL 监督环和 worker 接续层从“post-M12 方向”推进到“控制面、门禁、展示、文档都成立”，并把后续状态切到 M15 证据采集
  - Dependencies: `.codex/ptl-supervision.md`、`.codex/worker-handoff.md`、对应 sync / validate、README、roadmap、development plan、`progress / continue / handoff`
  - Risks: M13 / M14 看起来已经命名，但 PTL 不会真正常驻监督、worker 停下后项目仍会一起停住；多执行器会被过早误解成当前能力
  - Validation: `validate_ptl_supervision.py`、`validate_worker_handoff.py`、`deep` 与 `release` 通过；文档和控制面都把 M13 / M14 标成 done、M15 标成 evidence-gated later
  - Exit Condition: M13 / M14 成为 durable、可恢复、可校验的已完成里程碑；后续工作进入“是否需要 M15”的证据阶段
