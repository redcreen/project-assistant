# Plan

## Current Phase

`post-M16 rollout verification active`

## Current Execution Line
- Objective: 在代表性旧代际仓库上继续验证统一前门：`continue / progress / handoff` 会先升级到当前控制面代际，再输出结构化第一屏，并把剩余摩擦明确区分为 repo 层问题还是宿主桥接问题
- Plan Link: verify-unified-front-door-rollout-on-legacy-repos
- Runway: one checkpoint covering legacy-repo rollout evidence, host-bridge gap isolation, and next-step routing
- Progress: 4 / 6 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment
- Validation: `project_assistant_entry.py`、`sync_resume_readiness.py`、`continue / progress / handoff` entry、代表性 medium / large 旧代际仓库 rollout、README、roadmap、development plan、`.codex/entry-routing.md`、`deep` 与 `release` 一致

## Architecture Supervision
- Signal: `yellow`
- Signal Basis: repo 层统一前门已收口，但真实桌面 task / 新 session 仍可能绕过这条前门，所以当前还需要保持 rollout / bridge 摩擦可见
- Problem Class: repo 内的统一前门已经成立，但桌面宿主链路还没有被硬绑定到这条前门；如果不继续采证并把边界写清楚，维护者仍会看到“脚本对、真实入口飘”的割裂体验
- Root Cause Hypothesis: 当前剩余问题已经从 repo 脚本能力转成宿主 / 工具桥接问题；继续用 repo 内文案修补已经不能单独解决桌面真实入口绕过前门的问题
- Correct Layer: `.codex/entry-routing.md`、architecture、rollout evidence、宿主 / 插件桥接设计，而不是继续只改 snapshot 文案
- Rejected Shortcut: 把桌面宿主的入口问题继续伪装成 repo 文案问题，或提前声称宿主已经硬绑定
- Automatic Review Trigger: 当真实 task / 新 session 再次绕过统一前门时自动触发
- Escalation Gate: raise but continue

## Escalation Model

- Continue Automatically: 当前工作是在已批准方向内继续采集 rollout 证据，并保持 repo 层统一前门稳定
- Raise But Continue: 真实 task / 新 session rollout 暴露宿主桥接摩擦，但仍能在现有方向内先隔离问题、记录证据并继续
- Require User Decision: 如果要宣称桌面宿主已经硬绑定、改变业务方向，或引入多执行器复杂度，就必须停下来等用户裁决

## Execution Tasks
- [x] EL-1 confirm the rollout objective for `verify-unified-front-door-rollout-on-legacy-repos`: 证明旧代际仓库会先升级再输出结构化第一屏
- [x] EL-2 verify dependencies and affected boundaries: `project_assistant_entry.py`、`sync_resume_readiness.py`、`continue / progress / handoff` entry、README、architecture、roadmap、development plan、`.codex/entry-routing.md`
- [x] EL-3 confirm architecture signal, host-bridge boundary, and correct layer still hold
- [x] EL-4 validate representative medium / large legacy repos through the unified front door
- [ ] EL-5 isolate the remaining host-bridge gap and decide the next concrete bridge step
- [ ] EL-6 keep rollout evidence and next-step routing aligned across control truth and docs

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

- Slice: verify-unified-front-door-rollout-on-legacy-repos
  - Objective: 在代表性旧代际仓库上继续验证统一前门，把 repo 层已收口能力和宿主桥接剩余问题明确区分出来
  - Dependencies: `project_assistant_entry.py`、`sync_resume_readiness.py`、`continue / progress / handoff` entry、README、architecture、roadmap、development plan、`.codex/entry-routing.md`、代表性 medium / large 旧仓库
  - Risks: 如果宿主真实入口仍能绕过统一前门，维护者就会继续看到 “repo 内对了但桌面里还在飘”；同时不能为了追求一次性体验而谎称宿主已经硬绑定
  - Validation: `validate_entry_routing.py`、`deep`、`release` 通过；代表性旧仓库会先升级到当前控制面版本，再输出结构化面板；宿主桥接问题会被明确记录为 bridge evidence
  - Exit Condition: rollout 证据足够支撑下一步桥接设计，且 repo 层统一前门保持稳定
