# Plan

## Current Phase

`post-M21 daemon-host baseline active`

## Current Execution Line
- Objective: keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins
- Plan Link: stabilize-daemon-host-baseline-for-dogfooding
- Runway: one checkpoint covering runtime hardening, operator docs, and broader adoption evidence capture
- Progress: 3 / 4 tasks complete
- Stop Conditions:
  - a runtime or host regression changes the default path
  - release packaging or host-surface expansion needs human judgment
  - broader dogfooding shows the daemon-host baseline should not yet be the default fast path
- Validation: `validate_daemon_runtime.py`、`validate_vscode_host_extension.py`、`validate_daemon_host_mvp.py`、`validate_daemon_legacy_rollout.py` 已通过，M17-M21 baseline 已具备可持续回归的自动化入口

## Architecture Supervision
- Signal: `green`
- Signal Basis: `M17-M21` 现在不仅有设计文档，还有 working runtime、runtime control surface、VS Code host shell、continue bridge 和 dedicated validators。当前需要的是 baseline 稳定化和 adoption evidence，而不是再停在实现前讨论。
- Problem Class: 这是一个已经跨过“是否值得做”的阶段性产品问题；接下来重点是 runtime hardening、host adoption 和 regression confidence。
- Root Cause Hypothesis: 造成“写代码被过程拖慢”的主要因素是前台主写入线和支撑任务耦合；daemon-host baseline 已经把这类支撑任务迁到后台队列和宿主状态面。
- Correct Layer: daemon runtime contract、queue/event control surface、VS Code host shell、continue bridge、operator docs、gate coverage。
- Rejected Shortcut: 不回退到纯同步 orchestration，也不把“往聊天框里自动写继续”当成主恢复链路。
- Automatic Review Trigger: 当 runtime/host 边界、dogfooding 证据或 release 策略变化时自动触发
- Escalation Gate: continue automatically

## Escalation Model

- Continue Automatically: 继续做 post-M21 稳定化、文档收口和 dogfooding 采证，不需要新的架构裁决
- Raise But Continue: 局部 runtime/host UX 细节、日志展示方式或 operator docs 精简度可在当前方向内继续讨论
- Require User Decision: 任何会改变默认宿主、扩大自动继续权限、打开 web / remote 宿主，或重启 `M15` 的选择，都必须等用户裁决

## Execution Tasks
- [x] EL-1 harden daemon runtime edges exposed by concurrent startup, shutdown, or status polling in real workspaces
- [x] EL-2 keep README / architecture / usage / test plan / entry routing aligned with daemon-host as the new default fast path
- [x] EL-3 collect broader dogfooding evidence before opening the next host surface or any M15 discussion
- [ ] EL-4 keep “single foreground writer per repo” as evidence-gated backlog until real adoption proves it should move from follow-up into a formal slice

## Development Log Capture
- Trigger Level: high
- Auto-Capture When:
  - the daemon runtime contract changes in a way that affects host behavior
  - the default host or continue bridge boundary changes
  - a new dogfooding finding changes the release or rollout path
- Skip When:
  - the change is formatting-only
  - the change stays inside an already-approved boundary
  - the work only refreshes generated surfaces without a new durable tradeoff

## Slices

- Slice: close-m17-through-m21-daemon-host-baseline
  - Objective: 把 daemon runtime、VS Code host shell、continue bridge、本地验证、旧功能回归和 post-M16 rollout 恢复一口气收口成可用 baseline
  - Dependencies: `docs/reference/project-assistant/async-execution-and-latency-governance.md`、`ptl-daemon-mvp.md`、`host-resume-bridge.md`
  - Risks: 如果只交付设计文档或只验证局部 happy path，用户仍会感到 skill 太重
  - Validation: `validate_daemon_runtime.py`、`validate_vscode_host_extension.py`、`validate_daemon_host_mvp.py`、`validate_daemon_legacy_rollout.py`
  - Exit Condition: `M17-M21` 在同一轮里完成实现、验证，并成为新的 daemon-host baseline

- Slice: stabilize-daemon-host-baseline-for-dogfooding
  - Objective: 把刚完成的 daemon-host baseline 稳定成默认快路径，并为更广泛 dogfooding 准备好 operator docs 与采证入口
  - Dependencies: `close-m17-through-m21-daemon-host-baseline`
  - Risks: 如果 runtime control truth、文档和 gate 覆盖不同步，用户会重新感知到“做完了但不好用”
  - Validation: `validate_gate_set.py --profile deep`、runtime/host smoke、broader workspace dogfooding
  - Exit Condition: daemon-host baseline 可被更广泛使用，且没有高频 runtime/host 回归

