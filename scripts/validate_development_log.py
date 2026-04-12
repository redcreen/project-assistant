#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TODO_LINE_RE = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+|>\s+)?TODO\b", re.IGNORECASE | re.MULTILINE)
SECTION_ALIASES = {
    "problem": ["## Problem", "## 问题"],
    "thinking": ["## Thinking", "## Thinking Path", "## 思考", "## 思路", "## 分析"],
    "solution": ["## Solution", "## 解决方案"],
    "validation": ["## Validation", "## 验证"],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate development-log structure and entry quality.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    devlog_dir = repo / "docs/devlog"
    warnings: list[str] = []

    if not devlog_dir.exists():
        warnings.append("docs/devlog/ is missing")
    else:
        for required in ["README.md", "README.zh-CN.md"]:
            if not (devlog_dir / required).exists():
                warnings.append(f"docs/devlog/{required} is missing")

        readme = (devlog_dir / "README.md").read_text(encoding="utf-8") if (devlog_dir / "README.md").exists() else ""
        readme_zh = (devlog_dir / "README.zh-CN.md").read_text(encoding="utf-8") if (devlog_dir / "README.zh-CN.md").exists() else ""

        for path in sorted(devlog_dir.glob("*.md")):
            if path.name in {"README.md", "README.zh-CN.md"}:
                continue
            rel = path.relative_to(repo).as_posix()
            text = path.read_text(encoding="utf-8")
            if TODO_LINE_RE.search(text):
                warnings.append(f"{rel} still contains TODO-style placeholder lines")
            for label, aliases in SECTION_ALIASES.items():
                if not any(alias in text for alias in aliases):
                    warnings.append(f"{rel} missing required devlog section: {label}")
            if path.name not in readme:
                warnings.append(f"docs/devlog/README.md does not list {path.name}")
            if path.name not in readme_zh:
                warnings.append(f"docs/devlog/README.zh-CN.md does not list {path.name}")

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
