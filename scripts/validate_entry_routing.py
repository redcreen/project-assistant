#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import (
    ENTRY_ROUTING_REQUIRED_SECTIONS,
    entry_routing_expected,
    parse_entry_routing,
    read_text,
    section,
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
    parser = argparse.ArgumentParser(description="Validate the durable entry-routing surface when the hard-entry layer is expected.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/entry-routing.md"
    warnings: list[str] = []

    if entry_routing_expected(repo):
        if not path.exists():
            warnings.append(".codex/entry-routing.md is missing while the entry-routing layer is expected")
        else:
            text = read_text(path)
            for heading in ENTRY_ROUTING_REQUIRED_SECTIONS:
                if f"## {heading}" not in text:
                    warnings.append(f".codex/entry-routing.md missing section: {heading}")
                elif not section_has_substance(text, heading):
                    warnings.append(f".codex/entry-routing.md has a weak or placeholder section: {heading}")
            parsed = parse_entry_routing(repo)
            if not parsed["direction"] or parsed["direction"] == "n/a":
                warnings.append(".codex/entry-routing.md missing a concrete entry direction")
            if not parsed["preflight_rows"]:
                warnings.append(".codex/entry-routing.md missing a usable preflight contract")
            if not parsed["output_rows"]:
                warnings.append(".codex/entry-routing.md missing a usable structured-output contract")
            if not parsed["bridge_rows"]:
                warnings.append(".codex/entry-routing.md missing a host/tool bridge boundary")
            if not parsed["next_checks"]:
                warnings.append(".codex/entry-routing.md missing next entry checks")

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
