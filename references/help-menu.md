# Help Menu

Use this reference when the user asks for help, menu, available commands, or what this skill can do.

## Preferred Trigger

Prefer the alias:

- `项目助手`
- `project assistant`

Common help requests:

- `项目助手 菜单`
- `项目助手 帮助`
- `项目助手 你能做什么`
- `项目助手 怎么用`
- `项目助手 架构`

## Default Menu Shape

If the user is writing in Chinese, return a Chinese-first menu.

If the user is writing in English, return an English-first menu.

Chinese menu:

```md
项目助手可用命令：

- 启动（bootstrap）：建立项目控制面
- 规划（plan）：明确目标、阶段、切片、测试
- 执行（execute）：按当前切片推进实现
- 恢复（resume）：恢复当前状态并继续
- 进展（progress）：查看全局/子项目进展
- 整改（retrofit）：把现有项目补齐到规范
- 开发日志（devlog）：记录重要问题、思考和解决方案
- 架构（architecture）：进入架构监督与复盘子命令
- 收口（closeout）：结束当前阶段并准备下一阶段

最常用：
- 如果不确定从哪里开始，用 `项目助手 菜单`
- 如果怀疑实现方向可能偏了，用 `项目助手 架构 监督`

默认工作方式：
- 你主要给需求和业务方向
- 项目助手默认会自己规划、监督、执行、验证，并在检查点再回来汇报

示例：
- 项目助手 启动这个项目
- 项目助手 告诉我项目进展
- 项目助手 先做整改审计

不需要记精确名字，直接用自然语言也可以。
```

English menu:

```md
Project Assistant commands:

- start: create the control surface
- plan: clarify goals, slices, and validation
- execute: continue the active slice
- resume: recover state and continue
- progress: show global or module progress
- retrofit: align the repo to the operating model
- docs retrofit: normalize the doc system
- devlog: record a durable development note
- architecture: open architecture supervision subcommands
- handoff: prepare a new-thread resume pack

Most common:
- If you are unsure where to start, use `project assistant menu`
- If you suspect the implementation direction is drifting, use `project assistant architecture review`

Default working style:
- you mainly provide business direction
- Project Assistant should usually plan, supervise, execute, validate, and return at checkpoints on its own

Examples:
- project assistant start this project
- project assistant progress
- project assistant retrofit

You do not need to memorize exact names. Natural language is fine.
```

Architecture submenu:

```md
项目助手 架构 子命令：

- 最常用：`项目助手 架构 监督`
  什么时候用：准备开始改代码前，或者你怀疑 AI 正在为了当前需求走捷径
- 项目助手 架构 复盘
  什么时候用：一个 slice、一个阶段或一轮 bugfix 完成后，想看方向有没有漂
- 项目助手 架构 根因
  什么时候用：你感觉在“修一个又冒一个”，想先判断根因是否判断错层了
- 项目助手 架构 扩展性
  什么时候用：准备加抽象、接口、模块边界或复用机制时，先看扩展路径是否合理

English:
- Most common: `project assistant architecture review`
  When to use: before implementation, or when the solution feels too local or shortcut-heavy
- project assistant architecture retrospective
  When to use: after a slice, phase, or bugfix round to check whether the direction drifted
- project assistant architecture root-cause
  When to use: when fixes keep cascading and you want to test whether the real cause is elsewhere
- project assistant architecture extensibility
  When to use: before adding abstractions, interfaces, or reusable mechanisms
```

## Concision Rule

- keep it under about 12 lines when possible
- do not dump the full skill design
- optimize for quick recall, not completeness
