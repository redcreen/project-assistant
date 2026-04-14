# 项目助手交接

## 摘要
| 项目 | 当前值 |
| --- | --- |
| 仓库 | `/Users/redcreen/.codex/skills/project-assistant` |
| 层级 | `中型` |
| 当前阶段 | post-M21 daemon-host baseline active |
| 当前切片 | stabilize-daemon-host-baseline-for-dogfooding |
| 当前执行线 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins |
| 执行进度 | `2 / 3` |
| 架构信号 | `绿色` |
| 自动触发 | 当前没有自动触发 |
| 升级 Gate | `自动继续` |
| 战略方向 | stabilize-daemon-host-baseline-for-dogfooding |
| 战略状态 | `活跃` |
| 下一战略检查 | 在 daemon-host baseline 的 dogfooding 过程中继续要求战略判断引用 durable repo 证据，而不是只凭聊天感受。 |
| 程序编排方向 | stabilize-daemon-host-baseline-for-dogfooding |
| 程序编排状态 | `活跃` |
| 下一程序检查 | 在更多本地 workspace 上继续 dogfood daemon-host baseline，并记录 runtime / host 摩擦。 |
| 长期交付方向 | post-M21 daemon-host baseline active |
| 长期交付状态 | `活跃` |
| 下一长期交付检查 | 在更多本地 workspace 上继续 dogfood daemon-host baseline，并记录 runtime / host / operator docs 摩擦。 |
| PTL 监督方向 | post-M21 daemon-host baseline active |
| PTL 监督状态 | `活跃` |
| 下一 PTL 检查 | 在更多本地 workspace 上继续验证 PTL 监督判断会沿着 daemon-host baseline 推进，而不是退回同步串脚本路径。 |
| worker 接续方向 | post-M21 daemon-host baseline active |
| worker 接续状态 | `活跃` |
| 下一 handoff 检查 | 在更多本地 workspace 上验证 worker 停下后的接续、回流和升级都能靠 daemon-host baseline 的 durable 真相完成。 |
| 当前主要风险 | 当前无主要风险。 |
| 升级原因 | 当前执行可以沿既有方向继续，不需要用户层面的额外取舍。 |

## Usable Now
- 恢复当前状态与下一步
- 长任务执行线与可见任务板
- 默认架构监督与升级 gate
- 自动架构信号更新
- 架构整改审计与工作底稿
- 文档整改与 Markdown 治理
- 开发日志索引与自动沉淀
- 战略评估层与 review contract
- 程序编排层与 durable program board
- 长期受监督交付层与 checkpoint rhythm
- PTL 监督环与持续巡检 contract
- worker 接续与回流 contract
- 统一工具前门、版本 preflight 与结构化入口 contract
- dogfooding 采证与 evidence-gated 决策面
- 公开文档中英文切换
- CI deep 门禁
- CI release readiness 门禁
- CI 更严格发布保护门禁
- 版本发布与 tag 安装地址

## Human Windows
### Chinese
- `项目助手 菜单`
- `项目助手 进展`
- `项目助手 架构`
- `项目助手 开发日志`

### English
- `project assistant menu`
- `project assistant progress`
- `project assistant architecture`
- `project assistant devlog`

## Restore Order
1. `.codex/status.md`
2. `.codex/plan.md`
3. `.codex/strategy.md`
4. `.codex/program-board.md`
5. `.codex/delivery-supervision.md`
6. `.codex/brief.md`
7. `.codex/ptl-supervision.md`
8. `.codex/worker-handoff.md`

## Copy-Paste Commands

### Chinese
```text
项目助手 继续。先读取 .codex/status.md、.codex/plan.md、.codex/strategy.md、.codex/program-board.md、.codex/delivery-supervision.md、.codex/brief.md、.codex/ptl-supervision.md、.codex/worker-handoff.md；然后继续当前执行线：keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins。
项目助手 告诉我这个项目当前进展，用全局视角、模块视角和图示输出。
项目助手 继续当前执行线，并先运行验证：根据仓库测试入口执行验证。
```

### English
```text
project assistant continue. Read .codex/status.md, .codex/plan.md, .codex/strategy.md, .codex/program-board.md, .codex/delivery-supervision.md, .codex/brief.md, .codex/ptl-supervision.md, .codex/worker-handoff.md first; then continue the current execution line: keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins.
project assistant progress
project assistant continue the current execution line and run validation first: run the repo's primary test entry.
```

## Next 3 Actions
1. `stabilize-daemon-host-baseline-for-dogfooding`
2. `EL-3` collect broader dogfooding evidence before opening the next host surface or any M15 discussion
3. keep release packaging and broader host expansion evidence-gated until the new baseline proves stable in more workspaces

## Execution Tasks
1. [x] EL-1 harden daemon runtime edges exposed by concurrent startup, shutdown, or status polling in real workspaces
2. [x] EL-2 keep README / architecture / usage / test plan / entry routing aligned with daemon-host as the new default fast path
3. [ ] EL-3 collect broader dogfooding evidence before opening the next host surface or any M15 discussion

## Notes
- Start a new thread with this output and the repo path when you need a clean context.
- For large projects, read `.codex/module-dashboard.md` before `modules/*.md` after restore.
- 如果使用中文继续，也可以直接复制上面的中文命令。
