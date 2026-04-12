#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "# 项目助手交接",
    "## 摘要",
    "## Restore Order",
)


def render(script: Path, repo: Path) -> str:
    result = subprocess.run(
        [sys.executable, str(script), str(repo)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the canonical project-assistant handoff entry panel.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    scripts_dir = Path(__file__).resolve().parent
    output = render(scripts_dir / "context_handoff.py", repo)
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in output]
    if missing:
        raise SystemExit(f"handoff entry output missing required headings: {', '.join(missing)}")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
