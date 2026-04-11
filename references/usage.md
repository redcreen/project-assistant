# Usage

Use these prompt patterns to invoke the skill cleanly.

## Simple Commands | 简单指令

- 推荐总入口：`项目助手`
- `启动` = `bootstrap`
- `规划` = `plan`
- `执行` = `execute`
- `恢复` = `resume`
- `进展` = `progress`
- `整改` = `retrofit`
- `收口` = `closeout`

## Start or Bootstrap | 启动

- `用 $project-assistant 启动这个项目，先明确目标、约束、DoD，再生成最小控制面。`
- `Use $project-assistant to bootstrap this repo and create brief/plan/status.`

## Plan a Feature or Phase | 规划阶段/功能

- `用 $project-assistant 规划这个阶段，判断规模，并给出 architecture / roadmap / test-plan 是否需要。`
- `Use $project-assistant to break this feature into slices and define validation first.`

## Resume Work | 恢复工作

- `用 $project-assistant 恢复当前项目状态，然后继续下一步。`
- `Use $project-assistant to resume this repo from the current status and continue execution.`

## Ask for Progress | 查看进展

- `用 $project-assistant 告诉我这个项目当前进展，用全局视角、子项目视角和图示输出。`
- `Use $project-assistant to give me a concise progress dashboard with a Mermaid diagram.`

## Retrofit an Existing Repo | 整改现有仓库

- `用 $project-assistant 对这个仓库做整改审计（retrofit audit），先不要改文件。`
- `用 $project-assistant 审计这个仓库并给出 retrofit plan，先不要改文件。`
- `用 $project-assistant 引导式整改这个仓库，先审计、再给方案、再实施。`
- `用 $project-assistant 直接整改这个仓库，按最小安全改动补齐规范。`
- `Use $project-assistant to align this repo to the operating model and apply the minimum safe changes.`

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
- `收口当前阶段`

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
