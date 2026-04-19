#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import build_status_development_log_capture_body, read_text


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    replacement = rf"\1{body.rstrip()}\n\n"
    updated, count = re.subn(pattern, replacement, text, flags=re.MULTILINE | re.DOTALL)
    if count:
        return updated.rstrip() + "\n"
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh the live Development Log Capture state in .codex/status.md.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    status_path = repo / ".codex/status.md"
    status_text = read_text(status_path)
    if not status_text:
        raise SystemExit(".codex/status.md must exist before syncing development-log state")

    body = build_status_development_log_capture_body(repo)
    updated = replace_section(status_text, "Development Log Capture", body)
    status_path.write_text(updated, encoding="utf-8")
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
