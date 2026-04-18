# Project Assistant

[English](README.md) | [中文](README.zh-CN.md)

> A Codex skill for running real repository work with less drift and less repeated context loading.  
> It helps keep planning, execution, progress, docs, and handoff aligned so a repo can stay operable across long sessions and thread switches.

## What You Can Use It For

- take over an existing repo without losing the current truth
- let Codex keep plan, status, progress, docs, and handoff aligned while work moves
- retrofit messy repos until docs, control surfaces, and validation agree again
- keep long-running work recoverable across sessions instead of restarting from scratch
- use lightweight VS Code operator surfaces when you want live status and browser-based doc reading

## Best Fit

- you use Codex repeatedly on the same repo
- you want the assistant to plan, implement, validate, and update repo state by default
- you need recoverable progress across sessions, not one-off prompt output
- you care about durable docs, checkpoints, and handoff quality

If you only need a tiny one-file helper or a throwaway prompt, this skill is probably heavier than you need.

## Install

Safe tagged install:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.6/install.sh | bash
```

That install now auto-installs `Workspace Doc Browser` into `~/.vscode/extensions` by default.

Manual install from the stable tag:

```bash
git clone --branch v0.1.6 https://github.com/redcreen/project-assistant.git ~/.codex/skills/project-assistant
```

If you want the newest VS Code and daemon-host tooling, install from the repository mainline instead of the old stable tag.

## Minimal Configuration

No extra configuration is required.

## Quick Start

Recommended first steps:

1. install to `~/.codex/skills/project-assistant`
2. open the repo you want to work on
3. if the repo is new, run `project assistant start this project`
4. if the repo already has state, run `project assistant continue`
5. use `project assistant progress` whenever you want the current picture
6. use `project assistant handoff` before switching threads

Optional install overrides:

```bash
PROJECT_ASSISTANT_REF=v0.1.6 PROJECT_ASSISTANT_DIR="$HOME/.codex/skills/project-assistant" bash install.sh
```

Disable the automatic VS Code docs plugin install:

```bash
PROJECT_ASSISTANT_AUTO_VSCODE_COMPONENTS=none bash install.sh
```

## Commands You Will Actually Use

- `project assistant`: open the main menu
- `project assistant start this project`: bootstrap or take over a repo
- `project assistant continue`: resume the current execution line
- `project assistant progress`: get a progress snapshot
- `project assistant retrofit`: converge the whole repo
- `project assistant docs retrofit`: clean up docs only
- `project assistant architecture retrofit`: fix boundary and abstraction drift first
- `project assistant devlog`: persist one conclusion worth keeping
- `project assistant handoff`: build the next-thread handoff pack

If you use the host or daemon workflow, the most common background commands are:

- `project-assistant daemon start`
- `project-assistant queue`

## VS Code Status Bar Tools

If VS Code is your daily operator surface, there are two companion extensions that make this much easier:

- `Project Assistant Host` in [integrations/vscode-host](integrations/vscode-host/README.md): activity-bar workspace control plus a status-bar summary for daemon state and resume readiness
- `Workspace Doc Browser` in [integrations/workspace-doc-browser](integrations/workspace-doc-browser/README.md) and [中文说明](integrations/workspace-doc-browser/README.zh-CN.md): a `Browse Docs` status-bar button for GitHub-like local browser preview, plus a `Codex Context Meter` on the right side of the status bar

One-line install from the stable tag:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.6/install-vscode-tools.sh | bash
```

Install from the current checkout:

```bash
bash install-vscode-tools.sh
```

Then in VS Code run:

```text
Developer: Restart Extension Host
```

Notes:

- `install.sh` now auto-installs `Workspace Doc Browser` by default so the docs browser is ready right after the main skill install
- `Workspace Doc Browser` requires `mkdocs` on your local `PATH`
- both extensions are local operator add-ons and are not packaged as a Marketplace release yet
- if you only want one extension, run `curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.6/install-vscode-tools.sh | PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash` or replace it with `workspace-doc-browser`
- after updating either extension from source, rerun `bash install-vscode-tools.sh` and restart the extension host

