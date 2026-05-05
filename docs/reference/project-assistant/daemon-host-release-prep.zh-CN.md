# Daemon-Host Release Prep

[English](daemon-host-release-prep.md) | [中文](daemon-host-release-prep.zh-CN.md)

## 决策

`v0.1.9` 仍然是最后一个不可变稳定 tag。当前 daemon-host / PTL-loop baseline 只是 mainline release candidate，直到后续真正生成 release commit 和 tag。

不要把 `v0.1.9` 描述成已经包含当前 mainline-only 行为。`v0.1.9` tag 里已有 daemon-host 壳，但它自带的安装脚本默认仍安装旧的 `Workspace Doc Browser`；它不包含当前分支里的 PTL learning review、message ingress loop、completion gate、task pipeline 细化、Codex App loop hook 等新工作。

## 安装路径

上一版稳定发布：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.9/install.sh | bash
```

从 mainline 安装 daemon-host / PTL-loop release candidate：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_AUTO_VSCODE_COMPONENTS=project-assistant-host bash
```

只从 mainline 安装 host：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install-vscode-tools.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash
```

## `v0.1.9` 之后的 mainline delta

当前 `HEAD` 在这轮未提交 PTL-loop 工作之前，比 `v0.1.9` 多 7 个提交：

- 支持 workspace 外 Markdown 文档预览
- 给 workspace doc browser 增加图片预览
- 扩展项目文档，并改进 workspace doc browser routing / previews
- 给 workspace doc browser 增加 session reuse 和 self-reload
- 增加 workspace docs 的 Finder quick action
- 从 `project-assistant` 移除 browser preview integration

当前工作树又在此基础上增加 daemon-host / PTL-loop release-candidate 层：PTL learning review、task pipeline diagnostics、message ingress、completion gate、Codex App loop hook、Codex CLI wrapper，以及 install-ref validation。

## 发布门禁

生成新的不可变 tag 前：

1. 先提交当前 release-candidate changes。
2. 运行 `python3 scripts/validate_gate_set.py . --profile release`。
3. 然后再运行 `python3 scripts/release_skill.py patch` 或等价的 `项目助手 发布 patch` / `project assistant release patch`。

`scripts/validate_install_scripts.py` 已经进入 fast gate，因此 tag 和 branch/mainline 安装路径会在 release 前被自动验证。

## 当前边界

本文档只是准备 release 路径，本身不会创建新 tag。在新的 tag 存在前，需要当前 daemon-host / PTL-loop 行为的用户应使用 mainline release-candidate 命令，而不是 `v0.1.9` 稳定命令。
