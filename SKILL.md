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
- `消息` / `message` / `ingress`
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
4. before widening implementation, verify uncertain host, API, protocol, plugin, binary, or undocumented-behavior assumptions with the smallest feasible probe; if the probe fails, stop, shrink, or switch layer instead of continuing implementation
5. default to a meaningful uninterrupted execution line instead of waiting for repeated "continue" prompts
6. express that execution line as a visible task board mapped back to the active slice or development plan
7. keep a compact architecture-supervision state beside that task board
8. use an explicit escalation gate: continue automatically, raise but continue, or require user decision
9. keep status fresh at session boundaries
10. for existing repos, retrofit to convergence rather than stopping in a partial state
11. keep the user oriented during long-running work with short visible progress updates about the current phase, recent discovery, and next checkpoint
12. before declaring a project-assistant run complete, apply the no-known-required-next-step completion gate: if a known required next step remains and it is not blocked, human-decision-bound, or explicitly deferred, continue the work instead of leaving it as a follow-up
13. treat every non-trivial execution request as a task inside the programmatic task pipeline; enqueue the task first, then let the runner decide next-task, repair-task, return-to-mainline, completion, blocked, or human-decision states
14. route every non-empty project-assistant user message through message ingress when the host or local scripts can do so; execution messages enqueue and run, analysis/discussion messages still become explicit reviewable tasks, and classify-only must be deliberate
15. when human confirmation is required, represent it as an explicit `human-decision` task in the pipeline; after the human accepts, rejects, snoozes, or says `全部接受` for a scoped review, close that task and let the runner continue automatically
16. start every project-assistant reply with a state-sensitive compact loop header that states the current loop or task id and the goal for this turn; include exit or pause options only when work is still running or waiting, and if there is no active task or human action needed, explicitly say no human action is needed instead of asking the user to stop or pause
17. whenever human action is needed, include a separate `需要人类做什么` section that re-lists the required actions, exact reply format, and current pending items; never rely on earlier context

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
- `scripts/ptl_gate.py`
  中文：生成 repo 本地的 PTL policy，并在 `continue / progress / execute / release` 前运行轻量 preflight
- `scripts/ptl_learning.py`
  中文：从反复纠正、失败模式和轻量语义归纳生成可 review 的 PTL learning candidates，并把接受后的规则写入重装不覆盖的 learned registry
- `scripts/validate_ptl_gate.py`
  中文：用隔离 fixture 校验 PTL policy sync、缺控制面阻塞、出图域和 OpenClaw 域自动识别
- `scripts/validate_ptl_learning.py`
  中文：用隔离 fixture 校验 learning review、accept / reject / snooze、语义归纳、持久 registry，以及 accepted rules 注入 PTL preflight
- `scripts/completion_gate.py`
  中文：在 final / closeout 前判断是否还存在已知必要下一步，防止把必做项留成“下一步”
- `scripts/validate_completion_gate.py`
  中文：用隔离 fixture 校验 open task、未完成进度、final answer next-step、显式延期和人类决策停止语义
- `scripts/pipeline_runner.py`
  中文：运行 repo 本地 `.codex/task-pipeline.json` 程序循环，负责任务入队、下一步选择、失败修复、显式 human-decision gate、LLM task 完成写回、final-text 必做后续入队、历史 message backlog 维护、回到主线和完成判断
- `scripts/validate_pipeline_runner.py`
  中文：用隔离 fixture 校验自动继续、失败修复、LLM task 暂停与 resolve 写回、人类决策、final-text 后续入队、历史 backlog 归档和入口面板
- `scripts/message_ingress.py`
  中文：把 host/user message 分类、记录到 `.codex/message-ingress.json`，并默认入队到 task pipeline 后进入程序循环
- `scripts/validate_message_ingress.py`
  中文：用隔离 fixture 校验执行消息、讨论消息、classify-only、统一前门和入口面板
- `scripts/codex_message_wrapper.py`
  中文：轻量包装 Codex CLI 初始 prompt，在转发给真实 `codex` 前先写入 project-assistant message ingress
- `scripts/install_codex_message_wrapper.py`
  中文：把 wrapper 安装到 `~/.local/bin/codex`，保留真实 Codex binary 路径并允许环境变量覆盖
- `scripts/validate_codex_message_wrapper.py`
  中文：用 fake codex 校验初始 prompt、`exec` prompt、`app-server` 跳过和禁用开关
- `scripts/codex_app_loop.py`
  中文：监听 Codex Desktop App 写入的 session JSONL，把 App 内用户消息异步兜底路由到 project-assistant message ingress 和 task pipeline
- `scripts/codex_app_user_prompt_hook.py`
  中文：Codex `UserPromptSubmit` hook 命令入口，在 App prompt 提交时把消息同步写入 message ingress 和 task pipeline
- `scripts/install_codex_app_loop.py`
  中文：安装全局 `AGENTS.md` 提示词前门、`UserPromptSubmit` hook、`features.codex_hooks = true` 和 macOS LaunchAgent，使 Codex App 消息有同步主入口和异步兜底
