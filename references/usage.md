# Usage

Use these prompt patterns to invoke the skill cleanly.

## Primary Windows | 主窗口

These are the human-facing windows you should need most of the time:

- `项目助手 菜单` / `project assistant menu`
- `项目助手 进展` / `project assistant progress`
- `项目助手 架构` / `project assistant architecture`
- `项目助手 开发日志` / `project assistant devlog`

Everything else should increasingly behave like a background flow that the assistant runs on its own.

## Simple Commands | 简单指令

- 推荐总入口：`项目助手`
- Recommended English entry: `project assistant`
- `启动` = `bootstrap`
- `规划` = `plan`
- `架构` = `architecture`
- `执行` = `execute`
- `继续` = `continue / resume`
- `进展` = `progress`
- `整改` = `retrofit`
- `文档整改` / `文档整理` = `docs-retrofit`
- `开发日志` = `devlog`
- `发布` = `release`
- `收口` = `closeout`
- `压缩上下文 / 交接` = `handoff`

English simple commands:

- `project assistant menu`
- `project assistant start this project`
- `project assistant plan the next phase`
- `project assistant architecture`
- `project assistant continue`
- `project assistant progress`
- `project assistant retrofit`
- `project assistant docs retrofit`
- `project assistant devlog`
- `project assistant handoff`
- `project assistant release patch`

Gate commands:

- `python3 scripts/validate_gate_set.py /path/to/repo --profile fast`
- `python3 scripts/validate_gate_set.py /path/to/repo --profile deep`
- `python3 scripts/validate_gate_set.py /path/to/repo --profile release`
- `python3 scripts/continue_entry.py /path/to/repo`
- `python3 scripts/progress_entry.py /path/to/repo`
- `python3 scripts/handoff_entry.py /path/to/repo`
- `python3 scripts/validate_control_surface_quality.py /path/to/repo --format text`
- `python3 scripts/validate_development_log.py /path/to/repo --format text`
- `python3 scripts/validate_architecture_retrofit.py /path/to/repo --format text`
- `python3 scripts/capability_snapshot.py /path/to/repo --format text`
- `python3 scripts/sync_execution_line.py /path/to/repo --slice "slice name" --force`
- `python3 scripts/sync_architecture_supervision.py /path/to/repo`
- `python3 scripts/sync_architecture_retrofit.py /path/to/repo`
- `python3 scripts/sync_resume_readiness.py /path/to/repo`

## Start or Bootstrap | 启动

- `用 $project-assistant 启动这个项目，先明确目标、约束、DoD，再生成最小控制面。`
- `Use $project-assistant to bootstrap this repo and create brief/plan/status.`

## Plan a Feature or Phase | 规划阶段/功能

- `用 $project-assistant 规划这个阶段，判断规模，并给出 architecture / roadmap / test-plan 是否需要。`
- `Use $project-assistant to break this feature into slices and define validation first.`

默认语义：

- 规划不只输出“先做哪个后做哪个”
- 还要定义一个当前执行线（execution line）
- 当前执行线表示：AI 接下来应该一口气自主推进的那段工作，直到到达检查点、阻塞点或决策点
- 当前执行线下面要有一个可见的子任务板（execution tasks）
- 子任务板必须通过 `Plan Link` 映射回一个明确 slice
- 子任务数量没有硬上限；只要仍属于同一个检查点，5-20+ 个子任务都可以
- 同时要给出架构监督状态和升级模型，避免执行时重新掉回局部修补
- 如果已有 active slice，优先用 `sync_execution_line.py` 自动生成更长任务板，而不是手写零散 next actions

## Architecture Supervision | 架构监督

Most common:

- `项目助手 架构 监督`
- `project assistant architecture review`

When to start with it:

- before implementing a feature that may introduce hardcoding
- when fixes keep cascading and the root cause may be above the current patch
- when you want a higher-level judgment on abstraction boundaries

- `项目助手 架构`
- `项目助手 架构 监督`
- `项目助手 架构 复盘`
- `项目助手 架构 根因`
- `项目助手 架构 扩展性`
- `项目助手 架构 整改`
- `Use $project-assistant to review this change from the architecture level before implementation.`
- `project assistant architecture`
- `project assistant architecture review`
- `project assistant architecture retrospective`
- `project assistant architecture root-cause`
- `project assistant architecture extensibility`
- `project assistant architecture retrofit`

When the user enters only `项目助手 架构` or `project assistant architecture`, return the architecture submenu instead of a generic response.

Recommended usage notes:

- `项目助手 架构`
  用途：先看子命令，不确定时从这里开始
- `项目助手 架构 监督`
  用途：实现前或实现中，审查当前方向是不是在修局部现象
- `项目助手 架构 复盘`
  用途：一个 slice 或一轮 bugfix 后，检查有没有方向漂移
- `项目助手 架构 根因`
  用途：怀疑问题源头不在当前改动点时使用
- `项目助手 架构 扩展性`
  用途：准备新增抽象、接口或模块边界时使用
