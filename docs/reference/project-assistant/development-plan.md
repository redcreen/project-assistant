# project-assistant Development Plan

[English](development-plan.md) | [中文](development-plan.zh-CN.md)

## Purpose

This document is the durable maintainer-facing execution plan that sits below `docs/roadmap.md` and above `.codex/plan.md`.

It answers one practical question:

`what should happen next, where should maintainers resume, and what detail sits underneath each roadmap milestone?`

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
| Current Phase | `PTL supervision and worker handoff layers closed; M15 evidence collection queued` | `M13 / M14` are now durable capabilities rather than only roadmap names; the repo is now collecting cross-repo evidence to decide whether `M15` is actually needed |
| Active Slice | `close-m13-and-m14-and-queue-m15-evidence` | the current line has already closed `M13 / M14` and switched the mainline to post-M14 evidence collection |
| Current Execution Line | roll out the completed `PTL supervision loop` and `worker handoff and re-entry` on more repos, and prove that the PTL can durably catch and continue work after a worker stops | the current question is no longer “can we name M15,” but “should M15 exist at all” |
| Validation | PTL supervision / worker handoff control surfaces, gates, progress, handoff, and docs all exist; `deep` and `release` still pass | How this line proves `M13 / M14` are closed while `M15` remains evidence-gated |

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
| M8 | deferred | locale-aware internal control-surface output | handoff + command templates + validation policy | becomes supporting backlog under M10 instead of the mainline |
| M9 | deferred | slim continue/resume snapshots without losing recoverability | continue snapshot + handoff + validation policy | becomes supporting backlog under M10 instead of the mainline |
| M10 | done | add a PTL-driven strategic-evaluation layer above execution and retrofit | M7 + approved strategic direction | roadmap / governance / architecture adjustments become durable, reviewable strategy outputs instead of ad hoc intuition |
| M11 | done | add a PTL-driven program-orchestration layer across multiple slices or workers | M10 + durable program board | stabilize the durable orchestration truth inside one Codex first; if multi-executor scheduling is needed later, create it as a separate milestone |
| M12 | done | add PTL-driven supervised long-run delivery | M11 + stable escalation policy | long-running delivery can continue until a real business decision point |
| M13 | done | add a PTL-driven supervision loop | M12 + durable delivery supervision | the PTL keeps watching delivery through periodic and event-driven checks instead of letting the project stop with the worker |
| M14 | done | add worker handoff and re-entry | M13 + durable handoff / supervision truth | after checkpoints, timeouts, failures, or handoffs, unfinished work can still be resumed, reassigned, re-queued, or escalated |
| M15 | later | add selective multi-executor scheduling | M14 + disjoint write scopes + conflict control | only safe parallel work enters multi-executor scheduling; tightly coupled work stays on one primary write line |

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
| 11 | `activate-m10-strategic-evaluation-layer` | completed transition slice | promote the strategic layer from proposal to active roadmap direction and align roadmap / README / control truth | docs, roadmap, development plan, and control truth all point to M10 |
| 12 | `establish-strategy-surface-and-review-contract` | completed | create the first durable strategy surface, define review boundaries, and record how M8/M9 move into supporting backlog | `.codex/strategy.md` exists; docs and control truth align; `deep` passes |
| 13 | `close-m10-and-queue-m11` | completed | turn M10 from “approved direction” into “scripts, gates, snapshots, and docs all agree”, then queue M11 as the next mainline | `validate_strategy_surface.py`, `progress / continue / handoff`, README, roadmap, development plan, and control truth all align; `deep` and `release` pass |
| 14 | `close-m11-and-queue-m12` | completed | turn M11 from “program direction plus board sketch” into “program-board, gates, snapshots, and docs all agree”, then queue M12 as the next mainline | `validate_program_board.py`, `progress / continue / handoff`, README, roadmap, development plan, and control truth all align; `deep` and `release` pass |
| 15 | `close-m12-and-open-rollout` | completed | turn M12 from “approved direction” into “delivery-supervision, gates, snapshots, and docs all agree”, then open rollout / friction collection as the next durable state | `validate_delivery_supervision.py`, `progress / continue / handoff`, README, roadmap, development plan, and control truth all align; `deep` and `release` pass |
| 16 | `define-m13-m14-m15-post-m12-mainline` | completed | formalize post-M12 into `M13 / M14 / M15` and explain the practical meaning of `worker handoff and re-entry` | roadmap, README, development plan, strategic direction doc, and orchestration model all align; `deep` passes |
| 17 | `close-m13-and-m14-and-queue-m15-evidence` | current | turn `M13 / M14` into durable PTL supervision / worker handoff control surfaces, gates, progress, and handoff, then switch the mainline into post-M14 evidence collection | `deep` and `release` pass; control truth, README, roadmap, development plan, and snapshots all show `M13 / M14 done` and `M15 evidence-gated later` |

