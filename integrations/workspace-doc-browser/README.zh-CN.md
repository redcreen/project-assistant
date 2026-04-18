# Workspace Doc Browser

[English](README.md) | [中文](README.zh-CN.md)

这是一个面向 VS Code 的轻量状态栏扩展，主要补两类本地操作能力：

- `Browse Docs`：把当前工作区用接近 GitHub 的方式在浏览器里打开，适合多 Markdown 文档串联阅读
- `Codex Context Meter`：在状态栏右侧显示当前 Codex 输入 token 占模型上下文窗口的比例，方便你在上下文过满前提前处理

## 前置条件

- VS Code 1.100 或更新版本
- 本机 `PATH` 里可直接执行 `mkdocs`

## 从本地源码安装

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
- 当前工作区的本地浏览器文档预览
- 状态栏右侧的 `Codex Context Meter`

## 补充说明

- 这是本地 operator 工具，还没有打成 Marketplace release
- 如果你更新了源码，重新复制一次并重启 `Extension Host` 即可
