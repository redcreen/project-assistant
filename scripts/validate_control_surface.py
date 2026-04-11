#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from control_surface_lib import validate_repo


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a repo control surface against project-assistant rules.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    result = validate_repo(args.repo.resolve())

    if args.format == "json":
        print(
            json.dumps(
                {
                    "ok": result.ok,
                    "tier": result.tier,
                    "officialModules": result.official_modules,
                    "missing": result.missing,
                    "warnings": result.warnings,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(f"tier: {result.tier}")
        print(f"official modules: {', '.join(result.official_modules) or '(none)'}")
        if result.missing:
            print("missing:")
            for item in result.missing:
                print(f"- {item}")
        if result.warnings:
            print("warnings:")
            for item in result.warnings:
                print(f"- {item}")
        print(f"ok: {result.ok}")

    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

