#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
    parse_delivery_supervision,
    parse_ptl_supervision,
    parse_program_board,
    parse_strategy_surface,
    parse_worker_handoff,
    parse_tier,
    primary_human_windows,
    repo_capabilities,
    section,
)
from progress_snapshot import pretty_text_zh


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


def contains_cjk(text: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


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
    }.get(status.lower(), pretty_text_zh(status))


def zh_program_status(status: str) -> str:
    return {
        "active": "活跃",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
    }.get(status.lower(), pretty_text_zh(status))


def zh_delivery_status(status: str) -> str:
    return {
        "active": "活跃",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
    }.get(status.lower(), pretty_text_zh(status))


def zh_ptl_status(status: str) -> str:
    return {
        "active": "活跃",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
    }.get(status.lower(), pretty_text_zh(status))


def zh_handoff_status(status: str) -> str:
    return {
        "active": "活跃",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
    }.get(status.lower(), pretty_text_zh(status))


def humanize_text(text: str) -> str:
    return pretty_text_zh(text)


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
    english_execution_line = current_execution_line
    if contains_cjk(english_execution_line):
        english_execution_line = labeled_bullet_value(section(status_text, "Current Execution Line"), "Plan Link") or active_slice
    architecture_state = classify_architecture_signal(repo)
    strategy_state = parse_strategy_surface(repo)
    program_state = parse_program_board(repo)
    delivery_state = parse_delivery_supervision(repo)
    ptl_state = parse_ptl_supervision(repo)
    handoff_state = parse_worker_handoff(repo)
    architecture_signal = architecture_state["signal"]
    escalation_gate = architecture_state["gate"]
    escalation_reason = architecture_state["reason"]
    execution_tasks = execution_task_lines(status_text)
    done_tasks, total_tasks = execution_task_progress(execution_tasks)
    capabilities = repo_capabilities(repo)
    human_windows_zh = primary_human_windows("zh")
    human_windows_en = primary_human_windows("en")
    blockers = normalized_bullets(section(status_text, "Blockers / Open Decisions"))
    main_risk = blockers[0] if blockers else "当前无主要风险。"
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
    if strategy_state["exists"]:
        restore_docs.insert(2, ".codex/strategy.md")
    if program_state["exists"]:
        restore_docs.insert(3 if strategy_state["exists"] else 2, ".codex/program-board.md")
    if delivery_state["exists"]:
        restore_docs.insert(4 if strategy_state["exists"] and program_state["exists"] else 3 if (strategy_state["exists"] or program_state["exists"]) else 2, ".codex/delivery-supervision.md")
    if ptl_state["exists"]:
        restore_docs.append(".codex/ptl-supervision.md")
    if handoff_state["exists"]:
        restore_docs.append(".codex/worker-handoff.md")

    print("# Context Handoff\n")
    print("## 摘要")
    print("| 项目 | 当前值 |")
    print("| --- | --- |")
    print(f"| 仓库 | `{repo}` |")
    print(f"| 层级 | `{zh_tier(tier)}` |")
    print(f"| 当前阶段 | {humanize_text(current_phase)} |")
    print(f"| 当前切片 | {humanize_text(active_slice)} |")
    print(f"| 当前执行线 | {humanize_text(current_execution_line)} |")
    print(f"| 执行进度 | `{done_tasks} / {total_tasks}` |")
    print(f"| 架构信号 | `{zh_signal(architecture_signal)}` |")
    print(f"| 自动触发 | {humanize_text(architecture_state['automatic_review_trigger'])} |")
    print(f"| 升级 Gate | `{zh_gate(escalation_gate)}` |")
    if strategy_state["exists"]:
        print(f"| 战略方向 | {humanize_text(strategy_state['direction'])} |")
        print(f"| 战略状态 | `{zh_strategy_status(strategy_state['status'])}` |")
        print(f"| 下一战略检查 | {humanize_text(strategy_state['next_checks'][0]) if strategy_state['next_checks'] else '暂无'} |")
    if program_state["exists"]:
        print(f"| 程序编排方向 | {humanize_text(program_state['direction'])} |")
        print(f"| 程序编排状态 | `{zh_program_status(program_state['status'])}` |")
        print(f"| 下一程序检查 | {humanize_text(program_state['next_checks'][0]) if program_state['next_checks'] else '暂无'} |")
    if delivery_state["exists"]:
        print(f"| 长期交付方向 | {humanize_text(delivery_state['direction'])} |")
        print(f"| 长期交付状态 | `{zh_delivery_status(delivery_state['status'])}` |")
        print(f"| 下一长期交付检查 | {humanize_text(delivery_state['next_checks'][0]) if delivery_state['next_checks'] else '暂无'} |")
    if ptl_state["exists"]:
        print(f"| PTL 监督方向 | {humanize_text(ptl_state['direction'])} |")
        print(f"| PTL 监督状态 | `{zh_ptl_status(ptl_state['status'])}` |")
        print(f"| 下一 PTL 检查 | {humanize_text(ptl_state['next_checks'][0]) if ptl_state['next_checks'] else '暂无'} |")
    if handoff_state["exists"]:
        print(f"| worker 接续方向 | {humanize_text(handoff_state['direction'])} |")
        print(f"| worker 接续状态 | `{zh_handoff_status(handoff_state['status'])}` |")
        print(f"| 下一 handoff 检查 | {humanize_text(handoff_state['next_checks'][0]) if handoff_state['next_checks'] else '暂无'} |")
    if tier == "large":
        print(f"| 当前模块 | `{active_module}` |")
    print(f"| 当前主要风险 | {humanize_text(main_risk)} |")
    if escalation_reason:
        print(f"| 升级原因 | {humanize_text(escalation_reason)} |")

    if capabilities:
        print("\n## Usable Now")
        for _, label in capabilities:
            print(f"- {label}")

    print("\n## Human Windows")
    print("### Chinese")
    for item in human_windows_zh:
        print(f"- `{item}`")
    print("\n### English")
    for item in human_windows_en:
        print(f"- `{item}`")

    print("\n## Restore Order")
    for idx, item in enumerate(restore_docs, start=1):
        print(f"{idx}. `{item}`")

    docs_cn = "、".join(restore_docs)
    docs_en = ", ".join(restore_docs)

    print("\n## Copy-Paste Commands")
    print("\n### Chinese")
    print("```text")
    print(
        f"项目助手 继续。先读取 "
        + docs_cn
        + f"；然后继续当前执行线：{humanize_text(current_execution_line)}。"
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
        f"project assistant continue. Read {docs_en} first; then continue the current execution line: "
        f"{english_execution_line}."
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
            print(f"{idx}. {humanize_text(item)}")
    else:
        print("1. No next actions recorded.")

    if execution_tasks:
        print("\n## Execution Tasks")
        for idx, item in enumerate(execution_tasks, start=1):
            print(f"{idx}. {humanize_text(display_execution_task(item))}")

    print("\n## Notes")
    print("- Start a new thread with this output and the repo path when you need a clean context.")
    print("- For large projects, read `.codex/module-dashboard.md` before `modules/*.md` after restore.")
    print("- 如果使用中文继续，也可以直接复制上面的中文命令。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
