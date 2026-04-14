# Program Board

## Current Program Direction
- Direction: `stabilize-daemon-host-baseline-for-dogfooding`
- Status: `active`
- Why Now: keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins

## Program Orchestration Contract

- 程序编排必须引用 `.codex/strategy.md`、`.codex/plan.md`、`.codex/status.md` 和当前 durable 文档，而不是只凭聊天上下文。
- 程序编排层拥有多个 workstreams、切片、执行器输入和串并行边界；它不拥有业务方向变更。
- 任何跨到业务方向、兼容性承诺、外部定位或显著成本 / 时间边界的变化，必须继续升级给人类审批。
- program-board 必须让维护者一眼看出当前有哪些 active workstreams、哪些可并行、下一次调度点是什么。
- 重要的编排收口应写入 devlog，避免只留下结果而没有调度原因。

## Active Workstreams

| Workstream | Scope | State | Priority | Current Focus | Next Checkpoint |
| --- | --- | --- | --- | --- | --- |
| daemon-host baseline stabilization | 把 daemon runtime、queue、VS Code host、continue bridge、legacy rollout、文档与门禁继续收成同一条默认快路径 | active | P0 | 稳住 runtime contract、前门说明和 host 行为 | 更广泛 dogfooding 前保持 baseline 一致 |
| control truth and gates | 保持 `.codex` 真相、门禁和 release 保护一致 | active | P1 | 保持 strategy / program board / delivery supervision / plan / status / handoff 一致 | 继续只允许一套 control truth |
| operator-facing docs and host UX | 让 README / architecture / usage / queue / daemon 输出对维护者和使用者都足够清楚 | active | P1 | 让 daemon-host baseline 的第一屏和说明继续保持结构化、表格优先、可操作 | release 叙事与 operator docs 对齐 |
| supporting backlog routing | 管理 M8 / M9、future host surfaces 和 M15 evidence，不让它们无计划回流主线 | active | P2 | 只有 dogfooding 证据充分时才提升优先级 | 在没有证据前继续保持 backlog |

## Sequencing Queue

| Order | Workstream | Slice / Input | Executor | Status |
| --- | --- | --- | --- | --- |
| 1 | daemon-host baseline stabilization | keep the new runtime / host / continue baseline stable while dogfooding begins | delivery worker | active |
| 2 | control truth and gates | keep supervision surfaces, strategy, program board, plan, status, and handoff aligned | delivery worker | active |
| 3 | operator-facing docs and host UX | keep README / architecture / usage / queue / daemon surfaces aligned with the new baseline | docs-and-release | active |
| 4 | supporting backlog routing | decide when host expansion, M8 / M9 polish, or M15 evidence should re-enter | supervisor | next |

## Executor Inputs

| Executor | Current Input | Why It Exists | Status |
| --- | --- | --- | --- |
| supervisor | `.codex/strategy.md` + `.codex/program-board.md` + `.codex/delivery-supervision.md` + `.codex/entry-routing.md` + `.codex/status.md` | 决定 baseline 稳定化、release 包装与后续 host expansion 怎样排序和回流 | active |
| delivery worker | active slice + execution tasks + validator outputs | 推进当前 checkpoint 并保持 daemon-host baseline 与 program-board 对齐 | active |
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
| M9 slimmer continue snapshot | supporting backlog | 只有当 daemon-host baseline 已稳定且输出仍过重时，才允许进一步压缩 | 保持在 backlog |
| stronger host surfaces / M15 evidence | later / evidence-gated | 只有 dogfooding 证明当前 baseline 已稳定且仍有真实瓶颈时，才允许升主线 | 保持在 backlog |

## Next Orchestration Checks
1. 在更多本地 workspace 上继续 dogfood daemon-host baseline，并记录 runtime / host 摩擦。
2. 继续确认 README / architecture / usage / queue / daemon 输出和控制面真相保持同一套当前叙事。
3. 只有当 adoption 证据证明当前 baseline 已稳定且仍存在真实瓶颈时，才提更强宿主表面或 `M15`。
