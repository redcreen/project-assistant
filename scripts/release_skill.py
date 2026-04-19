#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from release_ref_lib import update_release_refs

ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "VERSION"
GATE_SCRIPT = ROOT / "scripts" / "validate_gate_set.py"


def run(*args: str) -> str:
    result = subprocess.run(args, cwd=ROOT, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def read_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def bump(version: str, mode: str) -> str:
    if re.fullmatch(r"\d+\.\d+\.\d+", mode):
        return mode
    major, minor, patch = [int(part) for part in version.split(".")]
    if mode == "major":
        return f"{major + 1}.0.0"
    if mode == "minor":
        return f"{major}.{minor + 1}.0"
    if mode == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Unsupported mode: {mode}")


def update_install_refs(version: str) -> list[Path]:
    VERSION_FILE.write_text(version + "\n", encoding="utf-8")
    return [VERSION_FILE, *update_release_refs(ROOT, version)]


def ensure_clean() -> None:
    status = run("git", "status", "--short")
    if status:
        raise SystemExit("working tree must be clean before release")


def ensure_release_gates() -> None:
    result = subprocess.run(
        [sys.executable, str(GATE_SCRIPT), str(ROOT), "--profile", "release"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise SystemExit(f"release validation gates failed before release\n{detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump project-assistant version, update install refs, commit, and tag.")
    parser.add_argument("mode", help="patch | minor | major | explicit version like 0.2.0")
    parser.add_argument("--push", action="store_true", help="Push commit and tag after creating them")
    args = parser.parse_args()

    ensure_clean()
    ensure_release_gates()
    current = read_version()
    next_version = bump(current, args.mode)
    tag = f"v{next_version}"

    touched = update_install_refs(next_version)

    run("git", "add", *sorted({str(path.relative_to(ROOT)) for path in touched}))
    run("git", "commit", "-m", f"chore: release {tag}")
    run("git", "tag", tag)

    if args.push:
        run("git", "push", "origin", "main")
        run("git", "push", "origin", tag)

    print(f"released: {tag}")
    if not args.push:
        print("next:")
        print("  git push origin main")
        print(f"  git push origin {tag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
