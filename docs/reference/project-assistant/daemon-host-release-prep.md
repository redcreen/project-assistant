# Daemon-Host Release Prep

[English](daemon-host-release-prep.md) | [中文](daemon-host-release-prep.zh-CN.md)

## Decision

The daemon-host/PTL-loop baseline has been cut as an immutable release tag. Use the current stable install command for normal installation.

`v0.1.9` remains the previous docs-browser-era release. Do not describe `v0.1.9` as containing PTL learning review, message ingress loop, completion gate, task pipeline refinements, or Codex App loop hook behavior.

## Install Paths

Current stable release:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.11/install.sh | bash
```

Mainline development install:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_AUTO_VSCODE_COMPONENTS=project-assistant-host bash
```

Mainline host-only development install:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install-vscode-tools.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash
```

## Release Delta Since `v0.1.9`

The daemon-host/PTL-loop release includes the earlier post-`v0.1.9` docs-browser work:

- support docs preview for Markdown outside the workspace
- add image previews to the workspace doc browser
- expand project docs and improve workspace doc browser routing/previews
- add session reuse and self-reload to the workspace doc browser
- add a Finder quick action for workspace docs
- remove browser preview integration from `project-assistant`

It also adds the daemon-host/PTL-loop baseline: PTL learning review, task pipeline diagnostics, message ingress, completion gate, Codex App loop hook, Codex CLI wrapper, semantic learning candidates, cross-project dogfood evidence, and install-ref validation.

## Release Gate

For future immutable tags:

1. Commit the current release-candidate changes.
2. Run `python3 scripts/validate_gate_set.py . --profile release`.
3. Only then run `python3 scripts/release_skill.py patch` or the equivalent `project assistant release patch`.

`scripts/validate_install_scripts.py` is now part of the fast gate so tag and branch/mainline install paths are tested before release.

## Current Boundary

Use the current stable tag for daemon-host/PTL-loop behavior. Use `main` only when intentionally testing unreleased development changes.
