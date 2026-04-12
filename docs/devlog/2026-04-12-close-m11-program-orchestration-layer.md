# Close M11 Program Orchestration Layer

## Problem

`M10` 已经把战略层变成 durable 能力，但多个 workstreams、切片和执行器的长期推进还没有一份真正可恢复、可校验、可展示的 `program-board`。如果继续推进到 `M12`，维护者会再次退回“知道大方向，但看不清编排边界”的状态。

## Thinking

`M11` 不该只新增一个文件名。要让程序编排层真正成立，至少需要四件事同时出现：durable 的 `.codex/program-board.md`、可复用的 sync / validate 路径、维护者第一屏能直接看到程序编排状态，以及 README / roadmap / development-plan 都承认它已经是当前真相。如果缺任何一项，程序编排层就仍然停留在提案或草图阶段。

## Solution

新增 `sync_program_board.py` 与 `validate_program_board.py`，把 `.codex/program-board.md` 变成正式控制面；让 `sync_control_surface.py` 和 `validate_gate_set.py` 默认接入这条链路；把 `progress / continue / handoff` 加上程序编排视角；然后把 README、roadmap、development plan、strategy surface、plan、status 一起切到 `M11 done / M12 next`，避免 durable docs 与控制面描述不同步。

## Validation

- `python3 scripts/validate_program_board.py . --format text`
- `python3 scripts/validate_gate_set.py . --profile deep`
- `python3 scripts/validate_gate_set.py . --profile release`
- `python3 scripts/progress_snapshot.py .`
- `python3 scripts/continue_snapshot.py .`
- `python3 scripts/context_handoff.py .`
