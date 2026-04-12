#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from control_surface_lib import (
    completion_band,
    completion_percent,
    parse_official_modules,
    parse_tier,
    read_text,
    write_control_surface_config,
    write_doc_governance_config,
)


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


BRIEF_TEMPLATE = """# Project Brief

## Delivery Tier
- Tier: `{tier}`
- Why this tier: {why_tier}
- Last reviewed: TODO

## Outcome

TODO: define the outcome this repo is meant to deliver.

## Scope

- TODO

## Non-Goals

- TODO

## Constraints

- TODO

## Definition of Done

- TODO
"""


PLAN_TEMPLATE = """# Project Plan

## Current Phase

{current_phase}

## Current Execution Line

- Objective: establish the next meaningful autonomous run
- Plan Link: next execution selection
- Runway: one checkpoint-sized execution line
- Progress: 0 / 4 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment
- Validation:
  - current execution line is reflected in `status.md`
  - next checkpoint is explicit

## Execution Tasks

- [ ] EL-1 confirm the active slice and intended checkpoint
- [ ] EL-2 run the highest-value implementation step in this execution line
- [ ] EL-3 run the primary validation for the slice
- [ ] EL-4 refresh status, next checkpoint, and next 3 actions

## Development Log Capture

- Trigger Level: high
- Auto-Capture When:
  - the root-cause hypothesis changes
  - a reusable mechanism replaces repeated local fixes
  - a retrofit changes governance, architecture, or release policy
  - a tradeoff or rejected shortcut is likely to matter in future work
- Skip When:
  - the change is mechanical or formatting-only
  - no durable reasoning changed
  - the work simply followed an already-approved path
  - the change stayed local and introduced no durable tradeoff

## Architecture Supervision

- Signal: `yellow`
- Signal Basis: current slice is explicit, but architecture supervision should stay visible until the default operating model fully converges
- Problem Class: architecture supervision is still mostly a policy, not yet a fully encoded operating surface
- Root Cause Hypothesis: execution and validation know the active slice, but the architecture judgment is not yet expressed as a durable state
- Correct Layer: control surface and validation gates
- Rejected Shortcut: relying on free-form prose instead of a reusable architecture-review state
- Automatic Review Trigger: no automatic trigger is currently active
- Escalation Gate: raise but continue

## Escalation Model

- Continue Automatically: implementation and validation work stay within the current direction and do not alter business behavior
- Raise But Continue: the assistant sees architectural drift or scope pressure but can still converge within the agreed direction
- Require User Decision: product behavior, compatibility, performance, cost, or UX tradeoffs would change the intended direction

## Slices
- Slice: control-surface alignment
  - Objective: establish or refresh `.codex/brief.md`, `.codex/plan.md`, `.codex/status.md`, and `.codex/COMMANDS.md`
  - Dependencies: current repo structure
  - Risks: control docs drift from actual repo state
  - Validation: `validate_control_surface.py` returns `ok: True`
  - Exit Condition: control surface exists and is coherent

- Slice: durable-doc alignment
  - Objective: align `README` and `docs/*` with the project-assistant document standards
  - Dependencies: existing repo docs, `sync_docs_system.py`, `validate_docs_system.py`
  - Risks: docs pass structure checks but still read like scaffolding
  - Validation: docs validators pass and README remains accurate
  - Exit Condition: public docs are readable and recoverable

- Slice: next execution selection
  - Objective: make the next implementation or maintenance slice explicit
  - Dependencies: current retrofit result
  - Risks: repo falls back into ad hoc maintenance
  - Validation: `status.md` records the next 3 actions
  - Exit Condition: next slice is concrete

- Slice: architecture retrofit
  - Objective: correct wrong boundaries, duplicate architecture owners, or repeated wrong-layer fixes through an architecture-first retrofit
  - Dependencies: `sync_architecture_retrofit.py`, control surface, current architecture signal
  - Risks: repo keeps fixing symptoms locally while the real boundary problem remains
  - Validation: `.codex/architecture-retrofit.md` exists, is usable, and `validate_architecture_retrofit.py` passes
  - Exit Condition: target architecture, scope, execution strategy, and exit conditions are explicit
"""


STATUS_TEMPLATE = """# Project Status

## Delivery Tier
- Tier: `{tier}`
- Why this tier: {why_tier}
- Last reviewed: TODO

## Current Phase

Retrofit in progress.

## Active Slice

Control surface and durable-doc alignment.

## Current Execution Line

- Objective: align the control surface, define the next checkpoint, and run validation before closing the current execution line
- Plan Link: next execution selection
- Runway: one checkpoint-sized execution line
- Progress: 0 / 4 tasks complete
- Stop Conditions:
  - blocker requires human direction
  - validation fails and changes the direction
  - business, compatibility, or cost decision requires user judgment

## Execution Tasks

- [ ] EL-1 establish or refresh `.codex` control files
- [ ] EL-2 verify public docs against the current standard
- [ ] EL-3 record the next checkpoint for the repo
- [ ] EL-4 prepare the next 3 actions from a validated state

## Development Log Capture

- Trigger Level: high
- Pending Capture: no
- Last Entry: none

## Architecture Supervision

- Signal: `yellow`
- Signal Basis: current slice is explicit, but architecture supervision should stay visible until the default operating model fully converges
- Root Cause Hypothesis: the repo may still drift toward local fixes because the architecture judgment is not yet encoded as a reusable state
- Correct Layer: control surface and validation gates
- Automatic Review Trigger: no automatic trigger is currently active
- Escalation Gate: raise but continue

## Current Escalation State

- Current Gate: raise but continue
- Reason: the assistant can keep converging the repo unless a business or compatibility tradeoff changes the intended direction
- Next Review Trigger: review again when blockers change, the active slice rolls forward, or release-facing work begins

## Done

- repository scanned

## In Progress

- establish `.codex` control surface
- align public docs with current standards

## Blockers / Open Decisions

- TODO

## Next 3 Actions
1. Finish the control-surface retrofit.
2. Run validation and verify the public docs.
3. Select the next concrete maintenance or feature slice.
"""


