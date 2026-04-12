# Close M6 Embedded Architect-Assistant Milestone

- Date: 2026-04-12
- Status: resolved

## Problem

`project-assistant` had accumulated the mechanisms needed for an embedded architect-assistant model, but the milestone was still marked active.

That left an avoidable gap between reality and the published control truth:

- planning, execution, architecture supervision, and devlog capture were already default-on in practice
- representative retrofit flows had already been proven on real repositories
- roadmap, development-plan, status, and README still described the repo as if M6 were not yet closed

## Thinking

This was no longer a feature-implementation problem.

The real issue was milestone truth and phase transition:

- if M6 stayed open after the default-on operating model was already working, the roadmap would understate what had been achieved
- if the next source of friction was already “human-facing narrative quality and automatic escalation triggers,” then the control surface should say that explicitly
- closing M6 without opening a new active slice would be another stale-truth bug in a repo whose whole purpose is to prevent stale truth

So the right move was to treat this as a milestone-closeout slice:

1. confirm the M6 exit criteria are already satisfied
2. write down that proof in a durable devlog
3. flip roadmap, development plan, and control surface to `M6 done / M7 active`

## Solution

Close M6 and immediately promote the repo into the next active milestone.

The concrete changes were:

1. update `.codex/plan.md` and `.codex/status.md`
2. change roadmap milestone state from `M6 active / M7 next` to `M6 done / M7 active`
3. move the current active slice to a new M7 slice focused on:
   - maintainer-facing narrative quality
   - less AI-centric progress/continue/handoff wording
   - at least one automatic architecture-review trigger
4. refresh the durable development plan from the updated roadmap and control surface
5. add a short README statement that the embedded model is now the default operating mode

## Validation

- `python3 scripts/sync_docs_system.py .`
- `python3 scripts/capability_snapshot.py .`
- `python3 scripts/progress_snapshot.py .`
- `python3 scripts/context_handoff.py .`
- `python3 scripts/validate_gate_set.py . --profile deep`
- `python3 scripts/validate_gate_set.py . --profile release`

All passed after the phase transition and doc refresh.

## Follow-Ups

- Use M7 to reduce maintainer-facing narrative drift on representative repos.
- Add at least one automatic architecture-review trigger derived from real drift signals.
- Revisit release tagging after M7 friction drops enough on additional repos.

## Related Files

- .codex/plan.md
- .codex/status.md
- README.md
- README.zh-CN.md
- docs/roadmap.md
- docs/roadmap.zh-CN.md
- docs/reference/project-assistant/development-plan.md
- docs/reference/project-assistant/development-plan.zh-CN.md
