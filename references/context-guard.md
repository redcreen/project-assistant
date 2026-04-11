# Context Guard

Use this reference when the user wants to:

- compress context
- prepare a new thread
- hand off active work
- get copy-paste restore commands

## Goal

Make long sessions resumable without keeping unnecessary context alive.

## Hard Constraint

Do not claim exact context-percentage visibility unless the runtime exposes it.

That means:

- you may target `60%` as a soft threshold
- you may not claim that `58%`, `61%`, or similar values are known precisely without a meter

## Expected Behavior

When context drift is becoming likely:

1. suggest compression in one short line
2. generate a compact handoff
3. include copy-paste restore commands
4. keep the handoff focused on current phase, active slice, main risk, and next actions

## Preferred Output

Use `scripts/context_handoff.py` when present.

Expected sections:

- `Summary`
- `Restore Order`
- `Copy-Paste Commands`
- `Next 3 Actions`

## Command Aliases

- `项目助手 压缩上下文`
- `项目助手 生成恢复包`
- `项目助手 给我新对话恢复指令`
- `项目助手 交接`

## Copy-Paste Command Requirements

Always include:

- one resume command
- one progress command
- one continue-and-validate command

The commands should be short enough for the user to paste directly into a new thread.
