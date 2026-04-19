# Restore accurate devlog capture and the devlog front door

- Date: 2026-04-19
- Status: resolved

## Problem

Project Assistant claimed that devlog capture updated automatically, but the canonical front door had no devlog mode and status refresh kept writing Pending Capture: no even after multiple durable commits landed after April 14.

## Thinking

The failure was structural rather than editorial: devlog capture state existed only as prose and one-off writer logic, so continue/progress/handoff could not refresh it and validators could not detect drift. The fix had to centralize live capture detection around the latest devlog baseline, expose a real devlog backend on the unified front door, and let normal entry flows refresh status before people read it.

## Solution

Added live development-log capture detection in control_surface_lib.py, a dedicated sync_development_log_state.py refresher, a real devlog_entry.py backend routed through project_assistant_entry.py, and hooked sync_plan_docs.py, sync_execution_line.py, write_development_log.py, and release/control-surface validation onto the same source of truth.

## Validation

Validated with python3 -m py_compile for the touched scripts, python3 scripts/devlog_entry.py . to confirm Pending Capture turned visible, python3 scripts/project_assistant_entry.py devlog . to exercise the front door, and python3 scripts/validate_control_surface.py . --format text before and after writing the entry.

## Follow-Ups

- Backfill the missing devlog entries in other managed repos and refresh their status files with the new live capture logic.

## Related Files

- scripts/control_surface_lib.py
- scripts/project_assistant_entry.py
- scripts/devlog_entry.py
- scripts/sync_development_log_state.py
- scripts/sync_plan_docs.py
- scripts/sync_execution_line.py
- scripts/write_development_log.py
- scripts/validate_release_readiness.py
