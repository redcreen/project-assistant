# project-assistant Development Plan

[English](development-plan.md) | [中文](development-plan.zh-CN.md)

## Purpose

This document is the durable maintainer-facing execution plan that sits below `docs/roadmap.md` and above the AI control surfaces.

It answers one practical question:

`what should happen next, where should maintainers resume, and what detail sits underneath each roadmap milestone?`

## Related Documents

- [../../roadmap.md](../../roadmap.md)
- [../../architecture.md](../../architecture.md)
- [../../test-plan.md](../../test-plan.md)

## How To Use This Plan

1. Read the roadmap first to understand overall progress and the next stage.
2. Read `Overall Progress`, `Execution Task Progress`, and `Ordered Execution Queue` here to know where to resume.
3. Only drop into the internal control docs when you are maintaining the automation itself.

## Overall Progress

| Item | Current Value |
| --- | --- |
| Overall Progress | 3 / 4 execution tasks complete |
| Current Phase | `post-M21 daemon-host baseline active` |
| Active Slice | `stabilize-daemon-host-baseline-for-dogfooding` |
| Current Objective | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins |
| Active Slice Exit Signal | daemon-host baseline 可被更广泛使用，且没有高频 runtime/host 回归 |
| Clear Next Move | EL-4 keep “single foreground writer per repo” as evidence-gated backlog until real adoption proves it should move from follow-up into a formal slice |
| Next Candidate Slice | `package-daemon-host-baseline-for-release` |

## Current Position

