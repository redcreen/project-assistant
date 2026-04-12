#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import (
    PROGRAM_BOARD_REQUIRED_SECTIONS,
    parse_program_board,
    program_board_expected,
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
    parser = argparse.ArgumentParser(description="Validate a durable program-board surface when the orchestration layer is expected.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/program-board.md"
    warnings: list[str] = []

    if program_board_expected(repo):
        if not path.exists():
            warnings.append(".codex/program-board.md is missing while the program-orchestration layer is expected")
        else:
            text = read_text(path)
            for heading in PROGRAM_BOARD_REQUIRED_SECTIONS:
                if f"## {heading}" not in text:
                    warnings.append(f".codex/program-board.md missing section: {heading}")
                elif not section_has_substance(text, heading):
                    warnings.append(f".codex/program-board.md has a weak or placeholder section: {heading}")
            parsed = parse_program_board(repo)
            if not parsed["direction"] or parsed["direction"] == "n/a":
                warnings.append(".codex/program-board.md missing a concrete program direction")
            if not parsed["why_now"] or parsed["why_now"] == "n/a":
                warnings.append(".codex/program-board.md missing a concrete why-now explanation")
            if not parsed["contract"]:
                warnings.append(".codex/program-board.md missing a usable program orchestration contract")
            if not parsed["workstreams"]:
                warnings.append(".codex/program-board.md missing active workstreams")
            if not parsed["queue"]:
                warnings.append(".codex/program-board.md missing sequencing queue rows")
            if not parsed["executors"]:
                warnings.append(".codex/program-board.md missing executor inputs")
            if not parsed["next_checks"]:
                warnings.append(".codex/program-board.md missing next orchestration checks")

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
