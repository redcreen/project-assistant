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
| Current Phase | `locale-aware internal control-surface output` | Current maintainer-facing phase from `.codex/plan.md` |
| Active Slice | `evaluate-locale-aware-internal-output` | The slice tied to the current execution line |
| Current Execution Line | 评估哪些内部控制面输出应该按用户语言做单通道展示，减少中文工作流里的冗余英文，同时不削弱公开文档双语和 AI 恢复精度 | What the repo is trying to finish now |
| Validation | representative Chinese-first repo snapshots are shorter without losing restore anchors; public-doc bilingual gates remain intact; `deep` continues to pass | How this line proves itself before moving on |

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
| M8 | active | evaluate locale-aware internal control-surface output | handoff + command templates + validation policy | Chinese-only workflows can suppress redundant English without weakening public-doc bilingual support |
| M9 | later | slim continue/resume snapshots without losing recoverability | continue snapshot + handoff + validation policy | `project assistant continue` carries only minimal restore state and does not duplicate progress content |
| M10 | proposed | add a strategic-evaluation layer above execution and retrofit | M8 + M9 + durable strategy proposal | roadmap / governance / architecture adjustments become explicit proposals instead of ad hoc intuition |
| M11 | proposed | add a program-orchestration layer across multiple slices or workers | M10 + durable program board | the system can coordinate several related slices without constant human continuation prompts |
| M12 | proposed | add supervised long-run delivery | M11 + stable escalation policy | long-running delivery can continue until a real business decision point |

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
| 11 | `evaluate-locale-aware-internal-output` | current | decide which internal surfaces should become locale-aware without splitting public truth from AI truth | Chinese-first internal surfaces get shorter while public-doc bilingual gates stay stable |

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
| Status | active |
| Goal | evaluate locale-aware internal control-surface output |
| Depends On | handoff + command templates + validation policy |
| Exit Criteria | Chinese-only workflows can suppress redundant English without weakening public-doc bilingual support |

### M9

| Item | Current Value |
| --- | --- |
| Status | later |
| Goal | slim continue/resume snapshots without losing recoverability |
| Depends On | continue snapshot + handoff + validation policy |
| Exit Criteria | `project assistant continue` carries only minimal restore state and does not duplicate progress content |

### M10

| Item | Current Value |
| --- | --- |
| Status | proposed |
| Goal | add a strategic-evaluation layer above execution and retrofit |
| Depends On | M8 + M9 + durable strategy proposal |
| Exit Criteria | roadmap / governance / architecture adjustments become explicit proposals instead of ad hoc intuition |

### M11

| Item | Current Value |
| --- | --- |
| Status | proposed |
| Goal | add a program-orchestration layer across multiple slices or workers |
| Depends On | M10 + durable program board |
| Exit Criteria | the system can coordinate several related slices without constant human continuation prompts |

### M12

| Item | Current Value |
| --- | --- |
| Status | proposed |
| Goal | add supervised long-run delivery |
| Depends On | M11 + stable escalation policy |
| Exit Criteria | long-running delivery can continue until a real business decision point |

## Current Next Step

| Next Move | Why |
| --- | --- |
| Continue from `evaluate-locale-aware-internal-output` onward | M7 is closed; the next durable question is where locale-aware internal output should begin and where it must stop |

## Strategic Backlog

| Topic | Scope | Entry Condition |
| --- | --- | --- |
| business-planning and program-orchestration layer | evaluate whether `project-assistant` needs a higher-level planner / supervising role that can steer multiple Codex workstreams, decide when governance or architecture side-tracks should be inserted, detect when earlier milestones or project positioning should change, and keep humans focused on business direction while still escalating requirement changes back for review | revisit after M8 and M9 close; discuss first, review the proposal, then promote it into a formal milestone or active slice if it survives scrutiny |

Proposal:

- [Strategic Planning And Program Orchestration Proposal](strategic-planning-and-program-orchestration-proposal.md)
