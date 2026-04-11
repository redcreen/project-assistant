# Governance

Use this reference to keep project control surfaces consistent.

## Tier Decision Table

Start with Codex's first-pass classification, then let the user override if needed.

| Tier | Typical shape | Required artifacts | Optional artifacts |
| --- | --- | --- | --- |
| `small` | one task, one session, low cross-cutting risk | `brief`, inline acceptance checks, `status` | `plan` |
| `medium` | one feature or subproject across multiple sessions | `brief`, `plan`, `status`, `test-plan` | `architecture`, `adr` |
| `large` | multi-milestone, multi-system, or architecture-heavy work | `brief`, `plan`, `status`, `roadmap`, `test-plan`, `architecture` | `module-dashboard`, `modules/*.md`, `adr`, `migration-plan`, `release-plan`, `ownership-map`, `deployment-topology` |

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

### status

Must answer:

- current phase
- active slice
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
