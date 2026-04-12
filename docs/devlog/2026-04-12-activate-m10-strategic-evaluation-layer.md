# Activate M10 Strategic Evaluation Layer

## Problem

Promoted the strategic-planning layer from a deferred proposal into the official current direction for `project-assistant`.

## Thinking

The execution, retrofit, reporting, and documentation layers are already mature enough that the next meaningful gap is no longer a local workflow feature. The real missing layer is a durable strategic surface that can answer where the project should go next, when governance or architecture tracks should be inserted, and how roadmap changes should be proposed without drifting into business-direction overreach.

## Solution

| Area | Change |
| --- | --- |
| roadmap | M10 is now active; M11 is next; M12 remains later |
| carryover | M8 and M9 are now supporting backlog topics instead of the mainline |
| docs | the old strategic proposal has been upgraded into a formal strategic direction document |
| control truth | `.codex/status.md`, `.codex/plan.md`, and `.codex/strategy.md` now agree on the same current direction |
| README | the positioning section now states that strategic evaluation is the active next layer |

## Key Decision

The strategic layer is approved as direction, but it still does not get to auto-change business direction, compatibility promises, or external positioning. It can propose, prioritize, and frame the questions; humans still approve those higher-stakes changes.

## Validation

- `docs/roadmap(.zh-CN).md`, `docs/reference/project-assistant/development-plan(.zh-CN).md`, `README(.zh-CN).md`, `.codex/plan.md`, and `.codex/status.md` now point to the same current direction
- `.codex/strategy.md` exists as the first durable strategic surface
- `deep` validation passes after the direction switch

## Next

1. Expand `.codex/strategy.md` into a reusable strategic review template.
2. Define the evidence contract for strategic recommendations.
3. Design the future `program-board` surface without prematurely activating M11.