- `项目助手 架构 整改`
  用途：当边界、状态流或架构所有权已经系统性错位，需要直接执行架构优先的整改并收敛时使用
  额外：如果仓库有未提交改动，先提示是否做 checkpoint 提交

English usage notes:

- `project assistant architecture`
  Use: open the submenu when you are unsure which architecture check you need
- `project assistant architecture review`
  Use: before or during implementation to stop local-only fixes
- `project assistant architecture retrospective`
  Use: after a slice or bugfix round to check for drift
- `project assistant architecture root-cause`
  Use: when symptoms keep reappearing and the cause may be elsewhere
- `project assistant architecture extensibility`
  Use: before introducing abstractions, interfaces, or reusable mechanisms
- `project assistant architecture retrofit`
  Use: when the repo needs an architecture-first retrofit that should execute to convergence, not stop at a checklist
  Extra: if the repo is dirty, ask whether to create a checkpoint commit first

## Resume Work | 恢复工作

- `项目助手 继续`
- `用 $project-assistant 继续这个仓库的当前执行线。`
- `Use $project-assistant to continue this repo from the current execution line.`
- `project assistant continue`
- `兼容别名：项目助手 恢复当前状态 / project assistant resume current status`

默认语义：

- `继续` 直接表示“恢复当前状态并继续当前执行线”
- `继续` 不要求用户自己判断项目是不是旧代际；系统应先自动读取 `.codex/control-surface.json`，检查当前控制面版本是否落后
- 如果控制面版本过旧，或缺少当前要求的 surface 版本，`继续` 应先自动补齐最小安全升级，再进入真正的恢复与继续
- `继续` 默认先给一个简版进展快照，而不是完整 dashboard
- `继续` 必须先输出结构化 continue 面板；不能先写自由 prose
- 简版快照至少要带：当前阶段、当前切片、当前长任务、执行进度、架构信号、接下来要做的事
- “接下来要做的事”应优先来自当前任务板里的未完成任务，这样和下面的 task board 是对应的
- 应直接进入当前执行线，继续一段有意义的长任务
- 同时要明确提示：如果想看完整全局视图，用 `项目助手 进展`
- 恢复输出应优先展示执行线目标、done/total 进度和当前可见子任务板
- 恢复输出也应展示当前架构监督信号和升级 gate
- 恢复输出也应带一个 `Usable Now` 快照，让用户知道当前有哪些能力已经能直接使用
- 如果在继续前触发了自动补齐，应先用一句短话告诉用户“我正在检查 / 补齐哪些控制面”，不要长时间沉默
- 如果 `继续` 过程中实际改动了仓库，应在 continue 面板后另起一个 `本轮动作` 区块，不要把面板替换成 prose 摘要

## Ask for Progress | 查看进展

- `用 $project-assistant 告诉我这个项目当前进展，用全局视角、子项目视角和图示输出。`
- `用 $project-assistant 告诉我这个大项目的模块进展，用全局视角、模块视角和图示输出。`
- `用 $project-assistant 先跑进展快照，再告诉我项目当前进展。`
- `Use $project-assistant to give me a concise progress dashboard with a Mermaid diagram.`
- `project assistant progress`

## Compress Context | 压缩上下文

- `用 $project-assistant 压缩当前上下文，并给我一个可复制的新对话恢复包。`
- `用 $project-assistant 生成恢复包，包含恢复、进展、继续执行并验证的命令。`
- `Use $project-assistant to compress the current context and emit a resume pack for the next thread.`
- `project assistant handoff`

## Record a Development Log | 记录开发日志

- `项目助手 开发日志`
- `用 $project-assistant 记录一条开发日志，写清楚问题、思考、解决方案和验证结果。`
- `Use $project-assistant to record a development log with the problem, thinking path, chosen solution, and validation.`
- `project assistant devlog`

## Retrofit an Existing Repo | 整改现有仓库

- `项目助手 整改`
- `项目助手 文档整改`
- `项目助手 文档整理`
- `项目助手 架构 整改`
- `project assistant retrofit`
- `project assistant docs retrofit`
- `project assistant architecture retrofit`
- `project assistant docs retrofit all markdown`
- `用 $project-assistant 对这个仓库做整改审计（retrofit audit），先不要改文件。`
- `用 $project-assistant 审计这个仓库并给出 retrofit plan，先不要改文件。`
- `用 $project-assistant 引导式整改这个仓库，先审计、再给方案、再实施。`
- `用 $project-assistant 直接整改这个仓库，按最小安全改动补齐规范。`
- `用 $project-assistant 整改这个仓库，按当前最新规范自动补齐到目标结构。`
- `用 $project-assistant 整改这个仓库的文档系统，按最新文档规范一次性收敛。`
- `用 $project-assistant 整改这个仓库的全部 Markdown，按最新治理规则一次性收敛。`
- `用 $project-assistant 整改这个仓库，一次性补齐到最新版规范，不要停在中间状态。`
- `用 $project-assistant 整改这个仓库，并通过控制面校验和文档校验后再结束。`
- `用 $project-assistant 文档整改这个仓库，并通过全仓 Markdown 门禁后再结束。`
- `用 $project-assistant 文档整理这个仓库，并把缺失的 Stage -> development plan 链接一起补齐。`
- `用 $project-assistant 文档整改这个仓库，建立 roadmap -> development plan -> 详细执行队列 这条维护者文档链。`
- `用 $project-assistant 把这个大项目整改到模块视角，补 module dashboard 和 modules 状态文件。`
- `用 $project-assistant 先做架构整改，生成架构整改工作底稿，再按它来切执行线。`
- `用 $project-assistant 整改这个仓库，并通过脚本校验后再结束。`
- `Use $project-assistant to align this repo to the operating model and apply the minimum safe changes.`