- Slice: package-daemon-host-baseline-for-release
  - Objective: 决定 daemon-host baseline 的 release 叙事、安装说明和版本落点
  - Dependencies: `stabilize-daemon-host-baseline-for-dogfooding`
  - Risks: 如果在 baseline 还不稳时过早打包 release，会把后续修正成本抬高
  - Validation: release-facing docs、gate outputs 和 install path 对齐
  - Exit Condition: 用户可以通过明确版本入口获取 daemon-host baseline，而不是只依赖当前仓库 mainline

- Slice: future-host-expansion-and-m15-evidence
  - Objective: 只在 daemon-host baseline 已稳定、dogfooding 证据充分后，再判断是否扩大到更强宿主表面或重新讨论 `M15`
  - Dependencies: `stabilize-daemon-host-baseline-for-dogfooding`
  - Risks: 过早扩宿主或重谈多执行器会把本轮“先变快、再验证”的主目标冲散
  - Validation: real adoption evidence + clear write-scope boundaries
  - Exit Condition: 有足够证据支持下一条更大的主线，而不是靠猜测扩范围

- Slice: M17 / build-ptl-daemon-runtime-core
  - Objective: 建立 daemon runtime、runtime store、queue/event contract，以及最小的 `start/status/stop/queue` 控制面
  - Dependencies: `ptl-daemon-mvp`、`host-resume-bridge`
  - Risks: runtime store 漂移、queue 状态不稳定、event schema 后续难以承载 host UI
  - Validation: `validate_daemon_runtime.py`
  - Exit Condition: 已完成并成为 daemon-host baseline 的基础层

- Slice: M18 / build-vscode-host-shell-and-live-status
  - Objective: 建立 VS Code 宿主前端壳，至少包含 Tree View、Status Bar、Output channel，以及与 daemon 的连接
  - Dependencies: daemon queue/event contract
  - Risks: 过早追求 Webview 或 chat 集成，导致首版宿主壳过重
  - Validation: `validate_vscode_host_extension.py`
  - Exit Condition: 已完成，用户已能在 VS Code 中感知“页面在动、任务在推进”

- Slice: M19 / wire-manual-and-one-click-continue
  - Objective: 把 `resume-ready` 事件接成 `manual continue`，并补上保守的 `one-click continue`
  - Dependencies: daemon event schema、VS Code host shell、Codex runner / 命令契约
  - Risks: 错误 targeting 到错误 session、重复启动、或被迫回退到聊天框注入
  - Validation: `validate_vscode_host_extension.py` + host continue smoke
  - Exit Condition: 已完成，worker 停止后宿主能接住继续动作

- Slice: M20 / validate-daemon-host-mvp-on-local-workspaces
  - Objective: 在代表性的本地 workspace 上验证 daemon + VS Code host MVP 的状态展示、恢复路径和稳定性
  - Dependencies: daemon runtime、VS Code host shell、resume bridge
  - Risks: demo 可用但状态漂移、事件丢失、或 continue 体验不稳定
  - Validation: `validate_daemon_host_mvp.py`
  - Exit Condition: 已完成，daemon-host MVP 已可作为旧功能回归的新基线

- Slice: M20 / validate-legacy-feature-set-on-daemon-host-baseline
  - Objective: 在 daemon-host 基线上按家族逐项回归旧功能，而不是等所有能力都迁完再统一验收
  - Dependencies: daemon-host MVP 已稳定、旧功能验证清单
  - Risks: 只顾把宿主做出来，不做旧能力回归，会让实际 skill 体验失真
  - Validation: `validate_daemon_host_mvp.py` + `validate_gate_set.py --profile deep`
  - Exit Condition: 已完成，旧功能在新基线上持续重新通过

- Slice: M21 / resume-post-m16-rollout-on-daemon-host-baseline
  - Objective: 在 daemon-host 基线稳定后，恢复 post-M16 rollout verification，并重新评估 host-bridge 证据
  - Dependencies: 旧功能回归通过
  - Risks: 过早恢复 rollout，会把 daemon-host 自身问题和外部 rollout 摩擦混在一起
  - Validation: `validate_daemon_legacy_rollout.py`
  - Exit Condition: 已完成，legacy repo 已在 daemon-host 基线上继续先升级再输出结构化面板
