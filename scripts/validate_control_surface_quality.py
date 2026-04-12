#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import parse_official_modules, parse_tier, read_text


TODO_LINE_RE = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+|>\s+)?TODO\b", re.IGNORECASE | re.MULTILINE)
TEMPLATE_SNIPPETS = [
    "define the outcome this repo is meant to deliver",
    "define what this module owns",
    'define what "good enough" looks like for this module',
    "define the next concrete checkpoint",
    "retrofit in progress.",
    "control surface and durable-doc alignment.",
    "slice: control-surface alignment",
    "slice: durable-doc alignment",
    "slice: next execution selection",
    "repository scanned",
    "establish the next meaningful autonomous run",
    "one checkpoint-sized execution line",
    "confirm the active slice and intended checkpoint",
    "architecture supervision is still mostly a policy",
    "the repo may still drift toward local fixes",
    "the assistant can keep converging the repo unless",
]


def section_block(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def section_has_substance(text: str, heading: str) -> bool:
    block = section_block(text, heading)
    lines = [line.strip("` ").strip() for line in block.splitlines() if line.strip()]
    return any(len(line) > 12 for line in lines)


def extract_tasks(text: str) -> list[str]:
    block = section_block(text, "Execution Tasks")
    tasks: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if re.match(r"^- \[[ xX]\]\s+", stripped):
            tasks.append(stripped)
    return tasks


def has_bullet_label(text: str, label: str) -> bool:
    prefix = f"- {label}:"
    return any(line.strip().startswith(prefix) for line in text.splitlines())


def has_substantive_labeled_bullet(text: str, label: str) -> bool:
    for line in text.splitlines():
        stripped = line.strip()
        prefix = f"- {label}:"
        if stripped.startswith(prefix):
            value = stripped.split(":", 1)[1].strip().strip("`")
            min_len = 1 if label in {"Signal", "Current Gate", "Escalation Gate", "Trigger Level", "Pending Capture"} else 8
            return len(value) >= min_len
    return False


def has_nested_items_after_label(text: str, label: str) -> bool:
    lines = text.splitlines()
    prefix = f"- {label}:"
    for index, line in enumerate(lines):
        if line.strip().startswith(prefix):
            for follow in lines[index + 1 :]:
                stripped = follow.strip()
                if not stripped:
                    continue
                if stripped.startswith("- "):
                    return True
                if re.match(r"^\d+\.\s+", stripped):
                    return True
                if stripped.startswith("- ") and not follow.startswith("  "):
                    break
                if re.match(r"^- [A-Za-z].*:", stripped):
                    break
            return False
    return False


def warn_quality(rel: str, text: str, warnings: list[str]) -> None:
    if not text:
        warnings.append(f"{rel} is missing content")
        return
    if TODO_LINE_RE.search(text):
        warnings.append(f"{rel} still contains TODO-style placeholder lines")
    lowered = text.lower()
    for snippet in TEMPLATE_SNIPPETS:
        if snippet in lowered:
            warnings.append(f"{rel} still contains control-surface template text: {snippet}")
    if "## Current Execution Line" in text and not section_has_substance(text, "Current Execution Line"):
        warnings.append(f"{rel} has a Current Execution Line section without concrete content")
    if "## Execution Tasks" in text:
        tasks = extract_tasks(text)
        if len(tasks) < 2:
            warnings.append(f"{rel} has too few execution tasks for a meaningful execution line")
        if not tasks:
            warnings.append(f"{rel} execution tasks are missing checkbox-style task lines")
    if "## Architecture Supervision" in text:
        for label in ["Signal", "Signal Basis", "Root Cause Hypothesis", "Correct Layer", "Escalation Gate"]:
            if not has_substantive_labeled_bullet(section_block(text, "Architecture Supervision"), label):
                warnings.append(f"{rel} has an Architecture Supervision section without a concrete {label}")
    if "## Development Log Capture" in text:
        block = section_block(text, "Development Log Capture")
        if "Pending Capture" in block or "Last Entry" in block:
            for label in ["Trigger Level", "Pending Capture", "Last Entry"]:
                if not has_substantive_labeled_bullet(block, label):
                    warnings.append(f"{rel} has a Development Log Capture section without a concrete {label}")
        else:
            if not has_substantive_labeled_bullet(block, "Trigger Level"):
                warnings.append(f"{rel} has a Development Log Capture section without a concrete Trigger Level")
            for label in ["Auto-Capture When", "Skip When"]:
                if not has_bullet_label(block, label) or not has_nested_items_after_label(block, label):
                    warnings.append(f"{rel} has a Development Log Capture section without a concrete {label}")
    if "## Escalation Model" in text:
        for label in ["Continue Automatically", "Raise But Continue", "Require User Decision"]:
            if not has_substantive_labeled_bullet(section_block(text, "Escalation Model"), label):
                warnings.append(f"{rel} has an Escalation Model section without a concrete {label}")
    if "## Current Escalation State" in text:
        for label in ["Current Gate", "Reason", "Next Review Trigger"]:
            if not has_substantive_labeled_bullet(section_block(text, "Current Escalation State"), label):
                warnings.append(f"{rel} has a Current Escalation State section without a concrete {label}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate living control docs are not stuck in template state.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    tier = parse_tier(repo)
    warnings: list[str] = []

    paths = [repo / ".codex/brief.md", repo / ".codex/status.md"]
    if tier in {"medium", "large"}:
        paths.append(repo / ".codex/plan.md")

    for path in paths:
        rel = path.relative_to(repo).as_posix()
        warn_quality(rel, read_text(path), warnings)

    if tier == "large":
        for module in parse_official_modules(repo):
            path = repo / ".codex/modules" / f"{module}.md"
            if path.exists():
                warn_quality(path.relative_to(repo).as_posix(), read_text(path), warnings)

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
