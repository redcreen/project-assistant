#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REQUIRED_HEADINGS = (
    "# 项目进展",
    "## 一眼总览",
    "## 当前定位",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the canonical project-assistant progress entry panel.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    scripts_dir = Path(__file__).resolve().parent
    subprocess.run([sys.executable, str(scripts_dir / "sync_plan_docs.py"), str(repo)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = render(scripts_dir / "progress_snapshot.py", repo)
    ptl_result = subprocess.run(
        [sys.executable, str(scripts_dir / "ptl_gate.py"), "preflight", str(repo), "--mode", "progress"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if ptl_result.stdout.strip():
        output = f"{output}\n\n{ptl_result.stdout.strip()}"
    completion_result = subprocess.run(
        [sys.executable, str(scripts_dir / "completion_gate.py"), "check", str(repo)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if completion_result.stdout.strip():
        output = f"{output}\n\n{completion_result.stdout.strip()}"
    pipeline_result = subprocess.run(
        [sys.executable, str(scripts_dir / "pipeline_runner.py"), "panel", str(repo)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if pipeline_result.stdout.strip():
        output = f"{output}\n\n{pipeline_result.stdout.strip()}"
    ingress_result = subprocess.run(
        [sys.executable, str(scripts_dir / "message_ingress.py"), "panel", str(repo)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if ingress_result.stdout.strip():
        output = f"{output}\n\n{ingress_result.stdout.strip()}"
    app_loop_result = subprocess.run(
        [sys.executable, str(scripts_dir / "codex_app_loop.py"), "panel", str(repo)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if app_loop_result.stdout.strip():
        output = f"{output}\n\n{app_loop_result.stdout.strip()}"
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in output]
    if missing:
        raise SystemExit(f"progress entry output missing required headings: {', '.join(missing)}")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
