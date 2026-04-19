# Governance

Use this reference to keep project control surfaces consistent.

## Tier Decision Table

Start with Codex's first-pass classification, then let the user override if needed.

| Tier | Typical shape | Required artifacts | Optional artifacts |
| --- | --- | --- | --- |
| `small` | one task, one session, low cross-cutting risk | `brief`, inline acceptance checks, `status` | `plan` |
| `medium` | one feature or subproject across multiple sessions | `brief`, `plan`, `status`, `test-plan` | `docs/README`, `architecture`, `adr`, `how-to`, `reference` |
| `large` | multi-milestone, multi-system, or architecture-heavy work | `brief`, `plan`, `status`, `roadmap`, `test-plan`, `architecture` | `docs/README`, `module-dashboard`, `modules/*.md`, `adr`, `migration-plan`, `release-plan`, `ownership-map`, `deployment-topology`, `how-to`, `reference` |

## Sizing Heuristics

Score the work informally across these signals:

- scope breadth
- number of affected modules
- interface or data-contract change
- migration or rollback risk
- expected duration
- number of milestones
- number of consumers or runtimes
- test complexity

Interpretation:

- mostly one-module and one-session -> usually `small`
- multiple slices with explicit dependencies -> usually `medium`
- architecture, rollout, or multi-consumer coordination -> usually `large`

When uncertain between two tiers, start with the heavier one only if the extra artifacts reduce real execution risk. Otherwise start lighter and escalate when the risk becomes concrete.

## Document Roles

When generating durable docs, follow [document-standards.md](document-standards.md).
When the repo requires bilingual public docs, treat English/Chinese file pairs and language switch links as part of the durable-doc gate set, including user-facing landing or install `README` pages under top-level module or skill folders.

### brief

Must answer:

- what outcome is desired
- what is in scope and out of scope
- what constraints or assumptions apply
- what definition of done closes the work

### plan

Must answer:

- what slices exist
- what order they should happen in
- what dependencies or risks matter
- what validation closes each slice
- what the current execution line is: the next meaningful autonomous run the assistant should complete before returning
- which slice the execution line belongs to via `Plan Link`
- what visible execution task board sits under that line, including checkbox tasks and a clear done/total count
- what the current architecture-supervision judgment is
- what escalation model decides whether the assistant continues automatically, raises but continues, or stops for user judgment

### status

Must answer:

- current phase
- active slice
- current execution line
- current architecture-supervision signal
- current escalation gate
- done
- in progress
- blockers or open decisions
- next 3 actions

### module-dashboard

Must answer:

- which modules or subsystems matter now
- what state each module is in
- what each module already has
- what each module needs next

### module status

Must answer:

- what that module owns
- current status
- already implemented capability
- remaining steps
- next checkpoint

### architecture

Must answer:

- what the stable system shape is
- where the boundaries are
- which tradeoffs were chosen

### roadmap

Must answer:

- which milestone comes next
- what each milestone unlocks
- what exit criteria close each milestone

### docs/README

Must answer:

- where to start
- where to go for setup, architecture, how-to, reference, roadmap, and testing
- how the docs are grouped

### test-plan / case-matrix

Must answer:

- how success is verified
- what cases are covered
- what still requires manual checks

## Artifact Lifecycle

Create:

- create a document only when it answers a distinct operational question

Promote:

- promote a short-lived insight into durable docs only when it remains true beyond the current slice

Demote:

- demote stale plans, speculative notes, or finished run logs out of the control surface

Archive:

- archive obsolete reports or superseded plans so the active surface stays small

## Autonomous Execution Rule

Project Assistant should not require the user to repeatedly type "continue" for normal execution.

Default behavior:

- once the goal, constraints, and active slice are clear, run a meaningful execution line
- prefer a checkpoint-sized autonomous run, often around 20-30 minutes of real work when the task supports it
- make the execution line visible as a task board, not just a sentence
- let the task board grow to the detail needed for the checkpoint, including 5-20+ subtasks when that improves clarity
- keep that task board mapped to the active slice instead of drifting into unrelated maintenance
- keep a compact architecture-supervision state beside the task board so execution does not lose the higher-level direction
- prefer a computed architecture signal and escalation state over stale prose when scripts are available
- stop only at a meaningful checkpoint, blocker, failed validation that needs direction, or user-decision gate

## Escalation Model Rule

Use three gates:

- `continue automatically`: safe to keep executing inside the agreed direction
- `raise but continue`: record the risk or drift, but keep converging unless the risk changes the business direction
- `require user decision`: stop and ask the user because product behavior, compatibility, UX, performance, or cost tradeoffs would change the intended direction

Use manual commands as override windows, not as the primary control surface for ordinary progress.

Prefer the four primary human windows:

- `项目助手 菜单` / `project assistant menu`
- `项目助手 进展` / `project assistant progress`
- `项目助手 架构` / `project assistant architecture`
- `项目助手 开发日志` / `project assistant devlog`

## Architecture Supervision Rule

Architecture supervision should begin with a high-level package, not a full implementation dump.

Start from:

- goal
- constraints
- root-cause hypothesis
- affected boundaries
- proposed layer of change

Only pull detailed code, diffs, or call chains when the high-level review needs evidence.

## Retrofit Completion Rule

For each tier, retrofit is complete only when the repo has reached the required control structure for that tier.

- `small`: `brief` and `status` exist and are usable
- `medium`: `brief`, `plan`, `status`, and the needed verification surface exist and are usable
- `large`: `brief`, `plan`, `status`, plus the module layer when module-level progress matters, are all present and usable

If the repo is still missing a required element, retrofit remains in progress.

Usable means the file is not merely present; it must answer its required operational question clearly enough to drive the next session.

## Session Resume Protocol

When resuming, read in this order:

1. `status`
2. `brief`
3. `plan`
4. `module-dashboard` and active module files for large projects
5. any directly relevant durable doc for the active slice
6. code and recent diffs

Do not start from architecture or historical reports unless the active slice depends on them.
