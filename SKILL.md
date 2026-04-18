---
name: project-assistant
description: Scale Codex-led software delivery with right-sized planning, status tracking, staged execution, retrofit, progress reporting, development logs, and context handoff. Combines best practices from architects, tech leads, reviewers, QA owners, and technical writers. 适用于项目规划、架构讨论、roadmap、test case、development plan、阶段推进、状态恢复、项目整改、进展汇报、开发日志、上下文交接，并融入架构师、技术负责人、代码审查者、QA/验证负责人和技术写作者的最佳实践。
---

# Project Assistant

Use this skill as a lightweight project operating system. Prefer the smallest control surface that preserves alignment, recoverability, and testability.

## Entry Rules

Treat these as invoking this skill:

- `项目助手`
- `项目操作系统`
- `项目治理`
- `project assistant`
- `project helper`
- `$project-assistant`

Primary modes:

- `启动` / `bootstrap`
- `规划` / `plan`
- `架构` / `architecture`
- `架构整改` / `architecture-retrofit`
- `执行` / `execute`
- `继续` / `恢复` / `continue` / `resume`
- `进展` / `progress`
- `整改` / `retrofit`
- `文档整改` / `文档整理` / `docs-retrofit`
- `开发日志` / `devlog`
- `发布` / `release`
- `压缩上下文` / `交接` / `handoff`
- `收口` / `closeout`

Also trigger this skill when the user clearly asks for project startup, rescue, architecture supervision, progress, retrofit, recovery, development logging, or handoff, even if the exact alias is not used.
Treat `文档整改`, `文档整理`, `文档重构`, and `整理文档系统` as the documentation-focused variant of `retrofit`.
Treat `架构整改`, `架构重构整改`, and `architecture retrofit` as the architecture-focused variant of `retrofit`.
Treat `发布`, `打标`, and `发版` as the release flow when the repo supports versioned install docs.
Treat `architecture`, `docs retrofit`, `devlog`, `release`, and `handoff` as the English-friendly variants of those flows.
Treat `继续` / `continue` as the default short resume-and-keep-going entry.

Choose command examples to match the user's language:

- Chinese user -> show Chinese simple commands first
- English user -> show English simple commands first

If public docs are bilingual, keep command examples localized per file:

- English doc -> English simple commands
- Chinese doc -> Chinese simple commands

When using English operation names in Chinese user-facing output, explain them in Chinese the first time. Do not force Chinese command examples into English docs.

## Menu Behavior

If the user asks:

- `项目助手 菜单`
- `项目助手 帮助`
- `项目助手 你能做什么`
- `项目助手 怎么用`

return a short command menu. Use [references/usage.md](references/usage.md) and [references/help-menu.md](references/help-menu.md).

If the user asks:

- `项目助手 架构`
- `project assistant architecture`

return a short architecture submenu instead of the general menu.

Primary human-facing windows:

- `项目助手 菜单` / `project assistant menu`
- `项目助手 进展` / `project assistant progress`
- `项目助手 架构` / `project assistant architecture`
- `项目助手 开发日志` / `project assistant devlog`

Most other flows should behave like background operating flows unless the user explicitly overrides them.

## Core Contract

1. classify the work as `small`, `medium`, or `large`
2. create or refresh the minimum required control surface
3. execute one slice at a time
4. default to a meaningful uninterrupted execution line instead of waiting for repeated "continue" prompts
5. express that execution line as a visible task board mapped back to the active slice or development plan
6. keep a compact architecture-supervision state beside that task board
7. use an explicit escalation gate: continue automatically, raise but continue, or require user decision
8. keep status fresh at session boundaries
9. for existing repos, retrofit to convergence rather than stopping in a partial state
10. keep the user oriented during long-running work with short visible progress updates about the current phase, recent discovery, and next checkpoint

### Tier Rules

- `small`: one short, low-risk execution cycle
- `medium`: multi-session feature or milestone
- `large`: multiple modules, milestones, adapters, or long-running governance

Escalate to `medium` when the work spans sessions, modules, or explicit validation. Escalate to `large` when the repo has first-class modules, multiple workstreams, adapters, migrations, or phased rollout.

Codex makes the first pass. The user can override.

## Minimum Control Surface

Always keep one source of truth per operational question.

Default living docs:

- `.codex/brief.md`
- `.codex/status.md`
- `.codex/plan.md` for `medium` and `large`
- `.codex/doc-governance.json` for Markdown ownership, public-doc scope, and root-doc policy

Large-project module layer:

- `.codex/module-dashboard.md`
- `.codex/modules/*.md`

