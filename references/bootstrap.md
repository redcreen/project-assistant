# Bootstrap

Use this reference when starting a new project, a new major feature, or a new phase that needs its own execution surface.

## Bootstrap Goal

Create the smallest reliable control surface that lets Codex and the user:

- agree on the target
- know the current phase
- know the next execution slice
- resume later without reconstructing everything from scratch

## Default Bootstrap Sequence

1. classify the tier
2. write `brief`
3. write `status`
4. write `plan` if the work is `medium` or `large`
5. add `subprojects/` only if multiple active workstreams exist
6. for `large` projects with first-class modules, add `module-dashboard.md` and `modules/*.md`
7. create durable docs only when they answer a distinct question

## Bootstrap Questions

Capture these first:

- desired outcome
- scope
- non-goals
- constraints
- definition of done
- likely first slice

Ask the user only the missing high-risk questions. If the direction is clear enough, make safe assumptions and proceed.

## Bootstrap Output Targets

Default targets:

```text
.codex/
  brief.md
  status.md
  plan.md
  subprojects/
  module-dashboard.md
  modules/
```

Optional durable docs:

```text
docs/
  README.md
  architecture.md
  roadmap.md
  test-plan.md
  how-to/
  reference/
  adr/
```

When creating durable docs, use the standard shapes in [document-standards.md](document-standards.md) instead of inventing ad hoc section orders.
If the repo requires public bilingual docs, create switchable English/Chinese pairs for `README` and public `docs/*` pages at bootstrap time.

## Bootstrap Success Criteria

Bootstrap is complete when:

- the tier is explicit
- the goal and constraints are explicit
- the current phase is explicit
- the next 3 actions are explicit
- the module layer exists for large projects that need module-level clarity
- the next slice is implementable without re-planning from zero