COMMANDS_TEMPLATE = """# Commands

## Primary Windows | 中文主窗口

- `项目助手 菜单`
- `项目助手 进展`
- `项目助手 架构`
- `项目助手 开发日志`

## Primary Windows | English

- `project assistant menu`
- `project assistant progress`
- `project assistant architecture`
- `project assistant devlog`

## Background Flows | 后台主流程

- `项目助手 启动这个项目` / `project assistant start this project`
- `项目助手 规划下一阶段` / `project assistant plan the next phase`
- `项目助手 继续` / `project assistant continue`
- `项目助手 架构 整改` / `project assistant architecture retrofit`
- `项目助手 整改这个仓库` / `project assistant retrofit this repo`
- `项目助手 文档整改这个仓库` / `项目助手 文档整理这个仓库` / `project assistant docs retrofit this repo`
- `项目助手 收口当前阶段` / `project assistant close out the current phase`
- `项目助手 发布 patch` / `project assistant release patch`
- `项目助手 压缩上下文` / `project assistant handoff`

## Notes

- Human users usually only need the four primary windows above.
- The other flows should run mostly in the background unless the user explicitly overrides them.
- Use the language that matches the user, and accept natural-language variations when the intent is clear.
"""


def tier_reason(tier: str) -> str:
    if tier == "large":
        return "multiple modules, workstreams, or adapters require explicit status, plan, and module structure"
    if tier == "medium":
        return "multi-session maintenance needs a lightweight but durable control surface"
    return "single short execution cycle with low structural overhead"


def ensure_core_doc(path: Path, content: str) -> None:
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def template_sections(text: str) -> list[tuple[str, str]]:
    matches = re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return [(match.group(1).strip(), match.group(2).strip()) for match in matches]


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


def ensure_sections(path: Path, template: str) -> None:
    if not path.exists():
        path.write_text(template, encoding="utf-8")
        return
    text = path.read_text(encoding="utf-8")
    changed = False
    for heading, body in template_sections(template):
        if section(text, heading).strip():
            continue
        text = text.rstrip() + f"\n\n## {heading}\n\n{body}\n"
        changed = True
    if changed:
        path.write_text(text.rstrip() + "\n", encoding="utf-8")


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


def execution_tasks(text: str) -> list[str]:
    return bullet_lines(section(text, "Execution Tasks"))


def render_dashboard(repo: Path, official_modules: list[str]) -> str:
    dashboard_path = repo / ".codex/module-dashboard.md"
    existing = dashboard_path.read_text(encoding="utf-8") if dashboard_path.exists() else ""
    purpose = section(existing, "Purpose") or "这是当前仓库的模块级控制面总入口。"
    purpose = purpose.split("恢复时默认按这个顺序看：", 1)[0].strip()
    purpose = first_line(purpose) or "这是当前仓库的模块级控制面总入口。"
    entry_rules = section(existing, "Module Entry Rules") or DEFAULT_ENTRY_RULES
    current_execution = section(existing, "Current Execution Order")

    phase, active_slice, main_risk, next_actions = status_snapshot(repo)
    status_text = read_text(repo / ".codex/status.md")
    current_execution_line = first_line(section(status_text, "Current Execution Line")) or active_slice
    execution_task_lines = execution_tasks(status_text)
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
        task_lines = execution_task_lines or next_actions[:4]
        current_execution = f"- Execution Line: {current_execution_line}\n" + (
            "\n".join(f"{idx}. {item}" for idx, item in enumerate(task_lines, start=1))
            or "1. Follow `.codex/status.md` next actions."
        )

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
    primary_windows = [
        "项目助手 菜单",
        "项目助手 进展",
        "项目助手 架构",
        "项目助手 开发日志",
        "project assistant menu",
        "project assistant progress",
        "project assistant architecture",
        "project assistant devlog",
    ]
    if "项目助手" in text and "project assistant" in lowered and all(item.lower() in lowered or item in text for item in primary_windows):
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
    why_tier = tier_reason(tier)
    ensure_core_doc(codex_dir / "brief.md", BRIEF_TEMPLATE.format(tier=tier, why_tier=why_tier))
    plan_template = PLAN_TEMPLATE.format(
        current_phase="Retrofit and baseline alignment." if tier != "large" else "Retrofit, module alignment, and baseline execution."
    )
    status_template = STATUS_TEMPLATE.format(tier=tier, why_tier=why_tier)
    ensure_sections(codex_dir / "plan.md", plan_template)
    ensure_sections(codex_dir / "status.md", status_template)
    write_control_surface_config(repo, tier, official_modules)
    write_doc_governance_config(repo, tier, official_modules)

    if tier == "large" and official_modules:
        modules_dir = codex_dir / "modules"
        modules_dir.mkdir(exist_ok=True)
        for module in official_modules:
            path = modules_dir / f"{module}.md"
            if not path.exists():
                path.write_text(MODULE_TEMPLATE, encoding="utf-8")

        dashboard = codex_dir / "module-dashboard.md"
        dashboard.write_text(render_dashboard(repo, official_modules), encoding="utf-8")

    sync_arch_script = Path(__file__).resolve().parent / "sync_architecture_supervision.py"
    subprocess.run([sys.executable, str(sync_arch_script), str(repo)], check=True)

    print(f"tier: {tier}")
    print(f"official modules: {', '.join(official_modules) or '(none)'}")
    print("sync complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
