#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import completion_band, completion_percent, parse_official_modules, parse_tier, write_control_surface_config


MODULE_TEMPLATE = """# Module Status

## Ownership

TODO: define what this module owns.

## Current Status

`planned`

## Already Implemented

- TODO

## Remaining Steps
1. TODO
2. TODO
3. TODO

## Completion Signal

TODO: define what "good enough" looks like for this module.

## Next Checkpoint

TODO: define the next concrete checkpoint.
"""


COMMANDS_TEMPLATE = """# Commands

## Chinese

- `项目助手 菜单`
- `项目助手 启动这个项目`
- `项目助手 规划下一阶段`
- `项目助手 恢复当前状态`
- `项目助手 告诉我项目进展`
- `项目助手 先做整改审计`
- `项目助手 整改这个仓库`
- `项目助手 文档整改这个仓库`
- `项目助手 收口当前阶段`

## English

- `project assistant menu`
- `project assistant start this project`
- `project assistant plan the next phase`
- `project assistant resume current status`
- `project assistant progress`
- `project assistant retrofit audit`
- `project assistant retrofit this repo`
- `project assistant docs retrofit this repo`
- `project assistant close out the current phase`

## Notes

- Use the language that matches the user.
- Natural-language variations are fine as long as intent stays clear.
"""


DEFAULT_ENTRY_RULES = """- 当前状态，以 [status.md](status.md) 为准
- 模块边界，以 [../docs/module-map.md](../docs/module-map.md) 为准
- 模块内状态，以 `modules/*.md` 为准
- `subprojects/*.md` 只保留给横切工作流，不替代官方模块状态
- `project-roadmap.md` 负责总 roadmap，不负责当前执行点
- `reports/*` 负责证据和专题，不负责当前执行点"""


def section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def first_line(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line.strip("`")
    return ""


def bullet_lines(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            items.append(re.sub(r"^\d+\.\s+", "", line))
    return items


def compact_list(items: list[str], limit: int = 2) -> str:
    if not items:
        return "n/a"
    shown = items[:limit]
    text = "; ".join(shown)
    if len(items) > limit:
        text += "; ..."
    return text


def module_display_name(slug: str) -> str:
    return slug.replace("-", " ").title()


def load_module_summary(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    status = first_line(section(text, "Current Status")) or "planned"
    return {
        "status": status,
        "completion_percent": str(completion_percent(status)),
        "completion_band": completion_band(status),
        "implemented": compact_list(bullet_lines(section(text, "Already Implemented")), limit=2),
        "remaining": compact_list(bullet_lines(section(text, "Remaining Steps")), limit=2),
        "next_checkpoint": first_line(section(text, "Next Checkpoint")) or "n/a",
    }


def status_snapshot(repo: Path) -> tuple[str, str, str, list[str]]:
    status_text = (repo / ".codex/status.md").read_text(encoding="utf-8") if (repo / ".codex/status.md").exists() else ""
    phase = first_line(section(status_text, "Current Phase")) or "n/a"
    active_slice = first_line(section(status_text, "Active Slice")) or "n/a"
    blockers = bullet_lines(section(status_text, "Blockers / Open Decisions"))
    next_actions = bullet_lines(section(status_text, "Next 3 Actions"))
    return phase, active_slice, blockers[0] if blockers else "No major blocker recorded.", next_actions


def render_dashboard(repo: Path, official_modules: list[str]) -> str:
    dashboard_path = repo / ".codex/module-dashboard.md"
    existing = dashboard_path.read_text(encoding="utf-8") if dashboard_path.exists() else ""
    purpose = section(existing, "Purpose") or "这是当前仓库的模块级控制面总入口。"
    purpose = purpose.split("恢复时默认按这个顺序看：", 1)[0].strip()
    purpose = first_line(purpose) or "这是当前仓库的模块级控制面总入口。"
    entry_rules = section(existing, "Module Entry Rules") or DEFAULT_ENTRY_RULES
    current_execution = section(existing, "Current Execution Order")

    phase, active_slice, main_risk, next_actions = status_snapshot(repo)
    module_summaries = [load_module_summary(repo / ".codex/modules" / f"{module}.md") for module in official_modules]
    average_completion = round(sum(int(item["completion_percent"]) for item in module_summaries) / len(module_summaries)) if module_summaries else 0
    active_module = module_display_name(official_modules[0]) if official_modules else "n/a"
    found_explicit_active = False
    for module, summary in zip(official_modules, module_summaries):
        if re.search(r"\bactive\b", summary["status"].lower()):
            active_module = module_display_name(module)
            found_explicit_active = True
            break
    if not found_explicit_active:
        for module, summary in zip(official_modules, module_summaries):
            if summary["completion_band"] == "active":
                active_module = module_display_name(module)
                break

    if not current_execution:
        current_execution = "\n".join(
            f"{idx}. {item}" for idx, item in enumerate(next_actions[:4], start=1)
        ) or "1. Follow `.codex/status.md` next actions."

    rows = "\n".join(
        f"| {module_display_name(module)} | {summary['status']} | {summary['completion_percent']}% ({summary['completion_band']}) | {summary['implemented']} | {summary['remaining']} | {summary['next_checkpoint']} | [modules/{module}.md](modules/{module}.md) |"
        for module, summary in zip(official_modules, module_summaries)
    )

    return f"""# Module Dashboard

## Purpose

{purpose}

恢复时默认按这个顺序看：

1. [status.md](status.md)
2. 本文档
3. [../docs/module-map.md](../docs/module-map.md)
4. `.codex/modules/*.md`
5. `.codex/subprojects/*.md`（仅横切工作流需要时）

## Summary

- Overall: {phase}
- Average Completion: {average_completion}%
- Active Module: {active_module}
- Main Risk: {main_risk}
- Active Slice: {active_slice}

## Modules

| Module | Status | Completion % | Already Implemented | Remaining Steps | Next Checkpoint | Primary Entry |
| --- | --- | --- | --- | --- | --- | --- |
{rows}

## Module Entry Rules

{entry_rules}

## Current Execution Order

{current_execution}
"""


def ensure_commands_doc(repo: Path) -> None:
    path = repo / ".codex/COMMANDS.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    lowered = text.lower()
    if "项目助手" in text and "project assistant" in lowered:
        return
    path.write_text(COMMANDS_TEMPLATE, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create missing control-surface artifacts without overwriting existing content.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    codex_dir = repo / ".codex"
    codex_dir.mkdir(exist_ok=True)
    ensure_commands_doc(repo)

    tier = parse_tier(repo)
    official_modules = parse_official_modules(repo)
    write_control_surface_config(repo, tier, official_modules)

    if tier == "large" and official_modules:
        modules_dir = codex_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        for module in official_modules:
            path = modules_dir / f"{module}.md"
            if not path.exists():
                path.write_text(MODULE_TEMPLATE, encoding="utf-8")

        dashboard = codex_dir / "module-dashboard.md"
        dashboard.write_text(render_dashboard(repo, official_modules), encoding="utf-8")

    print(f"tier: {tier}")
    print(f"official modules: {', '.join(official_modules) or '(none)'}")
    print("sync complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
