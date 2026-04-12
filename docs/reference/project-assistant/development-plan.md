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
| Current Phase | `strategic evaluation layer foundation` | Current maintainer-facing phase from `.codex/plan.md` |
| Active Slice | `establish-strategy-surface-and-review-contract` | The slice tied to the current execution line |
| Current Execution Line | define the first durable strategic surface, make the strategic layer official in docs and control truth, and fold M8/M9 into supporting backlog instead of the mainline | What the repo is trying to finish now |
| Validation | strategy docs and control truth align; `.codex/strategy.md` exists; `deep` continues to pass | How this line proves itself before moving on |

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
| M10 | active | add a strategic-evaluation layer above execution and retrofit | M7 + approved strategic direction | roadmap / governance / architecture adjustments become durable, reviewable strategy outputs instead of ad hoc intuition |
| M11 | next | add a program-orchestration layer across multiple slices or workers | M10 + durable program board | the system can coordinate several related slices without constant human continuation prompts |
| M12 | later | add supervised long-run delivery | M11 + stable escalation policy | long-running delivery can continue until a real business decision point |

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
| 12 | `establish-strategy-surface-and-review-contract` | current | create the first durable strategy surface, define review boundaries, and record how M8/M9 move into supporting backlog | `.codex/strategy.md` exists; docs and control truth align; `deep` passes |

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
| Status | active |
| Goal | add a strategic-evaluation layer above execution and retrofit |
| Depends On | M7 + approved strategic direction |
| Exit Criteria | roadmap / governance / architecture adjustments become explicit strategy outputs backed by durable surfaces and review rules |

### M11

| Item | Current Value |
| --- | --- |
| Status | next |
| Goal | add a program-orchestration layer across multiple slices or workers |
| Depends On | M10 + durable program board |
| Exit Criteria | the system can coordinate several related slices without constant human continuation prompts |

### M12

| Item | Current Value |
| --- | --- |
| Status | later |
| Goal | add supervised long-run delivery |
| Depends On | M11 + stable escalation policy |
| Exit Criteria | long-running delivery can continue until a real business decision point |

## Current Next Step

| Next Move | Why |
| --- | --- |
| Continue from `establish-strategy-surface-and-review-contract` onward | the strategic layer is now the active mainline, so the next durable question is how to encode strategy judgment and review boundaries as first-class repo truth |

## Strategic Direction

| Topic | Scope | Current Position |
| --- | --- | --- |
| business-planning and program-orchestration layer | `project-assistant` now treats this as the approved mainline direction. Strategic evaluation is active, M8/M9 are folded into supporting backlog, and M11/M12 stay queued behind durable strategy surfaces and review rules | active |

Direction:

- [Strategic Planning And Program Orchestration Direction](strategic-planning-and-program-orchestration.md)
