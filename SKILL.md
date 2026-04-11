---
name: project-assistant
description: Scale Codex-led software delivery with right-sized planning, status tracking, and staged execution. Use when starting or rescuing a project, feature, subproject, or phase; when the user knows the direction but needs Codex to derive goals, constraints, architecture, roadmap, test cases, development plan, status, and next steps; or when ongoing work has become unclear and Codex must recover the current phase and continue. 适用于项目规划、架构讨论、roadmap、test case、development plan、阶段推进、状态恢复。
---

# AI Delivery Rhythm

Treat delivery as a control loop, not a one-time planning dump. Use the lightest artifact set that preserves alignment, recoverability, and testability.

## Route by Intent First

Before acting, classify the user's request into one primary mode:

- `bootstrap` (`启动`): start a new project or phase and create the initial control surface
- `plan` (`规划`): clarify goals, architecture, roadmap, tests, and execution slices
- `execute` (`执行`): implement the active slice and keep control docs current
- `resume` (`恢复`): recover current state and continue from the right slice
- `progress` (`进展`): report global and subproject progress clearly
- `retrofit` (`整改`): bring an existing repo into alignment with this system
- `closeout` (`收口`): close a slice or phase and prepare the next one

Pick one primary mode, then pull in the minimum supporting actions from the others.

When using English operation names in user-facing output, always pair them with a short Chinese explanation the first time they appear in a response. Prefer the Chinese alias in normal conversation unless the English term is needed for precision.

## Prefer One Simple Entry Alias

Recommend one Chinese entry alias for normal use:

- `项目助手`

Treat these requests as invoking this skill even if `$project-assistant` is not named explicitly:

- `项目助手`
- `项目操作系统`
- `项目治理`

If the user's wording clearly asks for project startup, planning, resume, progress, retrofit, or closeout, assume this skill should handle it.

## Support Help and Menu Queries

When the user asks:

- `项目助手 菜单`
- `项目助手 帮助`
- `项目助手 你能做什么`
- `项目助手 怎么用`

return a short command menu instead of a long explanation.

The menu should:

- list the simple Chinese commands first
- include the English term in parentheses only as a secondary cue
- include 1 short example per command group
- end with one reminder that the user can speak naturally without memorizing exact command names

## Decide the Delivery Tier Explicitly

Codex makes the first-pass classification. The user keeps veto power.

Use this rule:

- Codex assigns `small`, `medium`, or `large` at project start
- Codex states the reason for the tier in one short paragraph
- the user can override the tier explicitly
- if new complexity appears, Codex must reclassify and explain the change

Default ownership:

- Codex decides the initial tier because it can inspect scope, codebase shape, and risk
- the user decides when the business cost, timeline, or coordination model should force a heavier or lighter process

Escalate to at least `medium` when any of these are true:

- work spans multiple sessions
- work touches multiple modules or interfaces
- the task needs an explicit test plan
- the user asks for roadmap, architecture, or staged implementation
- the next step would be unclear without written status

Escalate to `large` when any of these are true:

- multiple milestones or workstreams must be coordinated
- architecture decisions affect several subsystems or runtimes
- migrations, deployment changes, or rollback strategy matter
- multiple adapters, consumers, or teams are involved
- long-running governance or phased rollout is required

Keep `small` only when the task is narrow, low-risk, and likely to finish in one short execution cycle.

## Bootstrap New Projects and New Phases

When starting a new repo, new major feature, or new phase:

1. classify the tier
2. capture the `brief`
3. create the minimum required control docs
4. decide whether architecture, roadmap, or test-plan are needed now
5. identify the first execution slice

Default bootstrap outputs:

- `.codex/brief.md`
- `.codex/status.md`
- `.codex/plan.md` for `medium` and `large`
- `.codex/subprojects/` only when multiple active workstreams already exist

Use [references/bootstrap.md](references/bootstrap.md) and [references/templates.md](references/templates.md) when creating the initial project control surface.

## Classify the Work First

Choose one lane before producing documents:

- `small`: one focused task or one short coding session. Keep planning inline unless the change is risky.
- `medium`: one feature, subproject, or multi-session milestone. Keep brief, plan, tests, and status as living artifacts.
- `large`: multi-feature, cross-cutting, or architecture-heavy work. Add roadmap and architecture decisions.

Do not force the same paperwork on every task. Expand only when complexity, risk, or duration justifies it.

## Use This Phase Loop

Move through these phases in order, but keep them brief when the work is small.

### 1. Frame the Work

Capture:

- desired outcome
- scope and non-goals
- constraints and assumptions
- definition of done
- important deadlines or sequencing constraints

Ask only the missing high-risk questions. If a reasonable assumption is safe, make it explicit and continue.

### 2. Design to the Needed Depth

