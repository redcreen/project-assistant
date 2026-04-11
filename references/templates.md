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
# Architecture

## Context

## Decision

## Alternatives Considered

## Consequences
```

```md
# Roadmap

## Milestones
- Milestone:
  - Goal:
  - Depends On:
  - Exit Criteria:
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
# 项目助手命令速查

推荐入口：
- 项目助手

常用命令：
- 项目助手 启动这个项目
- 项目助手 规划下一阶段
- 项目助手 恢复当前状态
- 项目助手 告诉我项目进展
- 项目助手 先做整改审计
- 项目助手 直接整改这个仓库
- 项目助手 收口当前阶段

提示：
- 不需要记精确命令，直接说自然语言也可以。
```
