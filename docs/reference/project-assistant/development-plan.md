# project-assistant Development Plan

[English](development-plan.md) | [中文](development-plan.zh-CN.md)

## Purpose

This document is the durable maintainer-facing execution plan that sits below `docs/roadmap.md` and above `.codex/plan.md`.

It answers:

`what should happen next, where maintainers should resume, and what detail sits underneath each roadmap milestone?`

## Related Documents

- [../../roadmap.md](../../roadmap.md)
- [../../architecture.md](../../architecture.md)
- [../../test-plan.md](../../test-plan.md)

## How To Use This Plan

1. Read the roadmap first to understand milestone order.
2. Read `Current Position` and `Ordered Execution Queue` here to know where to resume.
3. Drop into `.codex/plan.md` only when you need the live control-surface detail.

## Current Position

| Item | Current Value | Meaning |
| --- | --- | --- |
| Current Phase | `M17-M21 daemon-host mainline planning ready` | the discussion has moved from “should we do a daemon?” to “in what order do we build M17 through M21?” so implementation can now be user-directed by milestone |
| Active Slice | `define-m17-through-m21-daemon-host-mainline` | the current line turns the fast upgrade into an explicit milestone order: `M17 daemon core -> M18 VS Code host -> M19 resume bridge -> M20 validation -> M21 rollout resume` |
| Current Execution Line | write the default implementation order and first-host scope clearly enough that development can proceed slice by slice without bouncing between daemon internals, host UI, and chat integration | the real question now is “which cut should we build first, and how should each later cut attach?” |
| Validation | `async-execution-and-latency-governance.md`, `ptl-daemon-mvp.md`, `host-resume-bridge.md`, and the control truth all align on “daemon core first, VS Code host next, resume bridge after that” | the implementation plan is now durable and can be used directly to drive build order |

## Milestone Overview

| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |
| M1 | done | establish `.codex` control surface and tiering | core skill routing | current state is recoverable |
| M2 | done | establish convergent retrofit | control-surface scripts | retrofit no longer stops midway |
| M3 | done | establish progress and handoff workflows | module layer + snapshot scripts | progress and handoff are stable |
| M4 | done | establish durable-doc standards and doc validation | document standards + docs scripts | durable docs pass structural gates |
| M5 | done | establish bilingual public-doc switching and validation | i18n rules + i18n validator | public docs switch cleanly between English and Chinese |
| M6 | done | shift to an embedded architect-assistant operating model | previous milestones | planning, execution, architecture supervision, and devlog capture are default-on behaviors |
| M7 | done | improve narrative quality and automated architecture triggers | M6 | less manual cleanup after retrofit and fewer direction-correction prompts |
| M8 | deferred | locale-aware internal control-surface output | handoff + command templates + validation policy | becomes supporting backlog instead of the mainline |
| M9 | deferred | automatic context compression plus slimmer continue/resume/handoff snapshots without losing recoverability | continue snapshot + handoff + validation policy | becomes supporting backlog instead of the mainline |
| M10 | done | add a PTL-driven strategic-evaluation layer | M7 + approved strategic direction | roadmap / governance / architecture adjustments become durable, reviewable strategy outputs |
| M11 | done | add a PTL-driven program-orchestration layer | M10 + durable program board | the system coordinates multiple related slices instead of depending on repeated human “continue” prompts |
| M12 | done | add PTL-driven supervised long-run delivery | M11 + stable escalation policy | long-running delivery can continue until a real business decision point |
| M13 | done | add a PTL-driven supervision loop | M12 + durable delivery supervision | the PTL keeps watching the project through periodic and event-driven checks |
| M14 | done | add worker handoff and re-entry | M13 + durable handoff / supervision truth | `when a worker stops, the project should not stop with it` becomes durable behavior |
| M15 | later | add selective multi-executor scheduling | M14 + disjoint write scopes + conflict control | only safe parallel work enters multi-executor scheduling |
| M16 | done | add the tool-first front door and hard-entry bridge | M14 + versioned control surface + entry scripts | legacy repos auto-upgrade before resume, and `continue / progress / handoff` no longer fall back to free-form prose first |
| M17 | active | build the PTL daemon runtime core and the write-safe fast-upgrade baseline | M16 + daemon-first architecture + runtime contract | the daemon runtime, queue/event contract, runtime store, and minimum CLI control surface are usable |
| M18 | next | build the VS Code host shell and live-status surfaces | M17 + daemon event contract | users can see queue state, status, the active slice, and recent events in VS Code |
| M19 | next | build the host continue-resume bridge so `resume-ready` becomes a host action | M18 + Codex runner / command contract | `manual continue` works and conservative `one-click continue` can be added without relying on chat-box injection |
| M20 | next | validate the daemon-host baseline on local workspaces and re-validate older feature families on top of it | M19 + representative local workspaces | the daemon-host baseline is stable and older capabilities keep passing on the new baseline |
| M21 | next | resume post-M16 rollout verification on top of the daemon-host baseline | M20 | representative legacy repos still upgrade first, render structured panels, and are no longer dominated by avoidable synchronous work |