Use `.codex/subprojects/*.md` only for active cross-cutting workstreams. Do not use subprojects to replace required module files for large projects.

Document ownership and templates live in:

- [references/bootstrap.md](references/bootstrap.md)
- [references/architecture-retrofit.md](references/architecture-retrofit.md)
- [references/document-standards.md](references/document-standards.md)
- [references/governance.md](references/governance.md)
- [references/templates.md](references/templates.md)
- [references/module-layer.md](references/module-layer.md)

When generating `README`, `docs/README`, `architecture`, `roadmap`, `test-plan`, or ADRs, follow the document constraints in `references/document-standards.md`. Do not improvise a new structure when the standard already covers that doc type.
When a roadmap contains `Stage` milestones and the repo also has a development plan, link those `Stage` references to the matching development-plan headings with repository-relative links.
For `medium` and `large` repos, documentation retrofit should also establish a durable `development plan` layer under `docs/reference/<project-slug>/development-plan.md` so maintainers can move from roadmap-level direction to detailed execution order without dropping straight into `.codex/plan.md`.
When a repo requires bilingual public docs, generate switchable English/Chinese file pairs for `README` and public `docs/*` pages, and validate that the language switch exists.
When writing markdown into a repo, use repository-relative links. Do not write local absolute filesystem paths into repo docs.

Roadmap integrity rules:

- each roadmap milestone or stage must represent one clear goal, not a mixed bucket
- marking a roadmap item `done` / `complete` means that item is actually closed, not "partly done but continued elsewhere"
- do not spread one work item across multiple top-level roadmap milestones or stages; if a line continues, keep it as one milestone until it is truly complete
- if a large theme has multiple sub-steps, keep the roadmap milestone at the theme level and move the sub-steps into the development plan or execution task board instead of splitting the same theme across multiple roadmap buckets
- roadmap items should be readable by humans without needing `.codex/*` to understand whether the item is complete, still active, or deferred

## Script-First Execution

Prefer the bundled scripts when present:

- `scripts/sync_control_surface.py`
  中文：同步控制面脚手架并把仓库收敛到目标结构
- `scripts/validate_control_surface.py`
  中文：按 tier 规则校验控制面是否达标
- `scripts/sync_docs_system.py`
  中文：同步 durable 文档系统到标准结构
- `scripts/sync_markdown_governance.py`
  中文：对全仓 Markdown 做归类、迁移、链接修复和目录收敛
- `scripts/validate_docs_system.py`
  中文：按文档标准校验 README / docs / architecture / roadmap / test-plan
- `scripts/validate_public_docs_i18n.py`
  中文：校验公开文档是否具备中英文成对文件和语言切换入口
- `scripts/validate_markdown_governance.py`
  中文：校验全仓 Markdown 是否已经完成职责收口
- `scripts/validate_doc_quality.py`
  中文：校验公开文档是否仍然停留在模板态、假双语或坏链接状态
- `scripts/validate_control_surface_quality.py`
  中文：校验 `.codex/*` 活文档是否还停留在模板态
- `scripts/sync_execution_line.py`
  中文：从 active slice 自动生成更长的执行线任务板
- `scripts/sync_architecture_supervision.py`
  中文：从当前执行线、blockers 和升级状态自动刷新架构信号与升级 gate
- `scripts/sync_architecture_retrofit.py`
  中文：生成 repo 本地的架构整改工作底稿
- `scripts/validate_gate_set.py`
  中文：按 `fast` / `deep` 分层运行门禁
- `scripts/write_development_log.py`
  中文：写入一条带问题、思考、解决方案和验证的开发日志
- `scripts/validate_development_log.py`
  中文：校验开发日志索引和条目结构是否完整
- `scripts/bootstrap_entry.py`
  中文：`启动` 的事务化快路径：一次完成 control-surface、durable docs 和 fast gate
- `scripts/retrofit_entry.py`
  中文：`整改 / 文档整改` 的事务化快路径：一次完成 control-surface、docs、markdown governance 和 fast gate
- `scripts/continue_entry.py`
  中文：`继续` 的唯一结构化入口，强制先做 preflight 再输出表格化 continue 面板
- `scripts/progress_entry.py`
  中文：`进展` 的唯一结构化入口，强制输出表格化 maintainer dashboard
- `scripts/handoff_entry.py`
  中文：`交接` 的唯一结构化入口，强制输出可复制的交接面板
- `scripts/project_assistant_entry.py`
  中文：`启动 / 整改 / 文档整改 / 继续 / 进展 / 交接 / 继续前升级` 的统一前门，把 mode 路由到唯一后端链路
