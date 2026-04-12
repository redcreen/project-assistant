# Templates

Use the smallest template that still keeps the work controllable.

## Tier Header

Add this header at the top of `brief` or `status` when the project may span multiple sessions.

```md
## Delivery Tier
- Tier:
- Why this tier:
- Last reviewed:
```

## Small Task Template

Use for one focused task or a short coding session.

```md
# Task Brief

## Delivery Tier

## Goal

## Constraints

## Definition of Done

## Acceptance Checks

## Next 3 Actions
```

## Medium Feature Template

Use for one feature, subproject, or multi-session milestone.

```md
# Brief

## Delivery Tier

## Outcome

## Scope

## Non-Goals

## Constraints

## Definition of Done
```

```md
# Plan

## Current Phase

## Current Execution Line
- Objective:
- Plan Link:
- Runway:
- Progress:
- Stop Conditions:
- Validation:

## Execution Tasks
- [ ] EL-1
- [ ] EL-2
- [ ] EL-3

## Architecture Supervision
- Signal:
- Problem Class:
- Root Cause Hypothesis:
- Correct Layer:
- Rejected Shortcut:
- Escalation Gate:

## Escalation Model
- Continue Automatically:
- Raise But Continue:
- Require User Decision:

## Slices
- Slice:
  - Objective:
  - Dependencies:
  - Risks:
  - Validation:
  - Exit Condition:
```

```md
# Test Plan

## Acceptance Cases
- Case:
  - Setup:
  - Action:
  - Expected Result:

## Manual Checks

## Automated Coverage
```

```md
# Status

## Delivery Tier

## Current Phase

## Active Slice

## Current Execution Line
- Objective:
- Plan Link:
- Runway:
- Progress:
- Stop Conditions:

## Execution Tasks
- [ ] EL-1
- [ ] EL-2
- [ ] EL-3

## Architecture Supervision
- Signal:
- Root Cause Hypothesis:
- Correct Layer:
- Escalation Gate:

## Current Escalation State
- Current Gate:
- Reason:

## Done

## In Progress

## Blockers / Open Decisions

## Next 3 Actions
```

## Execution Line Notes

- Treat `Current Execution Line` as the one checkpoint-sized long run the assistant should finish before returning.
- Treat `Execution Tasks` as the visible task board for that run.
- Always map the task board back to one slice through `Plan Link`.
- The board does not need a hard cap; use as many tasks as the checkpoint needs, often anywhere from 5 to 20+ tasks.
- Keep an `Architecture Supervision` block beside the task board so the current root-cause hypothesis and correct layer stay visible.
- Keep an escalation section so the repo records whether the assistant should continue automatically, raise but continue, or require user decision.

## Architecture Retrofit Template

Use for `.codex/architecture-retrofit.md` when the repo needs an architecture-first retrofit rather than another local patch round.

```md
# Architecture Retrofit

## Trigger

## Primary Symptoms

## Root-Cause Drivers

## Affected Boundaries

## Current Architecture Sources

## Target Architecture

## Retrofit Scope

## Execution Strategy

## Validation

## Exit Conditions
```

## Module Dashboard Template

Use for `large` projects with first-class modules or subsystems.

```md
# Module Dashboard

## Summary
- Overall:
- Current Phase:
- Active Module:
- Main Risk:

## Modules
| Module | Status | Already Implemented | Remaining Steps | Completion Signal | Next Checkpoint |
| --- | --- | --- | --- | --- | --- |
```

## Module Status Template

Use for one large-project module or subsystem.

```md
# Module Status

## Ownership

## Current Status

## Already Implemented

## Remaining Steps
1.
2.
3.

## Completion Signal

## Next Checkpoint
```

## Subproject Status Template

Use only for active or blocked subprojects.

```md
# Subproject Status

## Parent Phase / Milestone

## Goal

## Current Slice

## Done

## In Progress

## Blockers / Open Decisions

## Exit Condition

## Next 3 Actions
```

## Large Project Template

Use for multi-milestone or architecture-heavy work.

```md
# README

[English](README.md) | [中文](README.zh-CN.md)

> One-line value proposition.

## Who This Is For

## Quick Start

## Core Capabilities

## Common Workflows

## Documentation Map
- [Docs Home](docs/README.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Test Plan](docs/test-plan.md)

## Development

## License
```

```md
# Docs Home

[English](README.md) | [中文](README.zh-CN.md)

## Start Here
- Getting started:
- Architecture:
- How-to:
- Reference:
- Roadmap:
- Testing:

## By Goal
| Goal | Read This |
| --- | --- |
| Try the project quickly | |
| Understand the system | |
| Perform a task | |
| Look up exact contracts | |
| See what is next | |
```

## Development Log Template

Use for durable debugging narratives, retrofit discoveries, or implementation decisions that future maintainers should understand.

```md
# Title

- Date:
- Status:

## Problem

## Thinking

## Solution

## Validation

## Follow-Ups

## Related Files
```

```md
# Architecture

[English](architecture.md) | [中文](architecture.zh-CN.md)

## Purpose and Scope

## System Context

```mermaid
flowchart TB
```

## Module Inventory

| Module | Responsibility | Key Interfaces |
| --- | --- | --- |

## Core Flow

```mermaid
flowchart LR
```

## Interfaces and Contracts

## State and Data Model

## Operational Concerns

## Tradeoffs and Non-Goals

## Related ADRs
```

