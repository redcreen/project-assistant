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
- 收口（closeout）：结束当前阶段并准备下一阶段

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
- handoff: prepare a new-thread resume pack

Examples:
- project assistant start this project
- project assistant progress
- project assistant retrofit

You do not need to memorize exact names. Natural language is fine.
```

## Concision Rule

- keep it under about 12 lines when possible
- do not dump the full skill design
- optimize for quick recall, not completeness
