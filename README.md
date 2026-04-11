# Project Assistant

`project-assistant` 是一个给 Codex 用的项目操作系统型 skill。

它解决的不是单点问答，而是这些持续性问题：

- 项目方向清楚，但实现路径不清楚
- 做到一半后，不知道当前在哪、下一步是什么
- 不同项目约束不同，每次都重新想流程
- 现有项目已经有很多文档，但状态恢复和进展表达仍然混乱
- 新开对话时，希望快速恢复上下文继续开发

---

## 用户视角

### 这个 skill 能做什么

- 启动项目：自动建立最小控制面
- 规划阶段：明确目标、约束、切片、验证方式
- 恢复状态：先恢复当前阶段，再继续执行
- 汇报进展：用全局视角、模块视角、图示输出
- 整改项目：把现有仓库收敛到规范结构
- 压缩上下文：生成可复制的新对话恢复包
- 阶段收口：结束当前阶段并明确下一阶段入口

### 推荐入口

平时只需要记住一个入口：

- `项目助手`

常用命令：

- `项目助手 菜单`
- `项目助手 启动这个项目`
- `项目助手 规划下一阶段`
- `项目助手 恢复当前状态`
- `项目助手 告诉我项目进展`
- `项目助手 整改这个仓库`
- `项目助手 压缩上下文`
- `项目助手 收口当前阶段`

### 你会得到什么

对中大型项目，默认会建立或刷新这些控制面文件：

- `.codex/brief.md`
- `.codex/status.md`
- `.codex/plan.md`

对 `large` 项目，还会补模块层：

- `.codex/module-dashboard.md`
- `.codex/modules/*.md`

### 进展输出长什么样

`项目助手 进展` 会优先读取控制面，然后输出：

- 当前阶段
- 当前切片
- 全局视角
- 模块视角
- 下一步 3 项
- Mermaid 图示

### 新开对话前怎么交接

直接说：

- `项目助手 压缩上下文`
- `项目助手 生成恢复包`
- `项目助手 给我新对话恢复指令`

它会生成：

- 当前阶段摘要
- 恢复顺序
- 可复制的恢复命令
- 继续执行与验证命令

---

## 开发者视角

### 目录结构

```text
project-assistant/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── bootstrap.md
│   ├── context-guard.md
│   ├── governance.md
│   ├── help-menu.md
│   ├── module-layer.md
│   ├── progress-reporting.md
│   ├── retrofit.md
│   ├── templates.md
│   └── usage.md
└── scripts/
    ├── context_handoff.py
    ├── control_surface_lib.py
    ├── progress_snapshot.py
    ├── sync_control_surface.py
    └── validate_control_surface.py
```

### 设计原则

- 主 `SKILL.md` 保持短，只放核心协议和硬规则
- 详细说明下沉到 `references/*.md`
- 可校验、可收敛、可复用的行为尽量放到 `scripts/`
- `整改` 必须是收敛任务，不允许停在中间态
- `进展` 必须优先脚本化，不靠自由发挥拼输出

### 核心脚本

- `scripts/sync_control_surface.py`
  同步控制面脚手架，补齐缺失结构
- `scripts/validate_control_surface.py`
  校验控制面是否按 tier 达标
- `scripts/progress_snapshot.py`
  输出机器校验过的进展面板
- `scripts/context_handoff.py`
  输出上下文压缩 / 新对话恢复包
- `scripts/control_surface_lib.py`
  共用解析、校验和完成度规则

### 维护方式

修改这个 skill 时，优先顺序是：

1. 先明确是行为规则问题，还是结构/校验问题
2. 结构收敛、进展输出、恢复包优先改脚本
3. 只有属于模型行为协议的部分，才改 `SKILL.md`
4. 文档模板和说明同步到 `references/`

### 推荐校验流程

如果你在某个项目上改进了 skill，至少跑一遍：

```bash
python3 scripts/sync_control_surface.py /path/to/repo
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/progress_snapshot.py /path/to/repo
python3 scripts/context_handoff.py /path/to/repo
```

理想结果：

- `validate_control_surface.py` 返回 `ok: True`
- `progress_snapshot.py` 输出足够清楚的全局 + 模块视角
- `context_handoff.py` 生成可直接复制的新对话恢复命令

### 当前边界

- 目前不能精确读取 Codex 运行时的上下文占用百分比
- 所以“context 超过 60% 自动提示”只能做到软触发，不能做到硬阈值自动检测
- 但已经支持稳定的 `压缩上下文 / 交接 / 恢复包` 工作流

---

## 开发和测试建议

如果你要继续扩这个 skill，建议优先从这三类能力继续演进：

- 更强的 `retrofit` 收敛规则
- 更短但更清晰的 `progress` 面板
- 更稳定的 `handoff` 恢复命令

如果未来 Codex 暴露上下文占用率接口，再把 `60%` 自动提示改成真正的硬触发。
