# Automate architecture signaling, release protection, and primary human windows

- Date: 2026-04-12
- Status: resolved

## Problem

Architecture supervision was still too static, release protection stopped at the tag edge, and the human command surface still exposed too many manual entry points.

## Thinking

We needed one shared architecture-signal source that progress, handoff, release gates, and control-surface sync could all consume. We also needed a stricter release profile that CI and the local release path would share, plus a smaller set of human-facing windows so the assistant can keep more flows in the background.

## Solution

Added shared architecture-signal inference, a sync_architecture_supervision script, a release gate profile and release-protection workflow, and rewrote command-facing docs around four primary windows with the rest treated as background flows.

## Validation

Updated the control surface, wired progress/handoff/release to the computed signal, added CI workflows, and reran deep validation successfully after the changes.

## Follow-Ups

- Apply the release profile to representative repos and tune it if it is too strict or too loose.
- Push architecture-signal refresh into more execute/retrofit entry points so fewer stale states survive between runs.

## Related Files

- scripts/control_surface_lib.py
- scripts/sync_architecture_supervision.py
- scripts/validate_gate_set.py
- .github/workflows/release-protection.yml
- .codex/status.md
