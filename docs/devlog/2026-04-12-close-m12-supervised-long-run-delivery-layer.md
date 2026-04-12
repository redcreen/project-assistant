# Close M12 Supervised Long-Run Delivery Layer

## Problem

`project-assistant` had already closed strategic evaluation and program orchestration, but the repo still lacked a durable layer that said how long-running delivery should actually continue: what the checkpoint rhythm is, when the system may auto-continue, when it must raise-but-continue, and when it must stop for a real user decision.

## Thinking

If M12 stayed only in roadmap prose, the assistant would still depend on human babysitting even after M10 and M11 were done. The missing piece was not another planning note; it was a durable delivery-supervision surface that could sit beside `strategy.md`, `program-board.md`, `plan.md`, and `status.md`, then drive first-screen outputs and release gates.

## Solution

Added `.codex/delivery-supervision.md` as the durable M12 surface, plus `sync_delivery_supervision.py` and `validate_delivery_supervision.py`. Wired delivery supervision into `sync_control_surface.py`, `validate_gate_set.py`, `progress_snapshot.py`, `continue_snapshot.py`, and `context_handoff.py`, then closed M12 across `README`, `roadmap`, `development plan`, `strategy`, `program-board`, and control-truth files. The repo now treats rollout / friction collection as the post-M12 follow-through instead of guessing a new milestone early.

## Validation

- `python3 scripts/validate_delivery_supervision.py . --format text`
- `python3 scripts/validate_gate_set.py . --profile deep`
- `python3 scripts/validate_gate_set.py . --profile release`
- `python3 scripts/progress_snapshot.py .`
- `python3 scripts/continue_snapshot.py .`
- `python3 scripts/context_handoff.py .`
