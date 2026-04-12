#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import (
    display_execution_task,
    execution_task_lines,
    execution_task_progress,
    first_line,
    labeled_bullet_value,
    parse_tier,
    section,
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""
def bullet_lines(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            items.append(re.sub(r"^\d+\.\s+", "", stripped))
    return items


def detect_commands(repo: Path) -> tuple[str, str, list[str]]:
    primary_test_cn = "根据仓库测试入口执行验证"
    primary_test_en = "run the repo's primary test entry"
    extra_checks: list[str] = []

    package_json = repo / "package.json"
    if package_json.exists():
        try:
            scripts = json.loads(package_json.read_text(encoding="utf-8")).get("scripts", {})
        except json.JSONDecodeError:
            scripts = {}
        if "test" in scripts:
            primary_test_cn = "npm test"
            primary_test_en = "npm test"
        for name in ["eval:smoke-promotion", "test:smoke", "lint", "build"]:
            if name in scripts:
                extra_checks.append(f"npm run {name}")
        return primary_test_cn, primary_test_en, extra_checks

    if (repo / "pyproject.toml").exists() or (repo / "pytest.ini").exists():
        return "pytest", "pytest", extra_checks

    if (repo / "Cargo.toml").exists():
        return "cargo test", "cargo test", extra_checks

    return primary_test_cn, primary_test_en, extra_checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit a compact context handoff / resume pack for a repo.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    tier = parse_tier(repo)
    status_text = read_text(repo / ".codex/status.md")
    module_dashboard = read_text(repo / ".codex/module-dashboard.md")

    current_phase = first_line(section(status_text, "Current Phase")) or "n/a"
    active_slice = first_line(section(status_text, "Active Slice")) or "n/a"
    current_execution_line = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective") or active_slice
    execution_tasks = execution_task_lines(status_text)
    done_tasks, total_tasks = execution_task_progress(execution_tasks)
    blockers = bullet_lines(section(status_text, "Blockers / Open Decisions"))
    main_risk = blockers[0] if blockers else "No major blocker recorded."
    next_actions = bullet_lines(section(status_text, "Next 3 Actions"))
    active_module = first_line(section(module_dashboard, "Summary").replace("- Active Module:", "").strip())
    if not active_module or active_module.startswith("- "):
        summary_lines = [line.strip() for line in section(module_dashboard, "Summary").splitlines()]
        active_module = "n/a"
        for line in summary_lines:
            if line.startswith("- Active Module:"):
                active_module = line.split(":", 1)[1].strip()
                break

    primary_test_cn, primary_test_en, extra_checks = detect_commands(repo)
    restore_docs = [
        ".codex/status.md",
        ".codex/plan.md",
        ".codex/module-dashboard.md" if tier == "large" else ".codex/brief.md",
    ]

    print("# Context Handoff\n")
    print("## Summary")
    print(f"- Repo: `{repo}`")
    print(f"- Tier: `{tier}`")
    print(f"- Current Phase: `{current_phase}`")
    print(f"- Active Slice: `{active_slice}`")
    print(f"- Current Execution Line: `{current_execution_line}`")
    print(f"- Execution Progress: `{done_tasks} / {total_tasks}`")
    if tier == "large":
        print(f"- Active Module: `{active_module}`")
    print(f"- Main Risk: {main_risk}")

    print("\n## Restore Order")
    for idx, item in enumerate(restore_docs, start=1):
        print(f"{idx}. `{item}`")

    docs_cn = "、".join(restore_docs)
    docs_en = ", ".join(restore_docs)

    print("\n## Copy-Paste Commands")
    print("\n### Chinese")
    print("```text")
    print(
        f"项目助手 恢复当前项目状态，然后继续当前执行线：{current_execution_line}。先读取 "
        + docs_cn
        + "。"
    )
    print("项目助手 告诉我这个项目当前进展，用全局视角、模块视角和图示输出。")
    test_line = f"项目助手 继续当前执行线，并先运行验证：{primary_test_cn}"
    if extra_checks:
        test_line += "；补充检查：" + "，".join(extra_checks)
    print(test_line + "。")
    print("```")

    print("\n### English")
    print("```text")
    print(
        f"project assistant resume current status and continue the current execution line: {current_execution_line}. "
        f"Read {docs_en} first."
    )
    print("project assistant progress")
    test_line = f"project assistant continue the current execution line and run validation first: {primary_test_en}"
    if extra_checks:
        test_line += "; extra checks: " + ", ".join(extra_checks)
    print(test_line + ".")
    print("```")

    print("\n## Next 3 Actions")
    if next_actions:
        for idx, item in enumerate(next_actions[:3], start=1):
            print(f"{idx}. {item}")
    else:
        print("1. No next actions recorded.")

    if execution_tasks:
        print("\n## Execution Tasks")
        for idx, item in enumerate(execution_tasks, start=1):
            print(f"{idx}. {display_execution_task(item)}")

    print("\n## Notes")
    print("- Start a new thread with this output and the repo path when you need a clean context.")
    print("- For large projects, read `.codex/module-dashboard.md` before `modules/*.md` after restore.")
    print("- 如果使用中文继续，也可以直接复制上面的中文命令。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