| Item | Current Value | Meaning |
| --- | --- | --- |
| Current Phase | `post-M21 daemon-host baseline active` | Current maintainer-facing phase |
| Active Slice | `stabilize-daemon-host-baseline-for-dogfooding` | The slice tied to the current execution line |
| Current Execution Line | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins | What the repo is trying to finish now |
| Validation | validate_daemon_runtime.py`、`validate_vscode_host_extension.py`、`validate_daemon_host_mvp.py`、`validate_daemon_legacy_rollout.py` 已通过，M17-M21 baseline 已具备可持续回归的自动化入口 | The checks that must stay true before moving on |

## Execution Task Progress

| Order | Task | Status |
| --- | --- | --- |
| 1 | EL-1 harden daemon runtime edges exposed by concurrent startup, shutdown, or status polling in real workspaces | done |
| 2 | EL-2 keep README / architecture / usage / test plan / entry routing aligned with daemon-host as the new default fast path | done |
| 3 | EL-3 collect broader dogfooding evidence before opening the next host surface or any M15 discussion | done |
| 4 | EL-4 keep “single foreground writer per repo” as evidence-gated backlog until real adoption proves it should move from follow-up into a formal slice | next |

## Milestone Overview

| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |
| M1 | done | establish `.codex` control surfaces and project tiering | core skill routing | current state is recoverable |
| M2 | done | establish convergent retrofit | control-surface scripts | retrofit no longer stops halfway |
| M3 | done | establish progress and handoff workflows | module layer + snapshot scripts | progress and handoff are stable |
| M4 | done | establish durable doc standards and doc validation | document standards + docs scripts | durable docs pass structure gates |
| M5 | done | establish public-doc bilingual switching and acceptance | i18n rules + i18n validator | public docs switch cleanly between English and Chinese |
| M6 | done | converge on the embedded architect-assistant operating model | previous milestones | planning, execution, architecture supervision, and devlogs are default capabilities |
| M7 | done | improve narrative quality and automatic architecture triggers | M6 | less manual cleanup and fewer direction corrections after retrofit |
| M8 | deferred | optimize internal control-surface output by language | handoff + command templates + validation policy | continues as bounded supporting backlog |
| M9 | deferred | compress continue / resume / handoff snapshots without losing recoverability | continue snapshot + handoff + validation policy | continues as bounded supporting backlog |
| M10 | done | add a strategic-evaluation layer above execution | [M7](reference/project-assistant/development-plan.md#m7) + approved strategic direction | the system emits durable strategic judgment and still leaves direction changes to human approval |
| M11 | done | add program orchestration across slices/executors | [M10](reference/project-assistant/development-plan.md#m10) + durable program board | the system coordinates related slices instead of depending on repeated human “continue” prompts |
| M12 | done | add supervised long-run delivery | [M11](reference/project-assistant/development-plan.md#m11) + stable escalation policy | long-running delivery can continue to real business decision points |
| M13 | done | add the PTL-driven supervision loop | [M12](reference/project-assistant/development-plan.md#m12) + durable delivery supervision | PTL can inspect, continue, re-sequence, or escalate periodically or by event |
| M14 | done | add worker handoff and re-entry | [M13](reference/project-assistant/development-plan.md#m13) + durable handoff / supervision truth | `when a worker stops, the project does not stop` becomes durable capability |
| M15 | later | add selective multi-executor scheduling only for safe parallel work | [M14](reference/project-assistant/development-plan.md#m14) + disjoint write scopes + conflict control | real multi-executor work is only allowed when write scopes and return paths are explicit |
| M16 | done | add the unified hard entry and tool front door | [M14](reference/project-assistant/development-plan.md#m14) + versioned control surface + entry scripts | old repos auto-upgrade first and `continue / progress / handoff` no longer fall back to free prose first |
| M17 | done | build the PTL daemon runtime core and write-safe fast-path baseline | [M16](reference/project-assistant/development-plan.md#m16) + daemon-first architecture + runtime contract | the daemon runtime, queue/event contract, runtime store, and minimum CLI control surface are usable |
| M18 | done | build the VS Code host shell and live-status surfaces | [M17](reference/project-assistant/development-plan.md#m17) + daemon event contract | users can see queue state, status, the active slice, and recent events in VS Code |
| M19 | done | build the host continue-resume bridge so `resume-ready` becomes a host action | [M18](reference/project-assistant/development-plan.md#m18) + Codex runner / command contract | `manual continue` and conservative `one-click continue` work without chat-box injection |
| M20 | done | validate the daemon-host baseline on local workspaces and re-validate older feature families on top of it | [M19](reference/project-assistant/development-plan.md#m19) + representative local workspaces | the daemon-host baseline is stable and older capabilities keep passing on the new baseline |
| M21 | done | resume post-M16 rollout verification on top of the daemon-host baseline | M20 | representative legacy repos still upgrade first, render structured panels, and are no longer dominated by avoidable synchronous work |

## Ordered Execution Queue

| Order | Slice | Status | Objective | Validation |
| --- | --- | --- | --- | --- |
| 1 | `close-m17-through-m21-daemon-host-baseline` | earlier slice | 把 daemon runtime、VS Code host shell、continue bridge、本地验证、旧功能回归和 post-M16 rollout 恢复一口气收口成可用 baseline | validate_daemon_runtime.py`、`validate_vscode_host_extension.py`、`validate_daemon_host_mvp.py`、`validate_daemon_legacy_rollout.py |
| 2 | `stabilize-daemon-host-baseline-for-dogfooding` | current | 把刚完成的 daemon-host baseline 稳定成默认快路径，并为更广泛 dogfooding 准备好 operator docs 与采证入口 | validate_gate_set.py --profile deep`、runtime/host smoke、broader workspace dogfooding |
| 3 | `package-daemon-host-baseline-for-release` | next / queued | 决定 daemon-host baseline 的 release 叙事、安装说明和版本落点 | release-facing docs、gate outputs 和 install path 对齐 |
| 4 | `future-host-expansion-and-m15-evidence` | next / queued | 只在 daemon-host baseline 已稳定、dogfooding 证据充分后，再判断是否扩大到更强宿主表面或重新讨论 `M15 | real adoption evidence + clear write-scope boundaries |
| 5 | `M17 / build-ptl-daemon-runtime-core` | next / queued | 建立 daemon runtime、runtime store、queue/event contract，以及最小的 `start/status/stop/queue` 控制面 | validate_daemon_runtime.py |
| 6 | `M18 / build-vscode-host-shell-and-live-status` | next / queued | 建立 VS Code 宿主前端壳，至少包含 Tree View、Status Bar、Output channel，以及与 daemon 的连接 | validate_vscode_host_extension.py |
| 7 | `M19 / wire-manual-and-one-click-continue` | next / queued | 把 `resume-ready` 事件接成 `manual continue`，并补上保守的 `one-click continue | validate_vscode_host_extension.py` + host continue smoke |
| 8 | `M20 / validate-daemon-host-mvp-on-local-workspaces` | next / queued | 在代表性的本地 workspace 上验证 daemon + VS Code host MVP 的状态展示、恢复路径和稳定性 | validate_daemon_host_mvp.py |
| 9 | `M20 / validate-legacy-feature-set-on-daemon-host-baseline` | next / queued | 在 daemon-host 基线上按家族逐项回归旧功能，而不是等所有能力都迁完再统一验收 | validate_daemon_host_mvp.py` + `validate_gate_set.py --profile deep |
| 10 | `M21 / resume-post-m16-rollout-on-daemon-host-baseline` | next / queued | 在 daemon-host 基线稳定后，恢复 post-M16 rollout verification，并重新评估 host-bridge 证据 | validate_daemon_legacy_rollout.py |

## Milestone Details

### M1

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | establish `.codex` control surfaces and project tiering |
| Depends On | core skill routing |
| Exit Criteria | current state is recoverable |

### M2

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | establish convergent retrofit |
| Depends On | control-surface scripts |
| Exit Criteria | retrofit no longer stops halfway |

### M3

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | establish progress and handoff workflows |
| Depends On | module layer + snapshot scripts |
| Exit Criteria | progress and handoff are stable |

### M4

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | establish durable doc standards and doc validation |
| Depends On | document standards + docs scripts |
| Exit Criteria | durable docs pass structure gates |

### M5

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | establish public-doc bilingual switching and acceptance |
| Depends On | i18n rules + i18n validator |
| Exit Criteria | public docs switch cleanly between English and Chinese |

### M6

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | converge on the embedded architect-assistant operating model |
| Depends On | previous milestones |
| Exit Criteria | planning, execution, architecture supervision, and devlogs are default capabilities |

### M7

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | improve narrative quality and automatic architecture triggers |
| Depends On | M6 |
| Exit Criteria | less manual cleanup and fewer direction corrections after retrofit |

### M8

| Item | Current Value |
| --- | --- |
| Status | deferred |
| Goal | optimize internal control-surface output by language |
| Depends On | handoff + command templates + validation policy |
| Exit Criteria | continues as bounded supporting backlog |

### M9

| Item | Current Value |
| --- | --- |
| Status | deferred |
| Goal | compress continue / resume / handoff snapshots without losing recoverability |
| Depends On | continue snapshot + handoff + validation policy |
| Exit Criteria | continues as bounded supporting backlog |

### M10

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add a strategic-evaluation layer above execution |
| Depends On | [M7](reference/project-assistant/development-plan.md#m7) + approved strategic direction |
| Exit Criteria | the system emits durable strategic judgment and still leaves direction changes to human approval |

### M11

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add program orchestration across slices/executors |
| Depends On | [M10](reference/project-assistant/development-plan.md#m10) + durable program board |
| Exit Criteria | the system coordinates related slices instead of depending on repeated human “continue” prompts |

### M12

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add supervised long-run delivery |
| Depends On | [M11](reference/project-assistant/development-plan.md#m11) + stable escalation policy |
| Exit Criteria | long-running delivery can continue to real business decision points |

### M13

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add the PTL-driven supervision loop |
| Depends On | [M12](reference/project-assistant/development-plan.md#m12) + durable delivery supervision |
| Exit Criteria | PTL can inspect, continue, re-sequence, or escalate periodically or by event |

### M14

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add worker handoff and re-entry |
| Depends On | [M13](reference/project-assistant/development-plan.md#m13) + durable handoff / supervision truth |
| Exit Criteria | `when a worker stops, the project does not stop` becomes durable capability |

### M15

| Item | Current Value |
| --- | --- |
| Status | later |
| Goal | add selective multi-executor scheduling only for safe parallel work |
| Depends On | [M14](reference/project-assistant/development-plan.md#m14) + disjoint write scopes + conflict control |
| Exit Criteria | real multi-executor work is only allowed when write scopes and return paths are explicit |

### M16

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add the unified hard entry and tool front door |
| Depends On | [M14](reference/project-assistant/development-plan.md#m14) + versioned control surface + entry scripts |
| Exit Criteria | old repos auto-upgrade first and `continue / progress / handoff` no longer fall back to free prose first |

### M17

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | build the PTL daemon runtime core and write-safe fast-path baseline |
| Depends On | [M16](reference/project-assistant/development-plan.md#m16) + daemon-first architecture + runtime contract |
| Exit Criteria | the daemon runtime, queue/event contract, runtime store, and minimum CLI control surface are usable |

### M18

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | build the VS Code host shell and live-status surfaces |
| Depends On | [M17](reference/project-assistant/development-plan.md#m17) + daemon event contract |
| Exit Criteria | users can see queue state, status, the active slice, and recent events in VS Code |

### M19

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | build the host continue-resume bridge so `resume-ready` becomes a host action |
| Depends On | [M18](reference/project-assistant/development-plan.md#m18) + Codex runner / command contract |
| Exit Criteria | `manual continue` and conservative `one-click continue` work without chat-box injection |

### M20

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | validate the daemon-host baseline on local workspaces and re-validate older feature families on top of it |
| Depends On | [M19](reference/project-assistant/development-plan.md#m19) + representative local workspaces |
| Exit Criteria | the daemon-host baseline is stable and older capabilities keep passing on the new baseline |

### M21

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | resume post-M16 rollout verification on top of the daemon-host baseline |
| Depends On | M20 |
| Exit Criteria | representative legacy repos still upgrade first, render structured panels, and are no longer dominated by avoidable synchronous work |

## Current Next Step

| Next Move | Why |
| --- | --- |
| EL-4 keep “single foreground writer per repo” as evidence-gated backlog until real adoption proves it should move from follow-up into a formal slice | This is the first unchecked execution task, so both the roadmap and this plan stay aligned to the same resume point. |
