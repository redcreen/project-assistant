# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-14`

## Current Phase

`post-M21 daemon-host baseline active`

## Active Slice
`stabilize-daemon-host-baseline-for-dogfooding`

## Current Execution Line
- Objective: keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins
- Plan Link: stabilize-daemon-host-baseline-for-dogfooding
- Runway: one checkpoint covering runtime hardening, operator docs, and broader adoption evidence capture
- Progress: 3 / 3 tasks complete
- Stop Conditions:
  - a runtime or host regression changes the default path
  - release packaging or host-surface expansion needs human judgment
  - broader dogfooding shows the daemon-host baseline should not yet be the default fast path

## Execution Tasks
- [x] EL-1 harden daemon runtime edges exposed by concurrent startup, shutdown, or status polling in real workspaces
- [x] EL-2 keep README / architecture / usage / test plan / entry routing aligned with daemon-host as the new default fast path
- [x] EL-3 collect broader dogfooding evidence before opening the next host surface or any M15 discussion

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Last Entry: docs/devlog/2026-04-13-daemon-host-baseline-m17-through-m21.md

## Architecture Supervision
- Signal: `green`
- Signal Basis: `M17-M21` now have working code instead of only planning notes: the repo has a daemon runtime, queue/runtime control surface, a VS Code host shell, manual/one-click continue hooks, dedicated validators, and local plus legacy baseline validation.
- Root Cause Hypothesis: the main latency pain was orchestration shape, not raw script runtime; the new baseline removes most support work from the foreground write lane by moving queueable work behind a local daemon and host shell.
- Correct Layer: keep the runtime contract, host shell, queue visibility, and regression coverage aligned; do not reopen chat-box injection or multi-executor scope prematurely.
- Automatic Review Trigger: when runtime control, host bridge, or dogfooding evidence changes the baseline boundary
- Escalation Gate: continue automatically

## Current Escalation State
- Current Gate: continue automatically
- Reason: `M17-M21` are implemented and validated; the next work is stabilization and adoption evidence, not a blocked design decision.
- Next Review Trigger: review again when daemon-host dogfooding exposes a new boundary, a release decision is requested, or a broader host surface is proposed

## Done

- M17 `build-ptl-daemon-runtime-core` 已完成：
  - `scripts/daemon_runtime.py` 与 `scripts/daemon_entry.py` 已提供本地 runtime、queue / events、foreground lease 和 `daemon start/status/stop/kill/queue` 控制面
  - `project_assistant_entry.py` 已把 `daemon / queue` 收进统一前门
  - runtime 已通过 `validate_daemon_runtime.py`
- M18 `build-vscode-host-shell-and-live-status` 已完成：
  - `integrations/vscode-host/` 已提供 VS Code 宿主壳、Tree View、Status Bar、Output channel 和 daemon 轮询连接
  - 宿主能显示 live 状态、当前切片、最近文件和任务日志入口
  - 扩展已通过 `validate_vscode_host_extension.py`
- M19 `wire-manual-and-one-click-continue` 已完成：
  - VS Code 宿主已提供 `manual continue` 与保守的 `one-click continue`
  - 恢复动作继续复用统一前门，不依赖聊天框注入
- M20 `validate-daemon-host-mvp-on-local-workspaces` 已完成：
  - `validate_daemon_host_mvp.py` 已覆盖 bootstrap、retrofit、docs-retrofit、validate-fast、progress、continue、handoff
  - daemon-host baseline 已在代表性本地 fixture 上通过验证
- M20 `validate-legacy-feature-set-on-daemon-host-baseline` 已完成：
  - 旧功能家族已在 daemon-host 基线上重新通过，而不是只验证新 runtime 自己能启动
- M21 `resume-post-m16-rollout-on-daemon-host-baseline` 已完成：
  - `validate_daemon_legacy_rollout.py` 已验证 legacy repo 会先升级，再走 daemon-host 路径输出结构化 continue / progress / handoff
  - `post-M16` rollout 验证现在已在 daemon-host 基线上恢复
- daemon startup race 已补强一轮：
  - runtime 现在用 startup lock 收敛并发 ensure，不再依赖“碰巧只启动一次”
  - `send_request` 现在会对 startup / shutdown 窗口里的 transient socket 错误做短重试
  - `status / queue / events / task` 现在在 runtime 窗口期有持久化快照回退，不再直接抛 traceback
  - daemon 重启后会自动把遗留的 `queued / running` 任务收口成 `cancelled`
  - `validate_daemon_runtime.py` 现在真实覆盖并发 `start + status + queue` 窗口，并验证 continue / progress / handoff 任务链仍可跑通
- EL-2 文档与入口真相已收口：
  - README / docs home / architecture / usage / test plan 现在都明确把 daemon-host baseline 写成默认快路径，并区分统一前门与 backend/debug 脚本
  - `.codex/entry-routing.md` 现在把 daemon-aware runtime control、transaction fast path 和 operator default 写成同一套 durable contract
  - `validate_gate_set.py --profile fast` 现在默认包含 `validate_entry_routing.py`，`validate_doc_quality.py` 也已收紧到 public-doc 范围，不再误报 `.codex/host-views/*`
  - `validate_gate_set.py --profile deep` 已重新通过，说明 operator docs、entry routing 与 daemon-host baseline 叙事一致

## In Progress

- `post-M21` 稳定化与 dogfooding 已成为新的当前切片：当前目标不是再讨论 daemon 值不值得做，而是把这条 baseline 保持成真实可用的默认快路径。
- broader dogfooding evidence 已扩到两个真实本地 repo：`/Users/redcreen/Project/unified-memory-core` 与 `/Users/redcreen/Project/codex limit` 都已通过 clean daemon session 下的 `continue / progress / handoff` 采证，说明 baseline 不再只靠 self-repo 与 fixtures 站立。
- `.codex/dogfooding-evidence.md` 现在已把 self-repo、runtime、fixture、legacy rollout、VS Code host 与 broader local repos 的证据、缺口和 evidence-gated 决策条件收口成 durable 真相；当前重点转为继续积累 adoption evidence，并保持 release packaging / stronger host surfaces / `M15` evidence-gated。

## Blockers / Open Decisions

- None currently.
- Follow-up: daemon-host baseline 的 release 打包与版本发布时间仍未决定。
- Follow-up: 更重的宿主 UI、web / remote 宿主支持，以及任何 `M15` 讨论都继续保持 evidence-gated。
- Follow-up: “同仓多宿主前台单写者保护” 已记入 backlog；当前 daemon 有 foreground lease，但 VS Code 宿主还没有把它真正接成硬互斥写入保护，是否需要升主线继续看证据。

## Next 3 Actions

1. `stabilize-daemon-host-baseline-for-dogfooding`
2. refresh deeper broader-workspace dogfooding evidence when new repos or repeated operator sessions are available
3. keep release packaging and broader host expansion evidence-gated until the new baseline proves stable in more workspaces
