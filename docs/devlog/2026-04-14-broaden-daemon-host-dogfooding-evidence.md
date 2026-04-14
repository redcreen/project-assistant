# Broaden daemon-host dogfooding evidence before any new host surface

- Date: 2026-04-14
- Status: resolved

## Problem

`M17-M21` 的 daemon-host baseline 已经在 self-repo、clean fixture 和 legacy fixture 上通过，但当前切片 `stabilize-daemon-host-baseline-for-dogfooding` 的下一动作不是继续开新宿主表面，而是先证明这条 baseline 在更广泛的真实 workspace 上也能复用。没有这层证据，就无法合理讨论 release packaging uplift、更重的 host surface，或任何 `M15` 重新升温。

## Thinking

如果只重复跑 fixture，得到的仍然是“验证脚本没坏”，而不是“真实使用开始成立”。更合适的证据是直接选现成的真实本地仓库，用 daemon clean session 分别跑 `continue / progress / handoff`，确认统一前门、任务日志和结构化 heading 在 repo 外也成立。与此同时，要把证据写回 durable surface，而不是停留在一次命令输出里。

## Solution

使用 `daemon_validation_lib` 在两个真实本地 repo 上启动 clean daemon session：`/Users/redcreen/Project/unified-memory-core` 与 `/Users/redcreen/Project/codex limit`。对每个 repo 依次执行 `continue`、`progress`、`handoff`，等待任务完成并检查输出 heading 与任务日志路径。随后把这批结果写回 `.codex/dogfooding-evidence.md`，并同步 `.codex/status.md`、`.codex/plan.md`，把 `EL-3` 从“准备采证”推进到“已有 broader real-workspace evidence”。同时保留 `EL-4` 为 evidence-gated backlog，不因为两次成功就提前打开 single foreground writer 主线。

## Validation

两个真实本地 repo 均通过 daemon-host `continue / progress / handoff` 采证；`validate_dogfooding_evidence.py --format json` 返回 `ok: true`，`validate_vscode_host_extension.py --format json` 返回 `ok: true`。这说明 broader dogfooding 证据面已经从 self-repo + fixtures 扩展到真实 workspace，而 evidence surface 仍然可被脚本校验。

## Follow-up

- 继续补更多真实 workspace 采证，优先覆盖不同 repo 形态、不同持续时长和不同操作者。
- 只有当 broader evidence 持续增加且没有重复 runtime / host / operator-doc regressions 时，再讨论 release packaging uplift。
- `single foreground writer per repo` 继续保留为 evidence-gated backlog，等待真实 adoption 暴露冲突。

## Related Files

- .codex/dogfooding-evidence.md
- .codex/status.md
- .codex/plan.md
- scripts/daemon_validation_lib.py
- scripts/validate_dogfooding_evidence.py