- `scripts/sync_resume_readiness.py`
  中文：在 `继续` / `恢复` 前按 `.codex/control-surface.json` 版本自动判断是否需要升级，并执行最小安全补齐
- `scripts/sync_entry_routing.py`
  中文：生成 `.codex/entry-routing.md`，把统一前门、preflight、结构化输出契约和宿主桥接边界写成 durable 真相
- `scripts/validate_entry_routing.py`
  中文：校验 `.codex/entry-routing.md` 是否真实可用
- `scripts/validate_architecture_retrofit.py`
  中文：校验架构整改工作底稿是否真实可用
- `scripts/capability_snapshot.py`
  中文：汇总当前仓库现在已经可用的项目助手能力
- `scripts/progress_snapshot.py`
  中文：生成机器校验过的项目进展面板
- `scripts/context_handoff.py`
  中文：生成上下文压缩 / 新对话恢复包
- `scripts/validate_release_readiness.py`
  中文：按架构信号、升级 gate 和开发日志状态校验发布就绪度
- `scripts/release_skill.py`
  中文：更新版本、安装地址，并创建 release commit 和 tag

Use scripts first for structure, convergence, and reporting. Use model judgment for content quality, prioritization, and implementation decisions.

## Per-Mode Rules

### 启动 / Bootstrap

- classify tier
- create minimum control surface
- decide whether architecture / roadmap / test-plan are needed
- identify the first execution slice

If `scripts/project_assistant_entry.py` exists, prefer `python3 scripts/project_assistant_entry.py bootstrap <repo>` as the canonical bootstrap fast path.
Otherwise, if `scripts/bootstrap_entry.py` exists, run it first.
Otherwise, if `scripts/sync_control_surface.py` exists, run it before filling content.

### 规划 / Plan

- clarify goal, scope, constraints, and definition of done
- slice work into independently verifiable steps
- define validation before implementation
- define the current execution line: a meaningful autonomous run that should continue until a checkpoint, blocker, or decision gate
- define the execution task board under that line so the user can see done/total progress at a glance
- define the architecture-supervision state for that line: signal, root-cause hypothesis, correct layer, rejected shortcut, and escalation gate
- keep roadmap milestones stable and non-overlapping: one milestone = one clear theme with one real completion boundary

Prefer a single execution plan unless the project truly needs both a roadmap and a development plan.

### 架构 / Architecture

Use architecture mode as the manual supervision entry.

Recommended subcommands:

- `项目助手 架构 监督` / `project assistant architecture review`
- `项目助手 架构 复盘` / `project assistant architecture retrospective`
- `项目助手 架构 根因` / `project assistant architecture root-cause`
- `项目助手 架构 扩展性` / `project assistant architecture extensibility`
- `项目助手 架构 整改` / `project assistant architecture retrofit`

When the user enters only `项目助手 架构` or `project assistant architecture`, show these subcommands with one-line explanations.
Mark the most common subcommand first and include a short "when to use it" note for each item.

Default responsibilities:

- identify whether the current change is addressing a symptom or a root cause
- check whether the chosen layer or abstraction boundary is correct
- reject one-off hardcoding that should become a reusable mechanism
- evaluate extensibility risk before or after implementation
- set a visible supervision signal: `green`, `yellow`, or `red`
- set an escalation gate: `continue automatically`, `raise but continue`, or `require user decision`

Review order:

1. start from the high-level package: goal, constraints, root-cause hypothesis, affected boundaries, proposed layer
2. challenge the direction before reading local implementation details
3. pull code paths, diffs, or concrete evidence only when the high-level review needs proof

For `medium` and `large` work, architecture supervision should run implicitly inside `plan`, `execute`, `retrofit`, and `closeout`, while these commands remain available as explicit manual overrides.
If the user explicitly chooses architecture retrofit, prefer the architecture-retrofit flow over generic retrofit.

### 执行 / Execute

- work one slice at a time
- derive a current execution line from the active slice
- map the execution line back to one explicit slice via `Plan Link`
- keep a visible execution task board with checkbox tasks and `EL-*` ids
- keep a visible architecture-supervision block beside the task board
- let the execution task board expand to as many subtasks as the checkpoint needs, often 5-20+ tasks for a meaningful long run
- prefer one meaningful uninterrupted run, with a target of roughly 20-30 minutes of autonomous progress when the repo and task support it
- do not stop after every micro-step just to ask for "continue"
- verify before moving on
- refresh `status` and `plan` as truth changes
- during long execution or retrofit runs, keep the user informed with short visible progress notes instead of going silent

