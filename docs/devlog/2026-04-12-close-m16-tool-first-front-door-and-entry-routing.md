# Close M16 Tool-First Front Door And Entry Routing

## Problem

`project-assistant` had already accumulated the right backend scripts for `continue`, `progress`, `handoff`, control-surface version upgrades, and structured maintainer-facing panels. The real failure was at the entry layer: a natural-language `项目助手 继续` could still bypass preflight, read stale `.codex/status.md`, and emit free-form prose before any structured panel.

That created a bad user experience in exactly the place that should have been most reliable:

- legacy repos were not always upgraded before resume
- maintainers could still see drifting prose instead of one predictable first screen
- the repo could claim “hard entry” in docs without owning one canonical front door

## Why The Previous Fix Was Incomplete

The earlier fix improved the capability layer:

- versioned control-surface upgrades
- `sync_resume_readiness.py`
- `continue_entry.py`, `progress_entry.py`, `handoff_entry.py`

But it did not fully close the entry contract. If the real entry path could still bypass the canonical route, the system still depended on the model “remembering” to call the right backend first. That was not a stable contract.

## Thinking

The key design mistake was treating this as a wording problem. It was not. The snapshots could keep getting better while the real entry path still bypassed them. That meant the repo needed to stop thinking only in terms of “better scripts” and start treating entry routing as its own architectural surface.

The other important boundary was honesty: the repo can truthfully own a canonical front door and script backend, but it should not pretend the desktop host is already hard-bound. The solution had to improve what the repo can really test today, while leaving the host bridge as an explicit later boundary.

## Chosen Direction

The repo now treats entry routing as its own architectural layer:

- one canonical front door
- one version-preflight contract
- one structured first-screen contract
- one durable `entry-routing` control surface

The chosen shape is:

`tool-shaped front door + script backend`

This is deliberately narrower than claiming a desktop-host hard bind. The repo can own and validate:

- a canonical front door script
- a CLI wrapper
- shared backends
- shared preflight
- shared structured-output expectations

It should not claim host-level hard binding until the host or plugin bridge is real.

## Solution

The final shape was:

- keep script backends for maintainability and validation
- add one tool-shaped front door as the canonical entry
- add one durable `entry-routing` control surface
- update roadmap, development plan, architecture, README, usage, and control truth so they all describe the same boundary
- validate the new contract on real legacy repos by upgrading them first and only then rendering structured panels

## Implementation

The closeout work introduced:

- `scripts/project_assistant_entry.py`
- `bin/project-assistant`
- `scripts/sync_entry_routing.py`
- `scripts/validate_entry_routing.py`
- `.codex/entry-routing.md`

It also updated:

- architecture docs
- roadmap
- development plan
- README
- usage/help/templates/commands
- control-surface versioning

The `entry-routing` surface now records:

- current entry direction
- front-door layers
- preflight contract
- structured-output contract
- host / tool bridge boundary
- next rollout checks

## Validation

Validation focused on three questions:

1. Does the skill repo now own one canonical front door?
2. Can legacy repos be upgraded before resume/progress/handoff?
3. Do entry docs, control truth, and validators all describe the same thing?

The closeout criteria are:

- `deep` passes
- `release` passes
- legacy repos upgrade to the current control-surface version before rendering structured entry panels
- `entry-routing` is a durable validated surface, not only prose in a devlog

## Remaining Boundary

M16 closes the repo-owned part of the problem.

It does **not** mean the desktop host is already hard-bound to that front door. That remains a later bridge problem and should only be claimed when the host or plugin layer truly enforces it.
