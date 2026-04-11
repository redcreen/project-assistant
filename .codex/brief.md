# Brief

## Delivery Tier

- Tier: `medium`
- Why this tier: `project-assistant` 是一个会跨多次会话持续演进的 skill 仓库，需要稳定的文档、脚本和状态恢复，但当前不需要 large 项目的模块层控制面。
- Last reviewed: `2026-04-11`

## Outcome

把 `project-assistant` 维护成一个可复用、可收敛、可校验的 Codex 项目操作系统 skill。

## Scope

- 维护 `SKILL.md` 的核心行为协议
- 维护 `references/` 下的规则、模板和使用说明
- 维护 `scripts/` 下的控制面、进展、交接和文档系统脚本
- 保持 skill 自身的 README、docs 和控制面符合当前规范

## Non-Goals

- 不把这个仓库扩成通用网站或文档平台
- 不在这个仓库里维护具体业务项目的事实内容
- 不实现运行时不可获得的硬能力，例如精确 context 占用率读取

## Constraints

- 保持中文优先的用户入口
- 脚本优先处理结构、校验和收敛
- 不允许整改停在中间态
- 文档标准必须与现有脚本门禁一致

## Definition of Done

- skill 规则、模板、脚本三者一致
- `validate_control_surface.py` 对本仓库返回 `ok: True`
- `validate_docs_system.py` 对本仓库返回 `ok: True`
- README、docs 和控制面能让维护者在新会话里快速恢复并继续迭代
