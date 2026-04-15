#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from control_surface_lib import ensure_roadmap_stage_links, parse_tier, relative_markdown_target
from sync_docs_system import ensure_roadmap_detail_link, project_doc_slug, sync_public_plan_surfaces


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize roadmap and development-plan surfaces from .codex/plan.md.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    tier = parse_tier(repo)
    docs_dir = repo / "docs"
    reference_dir = docs_dir / "reference" / project_doc_slug(repo)
    touched = sync_public_plan_surfaces(repo)

    if tier in {"medium", "large"}:
        development_plan = reference_dir / "development-plan.md"
        development_plan_zh = reference_dir / "development-plan.zh-CN.md"
        if development_plan.exists() and ensure_roadmap_detail_link(
            docs_dir / "roadmap.md",
            f"[{reference_dir.name}/development-plan.md]({relative_markdown_target(docs_dir, development_plan)})",
            chinese=False,
        ):
            touched.append("docs/roadmap.md")
        if development_plan_zh.exists() and ensure_roadmap_detail_link(
            docs_dir / "roadmap.zh-CN.md",
            f"[{reference_dir.name}/development-plan.zh-CN.md]({relative_markdown_target(docs_dir, development_plan_zh)})",
            chinese=True,
        ):
            touched.append("docs/roadmap.zh-CN.md")

    for rel in ensure_roadmap_stage_links(repo):
        if rel not in touched:
            touched.append(rel)

    print(f"touched: {', '.join(touched) if touched else '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
