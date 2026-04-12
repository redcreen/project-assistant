# Project Assistant

[English](README.md) | [中文](README.zh-CN.md)

> 一个用于项目规划、整改收敛、进展汇报、开发日志、文档治理和上下文交接的 Codex skill。  
> 它汇聚了架构师、技术负责人、代码审查者、QA/验证负责人和技术写作者的最佳实践，帮助 Codex 写出更稳、更清晰、更优雅、更易维护、也更容易持续演化的代码与项目结构。

## 适用对象

- 想让 Codex 按稳定节奏推进交付的团队或个人
- 需要可恢复状态、可收敛整改、可读文档的仓库
- 需要在多轮会话里始终看清当前阶段、下一步和变化点的项目

## 它现在是什么

| 项目 | 当前定位 |
| --- | --- |
| 产品角色 | 一个面向 Codex 交付的 AI 工程操作系统 |
| 当前最强能力 | 项目规划、整改收敛、架构监督、进展汇报、开发日志、文档治理、上下文交接 |
| 人类仍然负责 | 业务方向、产品优先级、兼容性承诺和重大取舍 |
| 默认工作模型 | 人类给方向；`project-assistant` 负责规划、执行、验证、更新状态，并只在需要判断时升级给人类 |
| 关键常驻角色 | 项目技术负责人（PTL）：在已批准业务方向内负责战略判断、程序编排、长期交付监督和升级 |
| 当前战略方向 | `M10 / M11 / M12 / M13 / M14` 已完成；当前进入 post-M14 证据采集，用真实 repo 证据判断 `M15 选择性多执行器调度` 是否真的需要 |
| 程序编排层当前边界 | 先把“单 Codex 内的 durable 编排真相层”和“worker 停下后项目不断线”做稳定；多桌面 Codex / 多执行器自动调度仍属于后续能力 |
| `M14` 人话解释 | `worker 停了，项目不能跟着停` |
| `继续` 的自动行为 | 先读取 `.codex/control-surface.json`；如果控制面版本过旧，或缺少当前 surface 版本，就先做最小安全补齐，再继续当前执行线 |

## 它接下来要去哪里

| 时间层级 | 重点 |
| --- | --- |
| 当前 | 在更多 repo 上 rollout 已完成的 `M13 PTL 监督环` 与 `M14 worker 接续与回流`，确认 worker 停下后项目仍能被 PTL durable 地接住并继续 |
| 下一步 | 根据 cross-repo 证据判断是否真的需要 `M15 选择性多执行器调度` |
| 更后面 | 只有当证据显示单 Codex PTL 模式已经成为瓶颈，且不相交写入边界成立时，才引入真正多执行器 |
| 战略入口 | [业务规划与程序编排方向](docs/reference/project-assistant/strategic-planning-and-program-orchestration.zh-CN.md) |

## 安装

