#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import (
    classify_architecture_signal,
    display_execution_task,
    execution_task_lines,
    execution_task_progress,
    first_line,
    labeled_bullet_value,
    normalized_bullets,
    parse_strategy_surface,
    parse_tier,
    read_text,
    section,
)
from progress_snapshot import pretty_text_zh


def bullet_lines(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            items.append(re.sub(r"^\d+\.\s+", "", stripped))
    return items


def first_risk(status_text: str) -> str:
    risks = normalized_bullets(section(status_text, "Blockers / Open Decisions"))
    return risks[0] if risks else "当前无主要风险。"


def zh_tier(tier: str) -> str:
    return {"small": "小型", "medium": "中型", "large": "大型"}.get(tier, tier)


def zh_signal(signal: str) -> str:
    return {"green": "绿色", "yellow": "黄色", "red": "红色"}.get(signal.lower(), signal)


def zh_gate(gate: str) -> str:
    return {
        "continue automatically": "自动继续",
        "raise but continue": "提醒后继续",
        "require user decision": "需要用户裁决",
    }.get(gate.lower(), gate)


def zh_strategy_status(status: str) -> str:
    return {
        "active": "活跃",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
    }.get(status.lower(), humanize_text(status))


def humanize_text(text: str) -> str:
    return pretty_text_zh(text)


def pending_execution_items(task_lines: list[str], limit: int = 3) -> list[str]:
    pending: list[str] = []
    for line in task_lines:
        lowered = line.lower()
        if "[x]" in lowered:
            continue
        item = display_execution_task(line)
        item = re.sub(r"^\[[ xX]\]\s*", "", item).strip()
        pending.append(humanize_text(item))
        if len(pending) >= limit:
            break
    return pending


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a compact continue snapshot for resume-and-keep-going flows.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    tier = parse_tier(repo)
    status_text = read_text(repo / ".codex/status.md")

    current_phase = first_line(section(status_text, "Current Phase")) or "n/a"
    active_slice = first_line(section(status_text, "Active Slice")) or "n/a"
    current_execution_line = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective") or active_slice
    architecture_state = classify_architecture_signal(repo)
    strategy_state = parse_strategy_surface(repo)
    execution_tasks = execution_task_lines(status_text)
    done_tasks, total_tasks = execution_task_progress(execution_tasks)
    next_actions = bullet_lines(section(status_text, "Next 3 Actions"))
    next_work = pending_execution_items(execution_tasks)
    if not next_work:
        next_work = next_actions[:3]

    print("# Continue Snapshot\n")
    print("## 现在在哪里")
    print("| 项目 | 当前值 |")
    print("| --- | --- |")
    print(f"| 层级 | `{zh_tier(tier)}` |")
    print(f"| 当前阶段 | {humanize_text(current_phase)} |")
    print(f"| 当前切片 | {humanize_text(active_slice)} |")
    print(f"| 当前执行线 | {humanize_text(current_execution_line)} |")
    print(f"| 执行进度 | `{done_tasks} / {total_tasks}` |")
    print(f"| 架构信号 | `{zh_signal(architecture_state['signal'])}` |")
    print(f"| 自动触发 | {humanize_text(architecture_state['automatic_review_trigger'])} |")
    print(f"| 升级 Gate | `{zh_gate(architecture_state['gate'])}` |")
    if strategy_state["exists"]:
        print(f"| 战略方向 | {humanize_text(strategy_state['direction'])} |")
        print(f"| 战略状态 | `{zh_strategy_status(strategy_state['status'])}` |")
        print(f"| 下一战略检查 | {humanize_text(strategy_state['next_checks'][0]) if strategy_state['next_checks'] else '暂无'} |")
    print(f"| 当前主要风险 | {humanize_text(first_risk(status_text))} |")
    print("| 完整看板 | `项目助手 进展` / `project assistant progress` |")

    print("\n## 接下来先做什么")
    print("| 顺序 | 当前要做的事 |")
    print("| --- | --- |")
    if next_work:
        for idx, item in enumerate(next_work, start=1):
            print(f"| {idx} | {humanize_text(item)} |")
    else:
        print("| 1 | 暂无下一步记录 |")

    if execution_tasks:
        print("\n## 当前任务板")
        print("| 任务 | 状态 |")
        print("| --- | --- |")
        for item in execution_tasks:
            lowered = item.lower()
            state = "已完成" if "[x]" in lowered else "待完成"
            content = re.sub(r"^\[[ xX]\]\s*", "", display_execution_task(item)).strip()
            print(f"| {humanize_text(content)} | {state} |")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