## What It Does For You

- creates and maintains `.codex` control surfaces
- keeps `continue / progress / handoff` aligned with the same current truth
- updates plan, status, and development-log surfaces as work moves
- promotes architecture review automatically when drift shows up
- can run a local daemon, queue, and VS Code host when you want a live operator workflow
- stops mainly at checkpoints, blockers, or decisions that need human judgment

## Current Reality

Already proven on representative repos:

- `project assistant retrofit`
- `project assistant docs retrofit`
- `project assistant architecture retrofit`
- `project assistant progress`
- `project assistant handoff`

Current boundary:

- this is optimized for one durable Codex-led execution line, not general multi-agent orchestration
- the deeper roadmap, milestone, and strategy details live in the docs, not in this README
- if you want the engineering rationale behind the current direction, start from the documentation map below

## Documentation Map

- [Docs Home](docs/README.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Strategic Direction](docs/reference/project-assistant/strategic-planning-and-program-orchestration.md)
- [Orchestration And Entry Model](docs/reference/project-assistant/orchestration-model.md)
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
├── install-vscode-tools.sh
├── README.md
├── README.zh-CN.md
├── docs/
├── agents/
├── references/
└── scripts/
```

### Key Scripts

- `scripts/project_assistant_entry.py`
- `scripts/sync_entry_routing.py`
- `scripts/validate_entry_routing.py`
- `scripts/sync_dogfooding_evidence.py`
- `scripts/validate_dogfooding_evidence.py`
- `scripts/daemon_entry.py`
- `scripts/daemon_runtime.py`
- `scripts/sync_control_surface.py`
- `scripts/validate_control_surface.py`
- `scripts/sync_docs_system.py`
- `scripts/sync_markdown_governance.py`
- `scripts/validate_docs_system.py`
- `scripts/validate_public_docs_i18n.py`
- `scripts/validate_markdown_governance.py`
- `scripts/validate_doc_quality.py`
- `scripts/validate_control_surface_quality.py`
- `scripts/sync_execution_line.py`
- `scripts/sync_architecture_supervision.py`
- `scripts/sync_architecture_retrofit.py`
- `scripts/validate_gate_set.py`
- `scripts/validate_release_readiness.py`
- `scripts/write_development_log.py`
- `scripts/validate_development_log.py`
- `scripts/validate_architecture_retrofit.py`
- `scripts/validate_daemon_runtime.py`
- `scripts/validate_vscode_host_extension.py`
- `scripts/validate_daemon_host_mvp.py`
- `scripts/validate_daemon_legacy_rollout.py`
- `scripts/capability_snapshot.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`
- `scripts/release_skill.py`

### Validation

```bash
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/validate_docs_system.py /path/to/repo --format text
python3 scripts/validate_public_docs_i18n.py /path/to/repo --format text
python3 scripts/validate_entry_routing.py /path/to/repo --format text
python3 scripts/validate_dogfooding_evidence.py /path/to/repo --format text
python3 scripts/validate_markdown_governance.py /path/to/repo --format text
python3 scripts/validate_doc_quality.py /path/to/repo --format text
python3 scripts/validate_control_surface_quality.py /path/to/repo --format text
python3 scripts/validate_development_log.py /path/to/repo --format text
python3 scripts/validate_architecture_retrofit.py /path/to/repo --format text
python3 scripts/validate_daemon_runtime.py /path/to/repo --format text
python3 scripts/validate_vscode_host_extension.py /path/to/repo --format text
python3 scripts/validate_daemon_host_mvp.py /path/to/repo --format text
python3 scripts/validate_daemon_legacy_rollout.py /path/to/repo --format text
python3 scripts/validate_gate_set.py /path/to/repo --profile fast
python3 scripts/validate_gate_set.py /path/to/repo --profile deep
python3 scripts/validate_gate_set.py /path/to/repo --profile release
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

Stricter release protection uses the same gate profile:

```bash
python3 scripts/validate_gate_set.py /path/to/repo --profile release
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
