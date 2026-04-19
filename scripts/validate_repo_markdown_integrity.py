#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


IGNORE_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
}

IGNORE_RELATIVE_PREFIXES = (
    ".codex/host-views/",
)

LINK_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)|\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
ABSOLUTE_LOCAL_RE = re.compile(r"(?<![A-Za-z0-9_])(?:file://)?/(?:Users|home|tmp|var|private|opt|Volumes)/[^\s)>\"]+")
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def strip_fenced_code_blocks(text: str) -> str:
    return CODE_FENCE_RE.sub("", text)


def repo_markdown_files(repo: Path) -> list[Path]:
    files: list[Path] = []
    for path in repo.rglob("*.md"):
        rel_path = path.relative_to(repo).as_posix()
        rel_parts = set(Path(rel_path).parts)
        if rel_parts & IGNORE_DIR_NAMES:
            continue
        if any(rel_path.startswith(prefix) for prefix in IGNORE_RELATIVE_PREFIXES):
            continue
        files.append(path)
    return sorted(files)


def markdown_heading_ids(text: str) -> set[str]:
    seen: dict[str, int] = {}
    ids: set[str] = set()
    for match in HEADING_RE.finditer(text):
        value = match.group(2).strip().lower()
        value = re.sub(r"[`*_]+", "", value)
        value = value.replace("&", " and ")
        chars: list[str] = []
        dash_open = False
        for ch in value:
            if ch.isalnum():
                chars.append(ch)
                dash_open = False
            elif chars and not dash_open:
                chars.append("-")
                dash_open = True
        slug = "".join(chars).strip("-") or "section"
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        ids.add(f"{slug}-{count}" if count else slug)
    return ids


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def is_ignored_target(target: str) -> bool:
    lowered = target.lower()
    return lowered.startswith(
        (
            "http://",
            "https://",
            "mailto:",
            "tel:",
            "data:",
            "app://",
            "plugin://",
            "vscode:",
        )
    )


def resolved_target(source: Path, target: str) -> Path | None:
    if is_ignored_target(target) or target.startswith("#"):
        return None
    path_part = target.split("#", 1)[0].strip()
    if not path_part:
        return None
    return (source.parent / path_part).resolve(strict=False)


def validate_repo(repo: Path) -> dict[str, object]:
    warnings: list[str] = []
    heading_cache: dict[Path, set[str]] = {}
    files = repo_markdown_files(repo)

    for path in files:
        rel = path.relative_to(repo).as_posix()
        text = read_text(path)
        visible_text = strip_fenced_code_blocks(text)

        for absolute_match in sorted(set(ABSOLUTE_LOCAL_RE.findall(visible_text))):
            warnings.append(f"{rel} contains a local absolute path: {absolute_match}")

        own_heading_ids = heading_cache.setdefault(path, markdown_heading_ids(text))
        for _, raw_target in LINK_RE.findall(visible_text):
            target = raw_target.strip()
            if not target or is_ignored_target(target):
                continue
            if target.startswith("#"):
                fragment = target[1:]
                if fragment and fragment not in own_heading_ids:
                    warnings.append(f"{rel} links to missing anchor: {target}")
                continue

            resolved = resolved_target(path, target)
            if resolved is None:
                continue
            if not resolved.exists():
                warnings.append(f"{rel} links to missing target: {target}")
                continue

            if "#" in target and resolved.suffix.lower() == ".md":
                fragment = target.split("#", 1)[1]
                target_heading_ids = heading_cache.setdefault(resolved, markdown_heading_ids(read_text(resolved)))
                if fragment and fragment not in target_heading_ids:
                    warnings.append(f"{rel} links to missing anchor: {target}")

    return {
        "ok": not warnings,
        "filesScanned": len(files),
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate markdown links and anchors across the whole repo.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    result = validate_repo(repo)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"files scanned: {result['filesScanned']}")
        if result["warnings"]:
            print("warnings:")
            for item in result["warnings"]:
                print(f"- {item}")
        print(f"ok: {result['ok']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
