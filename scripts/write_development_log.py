#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


DEVLOG_HOME = """# Development Log

[English](README.md) | [中文](README.zh-CN.md)

## Purpose

This directory records durable implementation narratives: what went wrong, what we considered, what we changed, and how we verified it.

## Entries

{entries}
"""

DEVLOG_HOME_ZH = """# 开发日志

[English](README.md) | [中文](README.zh-CN.md)

## 目的

这个目录记录值得长期保留的实现过程：问题是什么、思考路径是什么、最后怎么解决、又是如何验证的。

## 条目

{entries}
"""


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_]+", "", value)
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "entry"


def ensure_devlog_indexes(devlog_dir: Path) -> None:
    devlog_dir.mkdir(parents=True, exist_ok=True)
    (devlog_dir / "README.md").write_text(DEVLOG_HOME.format(entries="- no entries yet"), encoding="utf-8")
    (devlog_dir / "README.zh-CN.md").write_text(DEVLOG_HOME_ZH.format(entries="- 暂无条目"), encoding="utf-8")


def first_heading(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return path.stem


def refresh_indexes(devlog_dir: Path) -> None:
    entries = sorted(
        p for p in devlog_dir.glob("*.md") if p.name not in {"README.md", "README.zh-CN.md"}
    )
    entries.reverse()
    if entries:
        en_lines = [f"- [{first_heading(path)}]({path.name})" for path in entries]
        zh_lines = [f"- [{first_heading(path)}]({path.name})" for path in entries]
    else:
        en_lines = ["- no entries yet"]
        zh_lines = ["- 暂无条目"]
    (devlog_dir / "README.md").write_text(DEVLOG_HOME.format(entries="\n".join(en_lines)), encoding="utf-8")
    (devlog_dir / "README.zh-CN.md").write_text(DEVLOG_HOME_ZH.format(entries="\n".join(zh_lines)), encoding="utf-8")


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    replacement = rf"\1{body.rstrip()}\n\n"
    updated, count = re.subn(pattern, replacement, text, flags=re.MULTILINE | re.DOTALL)
    if count:
        return updated.rstrip() + "\n"
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def relativize_repo_local_paths(repo: Path, text: str) -> str:
    repo_abs = str(repo.resolve())
    normalized = text.replace(f"{repo_abs}/", "")
    normalized = normalized.replace(repo_abs, ".")
    return normalized


def refresh_status_devlog_state(repo: Path, entry_rel: str) -> None:
    status_path = repo / ".codex/status.md"
    if not status_path.exists():
        return
    text = status_path.read_text(encoding="utf-8")
    if "## Development Log Capture" not in text:
        return
    body = "\n".join(
        [
            "- Trigger Level: high",
            "- Pending Capture: no",
            f"- Last Entry: {entry_rel}",
        ]
    )
    status_path.write_text(replace_section(text, "Development Log Capture", body), encoding="utf-8")


def render_entry(args: argparse.Namespace) -> str:
    problem = relativize_repo_local_paths(args.repo_root, args.problem)
    thinking = relativize_repo_local_paths(args.repo_root, args.thinking)
    solution = relativize_repo_local_paths(args.repo_root, args.solution)
    validation = relativize_repo_local_paths(args.repo_root, args.validation)
    followup_items = [relativize_repo_local_paths(args.repo_root, item) for item in args.followup]
    related_items = [relativize_repo_local_paths(args.repo_root, item) for item in args.related]
    if args.lang == "zh-CN":
        followups = "\n".join(f"- {item}" for item in followup_items) if followup_items else "- 无"
        related = "\n".join(f"- {item}" for item in related_items) if related_items else "- 无"
        return f"""# {args.title}

- 日期：{args.date}
- 状态：{args.status}

## 问题

{problem}

## 思考

{thinking}

## 解决方案

{solution}

## 验证

{validation}

## 后续

{followups}

## 相关文件

{related}
"""
    followups = "\n".join(f"- {item}" for item in followup_items) if followup_items else "- none"
    related = "\n".join(f"- {item}" for item in related_items) if related_items else "- none"
    return f"""# {args.title}

- Date: {args.date}
- Status: {args.status}

## Problem

{problem}

## Thinking

{thinking}

## Solution

{solution}

## Validation

{validation}

## Follow-Ups

{followups}

## Related Files

{related}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Write a durable development-log entry.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--title", required=True)
    parser.add_argument("--problem", required=True)
    parser.add_argument("--thinking", required=True)
    parser.add_argument("--solution", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--followup", action="append", default=[])
    parser.add_argument("--related", action="append", default=[])
    parser.add_argument("--lang", choices=["en", "zh-CN"], default="en")
    parser.add_argument("--status", default="resolved")
    parser.add_argument("--date", default=str(date.today()))
    parser.add_argument("--slug")
    args = parser.parse_args()

    repo = args.repo.resolve()
    args.repo_root = repo
    devlog_dir = repo / "docs/devlog"
    ensure_devlog_indexes(devlog_dir)

    slug = slugify(args.slug or args.title)
    entry_path = devlog_dir / f"{args.date}-{slug}.md"
    entry_path.write_text(render_entry(args), encoding="utf-8")
    refresh_indexes(devlog_dir)
    rel = entry_path.relative_to(repo).as_posix()
    refresh_status_devlog_state(repo, rel)
    print(rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
