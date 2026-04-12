#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import (
    first_line,
    labeled_bullet_value,
    parse_strategy_surface,
    read_text,
    section,
    strategy_surface_expected,
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


def strategy_direction(repo: Path) -> tuple[str, str, str]:
    plan_text = read_text(repo / ".codex/plan.md")
    status_text = read_text(repo / ".codex/status.md")
    current_phase = first_line(section(status_text, "Current Phase")) or first_line(section(plan_text, "Current Phase"))
    objective = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective") or labeled_bullet_value(
        section(plan_text, "Current Execution Line"), "Objective"
    )
    status = "active"
    direction = "strategic evaluation layer"
    if "program orchestration" in current_phase.lower() or "程序编排" in current_phase:
        direction = "program orchestration layer"
    why_now = (
        "执行层、整改层、文档治理层和恢复层已经基本成形，当前最大的缺口转成“项目后续怎么走、何时插专项、何时调整路线”的更高层判断。"
    )
    if objective:
        why_now = objective
    return direction, status, why_now


def evidence_contract(repo: Path) -> list[str]:
    items = [
        "战略建议必须引用 roadmap、development plan、当前 `.codex/status.md` 和 `.codex/plan.md`，不能只凭聊天直觉。",
        "如果建议插入治理专项或架构专项，必须说明触发它的 durable repo 证据，而不是只说“感觉应该做”。",
        "如果建议调整 milestone 顺序，必须指出当前顺序哪里已经和真实执行不一致，以及调整后会减少什么长期风险。",
        "如果问题跨到业务方向、兼容性承诺、外部定位或显著成本 / 时间边界，必须升级给人类裁决。",
    ]
    if (repo / "docs/devlog").exists():
        items.append("重要战略判断应落成 devlog，避免下一次回来时只剩结论没有推理链。")
    return items


def owns_table(repo: Path) -> str:
    rows = [
        ("roadmap 调整建议", "yes", "但只提建议，不自动改业务方向"),
        ("是否插入治理 / 架构专项", "yes", "需要基于 repo 证据和长期风险"),
        ("项目定位是否需要提升", "yes", "作为建议输出，仍需人类审批"),
        ("多个切片 / 多个执行器编排", "not yet", "留给 M11"),
        ("长时间自动交付", "not yet", "留给 M12"),
    ]
    lines = ["| Topic | Strategic Layer Owns? | Notes |", "| --- | --- | --- |"]
    lines.extend(f"| {topic} | {owns} | {notes} |" for topic, owns, notes in rows)
    return "\n".join(lines)


def carryover_backlog_table(repo: Path) -> str:
    rows = [
        ("M8 locale-aware internal output", "supporting backlog", "这是表现层优化，不再是当前最大缺口"),
        ("M9 slimmer continue snapshot", "supporting backlog", "这是恢复体量优化，不再是当前最大缺口"),
    ]
    if not (repo / "README.zh-CN.md").exists():
        rows = [
            ("future strategic side-track candidates", "supporting backlog", "等待后续战略判断决定是否拉回主线"),
        ]
    lines = ["| Topic | Current Position | Why It Is Not Mainline |", "| --- | --- | --- |"]
    lines.extend(f"| {topic} | {position} | {why} |" for topic, position, why in rows)
    return "\n".join(lines)


def human_review_boundary() -> str:
    return "\n".join(
        [
            "- Human Approves:",
            "  - business direction changes",
            "  - compatibility promises",
            "  - external positioning changes",
            "  - significant cost or timeline tradeoffs",
            "- System May Propose:",
            "  - roadmap reshaping",
            "  - governance / architecture side-tracks",
            "  - milestone reorder suggestions",
            "  - strategic carryover decisions for supporting backlog topics",
        ]
    )


def future_program_board_boundary() -> str:
    return "\n".join(
        [
            "- M10 owns strategic judgment, evidence-backed suggestions, and the human review boundary.",
            "- M11 should own sequencing, orchestration, parallel-safe slices, and durable program-board state.",
            "- Do not let M10 silently grow into full orchestration before the program-board contract exists.",
        ]
    )


def next_checks(repo: Path) -> list[str]:
    existing = parse_strategy_surface(repo).get("next_checks", [])
    if existing:
        return existing
    return [
        "定义战略判断必须引用哪些 durable repo 证据。",
        "定义什么情况下战略层可以建议插入治理 / 架构专项。",
        "先设计 M11 所需的 `program-board`，但不提前激活程序编排。",
    ]


def render_strategy(repo: Path) -> str:
    direction, status, why_now = strategy_direction(repo)
    lines = [
        "# Strategy",
        "",
        "## Current Strategic Direction",
        "",
        f"- Direction: `{direction}`",
        f"- Status: `{status}`",
        f"- Why Now: {why_now}",
        "",
        "## Strategy Evidence Contract",
        "",
    ]
    lines.extend(f"- {item}" for item in evidence_contract(repo))
    lines.extend(
        [
            "",
            "## What This Layer Owns",
            "",
            owns_table(repo),
            "",
            "## Carryover Backlog",
            "",
            carryover_backlog_table(repo),
            "",
            "## Human Review Boundary",
            "",
            human_review_boundary(),
            "",
            "## Future Program-Board Boundary",
            "",
            future_program_board_boundary(),
            "",
            "## Next Strategic Checks",
            "",
        ]
    )
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(next_checks(repo), start=1))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or refresh a durable strategic surface when the strategy layer is active.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/strategy.md"
    if not strategy_surface_expected(repo):
        if path.exists():
            print(".codex/strategy.md already exists; no strategic sync needed")
        else:
            print("strategy surface not expected for this repo")
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    text = read_text(path)
    if not text:
        path.write_text(render_strategy(repo), encoding="utf-8")
        print(".codex/strategy.md")
        return 0

    rendered = render_strategy(repo)
    always_refresh = {"Current Strategic Direction", "Next Strategic Checks"}
    for heading in [
        "Current Strategic Direction",
        "Strategy Evidence Contract",
        "What This Layer Owns",
        "Carryover Backlog",
        "Human Review Boundary",
        "Future Program-Board Boundary",
        "Next Strategic Checks",
    ]:
        body = section(rendered, heading)
        if heading in always_refresh or not section(text, heading).strip():
            text = replace_section(text, heading, body)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(".codex/strategy.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
