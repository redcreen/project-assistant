# Project Assistant

[English](README.md) | [中文](README.zh-CN.md)

> A Codex skill for project planning, retrofit, progress reporting, development logging, documentation governance, and context handoff.

## Who This Is For

- Teams or solo developers who want Codex to drive delivery with a stable operating rhythm
- Repositories that need recoverable status, convergent retrofit, and readable docs
- Projects where current phase, next step, and change visibility must stay clear across sessions

## Install

One-line install from a stable tag:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.1/install.sh | bash
```

Manual install:

```bash
git clone --branch v0.1.1 https://github.com/redcreen/project-assistant.git ~/.codex/skills/project-assistant
```

## Minimal Configuration

No extra configuration is required.

Simplest path:

1. install to `~/.codex/skills/project-assistant`
2. start a new Codex session
3. run `project assistant menu`

Optional overrides:

```bash
PROJECT_ASSISTANT_REF=v0.1.1 PROJECT_ASSISTANT_DIR="$HOME/.codex/skills/project-assistant" bash install.sh
```

## Quick Start

Use one simple entry:

- `project assistant`

Common commands:

- `project assistant menu`
- `project assistant start this project`
- `project assistant architecture`
- `project assistant resume current status`
- `project assistant progress`
- `project assistant retrofit`
- `project assistant docs retrofit`
- `project assistant devlog`
- `project assistant handoff`

## Core Capabilities

- Create and maintain `.codex` control surfaces
- Maintain `.codex/doc-governance.json` as the Markdown-governance contract
- Plan work in verifiable slices
- Turn the active slice into a checkpoint-based long execution line instead of waiting for repeated "continue" prompts
- Show that execution line as a visible task board with done/total progress and a `Plan Link` back to the active slice
- Retrofit existing repos to convergence
- Report progress with global and module views
- Capture durable implementation reasoning as development logs
- Normalize durable docs into a standard system
- Emit a compact context handoff for the next thread

## Common Workflows

Default working style:

- you mainly provide business direction, priorities, and hard constraints
- `project-assistant` should usually plan, supervise, implement, validate, refresh status, and capture devlogs on its own
- it should only stop at checkpoints, blockers, or decisions that require user judgment
- its long-run execution should stay visible through an execution-task board, not disappear into free-form status prose

### Start or take over a project

```text
project assistant start this project
```

### Report current progress

```text
project assistant progress
```

### Review the current direction at the architecture level

```text
project assistant architecture
```

Most common:

- `project assistant architecture review`

When to use it:

- before changing code, if you want a higher-level check on the direction
- when the implementation is drifting toward hardcoded shortcuts
- when you want to test the abstraction boundary before adding more code

### Retrofit the whole repo

```text
project assistant retrofit
```

Default scope:

- control-surface retrofit
- documentation retrofit
- full Markdown-tree governance retrofit
- validation gates

### Focus on docs only

```text
project assistant docs retrofit
```

### Record a durable implementation note

```text
project assistant devlog
```

### Prepare a new thread

```text
project assistant handoff
```

## Documentation Map

- [Docs Home](docs/README.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Test Plan](docs/test-plan.md)
- [Development Log](docs/devlog/README.md)
- [ADR Index](docs/adr/README.md)
- [Skill Contract](SKILL.md)
- [References](references/README.md)

## Development

### Repository Layout

```text
project-assistant/
├── .codex/
├── SKILL.md
├── VERSION
├── install.sh
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
- `scripts/sync_markdown_governance.py`
- `scripts/validate_docs_system.py`
- `scripts/validate_public_docs_i18n.py`
- `scripts/validate_markdown_governance.py`
- `scripts/validate_doc_quality.py`
- `scripts/validate_control_surface_quality.py`
- `scripts/validate_gate_set.py`
- `scripts/write_development_log.py`
- `scripts/validate_development_log.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`
- `scripts/release_skill.py`

### Validation

```bash
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/validate_docs_system.py /path/to/repo --format text
python3 scripts/validate_public_docs_i18n.py /path/to/repo --format text
python3 scripts/validate_markdown_governance.py /path/to/repo --format text
python3 scripts/validate_doc_quality.py /path/to/repo --format text
python3 scripts/validate_control_surface_quality.py /path/to/repo --format text
python3 scripts/validate_development_log.py /path/to/repo --format text
python3 scripts/validate_gate_set.py /path/to/repo --profile fast
python3 scripts/validate_gate_set.py /path/to/repo --profile deep
```

### Release

When a feature improvement is stable and validations pass, use a short release command:

```text
project assistant release patch
```

Equivalent script command:

```bash
python3 scripts/release_skill.py patch
```

What it does:

- bump `VERSION`
- update the tag-based install URLs in both README files
- update `install.sh`
- create a release commit
- create a git tag

Short release hint for maintainers:

```text
Ready to release. Run: project assistant release patch
```

## License

Use the repository's chosen license and contribution policy.
