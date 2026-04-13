# Plan

## Current Phase

`daemon-first fast-upgrade planning ready`

## Current Execution Line
- Objective: 把首版快升级版明确拆成实现顺序：`daemon core -> VS Code host shell -> resume bridge -> local workspace validation -> old-feature re-validation`
- Plan Link: plan-daemon-fast-upgrade-and-vscode-host-mvp
- Runway: one checkpoint covering first host choice, queue/event contract, resume level, and local-workspace validation boundary
- Progress: 4 / 4 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - first implementation slice, first host boundary, or resume capability level requires user judgment
- Validation: daemon-first 专项设计文档、`PTL daemon MVP`、`host resume bridge` 文档已建立；`.codex/status.md` / `.codex/plan.md` / roadmap / development plan 能表达当前的默认开发顺序

## Architecture Supervision
- Signal: `yellow`
- Signal Basis: 用户要求先看 roadmap / plan 再按文档下开发指令，因此当前设计工作必须收成明确的默认构建顺序。与此同时，`host resume bridge` 已确认首个宿主应是 VS Code 扩展前端，而不是聊天框注入。
- Problem Class: 当前问题跨越 daemon 运行时、queue/event contract、宿主桥接、live UI、resume 动作，以及升级后的旧功能回归顺序；这是一个前后端协同的产品层交付问题。
- Root Cause Hypothesis: 没有常驻调度层和宿主恢复桥时，支撑任务、恢复动作和状态展示都还挤在主写入线周围；即使脚本级时延下降，用户仍然会感到系统“重”和“慢”。
- Correct Layer: daemon runtime、task queue、event schema、foreground gate、VS Code host shell、resume bridge、live status surfaces、本地工作区验证，以及之后的旧功能回归。
- Rejected Shortcut: 继续只做局部同步优化，或直接去赌“往内置聊天框里写继续”这类脆弱自动化
- Automatic Review Trigger: 当首版宿主、resume 能力级别、first-slice 边界或旧功能验证顺序改变时自动触发
- Escalation Gate: raise but continue

## Escalation Model

- Continue Automatically: 继续维护当前实现顺序文档与切片定义，但不直接跨到实现
- Raise But Continue: 局部实现范围、宿主 UI 精简度或 resume 默认级别仍可继续讨论
- Require User Decision: 任何会改变首个实现切片、首版宿主、或是否把 `one-click continue` 放进第一批的选择，都必须等用户裁决

## Execution Tasks
- [x] EL-1 record the systemic latency problem and hard requirements in durable markdown
- [x] EL-2 promote the issue into a named async-execution design initiative
- [x] EL-3 choose `daemon-first, write-safe, async-by-default` as the target architecture
- [x] EL-4 define the first implementation order around daemon + host bridge, and record it in roadmap / plan for user-directed execution

## Development Log Capture
- Trigger Level: high
- Auto-Capture When:
  - the target architecture switches to daemon-first
  - the fast-upgrade scope or daemon MVP boundary changes
  - the old-feature re-validation order is finalized
  - the first daemon / host implementation slice is approved
- Skip When:
  - the change is mechanical or formatting-only
  - no durable reasoning changed
  - the work simply followed an already-approved path
  - the change stayed local and introduced no durable tradeoff

## Slices

- Slice: design-daemon-first-ptl-scheduler-mvp
  - Objective: 把 daemon-first 目标架构和 write-safe 快升级版的边界写清楚，确保可以先发一版提升编码速度
  - Dependencies: `docs/devlog/2026-04-13-entry.md`、`docs/reference/project-assistant/async-execution-and-latency-governance.md`、`docs/reference/project-assistant/ptl-daemon-mvp.md`
  - Risks: 如果 MVP 边界不清楚，就会把快升级版拖成一个过大的 daemon 项目；如果验证顺序不清楚，旧功能会在升级后失去可控性
  - Validation: daemon-first 设计文档、MVP 文档、status / plan / roadmap / development plan 一致表达“先发快升级版，再逐项验证旧功能”
  - Exit Condition: 快升级版范围、首批后台任务名单、同步预算和旧功能验证顺序已经明确

