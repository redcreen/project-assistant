# Program Board

## Current Program Direction

- Direction: `program orchestration layer`
- Status: `done`
- Why Now: M11 已关闭；program-board 现在作为 M12 与 rollout / adoption 阶段的 durable 编排输入，继续表达 workstreams、边界和 backlog 回流规则

## Program Orchestration Contract

- 程序编排必须引用 `.codex/strategy.md`、`.codex/plan.md`、`.codex/status.md` 和当前 durable 文档，而不是只凭聊天上下文。
- 程序编排层拥有多个 workstreams、切片、执行器输入和串并行边界；它不拥有业务方向变更。
- 任何跨到业务方向、兼容性承诺、外部定位或显著成本 / 时间边界的变化，必须继续升级给人类审批。
- program-board 必须让维护者一眼看出当前有哪些 active workstreams、哪些可并行、下一次调度点是什么。
- 重要的编排收口应写入 devlog，避免只留下结果而没有调度原因。

## Active Workstreams

| Workstream | Scope | State | Priority | Current Focus | Next Checkpoint |
| --- | --- | --- | --- | --- | --- |
| rollout evidence collection | 在更多仓库上采集 adoption 摩擦、边界信号和下一里程碑候选 | active | P0 | 把 M12 模型带到更多真实 repo 上，并记录摩擦 | 决定是否需要 post-M12 里程碑 |
| control truth and gates | 保持 `.codex` 真相、门禁和 release 保护一致 | stable | P1 | 保持 strategy / program board / delivery supervision / plan / status 一致 | 继续只允许一套 control truth |
| maintainer-facing outputs | 让 progress / continue / handoff 对维护者和未来接手者足够清楚 | stable | P1 | 保持程序编排与长期交付状态都能直接出现在第一屏 | 只有 rollout 证据要求时再调整 |
| supporting backlog routing | 管理 M8 / M9 这类 supporting backlog 议题，不让它们无计划回流主线 | active | P1 | 用 rollout 证据决定 supporting backlog 是否回流 | 在没有证据前继续保持 backlog |

## Sequencing Queue

| Order | Workstream | Slice / Input | Executor | Status |
| --- | --- | --- | --- | --- |
| 1 | rollout evidence collection | carry the full M12 model onto more repos and record friction | supervisor | next |
| 2 | control truth and gates | keep delivery-supervision, strategy, program board, and status aligned | delivery worker | active |
| 3 | maintainer-facing outputs | only adjust progress / continue / handoff when rollout evidence shows confusion | docs-and-release | active |
| 4 | supporting backlog routing | decide whether M8 / M9 stay backlog or re-enter with evidence | supervisor | next |

## Executor Inputs

| Executor | Current Input | Why It Exists | Status |
| --- | --- | --- | --- |
| supervisor | `.codex/strategy.md` + `.codex/program-board.md` + `.codex/delivery-supervision.md` + `.codex/status.md` | 在 rollout 期间决定 workstream 顺序、升级点和下一里程碑候选 | active |
| delivery worker | active slice + execution tasks + validator outputs | 推进当前 checkpoint 并保持与 program-board 对齐 | active |
| docs-and-release | README + roadmap + development-plan + gate outputs | 保持 durable docs、交接与发布面一致 | active |

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

1. 在更多仓库上使用完整的 M12 模型，并记录 rollout 摩擦。
2. 继续确认 `M8 / M9` 是否保持在 supporting backlog，而不是被无计划地拉回主线。
3. 只有当 cross-repo adoption 摩擦重复出现时，再提新的 post-M12 里程碑。
