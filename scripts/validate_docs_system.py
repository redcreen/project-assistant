#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from control_surface_lib import find_best_development_plan, normalized_roadmap_stage_links, parse_tier, read_text, relative_markdown_target


def has_all(text: str, parts: list[str]) -> bool:
    return all(part in text for part in parts)


def links_to(text: str, relative_path: str) -> bool:
    return relative_path in text or f"../{relative_path}" in text


def first_existing(repo: Path, names: list[str]) -> Path | None:
    for name in names:
        path = repo / name
        if path.exists():
            return path
    return None


def parse_open_execution_tasks(plan_text: str) -> list[str]:
    tasks: list[str] = []
    in_execution_tasks = False
    for raw_line in plan_text.splitlines():
        if raw_line.startswith("## "):
            in_execution_tasks = raw_line.strip() == "## Execution Tasks"
            continue
        if in_execution_tasks and raw_line.strip().startswith("- [ ] "):
            tasks.append(raw_line.strip()[6:].strip().strip("`"))
    return tasks


def parse_current_execution_fields(plan_text: str) -> dict[str, str]:
    fields = {"objective": "n/a", "plan_link": "n/a"}
    in_current_execution = False
    for raw_line in plan_text.splitlines():
        if raw_line.startswith("## "):
            in_current_execution = raw_line.strip() == "## Current Execution Line"
            continue
        if not in_current_execution:
            continue
        stripped = raw_line.strip()
        if stripped.startswith("- Objective:"):
            fields["objective"] = stripped.split(":", 1)[1].strip().strip("`")
        elif stripped.startswith("- Plan Link:"):
            fields["plan_link"] = stripped.split(":", 1)[1].strip().strip("`")
    return fields


