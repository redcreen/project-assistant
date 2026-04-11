# Retrofit

Use this reference when the user wants to bring an existing repository into alignment with the delivery rhythm and governance system.

## Retrofit Modes

Choose one mode explicitly:

- `audit-only`: inspect the repo and produce a retrofit plan without edits
- `guided-retrofit`: inspect, propose, then apply the agreed structural changes
- `direct-retrofit`: inspect and apply the minimum safe structural changes immediately

When the user says "先不要动" or asks for a plan first, use `audit-only`.

## Retrofit Steps

### 1. Inventory the Current System

Inspect:

- root docs
- `docs/`
- `reports/`
- `test/`
- existing memory or status files
- active workstream notes

Capture:

- current status sources
- roadmap sources
- architecture sources
- testing sources
- generated evidence sources
- obvious duplication or drift

### 2. Classify Every Major Artifact

Assign each file or directory one role:

- `living`
- `durable`
- `generated`
- `archive`
- `unclear`

Any file with `unclear` ownership must be resolved before claiming the repo is aligned.

### 3. Define the Target Control Surface

For medium and large repos, the default target is:

```text
.codex/
  brief.md
  plan.md
  status.md
  subprojects/
docs/
reports/generated/
```

Allow existing paths to remain if they already fulfill these roles cleanly.

### 4. Plan the Delta

Describe:

- which files to create
- which files to merge
- which files to demote from active control to durable reference
- which files to move into generated or archive areas
- which links or references must be updated

Prefer moves and rewrites over deletion. Delete only when a file is clearly obsolete and fully superseded.

### 5. Apply in Safe Order

Use this sequence:

1. create `.codex` control files
2. populate them from the best current sources
3. update or add subproject status files if needed
4. reassign overlapping docs to one owner each
5. move generated evidence out of planning paths
6. update navigation in `README` or doc indexes

### 6. Verify Alignment

Confirm:

- the current project state is answerable from `status`
- the next execution order is answerable from `plan`
- the project goal and constraints are answerable from `brief`
- roadmap and architecture docs no longer act as session logs
- generated reports are not being used as the control surface

## Retrofit Heuristics

Use these heuristics during retrofit:

- if a file mixes ideas, status, and roadmap, split status out first
- if two files both answer "what is next", keep one and demote the other
- if reports contain durable strategy, promote that strategy into `docs/` and leave the report as evidence
- if the repo has good stable docs but no live control files, add `.codex` without restructuring everything else

## Retrofit Deliverable Template

Use this structure when reporting a retrofit audit:

```md
## Current State
- Tier:
- Main control source:
- Main duplication risk:

## Required Changes
1.
2.
3.

## File Role Reassignment
| Path | Current role | Target role | Action |
| --- | --- | --- | --- |

## Minimum Safe Sequence
1.
2.
3.
```
