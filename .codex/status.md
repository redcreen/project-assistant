# Status

## Delivery Tier

- Tier: `medium`
- Last reviewed: `2026-04-14`

## Current Phase

`release packaging prep active`

## Active Slice
`package-daemon-host-baseline-for-release`

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

## Execution Tasks
- [x] EL-1 inspect current release/version/install references and mainline delta since the last safe install tag
- [x] EL-2 align README, install instructions, and roadmap around the selected daemon-host baseline release path
- [x] EL-3 ensure gate outputs and validation commands match the release-facing path
- [x] EL-4 write release notes or release-prep summary for the daemon-host baseline
- [x] EL-5 run fast gate and final consistency checks

## Development Log Capture
- Trigger Level: high
- Pending Capture: no
- Reason: latest devlog already captures the most recent durable reasoning
- Last Entry: `docs/devlog/2026-05-05-daemon-host-release-prep.md`

## Architecture Supervision
- Signal: `green`
- Signal Basis: M22 governed learning is accepted and active; the daemon-host/PTL-loop baseline now has an immutable stable tag, while `v0.1.9` remains the previous docs-browser-era release.
- Root Cause Hypothesis: if release-facing docs mix the previous `v0.1.9` release with the current daemon-host/PTL-loop stable tag, users can install the wrong capability set.
- Correct Layer: release notes, install/version references, branch-aware install scripts, README/docs roadmap, and validation gates.
- Automatic Review Trigger: when version references, install scripts, release notes, or daemon-host baseline validation changes
- Escalation Gate: continue automatically

## Current Escalation State
- Current Gate: continue automatically
- Reason: release-prep baseline is complete and validated; publishing a new immutable tag remains a separate clean-tree release action.
- Next Review Trigger: review again when a new release tag is cut, package version changes, or the mainline install path changes

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
- M23 `ship-ptl-policy-gate-baseline` 已完成：
  - `scripts/ptl_gate.py` 已能生成 `.codex/ptl-policy/project-policy.json` 与 `.codex/ptl-policy/preflight.json`
  - `continue_entry.py` 与 `progress_entry.py` 已默认追加 `PTL Preflight` 面板
  - `scripts/validate_ptl_gate.py` 已覆盖 generic、missing-control、style-engine-like、openclaw-skills-like、entry-activation fixtures
  - `validate_gate_set.py --profile fast` 已把 PTL gate 纳入统一门禁
- M24 `ship-completion-gate-stop-semantics` 已完成：
  - `scripts/completion_gate.py` 已能生成 `.codex/completion-gate.json`，并区分 `allow / require-continue / blocked / requires-human-decision / explicitly-deferred`
  - `continue_entry.py` 与 `progress_entry.py` 已默认追加 `Completion Gate` 面板
  - `scripts/validate_completion_gate.py` 已覆盖 complete、open-task、final-text-next-step、explicit-deferred、human-decision fixtures
  - `validate_gate_set.py --profile fast` 已把 Completion gate 纳入统一门禁
- M25 `ship-task-pipeline-runner-loop` 已完成：
  - `scripts/pipeline_runner.py` 已能生成 `.codex/task-pipeline.json`，支持 `run --task`、`enqueue`、`panel`
  - runner 已支持 command task 自动执行、失败后创建 repair task、repair 后回到原 task、LLM task 暂停成 `awaiting-llm`
  - `continue_entry.py` 与 `progress_entry.py` 已默认追加 `Task Pipeline` 面板
  - `project_assistant_entry.py execute` 已路由到 `pipeline_runner.py`
  - `scripts/validate_pipeline_runner.py` 已覆盖 command-loop、repair-loop、llm-pause、run-argument-enqueue、human-decision、entry-panel fixtures
  - `validate_gate_set.py --profile fast` 已把 pipeline runner 纳入统一门禁
- M26 `ship-host-message-ingress-loop` 已完成：
  - `scripts/message_ingress.py` 已能生成 `.codex/message-ingress.json`，并分类 execution / analysis / progress / generic messages
  - message ingress 会把非 classify-only 消息入队到 `.codex/task-pipeline.json`，附带 raw message、message id、source 和 intent metadata
  - `continue_entry.py` 与 `progress_entry.py` 已默认追加 `Message Ingress` 面板
  - `project_assistant_entry.py message` 已路由到 `message_ingress.py ingest`
  - `scripts/validate_message_ingress.py` 已覆盖 execution-message、discussion-message、classify-only、front-door、entry-panel fixtures
  - `validate_gate_set.py --profile fast` 已把 message ingress 纳入统一门禁
  - `scripts/codex_message_wrapper.py` 与 `scripts/install_codex_message_wrapper.py` 已提供轻量 CLI wrapper，当前已安装到 `~/.local/bin/codex`
  - `scripts/validate_codex_message_wrapper.py` 已覆盖 initial prompt、`exec` prompt、`app-server` skip 和 disable switch fixtures
- M22 `connect-ptl-learning-review-to-host` 已完成：
  - `scripts/ptl_learning.py` 已提供 `scan / panel / status / accept / reject / snooze`
  - `.codex/ptl-policy/learning-review.json` 已记录 pending candidates，当前本仓库 dogfood 生成了 4 个待 review 候选
  - accepted rules 写入 `~/.codex/project-assistant/learned-registry.json`，不在 skill 安装目录内，重装不会覆盖
  - `scripts/ptl_gate.py` 会把 accepted rules 合成为 `learned.*` PTL preflight rules
  - Codex App hook 会在用户消息进入 loop 时同步扫描 PTL learning review
  - VS Code host 状态栏和 Tree View 已能显示 pending review，并提供 accept / reject / snooze 命令
  - `ptl_learning.py` 现在除固定纠错 pattern 外，还会按语义概念对归纳重复纠错候选；候选仍必须走 human review 后才会写入 registry
  - `scripts/validate_ptl_learning.py` 已覆盖 pending、accept、reject、snooze、registry persistence、semantic induction 和 accepted-rule preflight injection
  - `validate_gate_set.py --profile fast` 已把 PTL learning 纳入统一门禁
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

- release packaging prep 已完成：`v0.1.9` 被标为 previous docs-browser release，daemon-host / PTL-loop baseline 已通过当前 stable tag 获取。
- release gate 已在当前 release 内容上通过；clean-tree release flow 已创建 immutable tag。
- 跨项目 dogfood 已在 `style engine` 与 `openclaw-skills` 上执行：style-engine 命中 image-generation / learned rules；openclaw-skills 正确要求 Phase 6 bridge 前 human review，随后被显式暂停，避免误推进 order 主线。

## Blockers / Open Decisions

- None currently.

## Follow-ups

- 后续 release tag 仍需在 clean working tree 上由 release flow 创建。
- PTL learning 的跨项目自动晋升和规则衰减仍属于后续增强；基础语义归纳已进入当前 stable baseline。

## Next 3 Actions

1. Push `main` and the release tag when remote publication is intended.
2. Update representative downstream projects from the stable tag and verify PTL signals.
3. Monitor dogfood results before promoting cross-project rules automatically.