- `scripts/validate_codex_app_loop.py`
  中文：用隔离 fixture 校验 App `UserPromptSubmit` hook、session watcher、去重、trusted project 路由、安装器和入口面板
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
  中文：`启动 / 整改 / 文档整改 / 消息 / 执行 / 继续 / 进展 / 交接 / 继续前升级` 的统一前门，把 mode 路由到唯一后端链路
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
- `scripts/validate_repo_markdown_integrity.py`
  中文：对整个仓库的 Markdown 做本地链接、锚点和绝对路径完整性校验
- `scripts/nightly_project_audit.py`
  中文：按项目助手规范对多个本地仓库做夜间汇总巡检，并输出 Markdown / JSON 报告
- `scripts/install_nightly_project_audit.py`
  中文：把夜间巡检安装成 macOS `launchd` 定时任务

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

- when a non-empty user message arrives in project-assistant context and scripts are available, prefer `python3 scripts/message_ingress.py ingest <repo> --message "<user message>"` or `python3 scripts/project_assistant_entry.py message <repo> --message "<user message>"` before doing substantial work
- when using Codex from a terminal, install the lightweight wrapper with `python3 scripts/install_codex_message_wrapper.py` so `codex "<prompt>"` and `codex exec "<prompt>"` enter message ingress before the real Codex binary runs
- when using Codex Desktop App, install the App loop bridge with `python3 scripts/install_codex_app_loop.py`; it combines a `UserPromptSubmit` hook as the supported prompt-submit ingress, a global `AGENTS.md` front-door prompt, and a LaunchAgent session watcher fallback that routes Codex App `user_message` events into message ingress
- use direct `pipeline_runner.py run --task` only as the lower-level execution entry after a message has already been captured, or when the caller is explicitly submitting a task rather than a host/user message
- before doing implementation work, enqueue the user-requested work into the task pipeline; do not execute substantial project work outside the pipeline loop
- when the route depends on uncertain host capability, API, binary, plugin mechanism, external protocol, or undocumented behavior, run a feasibility probe before broad implementation or docs
- when scripts exist, prefer `python3 scripts/pipeline_runner.py run <repo> --task "<task title>"` for a new execution request, or `python3 scripts/project_assistant_entry.py execute <repo> --task "<task title>"` through the unified front door
- let the programmatic loop decide whether to run the next task, create a repair task, return to the original task, stop as complete, block, or require human decision
- LLM execution should happen inside one bounded pipeline task; control flow belongs to the runner, not to the model's memory or willingness to continue
- start user-facing progress updates and final answers with: current loop and current goal; add `停止`, `暂停`, or a human-decision response format only when the current state actually needs an exit, pause, or human decision
- when asking the human to decide, confirm, approve, reject, provide input, or unblock work, always restate `需要人类做什么` with numbered actions and exact reply examples before any optional detail
- when an LLM task from the pipeline is completed, blocked, deferred, or needs human judgment, write the outcome back with `python3 scripts/pipeline_runner.py resolve <repo> --task-id <task-id> --outcome done --summary "<what changed>" --run-next` or the matching non-done outcome before final response
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

Do not stop merely because a baseline or intermediate layer is usable. If the current answer would say "next step still needs X", decide whether X is required for the user's objective. Required X means continue automatically; optional, blocked, human-decision-bound, or explicitly deferred X must be labeled that way.

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
If `scripts/project_assistant_entry.py` exists, prefer it as the canonical front door for `bootstrap / retrofit / message / execute / continue / progress / handoff / resume-readiness`.
Otherwise, if `scripts/sync_resume_readiness.py` exists, run it first.
Otherwise, if `scripts/continue_snapshot.py` exists, run it first.

### 进展 / Progress

Use [references/progress-reporting.md](references/progress-reporting.md).

If `scripts/progress_entry.py` exists, run it first and use its output as the first user-visible block.
If `scripts/project_assistant_entry.py` exists, prefer it as the canonical front door for `bootstrap / retrofit / message / execute / continue / progress / handoff / resume-readiness`.
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

- `fast` = `validate_control_surface.py` + `validate_docs_system.py` + `validate_public_docs_i18n.py` + `validate_entry_routing.py` + `validate_ptl_gate.py` + `validate_ptl_learning.py` + `validate_completion_gate.py` + `validate_pipeline_runner.py` + `validate_message_ingress.py` + `validate_codex_message_wrapper.py` + `validate_codex_app_loop.py`
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
Treat versioned one-click install links as part of the default release surface: update them through the release automation before tagging, and fail release readiness when they drift from `VERSION`.

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
If `scripts/project_assistant_entry.py` exists, prefer it as the canonical front door for `bootstrap / retrofit / message / execute / continue / progress / handoff / resume-readiness`.
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
- run `scripts/completion_gate.py final-check <repo> --stop-reason complete` before declaring completion when scripts are available
- if the completion gate returns `require-continue`, continue execution instead of presenting the remaining work as a follow-up
- state next entry criteria only when the remaining work is optional, blocked, requires human decision, or explicitly deferred

Allowed stop taxonomy:

- `complete`: the objective contract is satisfied and no known required next step remains
- `blocked`: execution cannot continue because of a concrete tool, permission, environment, or missing-information blocker
- `requires-human-decision`: business direction, risk upgrade, accepted-rule promotion, external write, cost, compatibility, or product commitment requires human judgment
- `explicitly-deferred`: the user or objective contract explicitly moved the remaining work out of the current run

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
