# Close M13 And M14 PTL Supervision And Worker Handoff

## Problem

`project-assistant` had already named `M13 PTL supervision loop` and `M14 worker handoff and re-entry` in the roadmap, but they were still mostly directional promises. The repo lacked durable PTL and handoff surfaces, the validation stack did not enforce them, and maintainer-facing outputs still treated them like future work instead of closed capability layers.

## Thinking

The real gap was not “more explanation.” The gap was execution truth. If PTL supervision and worker handoff only lived in README or roadmap prose, the repo would still depend on human babysitting whenever a worker stopped. The correct closeout meant: add durable control surfaces, add sync and validation paths, wire the state into `progress / continue / handoff`, then switch the mainline into post-M14 evidence collection rather than prematurely treating multi-executor scheduling as current capability.

While closing that gap, the sync scripts exposed a second issue: section replacement used regex replacement strings, so numbered table bodies could be misread as invalid group references. That bug would have made the new durable surfaces unstable even after the design was right.

## Solution

Added `.codex/ptl-supervision.md` and `.codex/worker-handoff.md`, plus `sync_ptl_supervision.py`, `validate_ptl_supervision.py`, `sync_worker_handoff.py`, and `validate_worker_handoff.py`. Wired both surfaces into `sync_control_surface.py`, `validate_gate_set.py`, `progress_snapshot.py`, `continue_snapshot.py`, and `context_handoff.py`. Closed `M13` and `M14` across `README`, `roadmap`, `development plan`, and the strategic / orchestration reference docs, then changed the live control truth to `PTL supervision and worker handoff layers closed; M15 evidence collection queued`.

Also fixed the sync-script section-refresh bug by switching the regex replacements to callable substitutions, which makes numbered bodies safe to rewrite. After that, refreshed `.codex/strategy.md`, `.codex/program-board.md`, `.codex/delivery-supervision.md`, `.codex/ptl-supervision.md`, and `.codex/worker-handoff.md` so every derived surface spoke the same post-M14 truth.

## Validation

- `python3 scripts/sync_strategy_surface.py .`
- `python3 scripts/sync_program_board.py .`
- `python3 scripts/sync_delivery_supervision.py .`
- `python3 scripts/sync_ptl_supervision.py .`
- `python3 scripts/sync_worker_handoff.py .`
- `python3 scripts/validate_ptl_supervision.py . --format text`
- `python3 scripts/validate_worker_handoff.py . --format text`
- `python3 scripts/validate_gate_set.py . --profile deep`
- `python3 scripts/validate_gate_set.py . --profile release`
- `python3 scripts/progress_snapshot.py .`
- `python3 scripts/continue_snapshot.py .`
- `python3 scripts/context_handoff.py .`
