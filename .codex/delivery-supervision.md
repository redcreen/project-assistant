# Delivery Supervision

## Current Delivery Direction
- Direction: `post-M21 daemon-host baseline active`
- Status: `active`
- Why Now: keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins

## Supervised Delivery Contract

- 长期监督交付必须同时引用 `.codex/strategy.md`、`.codex/program-board.md`、`.codex/plan.md`、`.codex/status.md`、`.codex/entry-routing.md`、`.codex/dogfooding-evidence.md` 和当前 durable 文档，而不是只凭聊天上下文继续。
- 每个 checkpoint 都必须重新判断：当前工作是可以自动继续、提醒后继续，还是必须升级给人类裁决。
- 长期交付只允许在已批准的业务方向内自动继续；不能自动改变产品方向、兼容性承诺、外部定位或显著成本 / 时间边界。
- 每轮 checkpoint 都必须把验证结果、控制面真相、进展面和交接面刷新成同一套状态，而不是只更新其中一部分。
- 重要的监督循环调整、升级边界变化或 supporting backlog 回流判断，应写入 devlog，避免只剩结论没有推理链。

## Checkpoint Rhythm

| Order | Checkpoint | What Happens | Owner | When |
| --- | --- | --- | --- | --- |
| 1 | 对齐方向与输入 | 读取 strategy / program board / plan / status，确认当前工作流和 checkpoint 目标 | supervisor | 每轮开始前 |
| 2 | 推进执行线 | 执行当前切片，保持任务板、统一前门、验证入口和控制面一致 | delivery worker | 每轮主体 |
| 3 | 运行验证并刷新真相 | 运行 gate / tests，并刷新 status / progress / continue / handoff / entry-routing | delivery worker | 每轮验证后 |
| 4 | 决定继续 / 升级 / 暂停 | 根据信号、blocker 和升级边界决定下一轮动作 | supervisor | 每轮收口时 |
| 5 | 记录 dogfooding 摩擦 | 把 runtime / host / docs / adoption 的真实摩擦、supporting backlog 回流建议和下一里程碑候选沉淀到 `.codex/dogfooding-evidence.md` | supervisor + docs-and-release | 每个 adoption checkpoint |

## Automatic Continue Boundaries

| Situation | Gate | Why |
| --- | --- | --- |
| 已批准方向内的实现与验证 | continue automatically | 当前切片仍在既定方向内，验证通过，且没有新的用户级取舍 |
| 黄色信号但可在既有方向内收口 | raise but continue | 保留风险可见性，继续当前 checkpoint，并要求下一轮复核 |
| 出现新的 runtime / host / adoption 摩擦但尚未跨到业务裁决 | raise but continue | 先记进 strategy / program board / delivery-supervision / dogfooding-evidence，再继续 |
| 方向、兼容性、定位、成本 / 时间边界变化 | require user decision | 立即停止自动继续，升级给人类 |
| 验证失败或 release gate 退红 | raise but continue | 先停在当前 checkpoint，修复后再决定是否继续 |

## Escalation Timing

| When | Required Decision | Owner |
| --- | --- | --- |
| 开始新一轮长任务前 | 检查是否仍在已批准方向内；否则升级 | supervisor |
| 每轮验证之后 | 根据 gate / blocker / architecture signal 决定继续还是先提醒 | delivery worker + supervisor |
| 出现重复 runtime / host / adoption 摩擦时 | 考虑是否需要新的 milestone、治理专项或 supporting backlog 回流 | supervisor |
| 准备 release / tag 之前 | 必须重新确认 release gate、blockers、devlog capture 和 supervision state 都是绿色 | docs-and-release |

## Executor Supervision Loop

| Executor | Current Input | Responsibility | Status |
| --- | --- | --- | --- |
| supervisor | strategy + program board + delivery supervision + entry-routing + status | 确认当前 checkpoint、升级边界和下一轮入口 | active |
| delivery worker | active slice + execution tasks + validator outputs | 推进当前长任务、运行验证、刷新真相 | active |
| docs-and-release | README + architecture + roadmap + development-plan + handoff + release gates | 保持维护者文档、统一入口说明、交接和发布面一致 | active |

## Backlog Re-entry Policy

| Topic | Re-entry Rule | Current Position |
| --- | --- | --- |
| M8 locale-aware internal output | 只有 adoption 证据证明中文优先维护流程仍被冗余英文显著拖慢，且不会分叉真相时，才允许回流 | 先保持在 supporting backlog |
| M9 slimmer continue snapshot | 只有 daemon-host baseline 已稳定后，`continue` 输出仍显著过重，并且不损失恢复精度时，才允许回流 | 先保持在 supporting backlog |
| future runtime / host friction | 只有当同类摩擦跨多个 workspace 反复出现时，才升级成新的正式里程碑 | 先记录为 adoption evidence |

## Next Delivery Checks
1. 在更多本地 workspace 上继续 dogfood daemon-host baseline，并记录 runtime / host / operator docs 摩擦。
2. 根据真实 adoption 证据决定 `M8 / M9` 是否继续保持在 supporting backlog。
3. 当 daemon-host baseline 的 adoption 证据足够时，再决定是否需要更强宿主表面、release 包装升级或 `M15`。
