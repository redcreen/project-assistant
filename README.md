# Project Assistant

> A Codex skill for project planning, retrofit, progress reporting, and context handoff.

## Who This Is For

- 想让 Codex 按稳定流程推进项目的人
- 想把项目状态、模块进展、下一步和文档系统都固定下来的人
- 想避免“每个项目都重新想一次流程”和“做一半后不知道当前在哪”的人

## Quick Start

平时只需要记住一个入口：

- `项目助手`

常用命令：

- `项目助手 菜单`
- `项目助手 启动这个项目`
- `项目助手 恢复当前状态`
- `项目助手 进展`
- `项目助手 整改`
- `项目助手 文档整改`
- `项目助手 压缩上下文`

## Core Capabilities

- 启动项目：建立 `.codex` 控制面
- 规划阶段：明确目标、约束、切片和验证方式
- 整改项目：控制面和文档系统一起收敛
- 汇报进展：输出全局 + 模块 + 图示面板
- 压缩上下文：生成新对话恢复包

## Common Workflows

### 1. 启动或接管项目

```text
项目助手 启动这个项目
```

### 2. 看当前进展

```text
项目助手 进展
```

### 3. 一次性整改仓库

```text
项目助手 整改
```

默认包含：

- 控制面整改
- 文档整改
- 脚本验收

### 4. 只重点整理文档

```text
项目助手 文档整改
```

### 5. 新开对话前交接

```text
项目助手 压缩上下文
```

## Documentation Map

- [Docs Home](docs/README.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Test Plan](docs/test-plan.md)
- [Skill Contract](SKILL.md)
- [References](references/)

## Development

### Repository Layout

```text
project-assistant/
├── .codex/
├── SKILL.md
├── README.md
├── docs/
├── agents/
├── references/
└── scripts/
```

### Key Scripts

- `scripts/sync_control_surface.py`
- `scripts/validate_control_surface.py`
- `scripts/sync_docs_system.py`
- `scripts/validate_docs_system.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`

### Validation

```bash
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/validate_docs_system.py /path/to/repo --format text
```

理想结果：

- 控制面验收通过
- 文档系统验收通过

## License

Use the repository's chosen license and project policy.
