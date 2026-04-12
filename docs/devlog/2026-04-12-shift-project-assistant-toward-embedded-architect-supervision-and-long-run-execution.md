# Shift project assistant toward embedded architect supervision and long-run execution

- Date: 2026-04-12
- Status: resolved

## Problem

The skill still depended too much on explicit commands and short human-driven loops. That pushed the user to repeatedly type continue, while architecture review risked getting trapped inside local implementation details instead of challenging the direction from a higher level.

## Thinking

The desired role is not a command-heavy assistant but a default-on engineering system: the user provides business direction, and the assistant plans, supervises, implements, validates, and documents by default. To make architecture review useful, it must begin from a high-level package—goal, constraints, root-cause hypothesis, affected boundaries, and proposed layer—then pull code evidence only when needed. To make execution useful, the assistant should pursue a meaningful checkpoint-sized run instead of stopping after each micro-step.

## Solution

Updated the skill model so architecture supervision is treated as a built-in layer for medium and large work, while manual commands remain as override windows under 项目助手 架构 / project assistant architecture. Added the execution-line concept to planning and governance so normal execution targets one meaningful autonomous run, typically around 20-30 minutes when the task supports it. Also clarified that development logs should be captured automatically when durable reasoning appears, rather than relying on manual memory.

## Validation

Updated SKILL, governance, usage, README, and control-surface files to reflect the new model, then re-ran the deep validation gate on the skill repo.

## Follow-Ups

- Translate the new default-on interaction model into more explicit automated trigger rules inside execute and closeout behaviors.
- Evaluate later whether a separate architecture-quality gate is needed beyond the current process rules.

## Related Files

- /Users/redcreen/.codex/skills/project-assistant/SKILL.md
- /Users/redcreen/.codex/skills/project-assistant/references/governance.md
- /Users/redcreen/.codex/skills/project-assistant/references/usage.md