## Milestone Details

### M1

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | establish `.codex` control surface and tiering |
| Depends On | core skill routing |
| Exit Criteria | current state is recoverable |

### M2

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | establish convergent retrofit |
| Depends On | control-surface scripts |
| Exit Criteria | retrofit no longer stops midway |

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
| Goal | establish durable-doc standards and doc validation |
| Depends On | document standards + docs scripts |
| Exit Criteria | durable docs pass structural gates |

### M5

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | establish bilingual public-doc switching and validation |
| Depends On | i18n rules + i18n validator |
| Exit Criteria | public docs switch cleanly between English and Chinese |

### M6

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | shift to an embedded architect-assistant operating model |
| Depends On | previous milestones |
| Exit Criteria | planning, execution, architecture supervision, and devlog capture are default-on behaviors |

### M7

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | improve narrative quality and automated architecture triggers |
| Depends On | M6 |
| Exit Criteria | less manual cleanup after retrofit and fewer direction-correction prompts |

### M8

| Item | Current Value |
| --- | --- |
| Status | deferred |
| Goal | locale-aware internal control-surface output |
| Depends On | handoff + command templates + validation policy |
| Exit Criteria | this remains a bounded supporting backlog topic under M10 instead of a mainline milestone |

### M9

| Item | Current Value |
| --- | --- |
| Status | deferred |
| Goal | slim continue/resume snapshots without losing recoverability |
| Depends On | continue snapshot + handoff + validation policy |
| Exit Criteria | this remains a bounded supporting backlog topic under M10 instead of a mainline milestone |

### M10

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add a PTL-driven strategic-evaluation layer above execution and retrofit |
| Depends On | M7 + approved strategic direction |
| Exit Criteria | roadmap / governance / architecture adjustments become explicit strategy outputs backed by durable surfaces and review rules |

### M11

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add a PTL-driven program-orchestration layer across multiple slices or workers |
| Depends On | M10 + durable program board |
| Exit Criteria | the system can coordinate several related slices without constant human continuation prompts; the first stable form is a single-Codex orchestration truth, while multi-executor scheduling stays evidence-driven future scope |

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
| Exit Criteria | the PTL can inspect, continue, resequence, or escalate through periodic and event-driven checks instead of only appearing in chat |

### M14

| Item | Current Value |
| --- | --- |
| Status | done |
| Goal | add worker handoff and re-entry |
| Plain-Language Meaning | `when a worker stops, the project should not stop with it` |
| Depends On | M13 + durable handoff / supervision truth |
| Exit Criteria | after a checkpoint, timeout, failure, or handoff, remaining work still has a durable path forward through resume, reassignment, re-queueing, or escalation |

### M15

| Item | Current Value |
| --- | --- |
| Status | later |
| Goal | add selective multi-executor scheduling |
| Depends On | M14 + disjoint write scopes + conflict control |
| Exit Criteria | only work with clear write boundaries and safe merge paths enters multi-executor scheduling; tightly coupled work stays on one primary write line |

## Current Next Step

| Next Move | Why |
| --- | --- |
| Continue from `close-m13-and-m14-and-queue-m15-evidence` onward | `M13 / M14` are complete; the next work is to roll out PTL supervision + worker handoff on more repos and use real evidence to decide whether `M15` deserves to exist |

## Strategic Direction

| Topic | Scope | Current Position |
| --- | --- | --- |
| business-planning and program-orchestration layer | `project-assistant` has completed the PTL-centered `M10 / M11 / M12 / M13 / M14`; it is now in post-M14 evidence collection while `M15` remains an evidence-gated later layer and M8/M9 stay as supporting backlog under that line | active |

Direction:

- [Strategic Planning And Program Orchestration Direction](strategic-planning-and-program-orchestration.md)