def parse_slices(plan_text: str) -> list[str]:
    names: list[str] = []
    in_slices = False
    for raw_line in plan_text.splitlines():
        if raw_line.startswith("## "):
            in_slices = raw_line.strip() == "## Slices"
            continue
        if in_slices and raw_line.strip().startswith("- Slice:"):
            names.append(raw_line.strip().split(":", 1)[1].strip().strip("`"))
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the durable docs system against project-assistant rules.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    tier = parse_tier(repo)
    missing: list[str] = []
    warnings: list[str] = []

    readme = read_text(repo / "README.md")
    readme_zh = read_text(repo / "README.zh-CN.md")
    if not readme:
        missing.append("README.md")
    else:
        if "## Quick Start" not in readme:
            warnings.append("README.md missing Quick Start section")
        if "## Documentation Map" not in readme and "## Docs" not in readme:
            warnings.append("README.md missing Documentation Map section")
    installable = (repo / "install.sh").exists() or (repo / "scripts/install.sh").exists() or (repo / "VERSION").exists()
    if installable:
        if "## Install" not in readme:
            warnings.append("README.md missing Install section for installable repo")
        if "## Minimal Configuration" not in readme:
            warnings.append("README.md missing Minimal Configuration section for installable repo")
        if readme_zh:
            if "## 安装" not in readme_zh:
                warnings.append("README.zh-CN.md missing 安装 section for installable repo")
            if "## 最简配置" not in readme_zh:
                warnings.append("README.zh-CN.md missing 最简配置 section for installable repo")

    docs_home = read_text(repo / "docs/README.md")
    docs_home_zh = read_text(repo / "docs/README.zh-CN.md")
    live_plan_text = read_text(repo / ".codex/plan.md")
    live_open_tasks = parse_open_execution_tasks(live_plan_text)
    live_execution = parse_current_execution_fields(live_plan_text)
    live_slices = parse_slices(live_plan_text)
    current_slice_index = next((idx for idx, name in enumerate(live_slices) if name == live_execution["plan_link"]), None)
    next_slice = live_slices[current_slice_index + 1] if current_slice_index is not None and current_slice_index + 1 < len(live_slices) else ""
    if tier in {"medium", "large"}:
        development_plan = find_best_development_plan(repo, chinese=False)
        development_plan_zh = find_best_development_plan(repo, chinese=True)
        if not development_plan:
            missing.append("docs/reference/*/development-plan.md")
        if not development_plan_zh:
            warnings.append("missing Chinese development-plan counterpart for maintainer docs")
        if not docs_home:
            missing.append("docs/README.md")
        else:
            if not has_all(docs_home, ["## Start Here", "## By Goal"]):
                warnings.append("docs/README.md missing landing sections")
            docs_home_links = [
                ("architecture.md", repo / "docs/architecture.md"),
                ("roadmap.md", repo / "docs/roadmap.md"),
                ("adr/", repo / "docs/adr"),
            ]
            for label, path in docs_home_links:
                if label in docs_home and not path.exists():
                    warnings.append(f"docs/README.md links to missing {label}")
            release_doc = first_existing(repo, ["RELEASE.md", "release.md"])
            recommended_existing = [
                ("architecture.md", repo / "docs/architecture.md"),
                ("requirements.md", repo / "docs/requirements.md"),
                ("signing-and-notarization-plan.md", repo / "docs/signing-and-notarization-plan.md"),
            ]
            if release_doc:
                recommended_existing.append((release_doc.name, release_doc))
            for label, path in recommended_existing:
                if path.exists() and not links_to(docs_home, label):
                    warnings.append(f"docs/README.md should link to existing {label}")
            if development_plan:
                rel = relative_markdown_target((repo / "docs"), development_plan)
                if not links_to(docs_home, rel):
                    warnings.append("docs/README.md should link to the durable development-plan entry")
        if docs_home_zh and development_plan_zh:
            rel_zh = relative_markdown_target((repo / "docs"), development_plan_zh)
            if not links_to(docs_home_zh, rel_zh):
                warnings.append("docs/README.zh-CN.md should link to the durable development-plan entry")

        test_plan = read_text(repo / "docs/test-plan.md")
        if not test_plan:
            missing.append("docs/test-plan.md")
        else:
            if not has_all(test_plan, ["## Scope and Risk", "## Acceptance Cases", "## Automation Coverage", "## Manual Checks"]):
                warnings.append("docs/test-plan.md missing standard sections")
        if development_plan:
            development_plan_text = read_text(development_plan)
            required_plan_sections = [
                "## Purpose",
                "## How To Use This Plan",
                "## Current Position",
                "## Milestone Overview",
                "## Ordered Execution Queue",
            ]
            if not has_all(development_plan_text, required_plan_sections):
                warnings.append(f"{development_plan.relative_to(repo).as_posix()} missing standard development-plan sections")
            if live_open_tasks and live_open_tasks[0] not in development_plan_text:
                warnings.append(f"{development_plan.relative_to(repo).as_posix()} should surface the first open execution task from .codex/plan.md")
        if development_plan_zh:
            development_plan_zh_text = read_text(development_plan_zh)
            required_plan_sections_zh = [
                "## 目的",
                "## 怎么使用这份计划",
                "## 当前位置",
                "## 阶段总览",
                "## 顺序执行队列",
            ]
            if not has_all(development_plan_zh_text, required_plan_sections_zh):
                warnings.append(f"{development_plan_zh.relative_to(repo).as_posix()} missing standard development-plan sections")
            if live_open_tasks and live_open_tasks[0] not in development_plan_zh_text:
                warnings.append(f"{development_plan_zh.relative_to(repo).as_posix()} should surface the first open execution task from .codex/plan.md")
        roadmap_generic = read_text(repo / "docs/roadmap.md")
        if roadmap_generic and development_plan:
            rel = relative_markdown_target((repo / "docs"), development_plan)
            if rel not in roadmap_generic:
                warnings.append("docs/roadmap.md should point readers to the detailed development-plan")
            normalized = normalized_roadmap_stage_links(repo, repo / "docs/roadmap.md", roadmap_generic)
            if normalized != roadmap_generic:
                warnings.append("docs/roadmap.md should link roadmap milestones to the matching development-plan headings")
            if live_execution["objective"] != "n/a" and live_execution["objective"] not in roadmap_generic:
                warnings.append("docs/roadmap.md should surface the current execution objective from .codex/plan.md")
            if next_slice and next_slice not in roadmap_generic:
                warnings.append("docs/roadmap.md should surface the next queued slice from .codex/plan.md")
        roadmap_generic_zh = read_text(repo / "docs/roadmap.zh-CN.md")
        if roadmap_generic_zh and development_plan_zh:
            rel_zh = relative_markdown_target((repo / "docs"), development_plan_zh)
            if rel_zh not in roadmap_generic_zh:
                warnings.append("docs/roadmap.zh-CN.md should point readers to the detailed development-plan")
            normalized_zh = normalized_roadmap_stage_links(repo, repo / "docs/roadmap.zh-CN.md", roadmap_generic_zh)
            if normalized_zh != roadmap_generic_zh:
                warnings.append("docs/roadmap.zh-CN.md should link roadmap milestones to the matching development-plan headings")
            if live_execution["objective"] != "n/a" and live_execution["objective"] not in roadmap_generic_zh:
                warnings.append("docs/roadmap.zh-CN.md should surface the current execution objective from .codex/plan.md")
            if next_slice and next_slice not in roadmap_generic_zh:
                warnings.append("docs/roadmap.zh-CN.md should surface the next queued slice from .codex/plan.md")

    if tier == "large":
        architecture = read_text(repo / "docs/architecture.md")
        roadmap = read_text(repo / "docs/roadmap.md")
        if not architecture:
            missing.append("docs/architecture.md")
        else:
            required = ["## Purpose and Scope", "## System Context", "## Module Inventory", "## Core Flow"]
            if not has_all(architecture, required):
                warnings.append("docs/architecture.md missing standard sections")
            if "```mermaid" not in architecture:
                warnings.append("docs/architecture.md missing Mermaid diagram")
        if not roadmap:
            missing.append("docs/roadmap.md")
        else:
            required = ["## Scope", "## Now / Next / Later", "## Milestones", "## Risks and Dependencies"]
            if not has_all(roadmap, required):
                warnings.append("docs/roadmap.md missing standard sections")
            if "```mermaid" not in roadmap:
                warnings.append("docs/roadmap.md missing Mermaid diagram")
        adr_dir = repo / "docs/adr"
        if not adr_dir.exists():
            missing.append("docs/adr/")

    ok = not missing and not warnings
    payload = {"ok": ok, "tier": tier, "missing": missing, "warnings": warnings}

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"tier: {tier}")
        if missing:
            print("missing:")
            for item in missing:
                print(f"- {item}")
        if warnings:
            print("warnings:")
            for item in warnings:
                print(f"- {item}")
        print(f"ok: {ok}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
