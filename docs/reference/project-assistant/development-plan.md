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
| Current Phase | `narrative quality and automated architecture triggers` | Current maintainer-facing phase from `.codex/plan.md` |
| Active Slice | `tighten-maintainer-facing-narrative-and-architecture-triggers` | The slice tied to the current execution line |
| Current Execution Line | 收紧 maintainer-facing narrative，减少 `progress / continue / handoff` 里的 AI-centric 表达，并把至少一条架构升级触发从“手工识别”变成自动信号 | What the repo is trying to finish now |
| Validation | representative medium + large repo snapshots 可读；`deep` / `release` 继续通过 | How this line proves itself before moving on |

## Milestone Overview

| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |
| M1 | done | establish `.codex` control surface and tiering | core skill routing | current state is recoverable |
| M2 | done | establish convergent retrofit | control-surface scripts | retrofit no longer stops midway |
| M3 | done | establish progress and handoff workflows | module layer + snapshot scripts | progress and handoff are stable |
| M4 | done | establish durable-doc standards and doc validation | document standards + docs scripts | durable docs pass structural gates |
| M5 | done | establish bilingual public-doc switching and validation | i18n rules + i18n validator | public docs switch cleanly between English and Chinese |
| M6 | done | shift to an embedded architect-assistant operating model | previous milestones | planning, execution, architecture supervision, and devlog capture are default-on behaviors |
| M7 | active | improve narrative quality and automated architecture triggers | M6 | less manual cleanup after retrofit and fewer direction-correction prompts |
| M8 | later | evaluate locale-aware internal control-surface output | handoff + command templates + validation policy | Chinese-only workflows can suppress redundant English without weakening public-doc bilingual support |
| M9 | later | slim continue/resume snapshots without losing recoverability | continue snapshot + handoff + validation policy | `project assistant continue` carries only minimal restore state and does not duplicate progress content |

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
| 10 | `tighten-maintainer-facing-narrative-and-architecture-triggers` | current | n/a | n/a |

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
| Status | active |
| Goal | improve narrative quality and automated architecture triggers |
| Depends On | M6 |
| Exit Criteria | less manual cleanup after retrofit and fewer direction-correction prompts |

### M8

| Item | Current Value |
| --- | --- |
| Status | later |
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

## Current Next Step

| Next Move | Why |
| --- | --- |
| Continue from `tighten-maintainer-facing-narrative-and-architecture-triggers` onward | The live execution line already fixes the real resume point in `.codex/plan.md` |
