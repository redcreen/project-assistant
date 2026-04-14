#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import (
    DOGFOODING_EVIDENCE_REQUIRED_SECTIONS,
    dogfooding_evidence_expected,
    parse_dogfooding_evidence,
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
    parser = argparse.ArgumentParser(description="Validate the durable dogfooding-evidence surface when broader adoption evidence is active.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/dogfooding-evidence.md"
    warnings: list[str] = []

    if dogfooding_evidence_expected(repo):
        if not path.exists():
            warnings.append(".codex/dogfooding-evidence.md is missing while broader dogfooding evidence is expected")
        else:
            text = read_text(path)
            for heading in DOGFOODING_EVIDENCE_REQUIRED_SECTIONS:
                if f"## {heading}" not in text:
                    warnings.append(f".codex/dogfooding-evidence.md missing section: {heading}")
                elif not section_has_substance(text, heading):
                    warnings.append(f".codex/dogfooding-evidence.md has a weak or placeholder section: {heading}")
            parsed = parse_dogfooding_evidence(repo)
            if not parsed["direction"] or parsed["direction"] == "n/a":
                warnings.append(".codex/dogfooding-evidence.md missing a concrete evidence direction")
            if not parsed["why_now"] or parsed["why_now"] == "n/a":
                warnings.append(".codex/dogfooding-evidence.md missing a concrete why-now explanation")
            if not parsed["contract"]:
                warnings.append(".codex/dogfooding-evidence.md missing a usable evidence collection contract")
            if not parsed["snapshot_rows"]:
                warnings.append(".codex/dogfooding-evidence.md missing evidence snapshot rows")
            if not parsed["gap_rows"]:
                warnings.append(".codex/dogfooding-evidence.md missing evidence-gap rows")
            if not parsed["decision_rows"]:
                warnings.append(".codex/dogfooding-evidence.md missing evidence-gated decision rows")
            if not parsed["next_checks"]:
                warnings.append(".codex/dogfooding-evidence.md missing next evidence checks")

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
