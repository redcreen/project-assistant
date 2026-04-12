# Retrofit

Use this reference when the user wants to bring an existing repository into alignment with the delivery rhythm and governance system.

## Retrofit Modes

Choose one mode explicitly:

- `audit-only`: inspect the repo and produce a retrofit plan without edits
- `guided-retrofit`: inspect, propose, then apply the agreed structural changes
- `direct-retrofit`: inspect and apply the minimum safe structural changes immediately

When the user says "先不要动" or asks for a plan first, use `audit-only`.

Short Chinese commands:

- `项目助手 整改`
- `项目助手 文档整改`
- `项目助手 架构 整改`

Short English commands:

- `project assistant retrofit`
- `project assistant docs retrofit`
- `project assistant architecture retrofit`

## Core Rule

Retrofit is a convergence task.

That means each run should:

1. derive the current target structure from the latest skill rules and the repo tier
2. compare the repo against that target
3. apply or propose the remaining delta
4. stop only when the repo has reached the applicable target structure

Do not treat retrofit as "one helpful pass". Treat it as "bring the repo into compliance with the current model".

Unless the user explicitly narrows the scope, `整改` includes both:

- control-surface retrofit
- documentation-system retrofit
- full Markdown governance retrofit

That means README, docs landing, architecture, roadmap, test-plan, ADR layout, and document navigation are part of normal retrofit, not a separate optional pass.
It also means root Markdown clutter, `reports/` misuse, legacy single-file bilingual docs, and archive/reference separation must be resolved, not merely left in place beside the new stack.

If the user says `架构整改` / `architecture retrofit`, keep the same convergence expectation but switch the priority order:

1. architecture root cause and target boundaries
2. canonical architecture ownership and duplicate architecture-doc cleanup
3. affected modules, interfaces, tests, and release surfaces
4. only then the rest of the structure cleanup

Important default:

- `架构整改` is not plan-only by default
- it should continue from architecture diagnosis into actual repo changes and finish on the applicable gates
- stop after an audit note or retrofit checklist only when the user explicitly asks for `audit-only`, `先审计`, or `先不要改文件`

## Dirty Worktree Preflight

Before `整改`, `文档整改`, or `架构整改` starts applying changes:

1. check whether the repo is a git worktree
2. if it is dirty, tell the user briefly
3. ask whether to create a checkpoint commit first
4. do not auto-commit without approval
5. if the user wants to continue without committing, proceed and do not revert their changes

Keep this prompt short. It is a safety preflight, not a planning discussion.

If available, use:

- `scripts/sync_control_surface.py` to scaffold missing control-surface artifacts
- `scripts/validate_control_surface.py` to enforce completion gates
- `scripts/sync_docs_system.py` to scaffold or normalize durable docs
- `scripts/validate_docs_system.py` to enforce documentation completion gates
- `scripts/sync_markdown_governance.py` to converge the full Markdown tree
- `scripts/validate_markdown_governance.py` to enforce full-tree Markdown ownership gates
- `scripts/validate_doc_quality.py` to enforce that public docs are no longer scaffold-like or broken
- `scripts/validate_gate_set.py` to run the layered `fast` / `deep` gate sets
- `scripts/validate_control_surface_quality.py` to stop `.codex/*` from passing in template state
- `scripts/write_development_log.py` to record durable debugging or retrofit conclusions
- `scripts/validate_development_log.py` to enforce that the development-log index and entries stay usable
- `scripts/sync_architecture_retrofit.py` to generate a repo-local architecture-retrofit working note
- `scripts/validate_architecture_retrofit.py` to stop the architecture-retrofit note from staying in template state

## Mandatory Self-Check

After applying a retrofit, run a self-check against the target structure.

If any required item fails:

- report the remaining gap
- keep the retrofit in progress
- continue applying the minimum safe changes

Do not report retrofit as complete while a required target element is still missing, stale, or contradicted by another active document.

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
- documentation landing sources
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

Also classify each durable doc by question:

- landing
- architecture
- roadmap
- test-plan
- ADR
- how-to
- reference

Use `.codex/doc-governance.json` as the machine-readable contract for:

- which root docs are intentional
- which public-doc trees require bilingual switching
- which Markdown paths count as `living / durable / generated / archive`
- which docs are allowed to own architecture / roadmap / test-plan style questions

### 3. Define the Target Control Surface

For medium and large repos, the default target is:

```text
.codex/
  brief.md
  plan.md
  status.md
  doc-governance.json
  subprojects/
  module-dashboard.md
  modules/
docs/
reports/generated/
```

Allow existing paths to remain if they already fulfill these roles cleanly.

Define completion against this target structure. If required elements are still missing after a retrofit run, the retrofit is incomplete.

### 4. Plan the Delta

Describe:

- which files to create
- which files to merge
- which files to demote from active control to durable reference
- which files to move into generated or archive areas
- which links or references must be updated
- which doc pages need section-order normalization, table upgrades, or Mermaid diagrams

Prefer moves and rewrites over deletion. Delete only when a file is clearly obsolete and fully superseded.

### 5. Apply in Safe Order

Use this sequence:

1. create `.codex` control files
2. populate them from the best current sources
3. for large repos, add the module layer from roadmap and architecture docs
4. update or add subproject status files if needed
5. run doc-system sync to create or normalize durable doc skeletons
6. run full Markdown governance sync to classify, move, split, or archive the rest of the Markdown tree
7. normalize durable docs to the standard document roles
8. update navigation in `README` and `docs/README`
9. move generated evidence out of planning paths
10. if durable reasoning appeared during retrofit, create or update a development-log entry

### 6. Verify Alignment

Confirm:

- the current project state is answerable from `status`
- the next execution order is answerable from `plan`
- the project goal and constraints are answerable from `brief`
- for large repos, module-level progress is answerable from `module-dashboard` and `modules/*.md`
- roadmap and architecture docs no longer act as session logs
- generated reports are not being used as the control surface
- README and docs landing route readers clearly
- architecture, roadmap, and test-plan each answer one primary question
- root Markdown clutter is reduced to intentional top-level entry docs
- durable strategy docs no longer live under `reports/`
- superseded or exploratory docs are moved to `docs/archive/`
- durable but secondary references are moved under `docs/reference/` or `docs/workstreams/`

If any required target element is still missing, do not report success. Report the remaining delta explicitly.

### 7. Check Tier Gates

Check the required gate set for the current tier.

#### `small`

- `brief` exists and is usable
- `status` exists and is usable
- no parallel file is still acting as the real active status source

#### `medium`

- `brief`, `plan`, and `status` exist and are usable
- verification surface exists when needed
- current work can be resumed from the control surface

#### `large`

- `brief`, `plan`, and `status` exist and are usable
- `module-dashboard` exists and is usable
- `modules/*.md` exists when first-class modules or subsystems exist
- when an explicit first-class module list exists, `modules/*.md` reflects that list or explicitly justifies any merge
- the global status is no longer retrofit-oriented when retrofit has already finished
- module-level progress is answerable from the control surface

If any gate fails, retrofit is incomplete.

Run the validation script when present instead of relying only on manual inspection.
For documentation retrofit, `validate_docs_system.py` is part of the gate set when present.
For full Markdown retrofit, `validate_markdown_governance.py` is also part of the gate set when present.
For public-doc quality, `validate_doc_quality.py` is part of the gate set when present.
For durable reasoning capture, `validate_development_log.py` is part of the gate set when present.

Use layered gates:

- `fast` during iterative work
- `deep` before declaring retrofit complete
- `deep` before release
- `release` when architecture-sensitive release paths or workflows changed

## Architecture Retrofit Rule

Use architecture retrofit when the repo is structurally aligned enough to work, but the direction is still wrong.

Typical triggers:

- repeated fixes keep reappearing in different places
- the correct layer is unclear, so hardcoded shortcuts keep accumulating
- multiple architecture docs compete as active owners
- module boundaries or state flow are drifting away from the intended architecture
- release or CI behavior still assumes an outdated architecture direction

Architecture retrofit should leave behind:

- `.codex/architecture-retrofit.md`
- one explicit target architecture direction
- one explicit list of affected boundaries
- one explicit execution strategy for the retrofit
- one explicit exit condition set

## Documentation Retrofit Rule

When the repo has stable public docs or maintainer docs, retrofit should normalize them to the standard document system in `document-standards.md`.

Default durable doc targets:

```text
README.md
docs/README.md
docs/architecture.md
docs/roadmap.md
docs/test-plan.md
docs/adr/
docs/reference/
docs/workstreams/
docs/archive/
reports/generated/
```

For skill repositories, allow this equivalent durable reference layer:

```text
SKILL.md
references/
docs/
```

In that case, `references/` acts as the durable reference pack and should be linked from `docs/README.md`.

Documentation retrofit should:

- preserve facts and conclusions
- improve section order
- improve navigation
- add tables where they reduce scanning cost
- add Mermaid only where it clarifies structure or flow
- when bilingual public docs are required, create English/Chinese file pairs with switch links and validate them
- bootstrap `.codex` first even when the user asks only for documentation retrofit
- migrate legacy deep trees such as `docs/<legacy-root>/architecture|roadmaps|testing|todo` into governed locations
- resolve the ownership of every Markdown file in the repo, not only the top-level stack
- leave no `unclear` Markdown file in root, `docs/`, or `reports/`
- when retrofit produces durable implementation reasoning, capture it under `docs/devlog/`

Do not rewrite project truth just to fit a prettier template.

## Retrofit Heuristics

Use these heuristics during retrofit:

- if a file mixes ideas, status, and roadmap, split status out first
- if two files both answer "what is next", keep one and demote the other
- if reports contain durable strategy, promote that strategy into `docs/` and leave the report as evidence
- if the repo has good stable docs but no live control files, add `.codex` without restructuring everything else
- if the repo is large and already has module roadmaps, create the module layer instead of forcing all progress into one global status file

## Idempotence Rule

Running retrofit multiple times should converge the repo toward one stable structure.

- preserve already-correct structure
- fill missing required pieces
- reconcile drift
- never require the user to invent a second "special retrofit" command just to finish a previously incomplete retrofit

## Large-Project Special Rule

For large repos, do not accept a halfway state such as:

- global control surface exists but module layer is missing
- module dashboard exists but module status files are missing
- a few broad subproject files exist but the official first-class modules still have no module files
- module files exist but do not answer capability, remaining steps, and next checkpoint
- status still describes the project as "doing retrofit" when execution should already have resumed

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