通过稳定 tag 一键安装：

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.3/install.sh | bash
```

手动安装：

```bash
git clone --branch v0.1.3 https://github.com/redcreen/project-assistant.git ~/.codex/skills/project-assistant
```

## 最简配置

不需要额外配置。

最简单的方式：

1. 安装到 `~/.codex/skills/project-assistant`
2. 新开一个 Codex 会话
3. 执行 `项目助手 菜单`

可选覆盖：

```bash
PROJECT_ASSISTANT_REF=v0.1.3 PROJECT_ASSISTANT_DIR="$HOME/.codex/skills/project-assistant" bash install.sh
```

## 快速开始

只需要记住一个入口：

- `项目助手`

主窗口：

- `项目助手 菜单`
- `项目助手 进展`
- `项目助手 架构`
- `项目助手 开发日志`

后台流程（通常自动运行）：

- `项目助手 启动这个项目`
- `项目助手 继续`
- `项目助手 架构 整改`
- `项目助手 整改`
- `项目助手 文档整改`
- `项目助手 压缩上下文`

## 核心能力

- 创建并维护 `.codex` 控制面
- 维护 `.codex/doc-governance.json` 作为 Markdown 治理契约
- 把工作拆成可验证的切片
- 把当前工作收敛成一条有检查点的长任务执行线，而不是频繁等待“继续”
- 把执行线显示成一个可见的子任务板，并用 `Plan Link` 映射回当前切片
- 把架构监督状态和升级 gate 并排展示在执行线旁边
- 把 `progress / continue / handoff` 做成更像给维护者看的第一屏，而不是只剩 raw status dump
- 让 `继续` 自动判断旧项目是否需要最小控制面升级，而不是把这个判断甩给用户
- 当当前切片出现 ownership、boundary 或 repeated-fix drift 时，自动把架构复盘升上来
- 用一个简短的 `Usable Now` 快照告诉你现在已经能直接用什么
- 把现有仓库整改到收敛状态
- 用全局和模块视角汇报进展
- 把重要问题、思考路径和解决方案沉淀成开发日志
- 把战略评估沉淀成 `.codex/strategy.md`，并区分“系统可以自动建议什么”和“必须人类审批什么”
- 把 PTL 的战略评估沉淀成 `.codex/strategy.md`，并区分“系统可以自动建议什么”和“必须人类审批什么”
- 把 PTL 的程序编排沉淀成 `.codex/program-board.md`，并显式表达 workstreams、排序、并行边界和执行器输入；当前先面向单 Codex 总协调模式
- 把 PTL 的长期受监督交付沉淀成 `.codex/delivery-supervision.md`，并显式表达 checkpoint 节奏、自动继续边界、升级时机和 backlog 回流规则
- 把 PTL 监督环与 worker 接续做成 `.codex/ptl-supervision.md` 与 `.codex/worker-handoff.md`，并把多执行器进入条件继续保持为证据驱动 later 层
- 把 durable 文档整理到统一结构
- 为新对话生成紧凑恢复包

## 现在已经能直接用

已经在代表性仓库上跑通并可直接使用的稳定工作流：

- `项目助手 整改`
- `项目助手 文档整改`
- `项目助手 架构 整改`
- `项目助手 进展`
- `项目助手 压缩上下文`

这意味着：

- 规划、执行、架构监督和开发日志现在都已经是默认自动能力，而不是额外 opt-in 流程
- 这套 skill 已经不只是一个规划脚手架，而是真的在轻量仓库和大型文档型仓库上跑过收敛
- `progress`、`handoff`、控制面和门禁现在描述的是同一套当前真相
- 代表性的中型 / 大型仓库现在都能给出更像“维护者恢复面板”的第一屏，而不是只有 raw slice 名
- 至少一条架构复盘路径现在已经能从当前切片里的 drift 信号自动升级出来，而不是只靠手工提醒
- 战略评估层、程序编排层、长期受监督交付层、PTL 监督环和 worker 接续层现在都已经是 PTL 可运行能力，而不只是 proposal 文档
- 程序编排层当前是“一个 Codex 的总调度脑”，不是已经产品化成“自动拉起多个桌面 Codex 并回收结果”
- `M13 / M14` 已经关闭；下一步只在证据足够时才考虑是否打开 `M15 选择性多执行器调度`

## 常见工作流

默认工作方式：

- 你主要给需求、业务方向、优先级和硬约束
- `project-assistant` 默认负责规划、架构监督、实现、验证、状态更新和开发日志
- 只有在检查点、阻塞点或需要业务裁决时才应该停下来问你
- 长任务执行时，应通过可见的任务板体现 done/total 进度，而不是只剩下一段抽象状态描述
- 长任务执行时，也应持续用简短进度提示告诉你“现在在做什么 / 刚完成什么 / 下一检查点是什么”，不能无声跑很久
- 架构层还应持续表明：现在是可以自动继续、提醒但继续，还是必须停下来等用户裁决
- 进展和交接里还应明确告诉你：现在到底有哪些能力已经可用
- `继续` 应默认带一个简版进展快照；如果要完整全局视图，再用 `项目助手 进展`

### 启动或接管项目

```text
项目助手 启动这个项目
```

### 查看当前进展

```text
项目助手 进展
```

### 直接继续当前工作

```text
项目助手 继续
```

默认语义：

- 先自动检查这个仓库的控制面版本是不是已经落后
- 先读取 `.codex/control-surface.json`，比对控制面版本和各 surface 版本是否落后
- 如果控制面版本过旧，或缺少当前 surface 版本，先自动补齐最小安全升级
- 然后再恢复并继续当前执行线
- 如果过程较长，要持续告诉你当前在做什么，而不是沉默等待

### 从架构层审查当前方向

```text
项目助手 架构
```

最常用：

- `项目助手 架构 监督`

什么时候用：

- 准备改代码前，先看当前方向是不是在修局部现象
- 你怀疑 AI 为了当前功能开始硬编码
- 你希望先从整体边界和扩展性看一眼再继续实现

### 做架构整改，而不是只做普通整改

```text
项目助手 架构 整改
```

适用场景：

- 问题核心是边界、状态流或抽象方向错了
- 不是缺文档，而是架构 owner 和正确层级已经漂了
- “修一个冒一个”说明需要架构优先的整改，而不是继续局部补丁

### 整体整改仓库

```text
项目助手 整改
```

默认范围：

- 控制面整改
- 文档整改
- 全仓 Markdown 治理整改
- 脚本验收

当仓库主要问题是“结构散、状态不清、文档不一致”时，用这个入口。
如果问题核心是“边界错、层级错、一直在修表象”，应直接用 `项目助手 架构 整改`。

### 只重点整理文档

```text
项目助手 文档整改
```

### 记录一条值得保留的实现结论

```text
项目助手 开发日志
```

### 为新对话做交接

```text
项目助手 压缩上下文
```

## 文档导航

- [文档首页](docs/README.zh-CN.md)
- [架构](docs/architecture.zh-CN.md)
- [路线图](docs/roadmap.zh-CN.md)
- [战略方向](docs/reference/project-assistant/strategic-planning-and-program-orchestration.zh-CN.md)
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
- `scripts/capability_snapshot.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`
- `scripts/release_skill.py`

### 验收

```bash
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/validate_docs_system.py /path/to/repo --format text
python3 scripts/validate_public_docs_i18n.py /path/to/repo --format text
python3 scripts/validate_markdown_governance.py /path/to/repo --format text
python3 scripts/validate_doc_quality.py /path/to/repo --format text
python3 scripts/validate_control_surface_quality.py /path/to/repo --format text
python3 scripts/validate_development_log.py /path/to/repo --format text
python3 scripts/validate_architecture_retrofit.py /path/to/repo --format text
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