Stop only when:

- a checkpoint for the current execution line is reached
- a blocker or failed validation needs human direction
- a business, product, compatibility, or cost tradeoff requires user judgment
- the current direction is judged red by architecture supervision
- the escalation gate is `require user decision`

### 恢复 / Resume

- automatically judge whether the repo's control-surface version is stale before resuming
- if `.codex/control-surface.json` is missing, the control-surface version is old, or required surface versions are stale, run the minimum safe sync path first instead of asking the user whether to retrofit
- do not ask the user to make that generation judgment; decide it yourself and explain briefly what is being checked or upgraded
- read current control docs first
- render a compact continue snapshot instead of a full dashboard
- include current phase, active slice, long task, execution progress, architecture signal, next work, and the visible task board
- keep it short and explicitly say that full progress is available via `项目助手 进展` / `project assistant progress`
- continue from the right slice instead of replanning from zero
- treat the continue panel as a hard contract, not a suggestion
- never start `继续` with a free-form prose paragraph
- if the repo changed during `继续`, emit the continue panel first and add later narrative under a separate `本轮动作` block

If `scripts/continue_entry.py` exists, run it first and use its output as the first user-visible block.
If `scripts/project_assistant_entry.py` exists, prefer it as the canonical front door for `bootstrap / retrofit / continue / progress / handoff / resume-readiness`.
Otherwise, if `scripts/sync_resume_readiness.py` exists, run it first.
Otherwise, if `scripts/continue_snapshot.py` exists, run it first.

### 进展 / Progress

Use [references/progress-reporting.md](references/progress-reporting.md).

If `scripts/progress_entry.py` exists, run it first and use its output as the first user-visible block.
If `scripts/project_assistant_entry.py` exists, prefer it as the canonical front door for `bootstrap / retrofit / continue / progress / handoff / resume-readiness`.
Otherwise, if `scripts/progress_snapshot.py` exists, run it first.

For `medium` and `large` projects, progress output should be a compact dashboard, not free-form prose. For large projects, include module view and Mermaid when it improves orientation.
When an execution line exists, surface its task board and done/total count as a first-class part of the dashboard.
When architecture supervision is active, surface its signal and escalation gate beside the execution line.
When capabilities have become usable, surface a compact `Usable Now` snapshot so the user can see what is ready, not only what is still being built.

### 整改 / Retrofit

Use [references/retrofit.md](references/retrofit.md).

Hard rules:

- retrofit is a convergence task, not a one-pass cleanup
- retrofit should be idempotent
- retrofit must fail closed
- do not stop in an intermediate state
- default retrofit includes documentation retrofit
- if the repo is a git worktree and has uncommitted changes, prompt whether to create a checkpoint commit before restructuring
- do not auto-commit without user approval
- if the user wants to continue without committing, proceed without reverting their changes
- during retrofit, architecture-retrofit, and long repair runs, keep short user-visible progress notes so the user knows what is running now, what changed, and what remains

Default scope of `整改`:

- control surface
- module layer when needed
- durable documentation structure such as `README`, `docs/README`, `architecture`, `roadmap`, `test-plan`, and ADR layout when those docs exist or are needed

If the user says `文档整改` or `文档整理`, treat it as full Markdown governance convergence, not only the top-level durable doc stack.
That includes:

- bootstrap the control surface first
- durable doc stack
- full Markdown tree ownership cleanup
- migrating legacy deep Markdown trees into `docs/reference/`, `docs/workstreams/`, or `docs/archive/`
- moving durable strategy docs out of `reports/`
- archiving exploratory or superseded docs
- reducing root-doc clutter
- creating missing bilingual public-doc counterparts when the repo requires bilingual public docs
- fixing links after moves

If `scripts/project_assistant_entry.py` exists, prefer `python3 scripts/project_assistant_entry.py retrofit <repo>` for `整改`, and `python3 scripts/project_assistant_entry.py docs-retrofit <repo>` for `文档整改 / 文档整理`, so the structural pass is collapsed into one tool call.

If scripts exist:

1. run `scripts/sync_control_surface.py`
2. run `scripts/sync_docs_system.py`
3. run `scripts/sync_markdown_governance.py`
4. apply or refine content as needed
5. during active work, prefer `scripts/validate_gate_set.py --profile fast`
6. before declaring retrofit complete, run `scripts/validate_gate_set.py --profile deep`
7. do not declare completion unless the required validations pass

Gate policy:

