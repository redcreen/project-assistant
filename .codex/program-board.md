# Program Board

## Current Program Direction
- Direction: `close-m16-tool-first-front-door-and-queue-rollout-verification`
- Status: `active`
- Why Now: repo 层统一前门已经收口；当前需要继续采集跨 repo rollout 证据，并把剩余入口摩擦稳定归类到正确层。

## Program Orchestration Contract

- 程序编排必须引用 `.codex/strategy.md`、`.codex/plan.md`、`.codex/status.md` 和当前 durable 文档，而不是只凭聊天上下文。
- 程序编排层拥有多个 workstreams、切片、执行器输入和串并行边界；它不拥有业务方向变更。
- 任何跨到业务方向、兼容性承诺、外部定位或显著成本 / 时间边界的变化，必须继续升级给人类审批。
- program-board 必须让维护者一眼看出当前有哪些 active workstreams、哪些可并行、下一次调度点是什么。
- 重要的编排收口应写入 devlog，避免只留下结果而没有调度原因。

## Active Workstreams

| Workstream | Scope | State | Priority | Current Focus | Next Checkpoint |
| --- | --- | --- | --- | --- | --- |
| post-M16 rollout verification | 在更多旧代际仓库上 rollout 统一前门，并验证 continue / progress / handoff 会先升级再输出结构化面板 | active | P0 | 采集真实入口是否仍被绕过、是否需要宿主桥接 | 决定 M15 是否值得立项 |
| control truth and gates | 保持 `.codex` 真相、门禁和 release 保护一致 | stable | P1 | 保持 strategy / program board / delivery supervision / plan / status / handoff 一致 | 继续只允许一套 control truth |
| maintainer-facing outputs | 让 progress / continue / handoff 对维护者和未来接手者足够清楚 | stable | P1 | 让统一前门输出的第一屏继续保持结构化、表格优先、中文优先 | 只有 rollout 证据要求时再调整 |
| supporting backlog routing | 管理 M8 / M9 这类 supporting backlog 议题，不让它们无计划回流主线 | active | P1 | 用 rollout 证据决定 M8 / M9 是否继续保持 backlog | 在没有证据前继续保持 backlog |

## Sequencing Queue

| Order | Workstream | Slice / Input | Executor | Status |
| --- | --- | --- | --- | --- |
| 1 | post-M16 rollout verification | carry the unified front door onto more legacy repos and record entry friction | supervisor | active |
| 2 | control truth and gates | keep supervision surfaces, strategy, program board, plan, and status aligned while evidence accumulates | delivery worker | active |
| 3 | maintainer-facing outputs | only adjust continue / progress / handoff when rollout evidence shows confusion after the front door | docs-and-release | active |
| 4 | supporting backlog routing | decide whether M8 / M9 stay backlog or re-enter with evidence | supervisor | next |

## Executor Inputs

| Executor | Current Input | Why It Exists | Status |
| --- | --- | --- | --- |
| supervisor | `.codex/strategy.md` + `.codex/program-board.md` + `.codex/delivery-supervision.md` + `.codex/entry-routing.md` + `.codex/status.md` | 在 rollout 期间决定前门摩擦怎样回流成 M15 判断、宿主桥接判断或 backlog 调整 | active |
| delivery worker | active slice + execution tasks + validator outputs | 推进当前 checkpoint 并保持与 program-board 对齐 | active |
| docs-and-release | README + architecture + roadmap + development-plan + gate outputs | 保持 durable docs、统一入口说明、交接与发布面一致 | active |

## Parallel-Safe Boundaries

| Boundary | Parallel-Safe? | Notes |
| --- | --- | --- |
| control truth vs docs alignment | yes | 文档更新可以跟随 control truth，但 `.codex/plan.md` / `.codex/status.md` 仍保持唯一真相源 |
| maintainer outputs vs docs alignment | yes | progress / continue / handoff 的展示更新可以和 README / roadmap 调整并行 |
| strategy changes vs business direction changes | no | 一旦跨到业务方向、兼容性或外部定位，就必须停下来给人类审批 |

## Supporting Backlog Routing

| Topic | Current Position | Re-entry Rule | Notes |
| --- | --- | --- | --- |
| M8 locale-aware internal output | supporting backlog | 只有当它能降低维护者摩擦且不分叉真相时，才允许重新吸收 | 保持在 backlog |
| M9 slimmer continue snapshot | supporting backlog | 只有当 program-board 已能承载恢复真相时，才允许进一步压缩 continue 输出 | 保持在 backlog |

## Next Orchestration Checks
1. 在更多仓库上使用完整的 PTL supervision + worker handoff 模型，并记录真实接续摩擦。
2. 继续确认 `M8 / M9` 是否保持在 supporting backlog，而不是被无计划地拉回主线。
3. 只有当 cross-repo 证据证明单 Codex PTL 模式成为瓶颈时，才提 `M15`。
