#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import (
    STRATEGY_REQUIRED_SECTIONS,
    parse_strategy_surface,
    read_text,
    section,
    strategy_surface_expected,
)


PLACEHOLDER_RE = re.compile(r"\bTODO\b|\bn/?a\b|\bnone\b", re.IGNORECASE)


def section_has_substance(text: str, heading: str) -> bool:
    block = section(text, heading)
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if not lines:
        return False
    if all(PLACEHOLDER_RE.search(line) for line in lines):
        return False
    return any(len(line) > 12 for line in lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a durable strategic surface when the strategy layer is expected.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/strategy.md"
    warnings: list[str] = []

    if strategy_surface_expected(repo):
        if not path.exists():
            warnings.append(".codex/strategy.md is missing while the strategy layer is expected")
        else:
            text = read_text(path)
            for heading in STRATEGY_REQUIRED_SECTIONS:
                if f"## {heading}" not in text:
                    warnings.append(f".codex/strategy.md missing section: {heading}")
                elif not section_has_substance(text, heading):
                    warnings.append(f".codex/strategy.md has a weak or placeholder section: {heading}")
            parsed = parse_strategy_surface(repo)
            if not parsed["direction"] or parsed["direction"] == "n/a":
                warnings.append(".codex/strategy.md missing a concrete strategic direction")
            if not parsed["why_now"] or parsed["why_now"] == "n/a":
                warnings.append(".codex/strategy.md missing a concrete why-now explanation")
            if not parsed["evidence_contract"]:
                warnings.append(".codex/strategy.md missing a usable strategy evidence contract")
            if not parsed["next_checks"]:
                warnings.append(".codex/strategy.md missing next strategic checks")

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
