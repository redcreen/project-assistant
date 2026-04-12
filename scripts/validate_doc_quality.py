#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import load_doc_governance_config, match_glob

PLACEHOLDER_SNIPPETS = [
    "One-line value proposition.",
    "一句话说明这个项目解决什么问题。",
]

TODO_LINE_RE = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+|>\s+)?TODO\b", re.IGNORECASE | re.MULTILINE)
STUB_RE = re.compile(r"^>\s*TODO:\s*(translate the facts|把 .* 的事实同步翻译到这个文档)", re.IGNORECASE | re.MULTILINE)
MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ABSOLUTE_LOCAL_RE = re.compile(r"(?<![A-Za-z0-9_])(?:file://)?/(?:Users|home|tmp|var|private|opt|Volumes)/[^\s)>\"]+")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def public_docs(repo: Path) -> list[Path]:
    governance = load_doc_governance_config(repo)
    include_globs = [str(item) for item in governance.get("publicDocIncludeGlobs", [])]
    exclude_globs = [str(item) for item in governance.get("publicDocExcludeGlobs", [])]
    docs: list[Path] = []
    for path in sorted(repo.rglob("*.md")):
        rel = path.relative_to(repo).as_posix()
        base_rel = rel.replace(".zh-CN.md", ".md") if rel.endswith(".zh-CN.md") else rel
        if include_globs and not any(match_glob(base_rel, pattern) for pattern in include_globs):
            continue
        if any(match_glob(base_rel, pattern) for pattern in exclude_globs):
            continue
        docs.append(path)
    return docs


def all_markdown_docs(repo: Path) -> list[Path]:
    return sorted(repo.rglob("*.md"))


def warn_placeholders(rel: str, text: str, warnings: list[str]) -> None:
    for snippet in PLACEHOLDER_SNIPPETS:
        if snippet in text:
            warnings.append(f"{rel} still contains placeholder text: {snippet}")
    if TODO_LINE_RE.search(text):
        warnings.append(f"{rel} still contains TODO-style placeholder lines")
    if STUB_RE.search(text):
        warnings.append(f"{rel} is still a translation stub, not a finished public doc")


def warn_empty_tables(rel: str, text: str, warnings: list[str]) -> None:
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if not lines[i].strip().startswith("|"):
            i += 1
            continue
        block: list[str] = []
        while i < len(lines) and lines[i].strip().startswith("|"):
            block.append(lines[i].strip())
            i += 1
        if len(block) < 3:
            continue
        rows = block[2:]
        for row in rows:
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            if len(cells) < 2:
                continue
            if cells[0] and all(not cell for cell in cells[1:]):
                warnings.append(f"{rel} contains an empty table row: {row}")
                break


def warn_empty_mermaid(rel: str, text: str, warnings: list[str]) -> None:
    for match in MERMAID_RE.finditer(text):
        body = match.group(1).strip()
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines:
            warnings.append(f"{rel} contains an empty Mermaid block")
            continue
        if len(lines) == 1 and lines[0].startswith(("flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram")):
            warnings.append(f"{rel} contains a placeholder Mermaid block")


def resolved_target(path: Path, target: str) -> Path | None:
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    clean = target.split("#", 1)[0].strip()
    if not clean:
        return None
    return (path.parent / clean).resolve(strict=False)


def warn_broken_links(repo: Path, path: Path, text: str, warnings: list[str]) -> None:
    rel = path.relative_to(repo).as_posix()
    for target in LINK_RE.findall(text):
        resolved = resolved_target(path, target)
        if resolved is None:
            continue
        if not resolved.exists():
            warnings.append(f"{rel} links to missing target: {target}")


def warn_absolute_local_paths(rel: str, text: str, warnings: list[str]) -> None:
    matches = sorted(set(ABSOLUTE_LOCAL_RE.findall(text)))
    for match in matches:
        warnings.append(f"{rel} contains a local absolute path; use repo-relative links instead: {match}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate public-doc quality beyond structural gates.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    warnings: list[str] = []

    docs = public_docs(repo)
    for path in docs:
        rel = path.relative_to(repo).as_posix()
        text = read_text(path)
        warn_placeholders(rel, text, warnings)
        warn_empty_tables(rel, text, warnings)
        warn_empty_mermaid(rel, text, warnings)
        warn_broken_links(repo, path, text, warnings)
    for path in all_markdown_docs(repo):
        rel = path.relative_to(repo).as_posix()
        text = read_text(path)
        warn_absolute_local_paths(rel, text, warnings)

    ok = not warnings
    payload = {"ok": ok, "warnings": warnings}

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if warnings:
            print("warnings:")
            for item in warnings:
                print(f"- {item}")
        print(f"ok: {ok}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