## Release | 发布

- `项目助手 发布 patch`
- `项目助手 发布 minor`
- `项目助手 打标 patch`
- `用 $project-assistant 发布这个 skill，并更新 tag 安装地址。`
- `project assistant release patch`
- `project assistant release minor`

默认语义：

- 更新 `VERSION`
- 更新中英 README 的安装地址
- 更新 `install.sh`
- 创建 release commit 和 tag

默认规则：

- `整改` = 控制面整改 + 文档整改 + 全仓 Markdown 治理
- `文档整改` / `文档整理` = 先补控制面，再做文档系统和全仓 Markdown 治理
- `执行` = 默认进入一个有检查点的长任务执行线，而不是每做一点就等用户输入继续
- `继续` = 默认先按 `.codex/control-surface.json` 版本自动判断是否需要最小控制面升级；如果需要，先自动补齐，再继续当前执行线
- `执行线` = 一个和 active slice 明确映射的任务板，不只是抽象一句话
- 任务列表优先 = 识别到的长任务、整改任务、并行安全 sidecar 任务，都应尽量展开成可见任务板，而不是只写成一段 prose
- 并行任务展示 = 如果某个任务被识别为并行安全，应在同一块任务板里用 `并行:` / `parallel:` 标出来，让用户一眼看出哪些任务在并行运行
- `架构监督状态` = 和执行线并排存在的高层判断面，至少包含 signal、root cause、correct layer、escalation gate
- `自动架构信号更新` = 用 `sync_architecture_supervision.py` 从当前执行线、blockers 和升级状态推导 signal / gate / next review trigger
- `升级模型` = `continue automatically / raise but continue / require user decision`
- `可用能力快照` = 用最短列表告诉用户“现在已经能用什么”，不只汇报还在开发什么
- `sync_execution_line.py` = 把 active slice 自动展开成更长、更可视的任务板
- 长任务提示 = 在整改、架构整改、继续、长执行线这类长任务中，应持续用简短进度话术告诉用户“现在在做什么 / 刚发现什么 / 下一检查点是什么”
- `release` profile = `deep` 加 `release readiness`，用于本地发布和更严格的 CI 保护
- `.codex/doc-governance.json` = 文档治理配置入口，用来声明公开文档范围、根目录保留文档和 Markdown 所有权
- `deep` 现在还会检查 `.codex/*` 是否仍然停留在模板态
- `开发日志` = 把值得长期保留的问题、思考路径、解决方案和验证过程沉淀到 `docs/devlog/*.md`
- `架构监督` = 默认内嵌在 `plan / execute / retrofit / closeout` 中，人工命令只是覆盖窗口
- 如果项目要求公开文档双语，则整改还应补齐中英文可切换文档对
- 如果仓库仍有 legacy 深层文档树，整改应把它们迁入 `docs/reference/`、`docs/workstreams/` 或 `docs/archive/`
- 完成前还应通过 `validate_doc_quality.py`，避免公开文档停留在模板态、假双语或坏链接状态
- 日常迭代优先跑 `fast` 门禁；整改收口和发布前必须跑 `deep` 门禁
- 发布前还应通过 `validate_release_readiness.py`

## Close a Phase | 阶段收口

- `用 $project-assistant 收口当前阶段，更新状态，并告诉我下一阶段入口条件。`
- `Use $project-assistant to close the current phase and prepare the next entry criteria.`

## Ask with Only Chinese | 只用中文也可以

- `项目助手 菜单`
- `项目助手 帮助`
- `启动这个项目`
- `规划下一阶段`
- `继续`
- `告诉我项目进展`
- `先做整改审计`
- `直接整改这个仓库`
- `文档整改`
- `文档整理`
- `收口当前阶段`
- `压缩当前上下文`
- `生成恢复包`
- `给我新对话恢复指令`
- `项目助手 架构`

## Best Memory Shortcut | 最好记的用法

只记这一句就够了：

- `项目助手 菜单`

之后从菜单里选，或者直接自然语言描述你的意图。

## Simple Rule

If the user gives only direction, Codex should:

1. classify the tier
2. create or refresh the control surface
3. choose the next slice
4. continue execution