```md
# Roadmap

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## Scope

## Now / Next / Later
| Horizon | Focus | Exit Signal |
| --- | --- | --- |
| Now | | |
| Next | | |
| Later | | |

## Milestones
| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |

## Milestone Flow

```mermaid
flowchart LR
```

## Risks and Dependencies
```

```md
# Test Plan

[English](test-plan.md) | [中文](test-plan.zh-CN.md)

## Scope and Risk

## Acceptance Cases
| Case | Setup | Action | Expected Result |
| --- | --- | --- | --- |

## Automation Coverage

## Manual Checks

## Test Data and Fixtures

## Release Gate
```

```md
# ADR 0001: Title

[English](0001-title.md) | [中文](0001-title.zh-CN.md)

## Status

## Context

## Decision

## Consequences

## Alternatives Considered
```

Keep `brief` and `status` even for large projects. Do not replace them with only roadmap or architecture documents.

## Phase Exit Checklist

Use before moving to the next phase.

```md
- Goal still matches user direction
- Constraints are current
- Current slice is verified
- Status is updated
- Next 3 actions are explicit
- Open risks are visible
```

## Progress Dashboard Template

Use when the user asks for project progress on a medium or large project.

```md
# Progress Dashboard

## Summary
- Overall:
- Current Phase:
- Active Slice:
- Main Risk:

## Global View
| Area | Status | Current Focus | Exit Condition |
| --- | --- | --- | --- |

## Module View
| Module | Status | Already Implemented | Remaining Steps | Completion Signal | Next Checkpoint |
| --- | --- | --- | --- | --- | --- |

## Module Flow
```mermaid
flowchart TB
```

## Subprojects
| Subproject | Status | Current Focus | Next Checkpoint |
| --- | --- | --- | --- |

## Evidence
- Tests:
- Evals / Reports:

## Next 3 Actions
1.
2.
3.
```

## Context Handoff Template

Use when the session is long and the user needs a new-thread restore pack.

```md
# Context Handoff

## Summary
- Repo:
- Tier:
- Current Phase:
- Active Slice:
- Active Module:
- Main Risk:

## Restore Order
1. `.codex/status.md`
2. `.codex/plan.md`
3. `.codex/module-dashboard.md`

## Copy-Paste Commands
```text
项目助手 继续。先读取 .codex/status.md、.codex/plan.md；然后继续执行当前切片：...
项目助手 告诉我这个项目当前进展，用全局视角、模块视角和图示输出。
项目助手 继续当前切片，并先运行验证：...
```

```text
project assistant continue. Read .codex/status.md and .codex/plan.md first; then continue the active slice: ...
project assistant progress
project assistant continue the active slice and run validation first: ...
```

## Next 3 Actions
1.
2.
3.
```

## Continue Snapshot Template

Use when the user says `项目助手 继续` / `project assistant continue`.

```md
# Continue Snapshot

## Continue Now
- Current Phase:
- Active Slice:
- Long Task:
- Execution Progress:
- Architecture Signal:
- Main Risk:
- Full Dashboard: use `项目助手 进展` / `project assistant progress`

## Next Work
1.
2.
3.

## Task Board
- [ ] EL-1 ...
- [ ] EL-2 ...

## Stored Next 3 Actions
1.
2.
3.
```

## Retrofit Audit Template

Use when aligning an existing repository to this operating model.

```md
# Retrofit Audit

## Current State
- Tier:
- Main Control Source:
- Main Duplication Risk:

## Required Changes
1.
2.
3.

## File Role Reassignment
| Path | Current Role | Target Role | Action |
| --- | --- | --- | --- |

## Minimum Safe Sequence
1.
2.
3.
```

## Retrofit Completion Checklist Template

Use internally when verifying that retrofit has actually converged.

```md
# Retrofit Completion Checklist

## Tier
- Tier:

## Required Gates
- [ ] brief is usable
- [ ] status is usable
- [ ] plan is usable when required
- [ ] verification surface exists when required
- [ ] module-dashboard exists when required
- [ ] module status files exist when required
- [ ] no conflicting active status source remains
- [ ] current state is recoverable from the control surface

## Remaining Delta
- None / list remaining gaps
```

## Phase Closeout Template

Use when a slice or phase completes.

```md
# Phase Closeout

## Completed

## Deferred

## Evidence of Closure

## What This Unlocks Next

## New Risks In Next Phase

## Next Entry Criteria
```

## Commands Cheat Sheet Template

Use for `.codex/COMMANDS.md` when the repo needs a human-facing quick reminder.

```md
# Commands

## Primary Windows | 中文主窗口

- `项目助手 菜单`
- `项目助手 进展`
- `项目助手 架构`
- `项目助手 开发日志`

## Primary Windows | English

- `project assistant menu`
- `project assistant progress`
- `project assistant architecture`
- `project assistant devlog`

## Background Flows | 后台主流程

- `项目助手 启动这个项目` / `project assistant start this project`
- `项目助手 规划下一阶段` / `project assistant plan the next phase`
- `项目助手 继续` / `project assistant continue`
- `项目助手 架构 整改` / `project assistant architecture retrofit`
- `项目助手 整改这个仓库` / `project assistant retrofit this repo`
- `项目助手 收口当前阶段` / `project assistant close out the current phase`

## Notes

- Human users should usually need only the four primary windows above.
- The other flows should mostly run in the background unless the user explicitly overrides them.
- Use the language that matches the user.
- Natural-language variations are fine as long as intent stays clear.
```
