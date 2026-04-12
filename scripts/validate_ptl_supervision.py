#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import (
    PTL_SUPERVISION_REQUIRED_SECTIONS,
    parse_ptl_supervision,
    ptl_supervision_expected,
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
    parser = argparse.ArgumentParser(description="Validate a durable PTL supervision surface when M13 is expected.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/ptl-supervision.md"
    warnings: list[str] = []

    if ptl_supervision_expected(repo):
        if not path.exists():
            warnings.append(".codex/ptl-supervision.md is missing while the PTL supervision layer is expected")
        else:
            text = read_text(path)
            for heading in PTL_SUPERVISION_REQUIRED_SECTIONS:
                if f"## {heading}" not in text:
                    warnings.append(f".codex/ptl-supervision.md missing section: {heading}")
                elif not section_has_substance(text, heading):
                    warnings.append(f".codex/ptl-supervision.md has a weak or placeholder section: {heading}")
            parsed = parse_ptl_supervision(repo)
            if not parsed["direction"] or parsed["direction"] == "n/a":
                warnings.append(".codex/ptl-supervision.md missing a concrete PTL direction")
            if not parsed["why_now"] or parsed["why_now"] == "n/a":
                warnings.append(".codex/ptl-supervision.md missing a concrete why-now explanation")
            if not parsed["contract"]:
                warnings.append(".codex/ptl-supervision.md missing a usable PTL supervision contract")
            if not parsed["trigger_rows"]:
                warnings.append(".codex/ptl-supervision.md missing supervision trigger rows")
            if not parsed["responsibility_rows"]:
                warnings.append(".codex/ptl-supervision.md missing standing responsibilities")
            if not parsed["matrix_rows"]:
                warnings.append(".codex/ptl-supervision.md missing continue / resequence / escalate matrix rows")
            if not parsed["check_rows"]:
                warnings.append(".codex/ptl-supervision.md missing active supervision checks")
            if not parsed["next_checks"]:
                warnings.append(".codex/ptl-supervision.md missing next PTL checks")

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
