# Workspace Doc Browser

[English](README.md) | [中文](README.zh-CN.md)

这是一个面向 VS Code 的轻量状态栏扩展，主要补本地文档浏览能力：

- `Browse Docs`：把当前工作区用接近 GitHub 的方式在浏览器里打开，适合多 Markdown 文档串联阅读

## 前置条件

- VS Code 1.100 或更新版本

## 安装

稳定 tag 一键安装：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.8/install-vscode-tools.sh | PROJECT_ASSISTANT_VSCODE_COMPONENTS=workspace-doc-browser bash
```

从当前源码目录安装：

```bash
PROJECT_ASSISTANT_VSCODE_COMPONENTS=workspace-doc-browser bash install-vscode-tools.sh
```

本地源码手动安装备用方式：

```bash
mkdir -p ~/.vscode/extensions/redcreen.workspace-doc-browser-0.0.1
cp -R integrations/workspace-doc-browser/. ~/.vscode/extensions/redcreen.workspace-doc-browser-0.0.1/
```

然后在 VS Code 里执行：

```text
Developer: Restart Extension Host
```

## 安装后会得到什么

- 状态栏左侧的 `Browse Docs` 按钮
- 当前工作区的实时浏览器文档预览
- Markdown 链接继续按 Markdown 页面渲染，而不是退回原始 `.md` 文件
- 非 Markdown 文件也会继续出现在左侧文件树里，并通过本地预览后端打开

## 补充说明

- 这是本地 operator 工具，还没有打成 Marketplace release
- 现在走的是轻量本地实时预览后端，不依赖 `mkdocs`
- 如果你更新了源码，重新复制一次并重启 `Extension Host` 即可
