# Daemon-Host Release Prep

[English](daemon-host-release-prep.md) | [中文](daemon-host-release-prep.zh-CN.md)

## Decision

`v0.1.9` remains the last immutable stable tag. The current daemon-host/PTL-loop baseline is a mainline release candidate until a new release commit and tag are cut.

Do not describe `v0.1.9` as containing current mainline-only behavior. The `v0.1.9` tag has the daemon-host shell, but its bundled installer still defaults to the older `Workspace Doc Browser`; it does not include the current PTL learning review, message ingress loop, completion gate, task pipeline refinements, or Codex App loop hook work from this branch.

## Install Paths

Stable previous release:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.10/install.sh | bash
```

Daemon-host/PTL-loop release candidate from mainline:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_AUTO_VSCODE_COMPONENTS=project-assistant-host bash
```

Mainline host-only install:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install-vscode-tools.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash
```

## Mainline Delta Since `v0.1.9`

The checked-out `HEAD` is seven commits past `v0.1.9` before the current uncommitted PTL-loop work:

- support docs preview for Markdown outside the workspace
- add image previews to the workspace doc browser
- expand project docs and improve workspace doc browser routing/previews
- add session reuse and self-reload to the workspace doc browser
- add a Finder quick action for workspace docs
- remove browser preview integration from `project-assistant`

The current working tree then adds the daemon-host/PTL-loop release-candidate layer: PTL learning review, task pipeline diagnostics, message ingress, completion gate, Codex App loop hook, Codex CLI wrapper, and install-ref validation.

## Release Gate

Before cutting a new immutable tag:

1. Commit the current release-candidate changes.
2. Run `python3 scripts/validate_gate_set.py . --profile release`.
3. Only then run `python3 scripts/release_skill.py patch` or the equivalent `project assistant release patch`.

`scripts/validate_install_scripts.py` is now part of the fast gate so tag and branch/mainline install paths are tested before release.

## Current Boundary

This document prepares the release path; it does not itself create a new tag. Until a new tag exists, users who need the current daemon-host/PTL-loop behavior should use the mainline release-candidate command, not the `v0.1.9` stable command.
