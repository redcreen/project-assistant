# Plan

## Current Phase

`release packaging prep active`

## Current Execution Line
- Objective: prepare the daemon-host baseline for release-facing installation and update paths
- Plan Link: package-daemon-host-baseline-for-release
- Runway: one checkpoint covering release delta check, install/version truth, release-facing docs, gate outputs, and final validation
- Progress: 5 / 5 tasks complete
- Stop Conditions:
  - release docs point users at a stale install path
  - version references disagree across README, install scripts, and roadmap
  - daemon-host baseline changes are not validated through the fast gate
  - package-ready status is claimed without checking the current mainline delta
- Validation: release-facing docs, install path/version references, `validate_install_scripts.py`, and `validate_gate_set.py --profile fast` agree for the release-prep baseline

## Architecture Supervision
- Signal: `green`
- Signal Basis: M22 governed learning is accepted and active; release-prep now separates the immutable `v0.1.9` stable tag from the mainline daemon-host/PTL-loop release candidate.
- Problem Class: 这是 release packaging / operator truth 问题；用户需要明确版本入口，而不是靠 mainline 状态自行推断。
- Root Cause Hypothesis: 如果 README、安装脚本和 roadmap 把 `v0.1.9` 与 mainline release candidate 混成一个入口，用户会错误安装旧能力或误以为新能力已打 tag。
- Correct Layer: release notes、install/version references、README/docs roadmap、validation gates。
- Persistent Registry: accepted PTL learned rules already live in `~/.codex/project-assistant/learned-registry.json` and are no longer blocking this slice.
- Rejected Shortcut: 不只改一个 README 版本号；必须检查 release delta、安装路径、install script ref 支持和 gate 输出是否一致。
- Automatic Review Trigger: 当 release path、install script、version reference、release notes 或 daemon-host validation 变化时自动触发
- Escalation Gate: continue automatically

## Escalation Model

- Continue Automatically: scan message ingress and preflight events for repeated correction patterns, then create pending candidates without activating them
- Raise But Continue: pending candidates and accepted learned rules surface in host/status/PTL panels while ordinary work continues
- Require User Decision: accepting, rejecting, snoozing, or escalating a learned rule requires explicit human review

## Execution Tasks
- [x] EL-1 inspect current release/version/install references and mainline delta since the last safe install tag
- [x] EL-2 align README, install instructions, and roadmap around the selected daemon-host baseline release path
- [x] EL-3 ensure gate outputs and validation commands match the release-facing path
- [x] EL-4 write release notes or release-prep summary for the daemon-host baseline
- [x] EL-5 run fast gate and final consistency checks

## Development Log Capture
- Trigger Level: high
- Auto-Capture When:
  - release path, install script ref handling, version references, or release-prep notes change
  - a new immutable release tag is prepared
  - gate outputs change the release readiness decision
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

- Slice: ship-ptl-policy-gate-baseline
  - Objective: 把 PTL 角色职责转成其它项目入口默认运行的 policy sync + preflight，并生成可见 PTL signal
  - Dependencies: `ptl-role-and-governed-learning.md`、`M13` PTL supervision、`M16` unified hard entry
  - Risks: 如果只写文档不接入口，PTL 不会稳定生效；如果写成项目名特判，后续无法迁移和自我学习
  - Validation: `validate_ptl_gate.py`、`ptl_gate.py preflight`、`validate_gate_set.py --profile fast`
  - Exit Condition: generic、missing-control、style-engine-like、openclaw-skills-like、entry-activation fixtures 都能稳定给出正确 PTL decision

- Slice: ship-completion-gate-stop-semantics
  - Objective: 防止 project-assistant 在存在已知必要下一步时停下，把“继续做完”变成 final / closeout 前的 gate
  - Dependencies: `ship-ptl-policy-gate-baseline`、unified entry scripts、fast gate
  - Risks: 如果只写原则不落到 gate，assistant 仍会把必做项写成下一步后停下；如果 gate 误拦 optional backlog，会影响正常收口
  - Validation: `validate_completion_gate.py`、`completion_gate.py final-check`、`validate_gate_set.py --profile fast`
  - Exit Condition: complete、open-task、final-text-next-step、explicit-deferred、human-decision fixtures 都能稳定给出正确 completion decision

- Slice: ship-task-pipeline-runner-loop
  - Objective: 把每次非平凡执行请求先入队成 pipeline task，再由程序循环决定下一 task、repair task、回到主线和停止条件
  - Dependencies: `ship-completion-gate-stop-semantics`、`ptl_gate.py`、unified entry scripts
  - Risks: 如果只做 gate 而没有 runner，系统仍只能说“不该停”，不能保证自动进入下一步；如果 LLM 控制循环，仍会回到做一步停一步
  - Validation: `validate_pipeline_runner.py`、`pipeline_runner.py run --task`、`validate_gate_set.py --profile fast`
  - Exit Condition: command-loop、repair-loop、llm-pause、run-argument-enqueue、human-decision、entry-panel fixtures 都能稳定给出正确 pipeline state

- Slice: ship-host-message-ingress-loop
  - Objective: route host/user messages through message ingress so each message is classified, recorded, enqueued into the task pipeline, and run through the programmatic loop by default
  - Dependencies: `ship-task-pipeline-runner-loop`、unified entry scripts、`continue / progress` panels
  - Risks: 如果只覆盖 `execute --task`，普通用户消息仍会绕过 loop；如果入口只做记录不入队，程序循环仍不会稳定发生
  - Validation: `validate_message_ingress.py`、`message_ingress.py ingest`、`project_assistant_entry.py message`、`validate_gate_set.py --profile fast`
  - Exit Condition: execution-message、discussion-message、classify-only、front-door、entry-panel fixtures 都能稳定给出正确 message-ingress state

- Slice: connect-ptl-learning-review-to-host
  - Objective: 把 pending review、accept、reject、snooze 接入 VS Code host 与 learned registry
  - Dependencies: `ship-ptl-policy-gate-baseline`、host live status、宿主中立 registry root
  - Risks: 如果 accepted rules 写进 skill 安装目录，重装会覆盖；如果没有人类 review，PTL 会变成静默自我修改器
  - Validation: `validate_ptl_learning.py`、`validate_vscode_host_extension.py`、`validate_gate_set.py --profile fast`
  - Exit Condition: 已完成；用户能从状态栏或宿主面板 review PTL rule，并把 accepted rules 写入重装不覆盖的 registry；PTL learning 已支持固定 pattern 与语义概念对归纳两类候选，且都必须通过 human review

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