- `fast` = `validate_control_surface.py` + `validate_docs_system.py` + `validate_public_docs_i18n.py`
- `deep` = `fast` + `validate_markdown_governance.py` + `validate_doc_quality.py` + `validate_control_surface_quality.py` + `validate_development_log.py`
- `release` = `deep` + `validate_release_readiness.py`
- `整改`, `文档整改`, and `文档整理` must finish on `deep`
- `发布` must pass `release` before tagging

For large projects with first-class modules, retrofit is not complete without the module layer.

### 架构整改 / Architecture Retrofit

Use [references/architecture-retrofit.md](references/architecture-retrofit.md).

Architecture retrofit is for direction drift, not just structure drift.
It defaults to direct convergence, not audit-only output.

Default sequence:

1. run `scripts/sync_architecture_retrofit.py`
2. read `.codex/architecture-retrofit.md`
3. turn that note into one or more explicit slices
4. generate the current execution line from the chosen architecture-retrofit slice
5. apply the architecture retrofit, not only the architecture-retrofit note
6. keep the architecture signal visible during the retrofit
7. finish on `deep`; if release-facing behavior changed, also finish on `release`

Only stop at an audit note or retrofit checklist when the user explicitly says:

- `先不要改文件`
- `先审计`
- `先出整改方案`
- `plan first`
- `audit only`

If the repo is a git worktree and has uncommitted changes, run the same dirty-worktree preflight before applying architecture retrofit changes.

### 发布 / Release

Use release mode only when:

- a feature improvement is stable
- validations pass
- the repo uses tag-based install docs or explicit versioned release flow

Preferred maintainer hint:

- `可发布。执行：项目助手 发布 patch`

If the repo contains `VERSION`, `install.sh`, and tag-based install docs, prefer `scripts/release_skill.py`.
When scripts are available, prefer computed architecture signal output over stale prose and keep the release path on `validate_gate_set.py --profile release`.

### 开发日志 / Devlog

Use [references/development-log.md](references/development-log.md).

Write or update a development log when:

- retrofit, debugging, or implementation produced durable reasoning worth keeping
- a future maintainer would otherwise need to reconstruct the same path from diffs
- a design boundary changed because evidence or constraints invalidated the original assumption

Default behavior:

- write or update the devlog automatically when a durable reasoning thread appears
- keep a visible trigger-strength policy in the control surface so the assistant knows what must be captured and what can be skipped
- keep the manual `项目助手 开发日志` / `project assistant devlog` entry as an override or backfill window

Default location:

- `docs/devlog/README.md`
- `docs/devlog/README.zh-CN.md`
- `docs/devlog/YYYY-MM-DD-topic.md`

Prefer `scripts/write_development_log.py` when present. Treat the log as a durable reasoning note, not as a replacement for `status`, `roadmap`, or ADRs.

### 压缩上下文 / 交接 / Handoff

Use [references/context-guard.md](references/context-guard.md).

Important limit:

- if the runtime does not expose exact context usage, do not claim literal `60%` detection
- treat `60%` only as a soft trigger target

When asked to compress context or prepare a new thread:

- emit a compact resume pack
- include copy-paste commands for resume, progress, and continue-with-validation
- prefer a structured handoff panel over prose

If `scripts/handoff_entry.py` exists, run it first and use its output as the first user-visible block.
If `scripts/project_assistant_entry.py` exists, prefer it as the canonical front door for `bootstrap / retrofit / continue / progress / handoff / resume-readiness`.
Otherwise, prefer `scripts/context_handoff.py`.

You may proactively suggest `项目助手 压缩上下文` at natural phase boundaries or when the user is losing orientation, but do not spam it.

## Default Interaction Model

The user should primarily provide:

- business direction
- priority
- hard constraints
- decisions that truly require product or business judgment

Project Assistant should default to handling:

- planning
- architecture supervision
- execution
- validation
- status refresh
- development-log capture

Treat explicit commands as override windows, not as the primary way the user must drive ordinary progress.

### 收口 / Closeout

- confirm the current slice is verified
- update status
- state next entry criteria

## Freshness Rules

Update the control surface:

- after tier classification or reclassification
- after selecting the active slice
- after completing a slice
- when blockers appear or clear
- before ending a substantial session

Stale control docs are worse than missing docs.

## Operational Mapping

One operational question should have one primary answer:

- goal / scope / constraints -> `brief`
- current truth -> `status`
- next execution order -> `plan`
- stable system shape -> `architecture` / `adr`
- milestones -> `roadmap`
- durable reasoning path -> `docs/devlog/*.md`
- run outputs -> reports / evals / audits

If two docs answer the same question, collapse or demote one of them.
