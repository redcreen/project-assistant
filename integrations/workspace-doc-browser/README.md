# Workspace Doc Browser

[English](README.md) | [中文](README.zh-CN.md)

This VS Code companion extension adds a lightweight status-bar doc-browsing tool for local operator workflows:

- `Browse Docs`: open the current workspace in a local browser preview that is optimized for Markdown-heavy repos and cross-file browsing

## Prerequisites

- VS Code 1.100 or newer
- `mkdocs` available on your local `PATH`

## Install

One-line install from the stable tag:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.6/install-vscode-tools.sh | PROJECT_ASSISTANT_VSCODE_COMPONENTS=workspace-doc-browser bash
```

Install from the current checkout:

```bash
PROJECT_ASSISTANT_VSCODE_COMPONENTS=workspace-doc-browser bash install-vscode-tools.sh
```

Manual local-source fallback:

```bash
mkdir -p ~/.vscode/extensions/redcreen.workspace-doc-browser-0.0.1
cp -R integrations/workspace-doc-browser/. ~/.vscode/extensions/redcreen.workspace-doc-browser-0.0.1/
```

Then in VS Code run:

```text
Developer: Restart Extension Host
```

## What You Get

- a left-side status-bar button: `Browse Docs`
- a local browser preview for the current workspace

## Notes

- the extension is a local operator add-on and is not packaged as a Marketplace release yet
- after updating the source, copy it again and restart the extension host
