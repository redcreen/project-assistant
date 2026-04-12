#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from control_surface_lib import (
    classify_architecture_signal,
    display_execution_task,
    execution_task_lines,
    execution_task_progress,
    first_line,
    labeled_bullet_value,
    parse_tier,
    read_text,
    section,
)


def bullet_lines(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif stripped[:2].isdigit() and ". " in stripped:
            items.append(stripped.split(". ", 1)[1].strip())
    return items


def first_risk(status_text: str) -> str:
    risks = bullet_lines(section(status_text, "Blockers / Open Decisions"))
    return risks[0] if risks else "No major blocker recorded."


def pending_execution_items(task_lines: list[str], limit: int = 3) -> list[str]:
    pending: list[str] = []
    for line in task_lines:
        lowered = line.lower()
        if "[x]" in lowered:
            continue
        pending.append(display_execution_task(line))
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
    execution_tasks = execution_task_lines(status_text)
    done_tasks, total_tasks = execution_task_progress(execution_tasks)
    next_actions = bullet_lines(section(status_text, "Next 3 Actions"))
    next_work = pending_execution_items(execution_tasks)
    if not next_work:
        next_work = next_actions[:3]

    print("# Continue Snapshot\n")
    print("## Continue Now")
    print(f"- Tier: `{tier}`")
    print(f"- Current Phase: `{current_phase}`")
    print(f"- Active Slice: `{active_slice}`")
    print(f"- Long Task: `{current_execution_line}`")
    print(f"- Execution Progress: `{done_tasks} / {total_tasks}`")
    print(f"- Architecture Signal: `{architecture_state['signal']}`")
    print(f"- Escalation Gate: `{architecture_state['gate']}`")
    print(f"- Main Risk: {first_risk(status_text)}")
    print("- Full Dashboard: use `项目助手 进展` / `project assistant progress` if you want the full global view.")

    print("\n## Next Work")
    if next_work:
        for idx, item in enumerate(next_work, start=1):
            print(f"{idx}. {item}")
    else:
        print("1. No next work item recorded.")

    if execution_tasks:
        print("\n## Task Board")
        for item in execution_tasks:
            print(f"- {display_execution_task(item)}")

    if next_actions:
        print("\n## Stored Next 3 Actions")
        for idx, item in enumerate(next_actions[:3], start=1):
            print(f"{idx}. {item}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
