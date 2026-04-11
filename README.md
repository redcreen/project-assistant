# Project Assistant

[English](README.md) | [中文](README.zh-CN.md)

> A Codex skill for project planning, retrofit, progress reporting, documentation governance, and context handoff.

## Who This Is For

- Teams or solo developers who want Codex to drive delivery with a stable operating rhythm
- Repositories that need recoverable status, convergent retrofit, and readable docs
- Projects where “current phase”, “next step”, and “what changed” must stay clear across sessions

## Quick Start

Use one simple entry:

- `项目助手`

Common commands:

- `项目助手 菜单`
- `项目助手 启动这个项目`
- `项目助手 恢复当前状态`
- `项目助手 进展`
- `项目助手 整改`
- `项目助手 文档整改`
- `项目助手 压缩上下文`

## Core Capabilities

- Create and maintain `.codex` control surfaces
- Plan work in verifiable slices
- Retrofit existing repos to convergence
- Report progress with global and module views
- Normalize durable docs into a standard system
- Emit a compact context handoff for the next thread

## Common Workflows

### Start or take over a project

```text
项目助手 启动这个项目
```

### Report current progress

```text
项目助手 进展
```

### Retrofit the whole repo

```text
项目助手 整改
```

Default scope:

- control-surface retrofit
- documentation retrofit
- validation gates

### Focus on docs only

```text
项目助手 文档整改
```

### Prepare a new thread

```text
项目助手 压缩上下文
```

## Documentation Map

- [Docs Home](docs/README.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Test Plan](docs/test-plan.md)
- [ADR Index](docs/adr/README.md)
- [Skill Contract](SKILL.md)
- [References](references/)

## Development

### Repository Layout

```text
project-assistant/
├── .codex/
├── SKILL.md
├── README.md
├── README.zh-CN.md
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
- `scripts/validate_public_docs_i18n.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`

### Validation

```bash
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/validate_docs_system.py /path/to/repo --format text
python3 scripts/validate_public_docs_i18n.py /path/to/repo --format text
```

## License

Use the repository's chosen license and contribution policy.
