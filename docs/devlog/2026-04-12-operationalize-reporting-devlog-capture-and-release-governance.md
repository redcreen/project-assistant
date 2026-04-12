# Operationalize reporting, devlog capture, and release governance

- Date: 2026-04-12
- Status: resolved

## Problem

Even after execution lines and architecture supervision were in place, the assistant still had three practical gaps: users could not quickly tell what was already usable, development-log capture could still become noisy, and release readiness existed locally but not as a stricter CI path.

## Thinking

These were not separate feature requests. They all belonged to the same operating-surface problem: the assistant must make current capability, current reasoning burden, and current release readiness visible and enforceable. The clean solution was to treat them as one governance slice rather than a collection of unrelated tweaks.

## Solution

Added an execution-line generator for longer task boards, surfaced a usable-now capability snapshot in reporting, tightened development-log trigger strength to high with clearer skip rules, added release-readiness validation, and connected that stricter gate into CI via a dedicated workflow. Also updated the control surface and rules so these capabilities are part of the normal operating model.

## Validation

sync_execution_line.py generates a valid board from the next slice in a temp repo; capability_snapshot.py reports the usable set; validate_release_readiness.py passes for the skill repo; validate_gate_set.py --profile deep passes after the new slice is applied.

## Follow-Ups

- none

## Related Files

- /Users/redcreen/.codex/skills/project-assistant/scripts/sync_execution_line.py
- /Users/redcreen/.codex/skills/project-assistant/scripts/capability_snapshot.py
- /Users/redcreen/.codex/skills/project-assistant/scripts/validate_release_readiness.py
- /Users/redcreen/.codex/skills/project-assistant/.github/workflows/release-readiness.yml
