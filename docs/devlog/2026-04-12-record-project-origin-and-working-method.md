# Record Project Origin And Working Method

## Problem

`project-assistant` had already accumulated a large amount of behavior: planning, retrofit, architecture review, progress reporting, PTL supervision, worker handoff, and versioned control-surface upgrades. What was still missing was the durable statement of origin: the question that caused this whole skill to exist in the first place.

Without that origin, the repo could keep growing features while slowly losing the reason those features were added. The missing piece was not another control-surface layer. It was one stable maintainer-facing document that preserved the original prompt and explained why the workflow is structured as goal -> approach -> architecture -> roadmap -> test case -> development plan -> AI delivery.

## Thinking

The starting point was a practical observation: using Codex on real projects feels more stable when the team first agrees on the final goal, then the implementation approach, then writes architecture, roadmap, test cases, and a development plan, and only then lets the AI execute against that plan.

The user also made two important extensions:

- the same method should apply to subprojects and stage tasks, not only top-level projects
- this should be turned into a repeatable skill or tool, not remain a one-off conversation pattern

That is effectively the founding statement of `project-assistant`. The right durable response was therefore not “mention this in one more README sentence,” but “preserve the original prompt verbatim and turn it into a first-class maintainer reference.”

## Solution

I converted that origin into a durable reference document:

- `docs/reference/project-assistant/project-origin-and-working-method.zh-CN.md`
- `docs/reference/project-assistant/project-origin-and-working-method.md`

The document preserves the original Chinese prompt verbatim, explicitly labels it as the starting point of the project, and explains:

- the default working method derived from it
- why that method is close to current best practice for medium+ AI-driven delivery
- when the workflow can be lighter
- why it also applies to subprojects and stage tasks
- how the method now maps onto `project-assistant` surfaces such as roadmap, development plan, PTL supervision, progress, and handoff

I also linked that origin document from:

- `README`
- `docs/README`
- `docs/reference/project-assistant/README`
- `docs/devlog/README`

So the repo now exposes not only what the skill does, but also where its working model came from.

## Validation

- Added:
  - `docs/reference/project-assistant/project-origin-and-working-method.zh-CN.md`
  - `docs/reference/project-assistant/project-origin-and-working-method.md`
  - `docs/devlog/2026-04-12-record-project-origin-and-working-method.md`
- Updated:
  - `README.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/README.zh-CN.md`
  - `docs/reference/project-assistant/README.md`
  - `docs/reference/project-assistant/README.zh-CN.md`
  - `docs/devlog/README.md`
  - `docs/devlog/README.zh-CN.md`
- `python3 scripts/validate_gate_set.py . --profile deep`
