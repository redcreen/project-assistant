#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import parse_official_modules, parse_tier, read_text


TODO_LINE_RE = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+|>\s+)?TODO\b", re.IGNORECASE | re.MULTILINE)
TEMPLATE_SNIPPETS = [
    "define the outcome this repo is meant to deliver",
    "define what this module owns",
    'define what "good enough" looks like for this module',
    "define the next concrete checkpoint",
    "retrofit in progress.",
    "control surface and durable-doc alignment.",
    "slice: control-surface alignment",
    "slice: durable-doc alignment",
    "slice: next execution selection",
    "repository scanned",
]


def warn_quality(rel: str, text: str, warnings: list[str]) -> None:
    if not text:
        warnings.append(f"{rel} is missing content")
        return
    if TODO_LINE_RE.search(text):
        warnings.append(f"{rel} still contains TODO-style placeholder lines")
    lowered = text.lower()
    for snippet in TEMPLATE_SNIPPETS:
        if snippet in lowered:
            warnings.append(f"{rel} still contains control-surface template text: {snippet}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate living control docs are not stuck in template state.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    tier = parse_tier(repo)
    warnings: list[str] = []

    paths = [repo / ".codex/brief.md", repo / ".codex/status.md"]
    if tier in {"medium", "large"}:
        paths.append(repo / ".codex/plan.md")

    for path in paths:
        rel = path.relative_to(repo).as_posix()
        warn_quality(rel, read_text(path), warnings)

    if tier == "large":
        for module in parse_official_modules(repo):
            path = repo / ".codex/modules" / f"{module}.md"
            if path.exists():
                warn_quality(path.relative_to(repo).as_posix(), read_text(path), warnings)

    payload = {"ok": not warnings, "warnings": warnings}
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if warnings:
            print("warnings:")
            for item in warnings:
                print(f"- {item}")
        print(f"ok: {payload['ok']}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
