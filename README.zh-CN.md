# Project Assistant

[English](README.md) | [中文](README.zh-CN.md)

> 一个让 Codex 在真实仓库里少漂移、少反复补上下文的 skill。  
> 它的目标是把规划、执行、进展、文档和交接放在同一套真相里，让仓库在长任务和多轮会话里仍然可恢复、可继续、可维护。

## 你可以用它做什么

- 接管一个已有仓库，同时保住当前真相，不用每次重新摸底
- 让 Codex 在推进实现时，把 plan / status / progress / docs / handoff 一起维护起来
- 把已经发散的仓库重新收敛到“文档、控制面、验证、执行线”一致
- 让长任务跨会话可恢复，而不是每开新线程都从头讲一遍
- 如果你常驻 VS Code，可以直接用活动栏和状态栏做日常操作

## 适合什么场景

- 你会在同一个仓库里反复使用 Codex
- 你希望 assistant 默认负责规划、实现、验证和状态更新
- 你需要跨会话的可恢复进展，而不是一次性 prompt 输出
- 你在意 durable docs、checkpoint 和交接质量

如果你只是想让 AI 临时写一个很小的一次性脚本，这个 skill 可能偏重了。

## 安装

稳定 tag 一键安装（当前 release）：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.10/install.sh | bash
```

这个不可变 tag 已包含 daemon-host / PTL loop baseline：PTL learning review、message ingress、completion gate、task pipeline、Codex App loop hook 和本地 host 安装路径。

从 mainline 安装开发版：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_AUTO_VSCODE_COMPONENTS=project-assistant-host bash
```

这条 mainline 路径会安装当前 skill，并把 `Project Assistant Host` 装到 `~/.vscode/extensions`。

从稳定 tag 手动安装：

```bash
git clone --branch v0.1.10 https://github.com/redcreen/project-assistant.git ~/.codex/skills/project-assistant
```

如果你想直接用最新的 VS Code / daemon-host / PTL learning / task-loop 工具链，使用上面的 mainline 命令，不要把旧稳定 tag 当成当前能力入口。

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
PROJECT_ASSISTANT_REF=v0.1.10 PROJECT_ASSISTANT_DIR="$HOME/.codex/skills/project-assistant" bash install.sh
```

如果你不想自动安装 VS Code 组件：

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

- `project-assistant message . --message "实现当前用户任务"`
- `project-assistant daemon start`
- `project-assistant queue`

## 共享 Codex 线程入口

如果 Telegram 或别的 OpenClaw channel 已经绑到某条 Codex thread，而你想让本机终端加入同一条 thread，用：

```bash
bin/openclaw-codex list
bin/openclaw-codex resume
```

这个入口会读取 `~/.openclaw/openclaw-codex-app-server/state.json`，然后在本机用 `codex resume <threadId>` 恢复最新匹配的 thread。要共享同一条前台 thread，就走这个入口，不要指望一个无关的 API 聊天窗口自动刷新外部 thread 更新。

## VS Code 操作面

如果你把 VS Code 当作日常主操作面，当前的配套扩展是：

- [integrations/vscode-host](integrations/vscode-host/README.md) 里的 `Project Assistant Host`：提供活动栏工作区控制面，以及 daemon 状态 / resume readiness 的状态栏摘要

稳定 tag 一键安装 host：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.10/install-vscode-tools.sh | bash
```

mainline 一键安装 host：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/main/install-vscode-tools.sh | PROJECT_ASSISTANT_REF=main PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash
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

- 当前 tag 的 `install.sh` 默认会把 `Project Assistant Host` 装上；`v0.1.9` 保留为上一版 docs-browser 时代 release
- 这个扩展目前还是本地 operator 工具，还没有打成 Marketplace release
- 如果你只想显式安装 host，可以执行 `curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.10/install-vscode-tools.sh | PROJECT_ASSISTANT_VSCODE_COMPONENTS=project-assistant-host bash`
- 如果你更新了源码，重新执行一次 `bash install-vscode-tools.sh` 并重启 `Extension Host` 即可

## 它会替你做什么

- 创建并维护 `.codex` 控制面
- 让 `继续 / 进展 / 交接` 始终对着同一套当前真相
- 随着工作推进自动更新 plan、status 和 devlog
- 发现 drift 时自动把架构复盘拉上来
- 通过 message ingress 捕获 host/user message，让普通聊天也能被分类、记录、入队并进入程序化 task loop
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

## AI 编程模式定位

- `project-assistant` 当前更接近 `Agentic Engineering + Harness Engineering`，吸收了一部分 `SDD` 和 `BMAD` 的做法，但不是默认的 `Vibe Coding` 工具，也不把 `Ralph Wiggum Loop` 当主交付路径。
- 详细对比见：[AI 编程模式对比](docs/reference/project-assistant/ai-coding-modes-comparison.zh-CN.md)

## 文档导航

- [文档首页](docs/README.zh-CN.md)
- [架构](docs/architecture.zh-CN.md)
- [路线图](docs/roadmap.zh-CN.md)
- [AI 编程模式对比](docs/reference/project-assistant/ai-coding-modes-comparison.zh-CN.md)
- [PTL 角色与受治理自我学习职责](docs/reference/project-assistant/ptl-role-and-governed-learning.zh-CN.md)
- [Codex App Loop 方法验证](docs/reference/project-assistant/codex-app-loop-methods.zh-CN.md)
- [Daemon-Host Release Prep](docs/reference/project-assistant/daemon-host-release-prep.zh-CN.md)
- [纠错驱动的自我学习](docs/reference/project-assistant/correction-driven-self-learning.zh-CN.md)
- [自我学习治理总览](docs/reference/project-assistant/self-learning-governance-overview.zh-CN.md)
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
├── bin/
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

- `bin/openclaw-codex`
- `scripts/project_assistant_entry.py`
- `scripts/openclaw_codex_bridge.py`
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
- `scripts/ptl_gate.py`
- `scripts/validate_ptl_gate.py`
- `scripts/completion_gate.py`
- `scripts/validate_completion_gate.py`
- `scripts/pipeline_runner.py`
- `scripts/validate_pipeline_runner.py`
- `scripts/message_ingress.py`
- `scripts/validate_message_ingress.py`
- `scripts/codex_message_wrapper.py`
- `scripts/install_codex_message_wrapper.py`
- `scripts/validate_codex_message_wrapper.py`
- `scripts/codex_app_loop.py`
- `scripts/codex_app_user_prompt_hook.py`
- `scripts/install_codex_app_loop.py`
- `scripts/validate_codex_app_loop.py`
- `scripts/validate_install_scripts.py`
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
python3 scripts/ptl_gate.py preflight /path/to/repo --mode continue
python3 scripts/validate_ptl_gate.py /path/to/repo --format text
python3 scripts/completion_gate.py final-check /path/to/repo --stop-reason complete
python3 scripts/validate_completion_gate.py /path/to/repo --format text
python3 scripts/pipeline_runner.py run /path/to/repo --task "实现当前用户任务"
python3 scripts/validate_pipeline_runner.py /path/to/repo --format text
python3 scripts/message_ingress.py ingest /path/to/repo --message "实现当前用户任务"
python3 scripts/validate_message_ingress.py /path/to/repo --format text
python3 scripts/install_codex_message_wrapper.py
python3 scripts/validate_codex_message_wrapper.py /path/to/repo --format text
python3 scripts/install_codex_app_loop.py
python3 scripts/validate_codex_app_loop.py /path/to/repo --format text
python3 scripts/validate_install_scripts.py /path/to/repo --format text
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
