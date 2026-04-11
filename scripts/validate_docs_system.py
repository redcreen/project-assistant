#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from control_surface_lib import parse_tier, read_text


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
    if tier in {"medium", "large"}:
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
