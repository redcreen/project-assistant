# Project Assistant

[English](README.md) | [中文](README.zh-CN.md)

> 一个让 Codex 在真实仓库里少漂移、少反复补上下文的 skill。  
> 它的目标是把规划、执行、进展、文档和交接放在同一套真相里，让仓库在长任务和多轮会话里仍然可恢复、可继续、可维护。

## 你可以用它做什么

- 接管一个已有仓库，同时保住当前真相，不用每次重新摸底
- 让 Codex 在推进实现时，把 plan / status / progress / docs / handoff 一起维护起来
- 把已经发散的仓库重新收敛到“文档、控制面、验证、执行线”一致
- 让长任务跨会话可恢复，而不是每开新线程都从头讲一遍
- 如果你常驻 VS Code，可以直接用状态栏和浏览器文档预览做日常操作

## 适合什么场景

- 你会在同一个仓库里反复使用 Codex
- 你希望 assistant 默认负责规划、实现、验证和状态更新
- 你需要跨会话的可恢复进展，而不是一次性 prompt 输出
- 你在意 durable docs、checkpoint 和交接质量

如果你只是想让 AI 临时写一个很小的一次性脚本，这个 skill 可能偏重了。

## 安装

稳定 tag 一键安装：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.9/install.sh | bash
```

这个安装现在会默认把 `Workspace Doc Browser` 一起装到 `~/.vscode/extensions`。

从稳定 tag 手动安装：

```bash
git clone --branch v0.1.9 https://github.com/redcreen/project-assistant.git ~/.codex/skills/project-assistant
```

如果你想直接用最新的 VS Code / daemon-host 工具链，建议直接安装仓库主线，而不是旧的稳定 tag。

## 最简配置

不需要额外配置。

## 第一次怎么用

推荐第一次这样走：

1. 安装到 `~/.codex/skills/project-assistant`
2. 打开你要工作的仓库
3. 如果仓库是新的，执行 `项目助手 启动这个项目`
4. 如果仓库已经有状态，执行 `项目助手 继续`
5. 想看全局画面时，用 `项目助手 进展`
6. 切线程前，用 `项目助手 压缩上下文`

可选安装覆盖：

```bash
PROJECT_ASSISTANT_REF=v0.1.9 PROJECT_ASSISTANT_DIR="$HOME/.codex/skills/project-assistant" bash install.sh
```

如果你不想自动安装 VS Code 的 docs 插件：

```bash
PROJECT_ASSISTANT_AUTO_VSCODE_COMPONENTS=none bash install.sh
```

## 你实际会用到的命令

- `项目助手`：打开主菜单
- `项目助手 启动这个项目`：初始化或接管仓库
- `项目助手 继续`：继续当前执行线
- `项目助手 进展`：看当前进展快照
- `项目助手 整改`：整体收敛仓库
- `项目助手 文档整改`：只整理文档
- `项目助手 架构 整改`：优先修边界和抽象问题
- `项目助手 开发日志`：沉淀一条值得保留的结论
- `项目助手 压缩上下文`：生成下一线程交接包

如果你用宿主 / daemon 流程，最常见的后台命令是：

- `project-assistant daemon start`
- `project-assistant queue`

## VS Code 状态栏工具

如果你把 VS Code 当作日常主操作面，现在有两套配套扩展可以把体验做轻很多：

- [integrations/vscode-host](integrations/vscode-host/README.md) 里的 `Project Assistant Host`：提供活动栏工作区控制面，以及 daemon 状态 / resume readiness 的状态栏摘要
- [integrations/workspace-doc-browser](integrations/workspace-doc-browser/README.md) 与 [中文说明](integrations/workspace-doc-browser/README.zh-CN.md) 里的 `Workspace Doc Browser`：提供左侧状态栏 `Browse Docs` 按钮，用实时浏览器预览的方式查看 Markdown 密集型仓库

稳定 tag 一键安装：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.9/install-vscode-tools.sh | bash
```

从当前源码目录安装：

```bash
bash install-vscode-tools.sh
```

然后在 VS Code 里执行：

```text
Developer: Restart Extension Host
```

补充说明：

- `install.sh` 现在默认会把 `Workspace Doc Browser` 一起装上，这样主 skill 安装完就能直接用 docs 浏览器
- 这两套扩展目前还是本地 operator 工具，还没有打成 Marketplace release
- 如果你只想装其中一个扩展，可以执行 `curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.9/install-vscode-tools.sh | PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash`，或把它替换成 `workspace-doc-browser`
- 如果你更新了源码，重新执行一次 `bash install-vscode-tools.sh` 并重启 `Extension Host` 即可

## 它会替你做什么

- 创建并维护 `.codex` 控制面
- 让 `继续 / 进展 / 交接` 始终对着同一套当前真相
- 随着工作推进自动更新 plan、status 和 devlog
- 发现 drift 时自动把架构复盘拉上来
- 如果你愿意，也可以配合本地 daemon、queue 和 VS Code host 形成 live operator workflow
- 主要只在 checkpoint、阻塞点和需要人类判断时停下来

## 当前现实边界

已经在代表性仓库上稳定跑通过：

- `项目助手 整改`
- `项目助手 文档整改`
- `项目助手 架构 整改`
- `项目助手 进展`
- `项目助手 压缩上下文`

当前边界也很明确：

- 这套东西现在优化的是“一条 durable 的 Codex 主执行线”，不是通用多 agent 编排平台
- 更深的 roadmap、milestone 和策略叙事放在 docs 里，不放在这个首页 README 里
- 如果你要看工程侧原理和当前方向，直接从下面的文档导航进入

## 文档导航

- [文档首页](docs/README.zh-CN.md)
- [架构](docs/architecture.zh-CN.md)
- [路线图](docs/roadmap.zh-CN.md)
- [战略方向](docs/reference/project-assistant/strategic-planning-and-program-orchestration.zh-CN.md)
- [编排与入口模型](docs/reference/project-assistant/orchestration-model.zh-CN.md)
- [测试计划](docs/test-plan.zh-CN.md)
- [开发日志](docs/devlog/README.zh-CN.md)
- [ADR 索引](docs/adr/README.zh-CN.md)
- [Skill 契约](SKILL.md)
- [参考规则](references/README.zh-CN.md)

## 开发

### 仓库结构

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

### 关键脚本

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
- `scripts/validate_repo_markdown_integrity.py`
- `scripts/nightly_project_audit.py`
- `scripts/install_nightly_project_audit.py`
- `scripts/capability_snapshot.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`
- `scripts/release_skill.py`

### 验收

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
python3 scripts/validate_repo_markdown_integrity.py /path/to/repo --format text
python3 scripts/nightly_project_audit.py
python3 scripts/install_nightly_project_audit.py --hour 23 --minute 30
python3 scripts/validate_gate_set.py /path/to/repo --profile fast
python3 scripts/validate_gate_set.py /path/to/repo --profile deep
python3 scripts/validate_gate_set.py /path/to/repo --profile release
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

更严格的发布保护可以先跑：

```bash
python3 scripts/validate_gate_set.py /path/to/repo --profile release
```

它会自动：

- 更新 `VERSION`
- 默认同步所有版本化文档里的一键安装链接
- 更新 `install.sh` 和 `install-vscode-tools.sh`
- 如果安装链接和当前 `VERSION` 不一致，会先阻止发布
- 创建 release commit
- 创建 git tag

给维护者的最短提示：

```text
可发布。执行：项目助手 发布 patch
```

## 许可

使用仓库约定的 license 与贡献规则。