## Ordered Execution Queue

| Order | Slice | Status | Objective | Validation |
| --- | --- | --- | --- | --- |
| 1 | `redefine the operating model` | earlier slice | n/a | n/a |
| 2 | `embed architecture supervision by default` | earlier slice | n/a | n/a |
| 3 | `embed development-log capture by default` | earlier slice | n/a | n/a |
| 4 | `simplify the human surface` | earlier slice | n/a | n/a |
| 5 | `define the escalation and gate model` | earlier slice | n/a | n/a |
| 6 | `operationalize reporting and release governance` | earlier slice | n/a | n/a |
| 7 | `automate supervision, release protection, and human windows` | earlier slice | n/a | n/a |
| 8 | `make architecture retrofit a first-class flow` | earlier slice | n/a | n/a |
| 9 | `prepare project-assistant for broader repo adoption` | earlier slice | n/a | n/a |
| 10 | `tighten-maintainer-facing-narrative-and-architecture-triggers` | completed milestone slice | representative medium / large repos now read more like maintainer restore panels; at least one architecture trigger auto-escalates from drift | representative repo snapshots improved and automatic trigger visible |
| 11 | `activate-m10-strategic-evaluation-layer` | completed | promote the strategic layer from proposal to active roadmap direction and align roadmap / README / control truth | docs, roadmap, development plan, and control truth all point to M10 |
| 12 | `establish-strategy-surface-and-review-contract` | completed | create the first durable strategy surface, define review boundaries, and record how M8/M9 move into supporting backlog | `.codex/strategy.md` exists; docs and control truth align; `deep` passes |
| 13 | `close-m10-and-queue-m11` | completed | turn M10 into scripts, gates, snapshots, and docs that all agree | `deep` and `release` pass |
| 14 | `close-m11-and-queue-m12` | completed | turn M11 into a durable program board with gates, snapshots, and docs that all agree | `deep` and `release` pass |
| 15 | `close-m12-and-open-rollout` | completed | turn M12 into delivery-supervision, gates, snapshots, and docs that all agree | `deep` and `release` pass |
| 16 | `define-m13-m14-m15-post-m12-mainline` | completed | formalize post-M12 into `M13 / M14 / M15` and explain the practical meaning of worker handoff and re-entry | roadmap, README, development plan, strategic direction doc, and orchestration model all align |
| 17 | `close-m13-and-m14-and-queue-m15-evidence` | completed | turn `M13 / M14` into durable PTL supervision / worker handoff control surfaces, gates, progress, and handoff | `deep` and `release` pass; control truth, README, roadmap, development plan, and snapshots all show `M13 / M14 done` |
| 18 | `close-m16-tool-first-front-door-and-queue-rollout-verification` | completed | turn the real entry problem into one front door, one preflight, one structured-output contract, and one durable `entry-routing` surface | `project_assistant_entry.py`, `sync_resume_readiness.py`, `validate_entry_routing.py`, `deep`, and `release` all pass; representative legacy repos can upgrade first and then render panels |
| 19 | `define-m17-through-m21-daemon-host-mainline` | current mainline | turn the fast upgrade into an explicit `M17-M21` milestone line and make the VS Code extension frontend the default first host | roadmap, development plan, status, plan, and the host-bridge note all read back the same milestone order |
| 20 | `M17 / build-ptl-daemon-runtime-core` | next | build the daemon runtime, queue/event contract, runtime store, and minimum CLI control surface | the daemon can start / stop / expose queue state and emit host-consumable events |
| 21 | `M18 / build-vscode-host-shell-and-live-status` | next | build the VS Code host shell with at least a Tree View, Status Bar item, Output channel, and daemon connectivity | users can already see live state, the active slice, and recent events inside VS Code |
| 22 | `M19 / wire-manual-and-one-click-continue` | next | turn `resume-ready` into host-visible continue actions, starting with `manual continue` and optionally adding conservative `one-click continue` | stopped work can resume through the host without relying on chat-box injection |
| 23 | `M20 / validate-daemon-host-mvp-on-local-workspaces` | next | validate daemon + VS Code host MVP state, recovery, and stability on representative local workspaces | local-workspace validation shows the host MVP is stable enough to carry the next phase |
| 24 | `M20 / validate-legacy-feature-set-on-daemon-host-baseline` | next | re-validate older feature families one by one on the daemon-host baseline instead of waiting for a giant migration | older capabilities keep passing on the new baseline without regressing the coding-speed goal |
| 25 | `M21 / resume-post-m16-rollout-on-daemon-host-baseline` | next | resume post-M16 rollout verification only after the daemon-host baseline and older feature families are trusted | representative legacy repos still upgrade first, render structured panels, and no longer feel dominated by avoidable synchronous work |
| 26 | `formalize-issue-driven-closure-loop` | supporting backlog / todo | turn the recurring request shape `current problem -> reasoning -> solution -> devlog -> architecture -> roadmap / development plan -> one long implementation run` into a default skill behavior instead of relying on repeated user reminders | when implemented, durable problems should automatically trigger this closure chain |
| 27 | `formalize-control-truth-sync-determinism` | supporting backlog / todo | turn `.codex/status.md`, `.codex/plan.md`, the strategy / program-board / delivery / PTL / handoff surfaces, and the `continue / progress / handoff` outputs into one deterministic refresh transaction so users stop seeing partially updated or locally stale truth during `project assistant continue` | when implemented, legacy-repo upgrade, surface refresh, structured first screen, and durable truth should align within one checkpoint |

