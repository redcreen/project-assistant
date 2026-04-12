#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import (
    WORKER_HANDOFF_REQUIRED_SECTIONS,
    parse_worker_handoff,
    read_text,
    section,
    worker_handoff_expected,
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
    parser = argparse.ArgumentParser(description="Validate a durable worker-handoff surface when M14 is expected.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/worker-handoff.md"
    warnings: list[str] = []

    if worker_handoff_expected(repo):
        if not path.exists():
            warnings.append(".codex/worker-handoff.md is missing while the worker-handoff layer is expected")
        else:
            text = read_text(path)
            for heading in WORKER_HANDOFF_REQUIRED_SECTIONS:
                if f"## {heading}" not in text:
                    warnings.append(f".codex/worker-handoff.md missing section: {heading}")
                elif not section_has_substance(text, heading):
                    warnings.append(f".codex/worker-handoff.md has a weak or placeholder section: {heading}")
            parsed = parse_worker_handoff(repo)
            if not parsed["direction"] or parsed["direction"] == "n/a":
                warnings.append(".codex/worker-handoff.md missing a concrete handoff direction")
            if not parsed["why_now"] or parsed["why_now"] == "n/a":
                warnings.append(".codex/worker-handoff.md missing a concrete why-now explanation")
            if not parsed["contract"]:
                warnings.append(".codex/worker-handoff.md missing a usable handoff contract")
            if not parsed["trigger_rows"]:
                warnings.append(".codex/worker-handoff.md missing handoff trigger rows")
            if not parsed["source_rows"]:
                warnings.append(".codex/worker-handoff.md missing recovery sources")
            if not parsed["action_rows"]:
                warnings.append(".codex/worker-handoff.md missing re-entry actions")
            if not parsed["queue_rows"]:
                warnings.append(".codex/worker-handoff.md missing queue / return rules")
            if not parsed["escalation_rows"]:
                warnings.append(".codex/worker-handoff.md missing human escalation boundary")
            if not parsed["next_checks"]:
                warnings.append(".codex/worker-handoff.md missing next handoff checks")

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
