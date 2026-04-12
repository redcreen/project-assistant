#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO_CODEX = ".codex"
DOC_GOVERNANCE = ".codex/doc-governance.json"
COMMON_ROOT_DOCS = [
    "README.md",
    "README.zh-CN.md",
    "CHANGELOG.md",
    "CHANGELOG.zh-CN.md",
    "RELEASE.md",
    "RELEASE.zh-CN.md",
    "release.md",
    "architecture.md",
    "roadmap.md",
    "CONTRIBUTING.md",
    "CONTRIBUTING.zh-CN.md",
    "SECURITY.md",
    "SECURITY.zh-CN.md",
]


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


def is_skill_repo(repo: Path) -> bool:
    return (repo / "SKILL.md").exists() and (repo / "references").exists()


def parse_tier(repo: Path) -> str:
    for rel in [".codex/brief.md", ".codex/status.md"]:
        text = read_text(repo / rel)
        match = re.search(r"Tier:\s*`?([a-z]+)`?", text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
    return "medium"


def parse_official_modules(repo: Path) -> list[str]:
    if is_skill_repo(repo):
        return []
    configured = load_control_surface_config(repo).get("officialModules")
    if isinstance(configured, list) and configured:
        return [str(item) for item in configured if str(item).strip()]
    governance_path = repo / DOC_GOVERNANCE
    governance_configured: list[str] | None = None
    if governance_path.exists():
        try:
            payload = json.loads(governance_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        if isinstance(payload, dict):
            configured_list = payload.get("officialModules")
            if isinstance(configured_list, list):
                governance_configured = [str(item) for item in configured_list if str(item).strip()]
    if isinstance(governance_configured, list) and governance_configured:
        return governance_configured

    candidates: list[str] = []

    module_dir = repo / ".codex/modules"
    if module_dir.exists():
        for path in sorted(module_dir.glob("*.md")):
            if path.stem:
                candidates.append(slugify(path.stem))

    if candidates:
        return dedupe_preserve_order(candidates)

    dashboard_text = read_text(repo / ".codex/module-dashboard.md")
    dashboard_rows = parse_module_dashboard_rows(dashboard_text)
    if dashboard_rows:
        return sorted(dashboard_rows)

    module_map = read_text(repo / "docs/module-map.md")
    for line in module_map.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"Module", "---"}:
            continue
        if cells[0]:
            candidates.append(slugify(cells[0]))

    if candidates:
        return dedupe_preserve_order(candidates)

    architecture = read_text(repo / "docs/architecture.md")
    in_table = False
    for line in architecture.splitlines():
        stripped = line.strip()
        if stripped.startswith("| Module |"):
            in_table = True
            continue
        if in_table:
            if not stripped.startswith("|"):
                break
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if not cells or cells[0] in {"---", "Module"}:
                continue
            candidates.append(slugify(cells[0]))

    if candidates:
        return dedupe_preserve_order(candidates)

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


def validate_commands_doc(text: str) -> list[str]:
    warnings: list[str] = []
    lowered = text.lower()
    if "项目助手" not in text:
        warnings.append(".codex/COMMANDS.md missing Chinese simple commands")
    if "project assistant" not in lowered:
        warnings.append(".codex/COMMANDS.md missing English simple commands")
    return warnings


def validate_repo(repo: Path) -> ValidationResult:
    tier = parse_tier(repo)
    official_modules = parse_official_modules(repo)
    missing: list[str] = []
    warnings: list[str] = []

    required = [".codex/brief.md", ".codex/status.md", ".codex/COMMANDS.md", DOC_GOVERNANCE]
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

    commands_text = read_text(repo / ".codex/COMMANDS.md")
    if commands_text:
        warnings.extend(validate_commands_doc(commands_text))

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


def load_doc_governance_config(repo: Path) -> dict[str, Any]:
    path = repo / DOC_GOVERNANCE
    if not path.exists():
        return default_doc_governance_payload(repo, parse_tier(repo), parse_official_modules(repo))
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    merged = default_doc_governance_payload(repo, parse_tier(repo), parse_official_modules(repo))
    return merge_doc_governance(merged, payload)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def unique_list(values: Iterable[Any]) -> list[Any]:
    result: list[Any] = []
    seen: set[str] = set()
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else repr(value)
        if key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def merge_question_owner(default_spec: dict[str, Any], override_spec: dict[str, Any]) -> dict[str, Any]:
    merged = dict(default_spec)
    for key, value in override_spec.items():
        if key in {"allowed", "allowedGlobs", "tokens"} and isinstance(value, list):
            merged[key] = unique_list(list(default_spec.get(key, [])) + value)
        else:
            merged[key] = value
    return merged


def merge_doc_governance(defaults: dict[str, Any], existing: dict[str, Any]) -> dict[str, Any]:
    merged = dict(defaults)
    list_keys = {
        "rootKeep",
        "requiredPaths",
        "publicDocIncludeGlobs",
        "publicDocExcludeGlobs",
        "questionExcludeGlobs",
        "officialModules",
    }
    for key, value in existing.items():
        if key == "ownershipRules" and isinstance(value, list):
            merged[key] = unique_list(list(defaults.get(key, [])) + value)
        elif key == "questionOwners" and isinstance(value, dict):
            base_question_owners = defaults.get(key, {})
            combined: dict[str, Any] = dict(base_question_owners)
            for question, spec in value.items():
                if isinstance(spec, dict) and isinstance(base_question_owners.get(question), dict):
                    combined[question] = merge_question_owner(base_question_owners[question], spec)
                else:
                    combined[question] = spec
            merged[key] = combined
        elif key == "explicitMoves" and isinstance(value, dict):
            payload = dict(defaults.get(key, {}))
            payload.update(value)
            merged[key] = payload
        elif key in list_keys and isinstance(value, list):
            merged[key] = unique_list(list(defaults.get(key, [])) + value)
        else:
            merged[key] = value
    return merged


def default_root_keep(repo: Path, skill_repo: bool) -> list[str]:
    if skill_repo:
        keep = ["README.md", "README.zh-CN.md", "SKILL.md"]
    else:
        keep = [name for name in COMMON_ROOT_DOCS if (repo / name).exists()]
        if not keep:
            keep = ["README.md", "README.zh-CN.md"]
    return keep


def default_doc_governance_payload(repo: Path, tier: str, official_modules: list[str]) -> dict[str, Any]:
    skill_repo = is_skill_repo(repo)
    if skill_repo:
        return {
            "repoKind": "skill",
            "userCustomized": False,
            "rootKeep": default_root_keep(repo, True),
            "requiredPaths": [
                "references/README.md",
                "references/README.zh-CN.md",
            ],
            "docsHomeLinks": {
                "en": ["../SKILL.md", "../references/README.md"],
                "zh": ["../SKILL.md", "../references/README.zh-CN.md"],
            },
            "publicDocIncludeGlobs": [
                "README.md",
                "docs/*.md",
                "docs/**/*.md",
                "references/README.md",
            ],
            "publicDocExcludeGlobs": [
                ".codex/**",
            ],
            "ownershipRules": [
                {"glob": ".codex/*.md", "role": "living"},
                {"glob": ".codex/**/*.md", "role": "living"},
                {"glob": "README.md", "role": "durable"},
                {"glob": "README.zh-CN.md", "role": "durable"},
                {"glob": "SKILL.md", "role": "durable"},
                {"glob": "docs/*.md", "role": "durable"},
                {"glob": "docs/**/*.md", "role": "durable"},
                {"glob": "references/*.md", "role": "durable"},
                {"glob": "references/**/*.md", "role": "durable"},
                {"glob": "scripts/*.md", "role": "internal"},
                {"glob": "scripts/**/*.md", "role": "internal"},
                {"glob": "agents/**/*.md", "role": "internal"},
            ],
            "questionOwners": {
                "architecture": {
                    "allowed": ["docs/architecture.md", "docs/architecture.zh-CN.md"],
                    "allowedGlobs": [],
                    "tokens": ["architecture"],
                },
                "roadmap": {
                    "allowed": ["docs/roadmap.md", "docs/roadmap.zh-CN.md"],
                    "allowedGlobs": [],
                    "tokens": ["roadmap"],
                },
                "test-plan": {
                    "allowed": ["docs/test-plan.md", "docs/test-plan.zh-CN.md"],
                    "allowedGlobs": [],
                    "tokens": ["test-plan"],
                },
                "skill-contract": {
                    "allowed": ["SKILL.md"],
                    "allowedGlobs": [],
                    "tokens": ["skill"],
                },
            },
            "questionExcludeGlobs": [
                ".codex/**",
                "docs/adr/**",
                "scripts/**",
                "agents/**",
            ],
            "explicitMoves": {},
        }

    return {
        "repoKind": "repo",
        "userCustomized": False,
        "tier": tier,
        "officialModules": official_modules,
        "rootKeep": default_root_keep(repo, False),
        "requiredPaths": [
            "docs/reference/README.md",
            "docs/reference/README.zh-CN.md",
            "docs/workstreams/README.md",
            "docs/workstreams/README.zh-CN.md",
            "docs/archive/README.md",
            "docs/archive/README.zh-CN.md",
            "reports/generated/README.md",
        ],
        "docsHomeLinks": {
            "en": [
                "reference/README.md",
                "workstreams/README.md",
                "archive/README.md",
            ],
            "zh": [
                "reference/README.zh-CN.md",
                "workstreams/README.zh-CN.md",
                "archive/README.zh-CN.md",
            ],
        },
        "publicDocIncludeGlobs": [
            "README.md",
            "CHANGELOG.md",
            "RELEASE.md",
            "release.md",
            "docs/*.md",
            "docs/adr/*.md",
            "docs/adr/**/*.md",
            "docs/reference/*.md",
            "docs/reference/**/*.md",
            "docs/workstreams/*.md",
            "docs/workstreams/**/*.md",
            "docs/how-to/*.md",
            "docs/how-to/**/*.md",
            "integrations/**/README.md",
        ],
        "publicDocExcludeGlobs": [
            ".codex/**",
            "docs/archive/**",
            "reports/**",
            "workspace/**",
            "releases/**",
            "scripts/**",
            "src/**",
            "test/**",
            "evals/**",
        ],
        "ownershipRules": [
            {"glob": ".codex/*.md", "role": "living"},
            {"glob": ".codex/**/*.md", "role": "living"},
            {"glob": "README.md", "role": "durable"},
            {"glob": "README.zh-CN.md", "role": "durable"},
            {"glob": "CHANGELOG.md", "role": "durable"},
            {"glob": "CHANGELOG.zh-CN.md", "role": "durable"},
            {"glob": "RELEASE.md", "role": "durable"},
            {"glob": "RELEASE.zh-CN.md", "role": "durable"},
            {"glob": "release.md", "role": "durable"},
            {"glob": "docs/*.md", "role": "durable"},
            {"glob": "docs/**/*.md", "role": "durable"},
            {"glob": "docs/reference/*.md", "role": "durable"},
            {"glob": "docs/reference/**/*.md", "role": "durable"},
            {"glob": "docs/archive/*.md", "role": "archive"},
            {"glob": "docs/archive/**/*.md", "role": "archive"},
            {"glob": "integrations/**/*.md", "role": "durable"},
            {"glob": "docs/workstreams/*.md", "role": "durable"},
            {"glob": "docs/workstreams/**/*.md", "role": "durable"},
            {"glob": "reports/generated/*.md", "role": "generated"},
            {"glob": "reports/generated/**/*.md", "role": "generated"},
            {"glob": "workspace/*.md", "role": "working"},
            {"glob": "workspace/**/*.md", "role": "working"},
            {"glob": "releases/*.md", "role": "release"},
            {"glob": "releases/**/*.md", "role": "release"},
            {"glob": "scripts/**/*.md", "role": "internal"},
            {"glob": "src/**/*.md", "role": "internal"},
            {"glob": "test/**/*.md", "role": "internal"},
            {"glob": "evals/**/*.md", "role": "generated"},
        ],
        "questionOwners": {
            "architecture": {
                "allowed": ["docs/architecture.md", "docs/architecture.zh-CN.md"],
                "allowedGlobs": [
                    "docs/reference/*architecture*.md",
                    "docs/reference/**/architecture/**",
                    "docs/workstreams/*/architecture.md",
                    "docs/workstreams/*/architecture.zh-CN.md",
                ],
                "tokens": ["architecture"],
            },
            "roadmap": {
                "allowed": ["docs/roadmap.md", "docs/roadmap.zh-CN.md"],
                "allowedGlobs": [
                    "docs/reference/*roadmap*.md",
                    "docs/reference/**/roadmaps/**",
                    "docs/workstreams/*/roadmap.md",
                    "docs/workstreams/*/roadmap.zh-CN.md",
                ],
                "tokens": ["roadmap"],
            },
            "test-plan": {
                "allowed": ["docs/test-plan.md", "docs/test-plan.zh-CN.md"],
                "allowedGlobs": [
                    "docs/reference/*test*.md",
                    "docs/reference/**/testing/**",
                ],
                "tokens": ["test-plan", "testsuite", "test-suite"],
            },
            "release": {
                "allowed": ["release.md", "RELEASE.md", "RELEASE.zh-CN.md", "CHANGELOG.md", "CHANGELOG.zh-CN.md"],
                "allowedGlobs": [
                    "docs/reference/*release*.md",
                    "docs/reference/**/release*.md",
                    "releases/*.md",
                    "releases/**/*.md",
                ],
                "tokens": ["release", "changelog"],
            },
        },
        "questionExcludeGlobs": [
            ".codex/**",
            "docs/adr/**",
            "docs/archive/**",
            "reports/generated/**",
            "workspace/**",
            "scripts/**",
            "src/**",
            "test/**",
            "evals/**",
        ],
        "explicitMoves": {},
    }


def write_doc_governance_config(repo: Path, tier: str, official_modules: list[str]) -> None:
    path = repo / DOC_GOVERNANCE
    existing: dict[str, Any] = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                existing = loaded
        except json.JSONDecodeError:
            existing = {}
    defaults = default_doc_governance_payload(repo, tier, official_modules)
    payload = merge_doc_governance(defaults, existing) if existing else defaults
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def match_glob(rel_path: str, pattern: str) -> bool:
    regex: list[str] = ["^"]
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            regex.append("(?:.*/)?")
            i += 3
            continue
        if pattern.startswith("**", i):
            regex.append(".*")
            i += 2
            continue
        char = pattern[i]
        if char == "*":
            regex.append("[^/]*")
        elif char == "?":
            regex.append("[^/]")
        else:
            regex.append(re.escape(char))
        i += 1
    regex.append("$")
    return re.match("".join(regex), rel_path) is not None


def matches_any(rel_path: str, patterns: Iterable[str]) -> bool:
    return any(match_glob(rel_path, pattern) for pattern in patterns)


def classify_markdown_role(repo: Path, rel_path: str, config: dict[str, Any]) -> str | None:
    for rule in config.get("ownershipRules", []):
        glob = rule.get("glob")
        role = rule.get("role")
        if isinstance(glob, str) and isinstance(role, str) and match_glob(rel_path, glob):
            return role
    return None


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
