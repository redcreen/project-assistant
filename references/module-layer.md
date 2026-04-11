# Module Layer

Use this reference for `large` projects that already define first-class modules, subsystems, adapters, or workstreams.

## Goal

Add a second control layer so the project can be understood from both:

- the global project view
- the module or subsystem view

Without this layer, large-project progress reports stay too vague.

## Required Files

Default targets:

```text
.codex/
  module-dashboard.md
  modules/
    <module>.md
```

Create one module file per active or strategically important module. Do not create dozens of stale files for inactive areas.

If the repo already provides an official first-class module list, use that list as the default source of module files.

## When to Create the Module Layer

Create it when any of these are true:

- the project roadmap lists first-class modules
- architecture docs are already split by module
- the user asks for module-level progress or completion
- the project has multiple active workstreams with different states

## Module Status File Requirements

Each module file must answer:

- ownership boundary
- current status
- already implemented capability
- remaining steps
- current completion signal
- next checkpoint

Preferred status values:

- `not-started`
- `planned`
- `baseline-complete`
- `active`
- `governing`
- `complete`

## Module Dashboard Requirements

The dashboard should include:

- one short summary of the whole system
- a table of key modules
- module status
- already implemented capability
- current next track
- approximate completion signal when the repo already supports that claim

If completion cannot be stated honestly as a percent, use stage wording instead:

- `baseline complete`
- `enhancement phase`
- `governing and tuning`
- `planned next`

## Source Priority

Build the module layer from:

1. module roadmaps
2. module architecture docs
3. development plan
4. current code and tests
5. global roadmap

Do not invent module status from naming alone.

Do not let a small set of broad `subprojects/*.md` files stand in for the module layer when the repo already defines more specific first-class modules.
