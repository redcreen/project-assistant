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
    active_slice = first_line(section(status_text, "Active Slice")) or first_line(section(plan_text, "Active Slice"))
    objective = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective") or labeled_bullet_value(
        section(plan_text, "Current Execution Line"), "Objective"
    )
    status = "active"
    lowered = current_phase.lower()
    if any(token in lowered for token in ["done", "completed", "closed", "已完成", "已收口"]):
        status = "done"
    elif any(token in lowered for token in ["next", "later", "queued", "下一", "后续", "排队"]):
        status = "next"
    direction = active_slice or current_phase or "current repo direction"
    why_now = objective or current_phase or "需要持续确认 roadmap、当前切片和长期方向仍保持一致。"
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
        ("roadmap / development plan 对齐建议", "yes", "可以建议调整，但不代替业务裁决"),
        ("是否插入治理 / 架构专项", "yes", "需要基于 repo 证据和长期风险"),
        ("当前切片是否仍是主线", "yes", "用于判断继续、重排或挂回 backlog"),
        ("项目定位是否需要提升", "yes", "只提出建议，仍需人类审批"),
        ("业务方向变化", "no", "必须升级给人类"),
    ]
    lines = ["| Topic | Strategic Layer Owns? | Notes |", "| --- | --- | --- |"]
    lines.extend(f"| {topic} | {owns} | {notes} |" for topic, owns, notes in rows)
    return "\n".join(lines)


def carryover_backlog_table(repo: Path) -> str:
    rows = [
        ("future governance / architecture side-track", "supporting backlog", "只有 durable 证据证明当前主线无法继续时，才回拉主线"),
        ("maintainer-facing polish", "supporting backlog", "只有它能明显降低接手成本时，才升级优先级"),
        ("release / rollout follow-ups", "supporting backlog", "只有 release-facing 风险出现时，才回流当前阶段"),
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
            "- 战略层负责判断“为什么下一步是这条线”，以及何时建议插入专项或调整路线。",
            "- 程序编排层负责把战略判断翻译成 workstream、切片顺序和串并行边界。",
            "- 不要让战略层静默膨胀成全能调度器；编排仍应保留在 program-board。"
        ]
    )


def next_checks(repo: Path) -> list[str]:
    existing = parse_strategy_surface(repo).get("next_checks", [])
    if existing:
        return existing
    return [
        "确认 roadmap、development plan、当前切片和 Next 3 仍在同一条主线里。",
        "判断当前 blocker 或重复修补是否已经需要插入治理 / 架构专项。",
        "如果里程碑顺序、项目定位或长期目标需要调整，整理成待人类审批的建议。",
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
