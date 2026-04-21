# AI 编程模式对比

[English](ai-coding-modes-comparison.md) | [中文](ai-coding-modes-comparison.zh-CN.md)

## 目的

这份文档回答一个问题：和 2026 年常见的 AI 编程模式相比，`project-assistant` 当前更像什么，不像什么。

这里把 2026 年 4 月 15 日的“6 种 AI 编程模式”文章当作讨论框架，而不是把那 6 个名字当成正式行业标准。

## 一句话结论

`project-assistant` 不是单一模式。

它当前最接近 `Agentic Engineering + Harness Engineering`，并吸收了一部分 `SDD` 与 `BMAD` 的做法；它刻意不把自己定位成默认的 `Vibe Coding` 工具，也不把 `Ralph Wiggum Loop` 当主交付路径。

## 对比表

| 模式 | 这类模式强调什么 | `project-assistant` 当前对应关系 | 当前已具备 | 当前边界 |
| --- | --- | --- | --- | --- |
| `Vibe Coding` | 先聊想法，快速出代码，低流程 | 刻意保持距离 | 仍可用自然语言快速探索和起草 | 不是一次性 prompt 工具；默认会把工作拉回 `plan / status / docs / validation` |
| `Agentic Engineering` | 先想清楚、再拆任务、执行后验收 | 核心贴合 | `strategy / program-board / plan / status / delivery-supervision`、`continue / progress / handoff`、checkpoint 与升级 gate | 人类仍保留业务方向、兼容性承诺、成本边界裁决 |
| `Harness Engineering` | 用上下文、约束、反馈循环和熵管理让 AI 稳定工作 | 核心贴合 | control surface、docs system、validators、architecture triggers、worker handoff、daemon 托管安全支撑任务 | 还不是全自动多执行器冲突解决系统 |
| `Ralph Wiggum Loop` | `PRD + checklist + clean-context` 循环执行 | 局部吸收，非默认主线 | durable 真相、checkpoint、worker handoff、queue / ETA、可恢复执行线 | 不默认后台自动写业务代码；不鼓励无限循环自治 |
| `BMAD` | 角色化智能体，把分析 / 产品 / 架构 / 执行拆开 | 部分吸收 | PTL、worker、architecture supervision、docs / release / governance surfaces 已形成角色分层 | 还不是一套完整的多角色长驻 agent roster |
| `SDD` | spec 先行，把规范当 source of truth | 强相关，但不是纯实现 | roadmap、development plan、architecture、`.codex/*` 控制面共同约束执行 | 还没有把所有实现都统一成单一可执行 spec 工作流 |

## 当前能力更准确的说法

- `project-assistant` 更像一个 repo operating layer，而不是单一编程提示模板。
- 它的核心价值不是“替你多写一点代码”，而是“让规划、执行、验证、进展和交接围绕同一套 durable truth 收敛”。
- 这也是它为什么更接近 `Harness Engineering`：真正被产品化的是运行环境和治理层，而不是一次对话本身。

## 这对后续 self-learning 的意义

- 学习对象应优先落在 `spec / checklist / policy / review rule / escalation rule / template`，而不是直接把原始对话变成隐式人格漂移。
- PTL 适合消费“已经 promotion 成 stable 的经验”，不适合绕过治理直接自我改写。
- 如果后续要做从对话抽取经验，最自然的承载方式是 `candidate -> review -> stable -> decay` 的 artifact 生命周期。

## 相关内部文档

- [orchestration-model.zh-CN.md](orchestration-model.zh-CN.md)
- [ptl-daemon-mvp.zh-CN.md](ptl-daemon-mvp.zh-CN.md)
- [strategic-planning-and-program-orchestration.zh-CN.md](strategic-planning-and-program-orchestration.zh-CN.md)
- [development-plan.zh-CN.md](development-plan.zh-CN.md)

## 外部参考

- 2026-04-15 文章《别再说 AI 编程就是 Vibe Coding 了！6 种主流模式一次讲清》：
  `https://mbd.baidu.com/newspage/data/landingsuper?context=%7B%22nid%22%3A%22news_9381192559901099771%22%2C%22sourceFrom%22%3A%22bjh%22%7D&isBdboxFrom=1&pageType=1&rs=3339967809&ruk=AseIqI0YO6rBNSL13jIBSg&sid_for_share=&urlext=%7B%22cuid%22%3A%22_iB3uY8bvuYzi-fql8vAu_aO-8gsa2uFliv8i0i9vajx8S8I0OvgilfvQu5WfSOwM8VmA%22%7D`
- GitHub Spec Kit / Spec-Driven Development：
  `https://github.com/github/spec-kit`
- PMI Hybrid / fit-for-purpose：
  `https://www.pmi.org/blog/project-management-embraces-the-fit-for-purpose-approach`
- PMI Pulse 2025 / business acumen：
  `https://www.pmi.org/learning/thought-leadership/boosting-business-acumen`
- DORA 2025 / AI-assisted software development：
  `https://cloud.google.com/devops/state-of-devops`
- Atlassian System of Work：
  `https://www.atlassian.com/system-of-work`
