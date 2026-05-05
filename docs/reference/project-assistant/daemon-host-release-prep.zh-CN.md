# Daemon-Host Release Prep

[English](daemon-host-release-prep.md) | [中文](daemon-host-release-prep.zh-CN.md)

## 决策

daemon-host / PTL-loop baseline 已经生成不可变 release tag。正常安装应使用当前稳定安装命令。

`v0.1.9` 保留为上一版 docs-browser 时代 release。不要把 `v0.1.9` 描述成已经包含 PTL learning review、message ingress loop、completion gate、task pipeline 细化或 Codex App loop hook。

## 安装路径

当前稳定发布：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.11/install.sh | bash
```

从 mainline 安装开发版：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_AUTO_VSCODE_COMPONENTS=project-assistant-host bash
```

只从 mainline 安装 host 开发版：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install-vscode-tools.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash
```

## `v0.1.9` 之后的 release delta

daemon-host / PTL-loop release 包含早期 `v0.1.9` 之后的 docs-browser 工作：

- 支持 workspace 外 Markdown 文档预览
- 给 workspace doc browser 增加图片预览
- 扩展项目文档，并改进 workspace doc browser routing / previews
- 给 workspace doc browser 增加 session reuse 和 self-reload
- 增加 workspace docs 的 Finder quick action
- 从 `project-assistant` 移除 browser preview integration

它同时增加 daemon-host / PTL-loop baseline：PTL learning review、task pipeline diagnostics、message ingress、completion gate、Codex App loop hook、Codex CLI wrapper、语义 learning candidates、跨项目 dogfood 证据，以及 install-ref validation。

## 发布门禁

后续生成新的不可变 tag 前：

1. 先提交当前 release-candidate changes。
2. 运行 `python3 scripts/validate_gate_set.py . --profile release`。
3. 然后再运行 `python3 scripts/release_skill.py patch` 或等价的 `项目助手 发布 patch` / `project assistant release patch`。

`scripts/validate_install_scripts.py` 已经进入 fast gate，因此 tag 和 branch/mainline 安装路径会在 release 前被自动验证。

## 当前边界

需要 daemon-host / PTL-loop 行为时使用当前稳定 tag。只有在明确测试未发布开发变更时，才使用 `main`。
