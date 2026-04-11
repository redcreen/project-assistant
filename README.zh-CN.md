# Project Assistant

[English](README.md) | [中文](README.zh-CN.md)

> 一个用于项目规划、整改收敛、进展汇报、文档治理和上下文交接的 Codex skill。

## 适用对象

- 想让 Codex 按稳定节奏推进交付的团队或个人
- 需要可恢复状态、可收敛整改、可读文档的仓库
- 需要在多轮会话里始终看清当前阶段、下一步和变化点的项目

## 安装

通过稳定 tag 一键安装：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.1/install.sh | bash
```

手动安装：

```bash
git clone --branch v0.1.1 https://github.com/redcreen/project-assistant.git ~/.codex/skills/project-assistant
```

## 最简配置

不需要额外配置。

最简单的方式：

1. 安装到 `~/.codex/skills/project-assistant`
2. 新开一个 Codex 会话
3. 执行 `项目助手 菜单`

可选覆盖：

```bash
PROJECT_ASSISTANT_REF=v0.1.1 PROJECT_ASSISTANT_DIR="$HOME/.codex/skills/project-assistant" bash install.sh
```

## 快速开始

只需要记住一个入口：

- `项目助手`

常用命令：

- `项目助手 菜单`
- `项目助手 启动这个项目`
- `项目助手 恢复当前状态`
- `项目助手 进展`
- `项目助手 整改`
- `项目助手 文档整改`
- `项目助手 压缩上下文`

## 核心能力

- 创建并维护 `.codex` 控制面
- 把工作拆成可验证的切片
- 把现有仓库整改到收敛状态
- 用全局和模块视角汇报进展
- 把 durable 文档整理到统一结构
- 为新对话生成紧凑恢复包

## 常见工作流

### 启动或接管项目

```text
项目助手 启动这个项目
```

### 查看当前进展

```text
项目助手 进展
```

### 整体整改仓库

```text
项目助手 整改
```

默认范围：

- 控制面整改
- 文档整改
- 脚本验收

### 只重点整理文档

```text
项目助手 文档整改
```

### 为新对话做交接

```text
项目助手 压缩上下文
```

## 文档导航

- [文档首页](docs/README.zh-CN.md)
- [架构](docs/architecture.zh-CN.md)
- [路线图](docs/roadmap.zh-CN.md)
- [测试计划](docs/test-plan.zh-CN.md)
- [ADR 索引](docs/adr/README.zh-CN.md)
- [Skill 契约](SKILL.md)
- [参考规则](references/)

## 开发

### 仓库结构

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

### 关键脚本

- `scripts/sync_control_surface.py`
- `scripts/validate_control_surface.py`
- `scripts/sync_docs_system.py`
- `scripts/validate_docs_system.py`
- `scripts/validate_public_docs_i18n.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`
- `scripts/release_skill.py`

### 验收

```bash
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/validate_docs_system.py /path/to/repo --format text
python3 scripts/validate_public_docs_i18n.py /path/to/repo --format text
```

### 发布

当功能改进已经稳定并且验收通过后，用最短命令发布：

```text
项目助手 发布 patch
```

对应脚本命令：

```bash
python3 scripts/release_skill.py patch
```

它会自动：

- 更新 `VERSION`
- 更新中英 README 里的 tag 安装地址
- 更新 `install.sh`
- 创建 release commit
- 创建 git tag

给维护者的最短提示：

```text
可发布。执行：项目助手 发布 patch
```

## 许可

使用仓库约定的 license 与贡献规则。
