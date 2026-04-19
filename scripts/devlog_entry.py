#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from control_surface_lib import build_status_development_log_capture_body
from sync_resume_readiness import ensure_resume_ready


def render_panel(repo: Path) -> str:
    return "\n".join(
        [
            "# 项目助手开发日志",
            "",
            "## 当前捕获状态",
            build_status_development_log_capture_body(repo),
            "",
            "## 写入方法",
            "- `project-assistant devlog <repo> --title \"...\" --problem \"...\" --thinking \"...\" --solution \"...\" --validation \"...\"`",
            "- 可选参数：`--lang zh-CN|en`、`--status resolved`、`--date YYYY-MM-DD`、`--slug ...`、`--followup ...`、`--related ...`",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render the project-assistant devlog window or write a new devlog entry.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--title")
    parser.add_argument("--problem")
    parser.add_argument("--thinking")
    parser.add_argument("--solution")
    parser.add_argument("--validation")
    parser.add_argument("--followup", action="append", default=[])
    parser.add_argument("--related", action="append", default=[])
    parser.add_argument("--lang", choices=["en", "zh-CN"], default="en")
    parser.add_argument("--status", default="resolved")
    parser.add_argument("--date")
    parser.add_argument("--slug")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    ensure_resume_ready(repo, check_only=False)
    sync_script = Path(__file__).resolve().with_name("sync_development_log_state.py")
    subprocess.run(
        [sys.executable, str(sync_script), str(repo)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    required_fields = [args.title, args.problem, args.thinking, args.solution, args.validation]
    if not any(required_fields):
        print(render_panel(repo))
        return 0
    if not all(required_fields):
        raise SystemExit("--title, --problem, --thinking, --solution, and --validation must either all be provided or all be omitted")

    script = Path(__file__).resolve().with_name("write_development_log.py")
    cmd = [
        sys.executable,
        str(script),
        str(repo),
        "--title",
        args.title,
        "--problem",
        args.problem,
        "--thinking",
        args.thinking,
        "--solution",
        args.solution,
        "--validation",
        args.validation,
        "--lang",
        args.lang,
        "--status",
        args.status,
    ]
    if args.date:
        cmd.extend(["--date", args.date])
    if args.slug:
        cmd.extend(["--slug", args.slug])
    for item in args.followup:
        cmd.extend(["--followup", item])
    for item in args.related:
        cmd.extend(["--related", item])

    result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
