#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
from pathlib import Path

from control_surface_lib import COMMON_ROOT_DOCS, classify_markdown_role, load_doc_governance_config, match_glob
IGNORED_DIRS = {".git", "node_modules", ".obsidian", "__pycache__"}

DURABLE_IN_REPORTS_TOKENS = (
    "architecture",
    "roadmap",
    "policy",
    "workstream",
    "strategy",
    "blueprint",
    "design",
)


def inventory_markdown(repo: Path) -> list[Path]:
    items: list[Path] = []
    for path in repo.rglob("*.md"):
        if any(part in IGNORED_DIRS for part in path.relative_to(repo).parts):
            continue
        items.append(path)
    return sorted(items)


def question_token_matches(rel: str, tokens: list[str]) -> bool:
    path = PurePosixPath(rel.lower())
    stem = path.stem.lower()
    name = path.name.lower()
    parent = path.parent.name.lower() if path.parent != PurePosixPath(".") else ""
    return any(
        token in stem
        or token in name
        or token == stem
        or token == parent
        for token in tokens
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate full Markdown governance convergence.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    governance = load_doc_governance_config(repo)
    skill_repo = governance.get("repoKind") == "skill"
    missing: list[str] = []
    warnings: list[str] = []

    for required_rel in governance.get("requiredPaths", []):
        required = repo / str(required_rel)
        if not required.exists():
            missing.append(str(required.relative_to(repo)))

    root_docs = sorted(p for p in repo.glob("*.md"))
    allowed_root = set(str(item) for item in governance.get("rootKeep", []))
    for path in root_docs:
        rel = path.relative_to(repo).as_posix()
        role = classify_markdown_role(repo, rel, governance)
        if path.name not in allowed_root and not (path.name in COMMON_ROOT_DOCS and role in {"durable", "release"}):
            warnings.append(f"unexpected root markdown file: {path.name}")

    docs_home = (repo / "docs/README.md").read_text(encoding="utf-8") if (repo / "docs/README.md").exists() else ""
    docs_home_zh = (repo / "docs/README.zh-CN.md").read_text(encoding="utf-8") if (repo / "docs/README.zh-CN.md").exists() else ""
    docs_home_needles = [str(item) for item in governance.get("docsHomeLinks", {}).get("en", [])]
    docs_home_needles_zh = [str(item) for item in governance.get("docsHomeLinks", {}).get("zh", [])]
    for needle in docs_home_needles:
        if docs_home and needle not in docs_home:
            warnings.append(f"docs/README.md missing link to {needle}")
    for needle in docs_home_needles_zh:
        if docs_home_zh and needle not in docs_home_zh:
            warnings.append(f"docs/README.zh-CN.md missing link to {needle}")

    reports_root = repo / "reports"
    if reports_root.exists() and not skill_repo:
        for path in sorted(reports_root.glob("*.md")):
            if path.name == "README.md":
                continue
            lowered = path.name.lower()
            if any(token in lowered for token in DURABLE_IN_REPORTS_TOKENS):
                warnings.append(f"durable-looking doc still lives in reports/: {path.relative_to(repo)}")
            else:
                warnings.append(f"report markdown should be under reports/generated/: {path.relative_to(repo)}")

    markdown_paths = inventory_markdown(repo)
    for path in markdown_paths:
        rel = path.relative_to(repo).as_posix()
        if classify_markdown_role(repo, rel, governance) is None:
            warnings.append(f"unclassified markdown file: {rel}")

    exclude_globs = [str(item) for item in governance.get("questionExcludeGlobs", [])]
    question_owners = governance.get("questionOwners", {})
    for question, spec in question_owners.items():
        if not isinstance(spec, dict):
            continue
        allowed = {str(item) for item in spec.get("allowed", [])}
        allowed_globs = [str(item) for item in spec.get("allowedGlobs", [])]
        tokens = [str(item).lower() for item in spec.get("tokens", [])]
        if not tokens:
            continue
        for path in markdown_paths:
            rel = path.relative_to(repo).as_posix()
            if any(match_glob(rel, pattern) for pattern in exclude_globs):
                continue
            if rel in allowed:
                continue
            if any(match_glob(rel, pattern) for pattern in allowed_globs):
                continue
            if question_token_matches(rel, tokens):
                warnings.append(f"{question}-like doc outside owned set: {rel}")

    payload = {"ok": not missing and not warnings, "missing": missing, "warnings": warnings}
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if missing:
            print("missing:")
            for item in missing:
                print(f"- {item}")
        if warnings:
            print("warnings:")
            for item in warnings:
                print(f"- {item}")
        print(f"ok: {payload['ok']}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