Create architecture only when the work changes interfaces, data shape, operational behavior, or other cross-cutting decisions. Prefer a short decision record over a long speculative document.

Cover only what affects implementation:

- system boundaries
- interfaces and contracts
- data model and migrations
- failure modes and rollback
- key tradeoffs

### 3. Plan Delivery

Break the work into slices that can be implemented and verified independently.

For each slice, record:

- objective
- dependencies
- risks
- validation
- exit condition

Prefer a single execution plan over separate roadmap and development plan unless the project genuinely needs both.

### 4. Define Verification Before Building

Always define how success will be checked before implementation.

- `small`: acceptance checks or a short test list
- `medium`: test cases per slice plus manual checks if needed
- `large`: test strategy plus milestone-level acceptance criteria

Create automated tests when practical. If a check must stay manual, state why.

### 5. Execute One Slice at a Time

Implement, verify, update status, and then choose the next slice. Avoid opening many active fronts at once unless parallel work is clearly independent.

### 6. Re-Orient at Every Session Boundary

At the start and end of substantial work, restate:

- current phase
- completed work
- in-progress work
- blockers or open decisions
- next 3 actions

This is mandatory. It prevents the common failure mode where the user no longer knows where the project stands.

## Maintain the Minimum Artifact Set

Keep a single source of truth for these artifacts:

- `brief`: goal, scope, constraints, definition of done
- `status`: current phase, active slice, done/in progress/next, blockers, open decisions

Add these only when justified:

- `architecture`: for medium/large cross-cutting decisions
- `plan`: for multi-step delivery sequencing
- `roadmap`: for multi-milestone work across phases or teams
- `test-plan`: for non-trivial verification

Do not duplicate the same information across multiple documents.

## Govern the Document System

Treat documents as a system with clear ownership.

### Living control documents

These change often and control active execution:

- `brief`: what problem is being solved and under what constraints
- `plan`: how the current phase is sliced and validated
- `status`: where the project stands right now

Rules:

- keep them short
- update them during execution, not after the fact
- read them first when resuming work
- if they conflict with older docs, reconcile immediately

### Durable reference documents

These capture decisions or structures that outlive the current session:

- `architecture`
- `roadmap`
- `adr`
- `deployment-topology`
- `ownership-map`
- `migration-plan`
- `release-plan`
- stable testing references such as a `case-matrix`

Rules:

- update them only when the underlying truth changes
- do not turn them into session logs
- link them from living docs instead of copying content into the living docs

### Generated evidence

These are outputs, not control surfaces:

- eval reports
- audit reports
- benchmark reports
- exported artifacts

Rules:

- keep them out of the main decision path unless a result changes the plan
- summarize the conclusion in `status` or `plan` rather than treating the report as the current source of truth

## Assign One Question to One Document

Use this mapping:

- `What are we trying to achieve?` -> `brief`
- `What are we doing next, in what order?` -> `plan`
- `Where are we now?` -> `status`
- `How is the system shaped and why?` -> `architecture` or `adr`
- `What are the major phases and milestones?` -> `roadmap`
- `How will we verify the work?` -> `test-plan` or `case-matrix`
- `What actually happened in a run?` -> generated reports

If two files answer the same operational question, collapse or demote one of them.

## Place Artifacts Deliberately

Prefer these locations:

- repo-local working memory: `.codex/brief.md`, `.codex/plan.md`, `.codex/status.md`
- durable project docs: `docs/architecture.md`, `docs/adr/`, `docs/roadmap.md`

Use repo-local files for living execution state. Promote stable decisions into versioned docs when they matter beyond the current session.

## Handle Subprojects and Phase Work the Same Way

Apply the same loop recursively:

- create a child brief for a subproject only if it has distinct scope or constraints
- keep child slices linked to the parent roadmap or parent plan
- end each phase with explicit entry criteria for the next phase

Do not restart planning from zero for every subproject. Reuse the parent constraints and only add local deltas.

Subproject rules:

- create a subproject status file only for active, blocked, or coordination-heavy workstreams
- keep subproject files under `.codex/subprojects/`
- each subproject file must point back to the parent phase or milestone
- do not let subproject files become separate project roadmaps unless the work is truly independent

## Recover Context Before Continuing

When the user returns with "continue", "next", or a vague follow-up:

1. read the current brief, plan, and status artifacts if they exist
2. inspect the codebase and recent changes
3. summarize current phase, remaining work, and recommended next slice
4. continue execution from that point

If artifacts do not exist yet, create the smallest viable set before doing more work.

## Keep Control Surfaces Fresh During Execution

Update the control surface at these moments:

- after classifying or reclassifying the tier
- after finalizing the first slice
- after completing a slice
- when a blocker appears or clears
- before ending a substantial session

