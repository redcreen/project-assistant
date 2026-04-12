#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import completion_band, completion_percent, parse_official_modules, parse_tier, read_text


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


def first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
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


def mermaid_status_label(status: str) -> str:
    lowered = status.lower()
    if "active" in lowered:
        return "Active"
    if "governing" in lowered:
        return "Governing"
    if "planned" in lowered:
        return "Planned"
    if "complete" in lowered:
        return "Baseline Complete"
    if "maintain" in lowered:
        return "Maintain"
    return status


def first_risk(status_text: str) -> str:
    risks = bullet_lines(section(status_text, "Blockers / Open Decisions"))
    return risks[0] if risks else "No major blocker recorded."


def load_module_summary(module_path: Path) -> dict[str, str]:
    text = module_path.read_text(encoding="utf-8")
    status = first_line(section(text, "Current Status")) or "missing"
    return {
        "status": status,
        "completion_percent": str(completion_percent(status)),
        "completion_band": completion_band(status),
        "implemented": compact_list(bullet_lines(section(text, "Already Implemented")), limit=2),
        "remaining": compact_list(bullet_lines(section(text, "Remaining Steps")), limit=2),
        "completion": first_line(section(text, "Completion Signal")) or "n/a",
        "next_checkpoint": first_line(section(text, "Next Checkpoint")) or "n/a",
    }


def load_subproject_rows(repo: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    subproject_dir = repo / ".codex/subprojects"
    if not subproject_dir.exists():
        return rows
    for path in sorted(subproject_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        rows.append(
            (
                path.stem,
                first_line(section(text, "Current Slice")) or "n/a",
                first_line(section(text, "Next 3 Actions")) or compact_list(bullet_lines(section(text, "Next 3 Actions")), limit=1),
            )
        )
    return rows


def module_health_breakdown(module_summaries: list[dict[str, str]]) -> str:
    if not module_summaries:
        return "n/a"
    buckets = {"maintain": 0, "stable": 0, "active": 0, "forming": 0, "planned": 0}
    for summary in module_summaries:
        buckets[summary["completion_band"]] = buckets.get(summary["completion_band"], 0) + 1
    parts = [f"{label}:{count}" for label, count in buckets.items() if count]
    return ", ".join(parts) if parts else "n/a"


def project_display_name(repo: Path) -> str:
    brief_heading = first_heading(read_text(repo / ".codex/brief.md"))
    if brief_heading and brief_heading.lower() != "project brief":
        return brief_heading
    readme_heading = first_heading(read_text(repo / "README.md"))
    if readme_heading:
        return readme_heading
    return repo.name


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a quick markdown progress snapshot from the control surface.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    tier = parse_tier(repo)
    status_text = (repo / ".codex/status.md").read_text(encoding="utf-8")
    project_name = project_display_name(repo)

    current_phase = first_line(section(status_text, "Current Phase"))
    active_slice = first_line(section(status_text, "Active Slice"))
    next_actions = section(status_text, "Next 3 Actions")
    main_risk = first_risk(status_text)

    print("# Progress Dashboard\n")
    print("## Summary")
    print(f"- Project: `{project_name}`")
    print(f"- Tier: `{tier}`")
    print(f"- Current Phase: `{current_phase}`")
    print(f"- Active Slice: `{active_slice}`")
    print(f"- Main Risk: {main_risk}")

    print("\n## Global View")
    print("| Area | Status | Current Focus | Exit Condition |")
    print("| --- | --- | --- | --- |")
    print(f"| Project | {current_phase or 'n/a'} | {active_slice or 'n/a'} | Advance the current slice without losing module-view clarity |")

    module_dir = repo / ".codex/modules"
    official_modules = parse_official_modules(repo)
    module_summaries: list[dict[str, str]] = []
    if tier == "large" and module_dir.exists() and official_modules:
        for module in official_modules:
            path = module_dir / f"{module}.md"
            if path.exists():
                summary = load_module_summary(path)
            else:
                summary = {
                    "status": "missing",
                    "completion_percent": "0",
                    "completion_band": "planned",
                    "implemented": "missing",
                    "remaining": "missing",
                    "completion": "missing",
                    "next_checkpoint": "missing",
                }
            module_summaries.append(summary)

        average_completion = round(
            sum(int(summary["completion_percent"]) for summary in module_summaries) / len(module_summaries)
        )

        print("\n## Module Summary")
        print(f"- Official Modules: `{len(official_modules)}`")
        print(f"- Average Completion: `{average_completion}%`")
        print(f"- Health Mix: {module_health_breakdown(module_summaries)}")

        print("\n## Module View")
        print("| Module | Status | Completion % | Already Implemented | Remaining Steps | Completion Signal | Next Checkpoint |")
        print("| --- | --- | --- | --- | --- | --- | --- |")
        for module, summary in zip(official_modules, module_summaries):
            print(
                f"| {module_display_name(module)} | {summary['status']} | {summary['completion_percent']}% ({summary['completion_band']}) | {summary['implemented']} | {summary['remaining']} | {summary['completion']} | {summary['next_checkpoint']} |"
            )

        print("\n## Module Flow")
        print("```mermaid")
        print("flowchart TB")
        print(f'    P["{project_name}"]')
        for module, summary in zip(official_modules, module_summaries):
            label = module_display_name(module)
            status_label = f"{mermaid_status_label(summary['status'])} / {summary['completion_percent']}%"
            node_id = re.sub(r"[^A-Za-z0-9]+", "", module.title()) or "Module"
            print(f'    P --> {node_id}["{label}\\n{status_label}"]')
        print("```")

    subproject_rows = load_subproject_rows(repo)
    if subproject_rows:
        print("\n## Cross-Cutting View")
        print("| Workstream | Current Slice | Next Checkpoint |")
        print("| --- | --- | --- |")
        for name, current_slice, next_checkpoint in subproject_rows:
            print(f"| {name} | {current_slice or 'n/a'} | {next_checkpoint or 'n/a'} |")

    print("\n## Next 3 Actions")
    print(next_actions or "No next actions recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
