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
    replacement = rf"\1{body.rstrip()}\n\n"
    updated, count = re.subn(pattern, replacement, text, flags=re.MULTILINE | re.DOTALL)
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
        ("control truth and gates", "保持 `.codex` 真相、门禁和 release 保护一致", "active", "P0", "把 strategy / program board / plan / status 维持在同一套真相上", "继续只允许一套 control truth"),
        ("maintainer-facing outputs", "让 progress / continue / handoff 对维护者和未来接手者足够清楚", "active", "P0", "把程序编排状态直接暴露到第一屏输出", "继续压掉必须人工翻译的编排状态"),
        ("docs and durable planning", "保持 README / roadmap / development-plan / strategy docs 对齐", "active", "P1", "让 M11 与 M12 的层次关系在 durable docs 里清楚可追", "只在里程碑切换时更新"),
        ("supporting backlog routing", "管理 M8 / M9 这类 supporting backlog 议题，不让它们无计划回流主线", "active", "P1", "明确 supporting backlog 如何被重新吸收", "在 M12 前决定哪些继续保持 backlog"),
    ]
    lines = ["| Workstream | Scope | State | Priority | Current Focus | Next Checkpoint |", "| --- | --- | --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} | {e} | {f} |" for a, b, c, d, e, f in rows)
    return "\n".join(lines)


def sequencing_queue_table() -> str:
    rows = [
        ("1", "control truth and gates", "define durable program-board structure and control-truth ownership", "supervisor", "done"),
        ("2", "maintainer-facing outputs", "wire program-board summaries into progress / continue / handoff", "delivery worker", "done"),
        ("3", "docs and durable planning", "align README / roadmap / development-plan with M11 and M12", "docs-and-release", "done"),
        ("4", "supporting backlog routing", "keep M8 / M9 explicit as supporting backlog instead of accidental mainline work", "supervisor", "done"),
    ]
    lines = ["| Order | Workstream | Slice / Input | Executor | Status |", "| --- | --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows)
    return "\n".join(lines)


def executor_inputs_table() -> str:
    rows = [
        ("supervisor", "`.codex/strategy.md` + `.codex/program-board.md` + `.codex/status.md`", "定义 workstream 边界、调度顺序和升级点", "done"),
        ("delivery worker", "active slice + execution tasks + validator outputs", "推进当前切片并保持与 program-board 对齐", "done"),
        ("docs-and-release", "README + roadmap + development-plan + gate outputs", "保持 durable docs、发布说明和门禁一致", "done"),
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
        "为 M12 定义第一版受监督长跑交付的 checkpoint 节奏和自动升级规则。",
        "选择第一条真正进入长期监督交付层的 workstream，而不是继续停在编排演示层。",
        "继续确认 M8 / M9 是否保持在 supporting backlog，而不是被无计划地拉回主线。",
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
        if not section(text, heading).strip():
            text = replace_section(text, heading, body)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(".codex/program-board.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
