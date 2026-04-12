# 项目起点与工作方法

[English](project-origin-and-working-method.md) | [中文](project-origin-and-working-method.zh-CN.md)

## 这是什么

这份文档记录 `project-assistant` 的**项目起点**。

它回答两件事：

| 问题 | 说明 |
| --- | --- |
| 这个 skill 是从哪里长出来的 | 来自一条关于“如何更稳地使用 Codex 做项目开发”的原始提问 |
| 这个 skill 默认倡导什么工作方法 | 先把目标和方法讲清楚，再让 AI 在 durable 计划与门禁里长期推进 |

## 这是起点

`project-assistant` 不是先从“命令列表”开始的，而是先从下面这段问题开始的。

这段原文保留下来，是为了让后续维护者始终知道：

- 这个 skill 的出发点是什么
- 为什么它会强调架构、roadmap、test case、development plan、长期推进和恢复真相
- 为什么它不是单纯的“让 AI 直接写代码”

## 原始提问（原文保留）

> 我在使用codex开发一个项目时，发现先讨论清楚最终目标，然后在讨论实现方案，出系统架构文档  然后出roadmap 及test case，在出development plan，然后让ai按照plan去开发，会比较好； 这是ai编程的最佳实践么？ 还有哪些更好的方式么？ 我想把这个方法固化下来；  
> 包含开发项目的子项目或者阶段任务时也按照这个方法，这样会比较清晰，但不是知道这是不是最佳实践；  
> 同时我希望产出的这个最佳实践，可以像类似skill或者什么工具似的，可以引领我每次这样来做；

## 由起点沉淀出的默认工作方法

| 顺序 | 默认动作 | 为什么 |
| --- | --- | --- |
| 1 | 先讨论清楚最终目标 | 先收口结果，不让实现细节先带偏方向 |
| 2 | 再讨论实现方案 | 把候选路径和边界说清楚，再决定怎么做 |
| 3 | 先出系统架构文档 | 先明确模块、边界、职责和长期演化方向 |
| 4 | 再出 roadmap | 先有阶段路线，再决定每段工作怎么排 |
| 5 | 再出 test case / 验收标准 | 先定义什么算做完，避免只凭感觉推进 |
| 6 | 再出 development plan | 把阶段路线翻成顺序执行计划和恢复入口 |
| 7 | 再让 AI 按 plan 开发 | 让执行建立在 durable 真相上，而不是建立在当前聊天记忆上 |
| 8 | 推进过程中持续更新状态、进展、开发日志与门禁 | 让项目可恢复、可审计、可交接，不靠人脑记忆维持 |

## 这是不是最佳实践

| 结论 | 说明 |
| --- | --- |
| 很接近当前最稳的 AI 编程实践 | 它符合“人类定方向，AI 在 durable 计划、验证和门禁里执行”的模式 |
| 但不是唯一合法方式 | 小修复、紧急修补、极小型仓库可以更轻量 |
| 它最适合中型以上、需要多轮会话、需要恢复能力的项目 | 项目越长、越复杂，这套方法收益越大 |

## 什么时候可以变通

| 场景 | 可以怎么变通 |
| --- | --- |
| 很小的单文件修复 | 可以跳过完整 roadmap，只保留目标、验证和变更理由 |
| 明确且低风险的机械改动 | 可以压缩架构讨论，但仍应保留验证入口 |
| 已经存在稳定 roadmap / development plan 的项目 | 可以直接进入 `项目助手 继续`，不必每轮重写前置文档 |
| 高风险架构调整 | 不应省略架构文档、专项判断和升级边界 |

## 子项目与阶段任务也适用

| 场景 | 应怎么做 |
| --- | --- |
| 子项目 | 先明确子项目目标、边界、验收，再把它挂进总 roadmap |
| 阶段任务 | 先明确当前阶段目标和退出条件，再拆 development plan |
| 长任务执行 | 用 execution line + task board 表达，不要只写一句“继续做” |
| worker 停下 | 用 PTL supervision + worker handoff 保证项目不断线 |

## `project-assistant` 如何把它固化下来

| 这套方法的原始想法 | 现在落到哪里 |
| --- | --- |
| 先明确目标 | `brief / roadmap / strategy` |
| 再明确方案与边界 | `architecture / architecture retrofit / PTL review` |
| 先定义阶段，再定义执行 | `roadmap / development-plan / plan` |
| 让 AI 按 plan 长期推进 | `execution line / progress / continue / handoff` |
| 不让项目停在聊天里 | `.codex/status.md`、`.codex/plan.md`、`devlog`、门禁 |
| 让“有个总负责人盯着” | `PTL supervision / program board / delivery supervision` |

## 一句话总结

`project-assistant` 的起点不是“让 AI 多写代码”，而是：

**先把目标、方案、架构、roadmap、测试和 development plan 讲清楚，再让 AI 在 durable 真相和门禁里长期推进。**