Minimum freshness rules:

- `status` must always reflect the real active slice
- `plan` must always reflect the next execution order
- `brief` must change only when the actual goal, scope, or constraints change

Do not postpone these updates until "later". Stale control docs are worse than missing docs because they create false confidence.

## Retrofit Existing Projects to This System

When the user asks to align, normalize, clean up, reorganize, or retrofit an existing repository to this delivery model, treat that as a first-class workflow.

Run the retrofit in this order:

1. inspect the current repo structure, docs, tests, reports, and obvious status sources
2. classify the project tier
3. identify the missing control surfaces and duplicated document responsibilities
4. propose the minimum structural changes needed
5. if the user asked for planning only, stop at the retrofit plan
6. otherwise apply the retrofit in small safe steps and update links or references that would break

The retrofit must prefer minimal disruption:

- preserve working code paths
- preserve stable reference docs unless they are clearly redundant
- create missing `.codex` control files first
- demote or archive duplicate status documents before deleting anything
- move generated evidence out of the control surface instead of mixing it with planning docs

Default retrofit outputs:

- create or refresh `.codex/brief.md`
- create or refresh `.codex/plan.md`
- create or refresh `.codex/status.md`
- optionally create `.codex/subprojects/*.md` for active workstreams
- assign each major existing document a clear role: living, durable, generated, or archive
- propose merges or demotions for overlapping roadmap, architecture, and todo files

If the repository already has a strong document system, do not replace it blindly. Adapt this model onto the existing structure and only add the smallest missing pieces.

## Close Slices and Phases Deliberately

When a slice or phase finishes:

1. verify the exit condition
2. update `status`
3. update `plan`
4. promote any stable decisions into durable docs if needed
5. identify the next slice or next phase entry criteria

For phase closeout, explicitly state:

- what is now complete
- what remains deferred
- what unlocks next
- what new risks appear in the next phase

## Report Project Progress Clearly

When the user asks for project progress, current state, milestone status, where the project stands, what is next, or a similar status query, produce a compact progress dashboard instead of a loose narrative.

Read in this order:

1. global `status`
2. global `brief`
3. global `plan`
4. active subproject status files if they exist
5. roadmap for milestone context
6. relevant tests, evals, or reports only to confirm claims

The response must separate these views:

- `global view`: overall phase, milestone, active slice, major risks, next 3 actions
- `subproject view`: only active or blocked subprojects
- `evidence view`: key test or report signals that justify the current assessment

Keep it concise. Prefer a short executive summary plus one table or one diagram over a long document recap.

## Use Diagrams for Status Queries

For non-trivial projects, include one Mermaid diagram when it improves orientation.

Preferred diagram types:

- phase flow: show completed, active, and next phases
- workstream map: show active, blocked, and completed subprojects
- milestone ladder: show current milestone and what unlocks next

Diagram rules:

- keep the diagram small
- reflect current truth from `status` and active subproject files
- do not redraw the entire architecture unless the user asked for architecture status specifically
- pair the diagram with a short textual summary so the answer still scans quickly

If progress artifacts are missing or stale, say that directly and propose the minimum updates needed to restore a trustworthy status view.

## Keep the User Oriented

When driving the work, always surface:

- what phase the project is in
- what decision is being made now
- what will happen next
- what information is still missing

Do not leave the user to infer project state from raw diffs or long histories.

## Prefer These File Roles by Default

Unless the repo has an established better structure, prefer:

- `.codex/brief.md` for project intent and constraints
- `.codex/plan.md` for execution order
- `.codex/status.md` for current truth
- `.codex/subprojects/*.md` for active subproject state
- `docs/` for durable decisions and references
- `reports/generated/` for generated evidence

Keep the navigation simple enough that a fresh session can find the current truth within two file opens.

When bootstrapping or retrofitting a repo, optionally create `.codex/COMMANDS.md` as a human-facing quick command sheet if the user would benefit from a local reminder.

## Use the Templates Only When Needed

Read [references/templates.md](references/templates.md) when creating or refreshing project artifacts. Read [references/governance.md](references/governance.md) when deciding which documents to create, which ones are living versus durable, and how to map project size to artifact depth. Read [references/progress-reporting.md](references/progress-reporting.md) when answering project progress questions or creating status dashboards. Read [references/retrofit.md](references/retrofit.md) when aligning an existing repository to this operating model. Read [references/bootstrap.md](references/bootstrap.md) when creating a new project control surface. Read [references/usage.md](references/usage.md) when the user needs prompt patterns or invocation examples. Read [references/glossary.md](references/glossary.md) when using operation names or project-control terms in user-facing communication. Read [references/help-menu.md](references/help-menu.md) when the user asks for available commands, help, or a menu.
