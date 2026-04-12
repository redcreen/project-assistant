# Encode architecture supervision and escalation into the control surface

- Date: 2026-04-12
- Status: resolved

## Problem

Architecture supervision had become a rule and menu concept, but not a machine-readable part of the operating surface. That meant long execution could still lose the higher-level judgment about root cause, correct layer, and when to stop for user decision.

## Thinking

To make the assistant behave like an embedded architect rather than a command-heavy reviewer, the architecture judgment had to sit next to the execution line instead of living only in prose. The same control surface that tracks the current long run also needs to track whether the assistant should continue automatically, raise but continue, or stop for a user decision.

## Solution

Extended the control-surface templates with Architecture Supervision and escalation sections, required them in validators, and surfaced the signal and gate in progress and handoff output. Also updated the rules and templates so this becomes the default shape for medium and large work.

## Validation

validate_gate_set.py --profile deep passes for the skill repo after the control-surface, reporting, and docs updates.

## Follow-Ups

- none

## Related Files

- scripts/sync_control_surface.py
- scripts/control_surface_lib.py
- scripts/progress_snapshot.py
- scripts/context_handoff.py
