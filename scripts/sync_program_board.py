#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import (
    first_line,
    labeled_bullet_value,
    parse_program_board,
    read_text,
    section,
    program_board_expected,
)


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    updated, count = re.subn(
        pattern,
        lambda match: f"{match.group(1)}{body.rstrip()}\n\n",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if count:
        return updated.rstrip() + "\n"
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def program_direction(repo: Path) -> tuple[str, str, str]:
    plan_text = read_text(repo / ".codex/plan.md")
    status_text = read_text(repo / ".codex/status.md")
    current_phase = first_line(section(status_text, "Current Phase")) or first_line(section(plan_text, "Current Phase"))
    objective = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective") or labeled_bullet_value(
        section(plan_text, "Current Execution Line"), "Objective"
    )
    lowered = current_phase.lower()
    status = "active"
    if "closed" in lowered or "收口" in current_phase or "queued" in lowered or "排队" in current_phase:
        status = "done"
    elif "next" in lowered or "queued" in lowered:
        status = "next"
    direction = "program orchestration layer"
    why_now = (
        "战略评估层已经把“项目为什么往这边走”收口成 durable 真相，当前最大的缺口转成怎样管理多个 workstreams、切片和执行器，而不是继续靠人工不断输入“继续”。"
    )
    if objective:
        why_now = objective
    return direction, status, why_now


def orchestration_contract() -> list[str]:
    return [
        "程序编排必须引用 `.codex/strategy.md`、`.codex/plan.md`、`.codex/status.md` 和当前 durable 文档，而不是只凭聊天上下文。",
        "程序编排层拥有多个 workstreams、切片、执行器输入和串并行边界；它不拥有业务方向变更。",
        "任何跨到业务方向、兼容性承诺、外部定位或显著成本 / 时间边界的变化，必须继续升级给人类审批。",
        "program-board 必须让维护者一眼看出当前有哪些 active workstreams、哪些可并行、下一次调度点是什么。",
        "重要的编排收口应写入 devlog，避免只留下结果而没有调度原因。",
    ]