- Slice: plan-daemon-fast-upgrade-and-vscode-host-mvp
  - Objective: 把快升级版正式拆成可点名实现的默认顺序，并明确首个宿主是 VS Code 扩展前端
  - Dependencies: `docs/reference/project-assistant/ptl-daemon-mvp.md`、`docs/reference/project-assistant/host-resume-bridge.md`
  - Risks: 如果没有明确顺序，实际开发会在 daemon core、host UI 和恢复桥之间来回跳
  - Validation: roadmap / development plan / status / plan 都能直接读出相同的默认开发顺序
  - Exit Condition: 用户已经可以直接按文档点名第一个实现切片

- Slice: build-ptl-daemon-runtime-core
  - Objective: 建立 daemon runtime、runtime store、queue/event contract，以及最小的 `start/status/stop/queue` 控制面
  - Dependencies: `ptl-daemon-mvp`、`host-resume-bridge`、当前规划切片
  - Risks: runtime store 漂移、queue 状态不稳定、event schema 后续难以承载 host UI
  - Validation: 本地 daemon 能启动、停止、暴露队列状态，并产出宿主可消费的事件
  - Exit Condition: daemon 已能脱离前台主写入线托管最小支撑任务并提供稳定状态面

- Slice: build-vscode-host-shell-and-live-status
  - Objective: 建立 VS Code 宿主前端壳，至少包含 Tree View、Status Bar、Output channel，以及与 daemon 的连接
  - Dependencies: daemon queue/event contract
  - Risks: 过早追求 Webview 或 chat 集成，导致首版宿主壳过重
  - Validation: 在本地 workspace 中能看到队列、状态、当前切片、最近文件或事件
  - Exit Condition: 用户已能在 VS Code 中感知“页面在动、任务在推进”

- Slice: wire-manual-and-one-click-continue
  - Objective: 把 `resume-ready` 事件接成 `manual continue`，并在范围允许时补上保守的 `one-click continue`
  - Dependencies: daemon event schema、VS Code host shell、Codex runner / 命令契约
  - Risks: 错误 targeting 到错误 session、重复启动、或被迫回退到聊天框注入
  - Validation: 本地 workspace 中可通过宿主按钮或命令恢复继续，不要求聊天框注入
  - Exit Condition: worker 停止后，宿主能接住继续动作，不需要用户手工重组 prompt

- Slice: validate-daemon-host-mvp-on-local-workspaces
  - Objective: 在代表性的本地 workspace 上验证 daemon + VS Code host MVP 的状态展示、恢复路径和稳定性
  - Dependencies: daemon runtime、VS Code host shell、resume bridge
  - Risks: demo 可用但状态漂移、事件丢失、或 continue 体验不稳定
  - Validation: 至少在代表性本地仓库上完成队列、ETA、状态、resume-ready 和 continue 路径验证
  - Exit Condition: daemon-host MVP 足够稳定，可作为旧功能回归的新基线

- Slice: validate-legacy-feature-set-on-daemon-host-baseline
  - Objective: 在 daemon-host 基线上按家族逐项回归旧功能，而不是等所有能力都迁完再统一验收
  - Dependencies: daemon-host MVP 已稳定、旧功能验证清单
  - Risks: 只顾把宿主做出来，不做旧能力回归，会让实际 skill 体验失真
  - Validation: `continue / progress / handoff`、整改流、validator 等能力在新基线上持续重新通过
  - Exit Condition: 旧功能按顺序通过回归，且 daemon-host 基线被证明可用

- Slice: resume-post-m16-rollout-on-daemon-host-baseline
  - Objective: 在 daemon-host 基线稳定后，恢复 post-M16 rollout verification，并重新评估 host-bridge 证据
  - Dependencies: 旧功能回归通过
  - Risks: 过早恢复 rollout，会把 daemon-host 自身问题和外部 rollout 摩擦混在一起
  - Validation: 代表性旧代际仓库继续先升级再输出结构化面板，且体验已不再被可避免的同步工作主导
  - Exit Condition: post-M16 rollout 重新成为可读、可证据化的下一条主线
