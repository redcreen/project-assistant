# Help Menu

Use this reference when the user asks for help, menu, available commands, or what this skill can do.

## Preferred Trigger

Prefer the alias:

- `项目助手`

Common help requests:

- `项目助手 菜单`
- `项目助手 帮助`
- `项目助手 你能做什么`
- `项目助手 怎么用`

## Default Menu Shape

Return a short menu like this:

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

## Concision Rule

- keep it under about 12 lines when possible
- do not dump the full skill design
- optimize for quick recall, not completeness
