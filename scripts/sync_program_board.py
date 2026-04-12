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
    active_slice = first_line(section(status_text, "Active Slice")) or first_line(section(plan_text, "Active Slice"))
    objective = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective") or labeled_bullet_value(
        section(plan_text, "Current Execution Line"), "Objective"
    )
    lowered = current_phase.lower()
    status = "active"
    if "closed" in lowered or "收口" in current_phase or "queued" in lowered or "排队" in current_phase:
        status = "done"
    elif "next" in lowered or "queued" in lowered:
        status = "next"
    direction = active_slice or current_phase or "current repo program flow"
    why_now = objective or current_phase or "需要把主线、sidecar 和 backlog 的顺序维持在同一套 durable 真相上。"
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
        ("primary delivery line", "当前 active slice 与当前执行线", "active", "P0", "保持当前主线持续推进", "到达下一个 checkpoint 并刷新真相"),
        ("control truth and docs alignment", "plan / status / roadmap / development plan / docs", "active", "P1", "保持控制面、文档与当前执行同步", "避免恢复真相漂移"),
        ("validation and release gates", "tests / gate / release-facing evidence", "active", "P1", "保持验证入口与当前主线对齐", "下一轮变更前保持为绿"),
        ("supporting backlog routing", "暂不进入主线但需要保留可见性的议题", "active", "P2", "记录但不无计划回流主线", "只有证据充分时才升级"),
    ]
    lines = ["| Workstream | Scope | State | Priority | Current Focus | Next Checkpoint |", "| --- | --- | --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in rows)
    return "\n".join(lines)


def sequencing_queue_table() -> str:
    rows = [
        ("1", "primary delivery line", "继续当前 active slice 与当前执行线", "delivery worker", "active"),
        ("2", "control truth and docs alignment", "保持 plan / status / docs / handoff 同步", "docs-and-release", "active"),
        ("3", "validation and release gates", "运行 tests / gate 并把结果写回真相", "delivery worker", "active"),
        ("4", "supporting backlog routing", "判断哪些尾项回队列、哪些需要下轮主线", "PTL", "next"),
    ]
    lines = ["| Order | Workstream | Slice / Input | Executor | Status |", "| --- | --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows)
    return "\n".join(lines)


def executor_inputs_table() -> str:
    rows = [
        ("PTL", "`.codex/strategy.md` + `.codex/program-board.md` + `.codex/delivery-supervision.md` + `.codex/status.md`", "决定当前主线是否继续、重排或升级", "active"),
        ("delivery worker", "active slice + execution tasks + validator outputs", "推进当前 checkpoint 并保持与 program-board 对齐", "active"),
        ("docs-and-release", "README + roadmap + development-plan + gate outputs", "保持 durable docs、交接说明和门禁一致", "active"),
    ]
    lines = ["| Executor | Current Input | Why It Exists | Status |", "| --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return "\n".join(lines)


def parallel_safe_boundaries_table() -> str:
    rows = [
        ("读文件 / 快照 / 校验 / 测试", "yes", "安全的只读动作可以和主写入线并行"),
        ("docs alignment vs control truth", "yes", "文档更新可以跟随 control truth，但 `.codex/plan.md` / `.codex/status.md` 仍保持唯一真相源"),
        ("同一批文件的双写入", "no", "共享写入面必须串行，不要并行改同一套控制面或主代码边界"),
        ("战略变化 vs 业务方向变化", "no", "一旦跨到业务方向、兼容性或外部定位，就必须停下来给人类审批"),
    ]
    lines = ["| Boundary | Parallel-Safe? | Notes |", "| --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return "\n".join(lines)


def supporting_backlog_table() -> str:
    rows = [
        ("maintainer-facing polish", "supporting backlog", "只有明确降低接手成本时，才允许回流主线", "保持在 backlog"),
        ("doc-only tidy-up", "supporting backlog", "只有不会干扰当前主线且能降低恢复成本时，才并入下个 checkpoint", "按 sidecar 处理"),
        ("future governance / architecture side-track", "supporting backlog", "只有 durable 证据显示当前主线不够时，才升级", "先记录，不抢主线"),
    ]
    lines = ["| Topic | Current Position | Re-entry Rule | Notes |", "| --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return "\n".join(lines)


def next_checks(repo: Path) -> list[str]:
    existing = parse_program_board(repo).get("next_checks", [])
    if existing:
        return existing
    return [
        "确认当前 active slice、执行线和 supporting backlog 仍保持同一套排序真相。",
        "判断哪些 sidecar 工作可以并入下个 checkpoint，哪些必须继续留在队列里。",
        "如果单 Codex PTL 模式在真实仓库里成为瓶颈，再整理成后续多执行器候选。",
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
