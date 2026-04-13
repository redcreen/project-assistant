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
项目助手主窗口：

- 进展（progress）：查看全局/子项目进展
- 架构（architecture）：进入架构监督与复盘子命令
- 开发日志（devlog）：记录重要问题、思考和解决方案
- 菜单（menu）：查看入口与当前人工窗口
- 统一前门（tool-first front door）：`启动 / 整改 / 文档整改 / 继续 / 进展 / 交接` 先走同一条前门，再输出事务化结果或结构化面板

后台流程（通常自动运行，不必频繁手工调用）：
- 启动（bootstrap）
- 规划（plan）
- 执行（execute）
- 继续（continue / resume）
- 整改（retrofit）
- 收口（closeout）：结束当前阶段并准备下一阶段

最常用：
- 如果不确定从哪里开始，用 `项目助手 菜单`
- 如果怀疑实现方向可能偏了，用 `项目助手 架构 监督`

默认工作方式：
- 你主要给需求和业务方向
- 项目助手默认会自己规划、监督、执行、验证，并在检查点再回来汇报
- 进展和恢复默认会带一个“现在可用能力”快照，避免只看到还在开发什么
- `继续 / 进展 / 交接` 的第一屏应来自统一前门，不该先掉回自由 prose

示例：
- 项目助手 启动这个项目
- 项目助手 继续
- 项目助手 告诉我项目进展
- 项目助手 先做整改审计

不需要记精确名字，直接用自然语言也可以。
```

English menu:

```md
Project Assistant primary windows:

- progress: show global or module progress
- architecture: open architecture supervision subcommands
- devlog: record a durable development note
- menu: show the human-facing windows

Background flows (usually automatic):
- start
- plan
- execute
- continue
- retrofit
- closeout

Most common:
- If you are unsure where to start, use `project assistant menu`
- If you suspect the implementation direction is drifting, use `project assistant architecture review`

Default working style:
- you mainly provide business direction
- Project Assistant should usually plan, supervise, execute, validate, and return at checkpoints on its own
- it should keep architecture signal and escalation gate visible instead of hiding higher-level judgment inside free-form notes
- progress and handoff should also show what is usable now, not only what is still in progress
- `bootstrap / retrofit / continue / progress / handoff` should share one front door and a structured first screen instead of falling back to free-form orchestration or prose

Examples:
- project assistant start this project
- project assistant continue
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
- 项目助手 架构 整改
  什么时候用：边界、状态流或抽象整体错位，已经不是局部 review 能解决，而要直接做系统性架构收敛

English:
- Most common: `project assistant architecture review`
  When to use: before implementation, or when the solution feels too local or shortcut-heavy
- project assistant architecture retrospective
  When to use: after a slice, phase, or bugfix round to check whether the direction drifted
- project assistant architecture root-cause
  When to use: when fixes keep cascading and you want to test whether the real cause is elsewhere
- project assistant architecture extensibility
  When to use: before adding abstractions, interfaces, or reusable mechanisms
- project assistant architecture retrofit
  When to use: when boundaries, state flow, or abstractions are wrong at a system level and the repo needs an architecture-first retrofit that should actually land
```

## Concision Rule

- keep it under about 12 lines when possible
- do not dump the full skill design
- optimize for quick recall, not completeness
