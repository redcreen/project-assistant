# Usage

Use these prompt patterns to invoke the skill cleanly.

## Simple Commands | 简单指令

- 推荐总入口：`项目助手`
- Recommended English entry: `project assistant`
- `启动` = `bootstrap`
- `规划` = `plan`
- `执行` = `execute`
- `恢复` = `resume`
- `进展` = `progress`
- `整改` = `retrofit`
- `文档整改` = `docs-retrofit`
- `发布` = `release`
- `收口` = `closeout`
- `压缩上下文 / 交接` = `handoff`

English simple commands:

- `project assistant menu`
- `project assistant start this project`
- `project assistant plan the next phase`
- `project assistant resume current status`
- `project assistant progress`
- `project assistant retrofit`
- `project assistant docs retrofit`
- `project assistant handoff`
- `project assistant release patch`

Gate commands:

- `python3 scripts/validate_gate_set.py /path/to/repo --profile fast`
- `python3 scripts/validate_gate_set.py /path/to/repo --profile deep`

## Start or Bootstrap | 启动

- `用 $project-assistant 启动这个项目，先明确目标、约束、DoD，再生成最小控制面。`
- `Use $project-assistant to bootstrap this repo and create brief/plan/status.`

## Plan a Feature or Phase | 规划阶段/功能

- `用 $project-assistant 规划这个阶段，判断规模，并给出 architecture / roadmap / test-plan 是否需要。`
- `Use $project-assistant to break this feature into slices and define validation first.`

## Resume Work | 恢复工作

- `用 $project-assistant 恢复当前项目状态，然后继续下一步。`
- `Use $project-assistant to resume this repo from the current status and continue execution.`
- `project assistant resume current status`

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

## Retrofit an Existing Repo | 整改现有仓库

- `项目助手 整改`
- `项目助手 文档整改`
- `project assistant retrofit`
- `project assistant docs retrofit`
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
- `用 $project-assistant 把这个大项目整改到模块视角，补 module dashboard 和 modules 状态文件。`
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
- `文档整改` = 先补控制面，再做文档系统和全仓 Markdown 治理
- `.codex/doc-governance.json` = 文档治理配置入口，用来声明公开文档范围、根目录保留文档和 Markdown 所有权
- 如果项目要求公开文档双语，则整改还应补齐中英文可切换文档对
- 如果仓库仍有 legacy 深层文档树，整改应把它们迁入 `docs/reference/`、`docs/workstreams/` 或 `docs/archive/`
- 完成前还应通过 `validate_doc_quality.py`，避免公开文档停留在模板态、假双语或坏链接状态
- 日常迭代优先跑 `fast` 门禁；整改收口和发布前必须跑 `deep` 门禁

## Close a Phase | 阶段收口

- `用 $project-assistant 收口当前阶段，更新状态，并告诉我下一阶段入口条件。`
- `Use $project-assistant to close the current phase and prepare the next entry criteria.`

## Ask with Only Chinese | 只用中文也可以

- `项目助手 菜单`
- `项目助手 帮助`
- `启动这个项目`
- `规划下一阶段`
- `恢复当前状态`
- `告诉我项目进展`
- `先做整改审计`
- `直接整改这个仓库`
- `文档整改`
- `收口当前阶段`
- `压缩当前上下文`
- `生成恢复包`
- `给我新对话恢复指令`

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