## Milestone Details

### M10

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add a PTL-driven strategic-evaluation layer |
| Depends On | M7 + approved strategic direction |
| Exit Criteria | roadmap / governance / architecture adjustments become durable, reviewable strategy outputs |

### M11

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add a PTL-driven program-orchestration layer |
| Depends On | M10 + durable program board |
| Exit Criteria | the system can coordinate multiple related slices instead of depending on repeated human “continue” prompts |

### M12

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add PTL-driven supervised long-run delivery |
| Depends On | M11 + stable escalation policy |
| Exit Criteria | long-running delivery can continue until a real business decision point |

### M13

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add a PTL-driven supervision loop |
| Depends On | M12 + durable delivery supervision |
| Exit Criteria | the PTL can inspect, continue, resequence, or escalate through periodic and event-driven checks |

### M14

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add worker handoff and re-entry |
| Plain-Language Meaning | `when a worker stops, the project should not stop with it` |
| Depends On | M13 + durable handoff / supervision truth |
| Exit Criteria | remaining work still has a durable path forward through resume, reassignment, re-queueing, or escalation |

### M15

| Item | Current Value |
| --- | --- |
| Status | later |
| Goal | add selective multi-executor scheduling |
| Depends On | M14 + disjoint write scopes + conflict control |
| Exit Criteria | only work with clear write boundaries and safe merge paths enters multi-executor scheduling |

