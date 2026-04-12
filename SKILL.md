---
name: project-assistant
description: Scale Codex-led software delivery with right-sized planning, status tracking, staged execution, retrofit, progress reporting, and context handoff. 适用于项目规划、架构讨论、roadmap、test case、development plan、阶段推进、状态恢复、项目整改、进展汇报、上下文交接。
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
- `执行` / `execute`
- `恢复` / `resume`
- `进展` / `progress`
- `整改` / `retrofit`
- `文档整改` / `docs-retrofit`
- `发布` / `release`
- `压缩上下文` / `交接` / `handoff`
- `收口` / `closeout`

Also trigger this skill when the user clearly asks for project startup, rescue, progress, retrofit, recovery, or handoff, even if the exact alias is not used.
Treat `文档整改`, `文档重构`, and `整理文档系统` as the documentation-focused variant of `retrofit`.
Treat `发布`, `打标`, and `发版` as the release flow when the repo supports versioned install docs.
Treat `docs retrofit`, `release`, and `handoff` as the English-friendly variants of those flows.

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

## Core Contract

1. classify the work as `small`, `medium`, or `large`
2. create or refresh the minimum required control surface
3. execute one slice at a time
4. keep status fresh at session boundaries
5. for existing repos, retrofit to convergence rather than stopping in a partial state

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
- [references/document-standards.md](references/document-standards.md)
- [references/governance.md](references/governance.md)
- [references/templates.md](references/templates.md)
- [references/module-layer.md](references/module-layer.md)

When generating `README`, `docs/README`, `architecture`, `roadmap`, `test-plan`, or ADRs, follow the document constraints in `references/document-standards.md`. Do not improvise a new structure when the standard already covers that doc type.
When a repo requires bilingual public docs, generate switchable English/Chinese file pairs for `README` and public `docs/*` pages, and validate that the language switch exists.

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
- `scripts/validate_gate_set.py`
  中文：按 `fast` / `deep` 分层运行门禁
- `scripts/progress_snapshot.py`
  中文：生成机器校验过的项目进展面板
- `scripts/context_handoff.py`
  中文：生成上下文压缩 / 新对话恢复包
- `scripts/release_skill.py`
  中文：更新版本、安装地址，并创建 release commit 和 tag

Use scripts first for structure, convergence, and reporting. Use model judgment for content quality, prioritization, and implementation decisions.

## Per-Mode Rules

### 启动 / Bootstrap

- classify tier
- create minimum control surface
- decide whether architecture / roadmap / test-plan are needed
- identify the first execution slice

If `scripts/sync_control_surface.py` exists, run it before filling content.

### 规划 / Plan

- clarify goal, scope, constraints, and definition of done
- slice work into independently verifiable steps
- define validation before implementation

Prefer a single execution plan unless the project truly needs both a roadmap and a development plan.

### 执行 / Execute

- work one slice at a time
- verify before moving on
- refresh `status` and `plan` as truth changes

### 恢复 / Resume

- read current control docs first
- summarize current phase, active slice, blockers, and next 3 actions
- continue from the right slice instead of replanning from zero

### 进展 / Progress

Use [references/progress-reporting.md](references/progress-reporting.md).

If `scripts/progress_snapshot.py` exists, run it first.

For `medium` and `large` projects, progress output should be a compact dashboard, not free-form prose. For large projects, include module view and Mermaid when it improves orientation.

### 整改 / Retrofit

Use [references/retrofit.md](references/retrofit.md).

Hard rules:

- retrofit is a convergence task, not a one-pass cleanup
- retrofit should be idempotent
- retrofit must fail closed
- do not stop in an intermediate state
- default retrofit includes documentation retrofit

Default scope of `整改`:

- control surface
- module layer when needed
- durable documentation structure such as `README`, `docs/README`, `architecture`, `roadmap`, `test-plan`, and ADR layout when those docs exist or are needed

If the user says `文档整改`, treat it as full Markdown governance convergence, not only the top-level durable doc stack.
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
- `deep` = `fast` + `validate_markdown_governance.py` + `validate_doc_quality.py` + `validate_control_surface_quality.py`
- `整改` and `文档整改` must finish on `deep`
- `发布` must pass `deep` before tagging

For large projects with first-class modules, retrofit is not complete without the module layer.

### 发布 / Release

Use release mode only when:

- a feature improvement is stable
- validations pass
- the repo uses tag-based install docs or explicit versioned release flow

Preferred maintainer hint:

- `可发布。执行：项目助手 发布 patch`

If the repo contains `VERSION`, `install.sh`, and tag-based install docs, prefer `scripts/release_skill.py`.

### 压缩上下文 / 交接 / Handoff

Use [references/context-guard.md](references/context-guard.md).

Important limit:

- if the runtime does not expose exact context usage, do not claim literal `60%` detection
- treat `60%` only as a soft trigger target

When asked to compress context or prepare a new thread:

- emit a compact resume pack
- include copy-paste commands for resume, progress, and continue-with-validation
- prefer `scripts/context_handoff.py`

You may proactively suggest `项目助手 压缩上下文` at natural phase boundaries or when the user is losing orientation, but do not spam it.

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
- run outputs -> reports / evals / audits

If two docs answer the same question, collapse or demote one of them.
