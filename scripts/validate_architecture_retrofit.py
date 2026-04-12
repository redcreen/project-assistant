#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import read_text, section


REQUIRED_SECTIONS = [
    "Trigger",
    "Primary Symptoms",
    "Root-Cause Drivers",
    "Affected Boundaries",
    "Current Architecture Sources",
    "Target Architecture",
    "Retrofit Scope",
    "Execution Strategy",
    "Validation",
    "Exit Conditions",
]

PLACEHOLDER_RE = re.compile(r"\bTODO\b|\bnone\b", re.IGNORECASE)


def section_has_substance(text: str, heading: str) -> bool:
    block = section(text, heading)
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if not lines:
        return False
    if all(PLACEHOLDER_RE.search(line) for line in lines):
        return False
    return any(len(line) > 12 for line in lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an architecture-retrofit working note when present.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/architecture-retrofit.md"
    warnings: list[str] = []

    if path.exists():
        text = read_text(path)
        for heading in REQUIRED_SECTIONS:
            if f"## {heading}" not in text:
                warnings.append(f".codex/architecture-retrofit.md missing section: {heading}")
            elif not section_has_substance(text, heading):
                warnings.append(f".codex/architecture-retrofit.md has a weak or placeholder section: {heading}")

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