def active_workstreams_table() -> str:
    rows = [
        ("post-M14 evidence collection", "在更多仓库上 rollout PTL supervision + worker handoff，并记录是否真的需要 M15", "active", "P0", "采集 worker 停下后的真实接续摩擦、写入边界和回收口证据", "决定 M15 是否值得立项"),
        ("control truth and gates", "保持 `.codex` 真相、门禁和 release 保护一致", "stable", "P1", "把 strategy / program board / plan / status / supervision surfaces 维持在同一套真相上", "继续只允许一套 control truth"),
        ("maintainer-facing outputs", "让 progress / continue / handoff 对维护者和未来接手者足够清楚", "stable", "P1", "把 PTL supervision / worker handoff 状态直接暴露到第一屏输出", "只有 rollout 证据要求时再调整"),
        ("supporting backlog routing", "管理 M8 / M9 这类 supporting backlog 议题，不让它们无计划回流主线", "active", "P1", "用 rollout 证据决定 M8 / M9 是否继续保持 backlog", "在没有证据前继续保持 backlog"),
    ]
    lines = ["| Workstream | Scope | State | Priority | Current Focus | Next Checkpoint |", "| --- | --- | --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in rows)
    return "\n".join(lines)


def sequencing_queue_table() -> str:
    rows = [
        ("1", "post-M14 evidence collection", "carry PTL supervision + worker handoff onto more repos and record friction", "supervisor", "active"),
        ("2", "control truth and gates", "keep supervision surfaces, plan, and status aligned while rollout evidence accumulates", "delivery worker", "active"),
        ("3", "maintainer-facing outputs", "only refine progress / continue / handoff if rollout evidence shows maintainer confusion", "docs-and-release", "active"),
        ("4", "supporting backlog routing", "decide whether M8 / M9 stay backlog or re-enter with evidence", "supervisor", "next"),
    ]
    lines = ["| Order | Workstream | Slice / Input | Executor | Status |", "| --- | --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows)
    return "\n".join(lines)


def executor_inputs_table() -> str:
    rows = [
        ("supervisor", "`.codex/strategy.md` + `.codex/program-board.md` + `.codex/delivery-supervision.md` + `.codex/status.md`", "决定 rollout 证据怎么回流成 M15 判断或 backlog 调整", "active"),
        ("delivery worker", "active slice + execution tasks + validator outputs", "推进当前 checkpoint 并保持与 program-board 对齐", "active"),
        ("docs-and-release", "README + roadmap + development-plan + gate outputs", "保持 durable docs、发布说明和门禁一致", "active"),
    ]
    lines = ["| Executor | Current Input | Why It Exists | Status |", "| --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return "\n".join(lines)


def parallel_safe_boundaries_table() -> str:
    rows = [
        ("control truth vs docs alignment", "yes", "文档更新可以跟随 control truth，但 `.codex/plan.md` / `.codex/status.md` 仍保持唯一真相源"),
        ("maintainer outputs vs docs alignment", "yes", "progress / continue / handoff 的展示更新可以和 README / roadmap 调整并行"),
        ("strategy changes vs business direction changes", "no", "一旦跨到业务方向、兼容性或外部定位，就必须停下来给人类审批"),
    ]
    lines = ["| Boundary | Parallel-Safe? | Notes |", "| --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return "\n".join(lines)


def supporting_backlog_table() -> str:
    rows = [
        ("M8 locale-aware internal output", "supporting backlog", "只有当它能降低维护者摩擦且不分叉真相时，才允许重新吸收", "保持在 backlog"),
        ("M9 slimmer continue snapshot", "supporting backlog", "只有当 program-board 已能承载恢复真相时，才允许进一步压缩 continue 输出", "保持在 backlog"),
    ]
    lines = ["| Topic | Current Position | Re-entry Rule | Notes |", "| --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return "\n".join(lines)


def next_checks(repo: Path) -> list[str]:
    existing = parse_program_board(repo).get("next_checks", [])
    if existing:
        return existing
    return [
        "在更多 medium / large 仓库上使用完整的 PTL supervision + worker handoff 模型，并记录真实接续摩擦。",
        "继续确认 `M8 / M9` 是否保持在 supporting backlog，而不是被无计划地拉回主线。",
        "只有当 cross-repo 证据证明单 Codex PTL 模式成为瓶颈时，才提 `M15`。",
    ]


def render_program_board(repo: Path) -> str:
    direction, status, why_now = program_direction(repo)
    lines = [
        "# Program Board",
        "",
        "## Current Program Direction",
        "",
        f"- Direction: `{direction}`",
        f"- Status: `{status}`",
        f"- Why Now: {why_now}",
        "",
        "## Program Orchestration Contract",
        "",
    ]
    lines.extend(f"- {item}" for item in orchestration_contract())
    lines.extend(
        [
            "",
            "## Active Workstreams",
            "",
            active_workstreams_table(),
            "",
            "## Sequencing Queue",
            "",
            sequencing_queue_table(),
            "",
            "## Executor Inputs",
            "",
            executor_inputs_table(),
            "",
            "## Parallel-Safe Boundaries",
            "",
            parallel_safe_boundaries_table(),
            "",
            "## Supporting Backlog Routing",
            "",
            supporting_backlog_table(),
            "",
            "## Next Orchestration Checks",
            "",
        ]
    )
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(next_checks(repo), start=1))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or refresh a durable program board when the orchestration layer is expected.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/program-board.md"
    if not program_board_expected(repo):
        if path.exists():
            print(".codex/program-board.md already exists; no program-board sync needed")
        else:
            print("program board not expected for this repo")
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    text = read_text(path)
    if not text:
        path.write_text(render_program_board(repo), encoding="utf-8")
        print(".codex/program-board.md")
        return 0

    rendered = render_program_board(repo)
    always_refresh = {"Current Program Direction", "Next Orchestration Checks"}
    for heading in [
        "Current Program Direction",
        "Program Orchestration Contract",
        "Active Workstreams",
        "Sequencing Queue",
        "Executor Inputs",
        "Parallel-Safe Boundaries",
        "Supporting Backlog Routing",
        "Next Orchestration Checks",
    ]:
        body = section(rendered, heading)
        if heading in always_refresh or not section(text, heading).strip():
            text = replace_section(text, heading, body)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(".codex/program-board.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