### M16

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add the tool-first front door and hard-entry bridge |
| Depends On | M14 + versioned control surface + entry scripts |
| Exit Criteria | `continue / progress / handoff` share one front door, one preflight path, and one structured first-screen contract; the repo also owns a durable `entry-routing` contract and a CLI front door |

### M17

| Item | Current Value |
| --- | --- |
| Status | active |
| Goal | build the PTL daemon runtime core and the write-safe fast-upgrade baseline |
| Depends On | M16 + daemon-first architecture + runtime contract |
| Exit Criteria | the daemon runtime, queue/event contract, runtime store, and minimum CLI control surface are usable |

### M18

| Item | Current Value |
| --- | --- |
| Status | next |
| Goal | build the VS Code host shell and live-status surfaces |
| Depends On | M17 + daemon event contract |
| Exit Criteria | users can see queue state, status, the active slice, and recent events in VS Code |

### M19

| Item | Current Value |
| --- | --- |
| Status | next |
| Goal | build the host continue-resume bridge so `resume-ready` becomes a host action |
| Depends On | M18 + Codex runner / command contract |
| Exit Criteria | `manual continue` works and conservative `one-click continue` can be added without relying on chat-box injection |

### M20

| Item | Current Value |
| --- | --- |
| Status | next |
| Goal | validate the daemon-host baseline on local workspaces and re-validate older feature families on top of it |
| Depends On | M19 + representative local workspaces |
| Exit Criteria | the daemon-host baseline is stable and older capabilities keep passing on the new baseline |

### M21

| Item | Current Value |
| --- | --- |
| Status | next |
| Goal | resume post-M16 rollout verification on top of the daemon-host baseline |
| Depends On | M20 |
| Exit Criteria | representative legacy repos still upgrade first, render structured panels, and are no longer dominated by avoidable synchronous work |

## Current Next Step

| Next Move | Why |
| --- | --- |
| Start with `build-ptl-daemon-runtime-core` | the daemon core is the shared base for the host shell, resume bridge, and live status; without it, host work will float |
| Then move into `build-vscode-host-shell-and-live-status` | the user wants to see that the page is moving and code is changing, so the first host frontend should not wait behind later chat integration ideas |
| Then run `wire-manual-and-one-click-continue` | the resume action is the key value of the host bridge and should land after daemon core and live status already exist |
| Run `validate-daemon-host-mvp-on-local-workspaces` before wider re-validation | prove the MVP chain on real local workspaces before asking older feature families to stand on it |
| Then run `validate-legacy-feature-set-on-daemon-host-baseline` | the strategy is explicitly “make the experience lighter first, then re-validate older capabilities in order” instead of performing one giant migration |
| Reserve `formalize-issue-driven-closure-loop` | this request shape is now recurring often enough that it should become a first-class default behavior in the skill |
| Reserve `formalize-control-truth-sync-determinism` | `project assistant continue` can still feel like `.codex` truth refreshed in pieces; that lag should become an explicit determinism milestone instead of a recurring surprise |

## Strategic Direction

| Topic | Scope | Current Position |
| --- | --- | --- |
| daemon-first async execution, host resume bridge, and latency governance | the product goal is now immediate coding-speed recovery: land the daemon core, the VS Code host frontend, and the resume bridge first, then re-validate the older feature set on that new baseline | active |
| business planning, orchestration, and hard-entry routing | `project-assistant` has closed the PTL-centered `M10 / M11 / M12 / M13 / M14` layers and added `M16` so `continue / progress / handoff` now share a canonical front door; `M15` remains evidence-gated later, and M8/M9 stay bounded supporting backlog | active |

Direction document:

- [Strategic Planning And Program Orchestration](strategic-planning-and-program-orchestration.md)
- [Host Resume Bridge And VS Code Extension Feasibility](host-resume-bridge.md)
