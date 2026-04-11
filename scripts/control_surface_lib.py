#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REPO_CODEX = ".codex"


@dataclass
class ValidationResult:
    ok: bool
    tier: str
    official_modules: list[str]
    missing: list[str]
    warnings: list[str]


STATUS_COMPLETION_RULES: list[tuple[tuple[str, ...], int]] = [
    (("missing",), 0),
    (("planned",), 20),
    (("baseline-complete", "next-phase"), 78),
    (("candidate",), 70),
    (("active",), 80),
    (("governing",), 90),
    (("maintain",), 95),
    (("baseline-complete",), 85),
    (("complete",), 100),
]


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_]+", "", value)
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def parse_tier(repo: Path) -> str:
    for rel in [".codex/brief.md", ".codex/status.md"]:
        text = read_text(repo / rel)
        match = re.search(r"Tier:\s*`?([a-z]+)`?", text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    return "medium"


def parse_official_modules(repo: Path) -> list[str]:
    configured = load_control_surface_config(repo).get("officialModules")
    if isinstance(configured, list) and configured:
        return [str(item) for item in configured if str(item).strip()]

    candidates: list[str] = []

    project_roadmap = read_text(repo / "project-roadmap.md")
    match = re.search(
        r"first-class modules are:\s*(.*?)\n## ",
        project_roadmap,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        match = re.search(
            r"一等模块组织：\s*(.*?)\n## ",
            project_roadmap,
            re.IGNORECASE | re.DOTALL,
        )
    if match:
        for line in match.group(1).splitlines():
            m = re.match(r"\s*\d+\.\s+\**`?([^`\n*]+?)`?\**\s*$", line)
            if m:
                candidates.append(slugify(m.group(1)))

    if candidates:
        return dedupe_preserve_order(candidates)

    architecture_map = read_text(repo / "docs/unified-memory-core/architecture/README.md")
    for line in architecture_map.splitlines():
        m = re.match(r"\s*-\s+\[([^\]]+)\]\(([^)]+)\)", line)
        if not m:
            continue
        label = m.group(1).strip()
        if label.lower() in {"deployment-topology", "../deployment-topology.md"}:
            continue
        candidates.append(slugify(label))

    return dedupe_preserve_order(candidates)


def dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def expected_module_files(repo: Path, official_modules: list[str]) -> list[Path]:
    return [repo / ".codex/modules" / f"{name}.md" for name in official_modules]


def has_required_headings(text: str, headings: list[str]) -> bool:
    return all(f"## {heading}" in text for heading in headings)


def validate_repo(repo: Path) -> ValidationResult:
    tier = parse_tier(repo)
    official_modules = parse_official_modules(repo)
    missing: list[str] = []
    warnings: list[str] = []

    required = [".codex/brief.md", ".codex/status.md"]
    if tier in {"medium", "large"}:
        required.append(".codex/plan.md")
    if tier == "large":
        required.append(".codex/module-dashboard.md")

    for rel in required:
        if not (repo / rel).exists():
            missing.append(rel)

    status_text = read_text(repo / ".codex/status.md")
    if tier == "large" and "retrofit" in status_text.lower():
        warnings.append("status still contains retrofit-oriented language")

    if tier == "large" and official_modules:
        module_dir = repo / ".codex/modules"
        if not module_dir.exists():
            missing.append(".codex/modules/")
        for path in expected_module_files(repo, official_modules):
            if not path.exists():
                missing.append(str(path.relative_to(repo)))
                continue
            module_text = read_text(path)
            if not has_required_headings(
                module_text,
                [
                    "Ownership",
                    "Current Status",
                    "Already Implemented",
                    "Remaining Steps",
                    "Completion Signal",
                    "Next Checkpoint",
                ],
            ):
                warnings.append(f"{path.relative_to(repo)} missing required headings")

        dashboard_text = read_text(repo / ".codex/module-dashboard.md")
        if not has_required_headings(dashboard_text, ["Modules"]):
            warnings.append(".codex/module-dashboard.md missing Modules section")
        required_columns = ["Already Implemented", "Completion %", "Next Checkpoint"]
        if not all(column in dashboard_text for column in required_columns):
            warnings.append(".codex/module-dashboard.md missing detailed module columns")
        dashboard_modules = parse_module_dashboard_rows(dashboard_text)
        for module in official_modules:
            if module not in dashboard_modules:
                warnings.append(f".codex/module-dashboard.md missing row for {module}")

    return ValidationResult(
        ok=not missing and not warnings,
        tier=tier,
        official_modules=official_modules,
        missing=missing,
        warnings=warnings,
    )


def load_control_surface_config(repo: Path) -> dict:
    path = repo / ".codex/control-surface.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_control_surface_config(repo: Path, tier: str, official_modules: list[str]) -> None:
    path = repo / ".codex/control-surface.json"
    payload = {
        "tier": tier,
        "officialModules": official_modules,
        "requiredFiles": [
            ".codex/brief.md",
            ".codex/plan.md" if tier in {"medium", "large"} else None,
            ".codex/status.md",
            ".codex/module-dashboard.md" if tier == "large" else None,
        ],
    }
    payload["requiredFiles"] = [item for item in payload["requiredFiles"] if item]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def completion_percent(status: str) -> int:
    lowered = status.lower().strip()
    for tokens, value in STATUS_COMPLETION_RULES:
        if all(token in lowered for token in tokens):
            return value
    if "baseline" in lowered:
        return 80
    if "planned" in lowered:
        return 20
    return 60


def completion_band(status: str) -> str:
    percent = completion_percent(status)
    if percent >= 95:
        return "maintain"
    if percent >= 85:
        return "stable"
    if percent >= 75:
        return "active"
    if percent >= 50:
        return "forming"
    return "planned"


def parse_module_dashboard_rows(text: str) -> set[str]:
    modules_section = ""
    match = re.search(r"^## Modules\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if match:
        modules_section = match.group(1)
    rows: set[str] = set()
    for line in modules_section.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or cells[0] in {"Module", "---"}:
            continue
        rows.add(slugify(cells[0]))
    return rows
