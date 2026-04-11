#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from control_surface_lib import parse_tier, read_text


def has_all(text: str, parts: list[str]) -> bool:
    return all(part in text for part in parts)


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
    installable = (repo / "install.sh").exists() or (repo / "VERSION").exists()
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
    if tier in {"medium", "large"}:
        if not docs_home:
            missing.append("docs/README.md")
        else:
            if not has_all(docs_home, ["## Start Here", "## By Goal"]):
                warnings.append("docs/README.md missing landing sections")

        test_plan = read_text(repo / "docs/test-plan.md")
        if not test_plan:
            missing.append("docs/test-plan.md")
        else:
            if not has_all(test_plan, ["## Scope and Risk", "## Acceptance Cases", "## Automation Coverage", "## Manual Checks"]):
                warnings.append("docs/test-plan.md missing standard sections")

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
