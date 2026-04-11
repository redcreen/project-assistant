#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from control_surface_lib import parse_tier


SCRIPT_DIR = Path(__file__).resolve().parent

FAST_VALIDATORS = [
    "validate_control_surface.py",
    "validate_docs_system.py",
    "validate_public_docs_i18n.py",
]

DEEP_ONLY_VALIDATORS = [
    "validate_markdown_governance.py",
    "validate_doc_quality.py",
]


def resolved_profile(repo: Path, profile: str) -> str:
    if profile != "auto":
        return profile
    tier = parse_tier(repo)
    return "deep" if tier == "large" else "fast"


def run_validator(script_name: str, repo: Path) -> tuple[bool, str]:
    script = SCRIPT_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(script), str(repo), "--format", "text"],
        text=True,
        capture_output=True,
    )
    output = result.stdout.strip()
    if result.stderr.strip():
        output = (output + "\n" + result.stderr.strip()).strip()
    return result.returncode == 0, output


def main() -> int:
    parser = argparse.ArgumentParser(description="Run layered retrofit validation gates.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--profile", choices=["auto", "fast", "deep"], default="auto")
    args = parser.parse_args()

    repo = args.repo.resolve()
    profile = resolved_profile(repo, args.profile)
    validators = list(FAST_VALIDATORS)
    if profile == "deep":
        validators.extend(DEEP_ONLY_VALIDATORS)

    failed = False
    print(f"profile: {profile}")
    for script_name in validators:
        ok, output = run_validator(script_name, repo)
        print(f"[{script_name}]")
        if output:
            print(output)
        if not ok:
            failed = True

    print(f"ok: {not failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
