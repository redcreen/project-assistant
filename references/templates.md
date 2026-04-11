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

## Done

## In Progress

## Blockers / Open Decisions

## Next 3 Actions
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
项目助手 恢复当前项目状态，然后继续执行当前切片：...
项目助手 告诉我这个项目当前进展，用全局视角、模块视角和图示输出。
项目助手 继续当前切片，并先运行验证：...
```

```text
project assistant resume current status and continue the active slice: ...
project assistant progress
project assistant continue the active slice and run validation first: ...
```

## Next 3 Actions
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

## Chinese

- `项目助手 菜单`
- `项目助手 启动这个项目`
- `项目助手 规划下一阶段`
- `项目助手 恢复当前状态`
- `项目助手 告诉我项目进展`
- `项目助手 先做整改审计`
- `项目助手 直接整改这个仓库`
- `项目助手 收口当前阶段`

## English

- `project assistant menu`
- `project assistant start this project`
- `project assistant plan the next phase`
- `project assistant resume current status`
- `project assistant progress`
- `project assistant retrofit audit`
- `project assistant retrofit this repo`
- `project assistant close out the current phase`

## Notes

- Use the language that matches the user.
- Natural-language variations are fine as long as intent stays clear.
```
