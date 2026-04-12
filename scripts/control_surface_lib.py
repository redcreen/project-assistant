#!/usr/bin/env python3
from __future__ import annotations

import json
import os
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

ARCHITECTURE_DECISION_KEYWORDS = (
    "require user decision",
    "user decision",
    "product behavior",
    "compatibility",
    "breaking",
    "cost",
    "pricing",
    "release blocked",
    "security",
    "policy change",
)

ARCHITECTURE_CAUTION_KEYWORDS = (
    "drift",
    "hardcod",
    "root cause",
    "wrong layer",
    "unclear",
    "risk",
    "blocker",
    "tradeoff",
)

ARCHITECTURE_REVIEW_TRIGGER_GROUPS: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (
        ("source-of-truth", "canonical source", "mirror drift", "dual runtime", "two runtime", "same truth"),
        "source-of-truth or mirror drift is visible in the current slice",
        "review again when source-of-truth ownership, mirror sync, or canonical-root behavior changes",
    ),
    (
        ("ownership", "boundary", "wrong layer", "leak", "cross-layer", "adapter boundary", "state machine"),
        "ownership or boundary drift is visible in the current slice",
        "review again when ownership, boundary, or layer responsibilities change",
    ),
    (
        ("repeated fix", "local fix", "one-off", "hardcod", "symptom", "again and again", "keeps coming back"),
        "the current slice is close to a repeated-fix or symptom-only pattern",
        "review again when the same symptom reappears or the slice starts adding local-only exceptions",
    ),
)

STRATEGY_EXPECTATION_KEYWORDS = (
    "strategic evaluation",
    "战略评估",
    "strategic planning and program orchestration",
    "战略规划与程序编排",
    ".codex/strategy.md",
    "program-board",
)

STRATEGY_REQUIRED_SECTIONS = [
    "Current Strategic Direction",
    "Strategy Evidence Contract",
    "What This Layer Owns",
    "Carryover Backlog",
    "Human Review Boundary",
    "Future Program-Board Boundary",
    "Next Strategic Checks",
]

PROGRAM_BOARD_EXPECTATION_KEYWORDS = (
    "program orchestration",
    "程序编排",
    ".codex/program-board.md",
    "durable program board",
    "durable `program-board`",
    "program-board",
)

PROGRAM_BOARD_REQUIRED_SECTIONS = [
    "Current Program Direction",
    "Program Orchestration Contract",
    "Active Workstreams",
    "Sequencing Queue",
    "Executor Inputs",
    "Parallel-Safe Boundaries",
    "Supporting Backlog Routing",
    "Next Orchestration Checks",
]

DELIVERY_SUPERVISION_EXPECTATION_KEYWORDS = (
    "supervised long-run delivery",
    "长期受监督交付",
    ".codex/delivery-supervision.md",
    "delivery supervision",
    "checkpoint rhythm",
)

DELIVERY_SUPERVISION_REQUIRED_SECTIONS = [
    "Current Delivery Direction",
    "Supervised Delivery Contract",
    "Checkpoint Rhythm",
    "Automatic Continue Boundaries",
    "Escalation Timing",
    "Executor Supervision Loop",
    "Backlog Re-entry Policy",
    "Next Delivery Checks",
]

PTL_SUPERVISION_EXPECTATION_KEYWORDS = (
    "ptl supervision loop",
    "ptl 监督环",
    ".codex/ptl-supervision.md",
    "standing supervision loop",
    "standing technical lead",
)

PTL_SUPERVISION_REQUIRED_SECTIONS = [
    "Current PTL Direction",
    "PTL Supervision Contract",
    "Supervision Triggers",
    "Standing Responsibilities",
    "Continue / Resequence / Escalate Matrix",
    "Active Supervision Checks",
    "Next PTL Checks",
]

WORKER_HANDOFF_EXPECTATION_KEYWORDS = (
    "worker handoff and re-entry",
    "worker 接续与回流",
    ".codex/worker-handoff.md",
    "worker handoff",
    "worker stops, the project should not stop with it",
    "worker 停了，项目不能跟着停",
)

WORKER_HANDOFF_REQUIRED_SECTIONS = [
    "Current Handoff Direction",
    "Worker Handoff Contract",
    "Handoff Triggers",
    "Recovery Sources",
    "Re-entry Actions",
    "Queue / Return Rules",
    "Human Escalation Boundary",
    "Next Handoff Checks",
]

CONTROL_SURFACE_MANAGED_BY = "project-assistant"
CONTROL_SURFACE_VERSION = 2
CONTROL_SURFACE_COMPONENT_VERSIONS: dict[str, int] = {
    "strategy": 1,
    "programBoard": 1,
    "deliverySupervision": 1,
    "ptlSupervision": 1,
    "workerHandoff": 1,
}
CONTROL_SURFACE_COMPONENT_ORDER: tuple[str, ...] = (
    "strategy",
    "programBoard",
    "deliverySupervision",
    "ptlSupervision",
    "workerHandoff",
)
CONTROL_SURFACE_REQUIRED_COMPONENTS_BY_TIER: dict[str, tuple[str, ...]] = {
    "small": (),
    "medium": CONTROL_SURFACE_COMPONENT_ORDER,
    "large": CONTROL_SURFACE_COMPONENT_ORDER,
}
CONTROL_SURFACE_COMPONENT_PATHS: dict[str, str] = {
    "strategy": ".codex/strategy.md",
    "programBoard": ".codex/program-board.md",
    "deliverySupervision": ".codex/delivery-supervision.md",
    "ptlSupervision": ".codex/ptl-supervision.md",
    "workerHandoff": ".codex/worker-handoff.md",
}


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


def markdown_heading_slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[`*_]+", "", value)
    value = value.replace("&", " and ")
    chars: list[str] = []
    dash_open = False
    for ch in value:
        if ch.isalnum():
            chars.append(ch)
            dash_open = False
        elif chars and not dash_open:
            chars.append("-")
            dash_open = True
    return "".join(chars).strip("-")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def parse_intish(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def control_surface_required_files(tier: str) -> list[str]:
    required = [".codex/brief.md", ".codex/status.md", ".codex/COMMANDS.md", ".codex/control-surface.json"]
    if tier in {"medium", "large"}:
        required.append(".codex/plan.md")
    if tier == "large":
        required.append(".codex/module-dashboard.md")
    return required


def required_control_surface_components(tier: str) -> tuple[str, ...]:
    return CONTROL_SURFACE_REQUIRED_COMPONENTS_BY_TIER.get(tier, ())


def required_control_surface_surface_versions(tier: str) -> dict[str, int]:
    return {name: CONTROL_SURFACE_COMPONENT_VERSIONS[name] for name in required_control_surface_components(tier)}


def is_project_assistant_managed_repo(repo: Path, config: dict[str, Any] | None = None, tier: str | None = None) -> bool:
    if is_skill_repo(repo):
        return True
    config = config or load_control_surface_config(repo)
    if str(config.get("managedBy", "")).strip().lower() == CONTROL_SURFACE_MANAGED_BY:
        return True
    if (repo / ".codex/control-surface.json").exists():
        return True
    required = [repo / ".codex/brief.md", repo / ".codex/status.md"]
    if any(not path.exists() for path in required):
        return False
    effective_tier = tier or parse_tier(repo)
    if effective_tier in {"medium", "large"} and not (repo / ".codex/plan.md").exists():
        return False
    return True


def control_surface_version_state(repo: Path, tier: str | None = None) -> dict[str, Any]:
    config = load_control_surface_config(repo)
    effective_tier = str(config.get("tier") or tier or parse_tier(repo)).lower()
    managed = is_project_assistant_managed_repo(repo, config=config, tier=effective_tier)
    required_surface_versions = required_control_surface_surface_versions(effective_tier) if managed else {}
    raw_surface_versions = config.get("surfaceVersions")
    stored_surface_versions: dict[str, int] = {}
    if isinstance(raw_surface_versions, dict):
        for key, value in raw_surface_versions.items():
            stored_surface_versions[str(key)] = parse_intish(value, 0)
    missing_components = [
        name
        for name, required_version in required_surface_versions.items()
        if stored_surface_versions.get(name, 0) < required_version
    ]
    current_version = parse_intish(config.get("controlSurfaceVersion"), 0)
    managed_by = str(config.get("managedBy", "")).strip().lower()
    needs_config_upgrade = managed and (
        not (repo / ".codex/control-surface.json").exists()
        or managed_by != CONTROL_SURFACE_MANAGED_BY
        or current_version < CONTROL_SURFACE_VERSION
        or bool(missing_components)
    )
    return {
        "managed": managed,
        "tier": effective_tier,
        "currentVersion": current_version,
        "targetVersion": CONTROL_SURFACE_VERSION,
        "requiredSurfaceVersions": required_surface_versions,
        "storedSurfaceVersions": stored_surface_versions,
        "missingComponents": missing_components,
        "needsConfigUpgrade": needs_config_upgrade,
        "managedBy": managed_by,
        "configPath": repo / ".codex/control-surface.json",
    }


def relative_markdown_target(from_dir: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, start=from_dir).replace(os.sep, "/")


MILESTONE_HEADING_RE = re.compile(r"^###\s*(.+?)\s*$")
MILESTONE_PREFIX_RE = re.compile(r"^(Stage\s+\d+(?:-\d+)?|Phase\s+\d+(?:-\d+)?)\b", re.IGNORECASE)
MARKDOWN_LINK_RE = re.compile(r"^\[(?P<label>[^\]]+)\]\((?P<target>[^)]+)\)$")


def is_chinese_doc(path: Path) -> bool:
    return path.name.endswith(".zh-CN.md")


def unwrap_markdown_label(value: str) -> str:
    match = MARKDOWN_LINK_RE.match(value.strip())
    return match.group("label").strip() if match else value.strip()


def find_best_development_plan(repo: Path, chinese: bool) -> Path | None:
    candidates: list[Path] = []
    for path in sorted(repo.rglob("*.md")):
        if ".git" in path.parts:
            continue
        stem = path.stem.replace(".zh-CN", "")
        if slugify(stem) != "development-plan":
            continue
        candidates.append(path)
    if not candidates:
        return None
    preferred = [path for path in candidates if is_chinese_doc(path) == chinese]
    pool = preferred or candidates
    return sorted(pool, key=lambda path: (len(path.relative_to(repo).parts), path.relative_to(repo).as_posix()))[0]


def milestone_key(value: str) -> str:
    value = unwrap_markdown_label(value)
    value = re.sub(r"[`*_]+", "", value.strip().lower())
    value = value.replace("：", ":")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def milestone_candidates(value: str) -> list[str]:
    stripped = unwrap_markdown_label(value).strip()
    candidates: list[str] = []
    for candidate in [stripped]:
        if candidate:
            candidates.append(milestone_key(candidate))
    prefix_match = MILESTONE_PREFIX_RE.match(stripped)
    if prefix_match:
        candidates.append(milestone_key(prefix_match.group(1)))
    for sep in [".", "：", ":"]:
        if sep in stripped:
            candidates.append(milestone_key(stripped.split(sep, 1)[0].strip()))
    return dedupe_preserve_order([item for item in candidates if item])


def milestone_targets_for_plan(plan_path: Path, from_dir: Path) -> dict[str, str]:
    targets: dict[str, str] = {}
    for line in read_text(plan_path).splitlines():
        match = MILESTONE_HEADING_RE.match(line.strip())
        if not match:
            continue
        heading = match.group(1).strip()
        if not heading:
            continue
        target = f"{relative_markdown_target(from_dir, plan_path)}#{markdown_heading_slug(heading)}"
        for candidate in milestone_candidates(heading):
            targets.setdefault(candidate, target)
    return targets


def normalized_roadmap_stage_links(repo: Path, roadmap_path: Path, text: str | None = None) -> str:
    original = read_text(roadmap_path) if text is None else text
    if not original:
        return original
    plan_path = find_best_development_plan(repo, chinese=is_chinese_doc(roadmap_path))
    if not plan_path:
        return original
    targets = milestone_targets_for_plan(plan_path, roadmap_path.parent)
    if not targets:
        return original

    normalized_lines: list[str] = []
    changed = False
    for line in original.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            normalized_lines.append(line)
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            normalized_lines.append(line)
            continue
        row_changed = False
        new_cells: list[str] = []
        for cell in cells:
            target = None
            label = unwrap_markdown_label(cell)
            for candidate in milestone_candidates(label):
                if candidate in targets:
                    target = targets[candidate]
                    break
            if not target:
                new_cells.append(cell)
                continue
            new_cell = f"[{label}]({target})"
            new_cells.append(new_cell)
            if new_cell != cell:
                row_changed = True
        if row_changed:
            line = "| " + " | ".join(new_cells) + " |"
            changed = True
        normalized_lines.append(line)

    normalized = "\n".join(normalized_lines)
    if original.endswith("\n"):
        normalized += "\n"
    return normalized if changed else original


def ensure_roadmap_stage_links(repo: Path) -> list[str]:
    changed: list[str] = []
    for rel in ["docs/roadmap.md", "docs/roadmap.zh-CN.md"]:
        path = repo / rel
        if not path.exists():
            continue
        original = read_text(path)
        normalized = normalized_roadmap_stage_links(repo, path, original)
        if normalized != original:
            path.write_text(normalized, encoding="utf-8")
            changed.append(rel)
    return changed


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


def section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def first_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped.strip("`")
    return ""


def bullet_lines(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s+", stripped):
            items.append(re.sub(r"^\d+\.\s+", "", stripped))
    return items


def labeled_bullet_value(text: str, label: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        prefix = f"- {label}:"
        if stripped.startswith(prefix):
            return stripped.split(":", 1)[1].strip().strip("`")
    return ""


def has_labeled_bullet(text: str, label: str) -> bool:
    return bool(labeled_bullet_value(text, label))


def has_bullet_label(text: str, label: str) -> bool:
    prefix = f"- {label}:"
    return any(line.strip().startswith(prefix) for line in text.splitlines())


def parse_markdown_table(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return rows
    header_cells = [cell.strip() for cell in lines[0].strip("|").split("|")]
    separator_cells = [cell.strip() for cell in lines[1].strip("|").split("|")]
    if not header_cells or not all(set(cell) <= {"-", ":"} for cell in separator_cells if cell):
        return rows
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(header_cells):
            continue
        rows.append({header: cell for header, cell in zip(header_cells, cells)})
    return rows


def nested_items_after_label(text: str, label: str) -> list[str]:
    lines = text.splitlines()
    prefix = f"- {label}:"
    items: list[str] = []
    collecting = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(prefix):
            collecting = True
            continue
        if collecting:
            if re.match(r"^- [A-Za-z].*:", stripped):
                break
            if stripped.startswith("- "):
                items.append(stripped[2:].strip())
    return items


def latest_devlog_entry(repo: Path) -> str:
    devlog_dir = repo / "docs/devlog"
    if not devlog_dir.exists():
        return ""
    entries = [p for p in devlog_dir.glob("20*.md") if p.is_file()]
    if not entries:
        return ""
    latest = max(entries, key=lambda p: (p.stat().st_mtime, p.name))
    return latest.relative_to(repo).as_posix()


def normalized_bullets(text: str) -> list[str]:
    normalized: list[str] = []
    for item in bullet_lines(text):
        lowered = item.lower()
        if lowered in {"todo", "none", "无", "n/a"}:
            continue
        if lowered.startswith("none") or lowered.startswith("no blocker") or lowered.startswith("无阻塞"):
            continue
        if lowered.startswith(("follow-up:", "strategic follow-up:", "watchlist:", "note:", "notes:")):
            continue
        normalized.append(item)
    return normalized


def strategy_surface_expected(repo: Path) -> bool:
    strategy_path = repo / ".codex/strategy.md"
    if strategy_path.exists():
        return True
    version_state = control_surface_version_state(repo)
    if version_state["managed"] and "strategy" in version_state["requiredSurfaceVersions"]:
        return True
    corpus_parts = [
        read_text(repo / ".codex/plan.md"),
        read_text(repo / ".codex/status.md"),
        read_text(repo / "README.md"),
        read_text(repo / "README.zh-CN.md"),
        read_text(repo / "docs/roadmap.md"),
        read_text(repo / "docs/roadmap.zh-CN.md"),
    ]
    docs_root = repo / "docs/reference"
    if docs_root.exists():
        for path in docs_root.rglob("*.md"):
            corpus_parts.append(read_text(path))
    lowered = "\n".join(part for part in corpus_parts if part).lower()
    return any(keyword in lowered for keyword in STRATEGY_EXPECTATION_KEYWORDS)


def parse_strategy_surface(repo: Path) -> dict[str, Any]:
    path = repo / ".codex/strategy.md"
    text = read_text(path)
    if not text:
        return {
            "path": path,
            "exists": False,
            "expected": strategy_surface_expected(repo),
            "direction": "n/a",
            "status": "n/a",
            "why_now": "n/a",
            "evidence_contract": [],
            "ownership_rows": [],
            "carryover_rows": [],
            "human_approves": [],
            "system_may_propose": [],
            "future_boundary": [],
            "next_checks": [],
        }

    direction_block = section(text, "Current Strategic Direction")
    human_block = section(text, "Human Review Boundary")
    return {
        "path": path,
        "exists": True,
        "expected": True,
        "direction": labeled_bullet_value(direction_block, "Direction") or "n/a",
        "status": labeled_bullet_value(direction_block, "Status") or "n/a",
        "why_now": labeled_bullet_value(direction_block, "Why Now") or first_line(direction_block) or "n/a",
        "evidence_contract": normalized_bullets(section(text, "Strategy Evidence Contract")),
        "ownership_rows": parse_markdown_table(section(text, "What This Layer Owns")),
        "carryover_rows": parse_markdown_table(section(text, "Carryover Backlog")),
        "human_approves": nested_items_after_label(human_block, "Human Approves"),
        "system_may_propose": nested_items_after_label(human_block, "System May Propose"),
        "future_boundary": normalized_bullets(section(text, "Future Program-Board Boundary")),
        "next_checks": normalized_bullets(section(text, "Next Strategic Checks")),
    }


def program_board_expected(repo: Path) -> bool:
    board_path = repo / ".codex/program-board.md"
    if board_path.exists():
        return True
    version_state = control_surface_version_state(repo)
    if version_state["managed"] and "programBoard" in version_state["requiredSurfaceVersions"]:
        return True
    corpus_parts = [
        read_text(repo / ".codex/plan.md"),
        read_text(repo / ".codex/status.md"),
        read_text(repo / ".codex/strategy.md"),
        read_text(repo / "README.md"),
        read_text(repo / "README.zh-CN.md"),
        read_text(repo / "docs/roadmap.md"),
        read_text(repo / "docs/roadmap.zh-CN.md"),
    ]
    docs_root = repo / "docs/reference"
    if docs_root.exists():
        for path in docs_root.rglob("*.md"):
            corpus_parts.append(read_text(path))
    lowered = "\n".join(part for part in corpus_parts if part).lower()
    return any(keyword in lowered for keyword in PROGRAM_BOARD_EXPECTATION_KEYWORDS)


def parse_program_board(repo: Path) -> dict[str, Any]:
    path = repo / ".codex/program-board.md"
    text = read_text(path)
    if not text:
        return {
            "path": path,
            "exists": False,
            "expected": program_board_expected(repo),
            "direction": "n/a",
            "status": "n/a",
            "why_now": "n/a",
            "contract": [],
            "workstreams": [],
            "queue": [],
            "executors": [],
            "boundaries": [],
            "backlog": [],
            "next_checks": [],
        }

    direction_block = section(text, "Current Program Direction")
    return {
        "path": path,
        "exists": True,
        "expected": True,
        "direction": labeled_bullet_value(direction_block, "Direction") or "n/a",
        "status": labeled_bullet_value(direction_block, "Status") or "n/a",
        "why_now": labeled_bullet_value(direction_block, "Why Now") or first_line(direction_block) or "n/a",
        "contract": normalized_bullets(section(text, "Program Orchestration Contract")),
        "workstreams": parse_markdown_table(section(text, "Active Workstreams")),
        "queue": parse_markdown_table(section(text, "Sequencing Queue")),
        "executors": parse_markdown_table(section(text, "Executor Inputs")),
        "boundaries": parse_markdown_table(section(text, "Parallel-Safe Boundaries")),
        "backlog": parse_markdown_table(section(text, "Supporting Backlog Routing")),
        "next_checks": normalized_bullets(section(text, "Next Orchestration Checks")),
    }


def delivery_supervision_expected(repo: Path) -> bool:
    surface_path = repo / ".codex/delivery-supervision.md"
    if surface_path.exists():
        return True
    version_state = control_surface_version_state(repo)
    if version_state["managed"] and "deliverySupervision" in version_state["requiredSurfaceVersions"]:
        return True
    corpus_parts = [
        read_text(repo / ".codex/plan.md"),
        read_text(repo / ".codex/status.md"),
        read_text(repo / ".codex/strategy.md"),
        read_text(repo / ".codex/program-board.md"),
        read_text(repo / "README.md"),
        read_text(repo / "README.zh-CN.md"),
        read_text(repo / "docs/roadmap.md"),
        read_text(repo / "docs/roadmap.zh-CN.md"),
    ]
    docs_root = repo / "docs/reference"
    if docs_root.exists():
        for path in docs_root.rglob("*.md"):
            corpus_parts.append(read_text(path))
    lowered = "\n".join(part for part in corpus_parts if part).lower()
    return any(keyword in lowered for keyword in DELIVERY_SUPERVISION_EXPECTATION_KEYWORDS)


def parse_delivery_supervision(repo: Path) -> dict[str, Any]:
    path = repo / ".codex/delivery-supervision.md"
    text = read_text(path)
    if not text:
        return {
            "path": path,
            "exists": False,
            "expected": delivery_supervision_expected(repo),
            "direction": "n/a",
            "status": "n/a",
            "why_now": "n/a",
            "contract": [],
            "checkpoint_rows": [],
            "continue_rows": [],
            "escalation_rows": [],
            "executor_rows": [],
            "backlog_rows": [],
            "next_checks": [],
        }

    direction_block = section(text, "Current Delivery Direction")
    return {
        "path": path,
        "exists": True,
        "expected": True,
        "direction": labeled_bullet_value(direction_block, "Direction") or "n/a",
        "status": labeled_bullet_value(direction_block, "Status") or "n/a",
        "why_now": labeled_bullet_value(direction_block, "Why Now") or first_line(direction_block) or "n/a",
        "contract": normalized_bullets(section(text, "Supervised Delivery Contract")),
        "checkpoint_rows": parse_markdown_table(section(text, "Checkpoint Rhythm")),
        "continue_rows": parse_markdown_table(section(text, "Automatic Continue Boundaries")),
        "escalation_rows": parse_markdown_table(section(text, "Escalation Timing")),
        "executor_rows": parse_markdown_table(section(text, "Executor Supervision Loop")),
        "backlog_rows": parse_markdown_table(section(text, "Backlog Re-entry Policy")),
        "next_checks": normalized_bullets(section(text, "Next Delivery Checks")),
    }


def ptl_supervision_expected(repo: Path) -> bool:
    surface_path = repo / ".codex/ptl-supervision.md"
    if surface_path.exists():
        return True
    version_state = control_surface_version_state(repo)
    if version_state["managed"] and "ptlSupervision" in version_state["requiredSurfaceVersions"]:
        return True
    corpus_parts = [
        read_text(repo / ".codex/plan.md"),
        read_text(repo / ".codex/status.md"),
        read_text(repo / ".codex/strategy.md"),
        read_text(repo / ".codex/program-board.md"),
        read_text(repo / ".codex/delivery-supervision.md"),
        read_text(repo / "README.md"),
        read_text(repo / "README.zh-CN.md"),
        read_text(repo / "docs/roadmap.md"),
        read_text(repo / "docs/roadmap.zh-CN.md"),
    ]
    docs_root = repo / "docs/reference"
    if docs_root.exists():
        for path in docs_root.rglob("*.md"):
            corpus_parts.append(read_text(path))
    lowered = "\n".join(part for part in corpus_parts if part).lower()
    return any(keyword in lowered for keyword in PTL_SUPERVISION_EXPECTATION_KEYWORDS)


def parse_ptl_supervision(repo: Path) -> dict[str, Any]:
    path = repo / ".codex/ptl-supervision.md"
    text = read_text(path)
    if not text:
        return {
            "path": path,
            "exists": False,
            "expected": ptl_supervision_expected(repo),
            "direction": "n/a",
            "status": "n/a",
            "why_now": "n/a",
            "contract": [],
            "trigger_rows": [],
            "responsibility_rows": [],
            "matrix_rows": [],
            "check_rows": [],
            "next_checks": [],
        }

    direction_block = section(text, "Current PTL Direction")
    return {
        "path": path,
        "exists": True,
        "expected": True,
        "direction": labeled_bullet_value(direction_block, "Direction") or "n/a",
        "status": labeled_bullet_value(direction_block, "Status") or "n/a",
        "why_now": labeled_bullet_value(direction_block, "Why Now") or first_line(direction_block) or "n/a",
        "contract": normalized_bullets(section(text, "PTL Supervision Contract")),
        "trigger_rows": parse_markdown_table(section(text, "Supervision Triggers")),
        "responsibility_rows": parse_markdown_table(section(text, "Standing Responsibilities")),
        "matrix_rows": parse_markdown_table(section(text, "Continue / Resequence / Escalate Matrix")),
        "check_rows": parse_markdown_table(section(text, "Active Supervision Checks")),
        "next_checks": normalized_bullets(section(text, "Next PTL Checks")),
    }


def worker_handoff_expected(repo: Path) -> bool:
    surface_path = repo / ".codex/worker-handoff.md"
    if surface_path.exists():
        return True
    version_state = control_surface_version_state(repo)
    if version_state["managed"] and "workerHandoff" in version_state["requiredSurfaceVersions"]:
        return True
    corpus_parts = [
        read_text(repo / ".codex/plan.md"),
        read_text(repo / ".codex/status.md"),
        read_text(repo / ".codex/strategy.md"),
        read_text(repo / ".codex/program-board.md"),
        read_text(repo / ".codex/delivery-supervision.md"),
        read_text(repo / "README.md"),
        read_text(repo / "README.zh-CN.md"),
        read_text(repo / "docs/roadmap.md"),
        read_text(repo / "docs/roadmap.zh-CN.md"),
    ]
    docs_root = repo / "docs/reference"
    if docs_root.exists():
        for path in docs_root.rglob("*.md"):
            corpus_parts.append(read_text(path))
    lowered = "\n".join(part for part in corpus_parts if part).lower()
    return any(keyword in lowered for keyword in WORKER_HANDOFF_EXPECTATION_KEYWORDS)


def parse_worker_handoff(repo: Path) -> dict[str, Any]:
    path = repo / ".codex/worker-handoff.md"
    text = read_text(path)
    if not text:
        return {
            "path": path,
            "exists": False,
            "expected": worker_handoff_expected(repo),
            "direction": "n/a",
            "status": "n/a",
            "why_now": "n/a",
            "contract": [],
            "trigger_rows": [],
            "source_rows": [],
            "action_rows": [],
            "queue_rows": [],
            "escalation_rows": [],
            "next_checks": [],
        }

    direction_block = section(text, "Current Handoff Direction")
    return {
        "path": path,
        "exists": True,
        "expected": True,
        "direction": labeled_bullet_value(direction_block, "Direction") or "n/a",
        "status": labeled_bullet_value(direction_block, "Status") or "n/a",
        "why_now": labeled_bullet_value(direction_block, "Why Now") or first_line(direction_block) or "n/a",
        "contract": normalized_bullets(section(text, "Worker Handoff Contract")),
        "trigger_rows": parse_markdown_table(section(text, "Handoff Triggers")),
        "source_rows": parse_markdown_table(section(text, "Recovery Sources")),
        "action_rows": parse_markdown_table(section(text, "Re-entry Actions")),
        "queue_rows": parse_markdown_table(section(text, "Queue / Return Rules")),
        "escalation_rows": parse_markdown_table(section(text, "Human Escalation Boundary")),
        "next_checks": normalized_bullets(section(text, "Next Handoff Checks")),
    }


def detect_automatic_architecture_review_trigger(context: str) -> tuple[str, str]:
    lowered = context.lower()
    for keywords, trigger, next_review in ARCHITECTURE_REVIEW_TRIGGER_GROUPS:
        if any(keyword in lowered for keyword in keywords):
            return trigger, next_review
    return "no automatic trigger is currently active", "review again when blockers change, the active slice rolls forward, or release-facing work begins"


def classify_architecture_signal(repo: Path) -> dict[str, str]:
    status_text = read_text(repo / ".codex/status.md")
    plan_text = read_text(repo / ".codex/plan.md")
    status_arch = section(status_text, "Architecture Supervision")
    plan_arch = section(plan_text, "Architecture Supervision")
    escalation_text = section(status_text, "Current Escalation State")

    blockers = normalized_bullets(section(status_text, "Blockers / Open Decisions"))
    active_slice = first_line(section(status_text, "Active Slice")) or labeled_bullet_value(
        section(status_text, "Current Execution Line"), "Plan Link"
    )
    current_line = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective")
    tasks = execution_task_lines(status_text)
    done_tasks, total_tasks = execution_task_progress(tasks)
    pending_capture = labeled_bullet_value(section(status_text, "Development Log Capture"), "Pending Capture").lower()

    root_cause = labeled_bullet_value(status_arch, "Root Cause Hypothesis") or labeled_bullet_value(
        plan_arch, "Root Cause Hypothesis"
    )
    correct_layer = labeled_bullet_value(status_arch, "Correct Layer") or labeled_bullet_value(plan_arch, "Correct Layer")
    problem_class = labeled_bullet_value(plan_arch, "Problem Class") or "active slice governance and architectural fit"
    rejected_shortcut = labeled_bullet_value(plan_arch, "Rejected Shortcut") or "letting execution continue without a visible architecture signal"
    trigger_context = " | ".join(
        [
            active_slice,
            current_line,
            problem_class,
            root_cause,
            rejected_shortcut,
            " | ".join(blockers),
        ]
    )
    automatic_review_trigger, next_review_trigger = detect_automatic_architecture_review_trigger(trigger_context)

    signal = "green"
    gate = "continue automatically"
    basis_parts: list[str] = []
    reason = "current execution can proceed inside the existing direction without a user-level tradeoff"

    lowered_blockers = " | ".join(blockers).lower()
    if not current_line:
        signal = "yellow"
        gate = "raise but continue"
        basis_parts.append("current execution line is missing an objective")
        reason = "execution should refresh its checkpoint before continuing"
    if not active_slice:
        signal = "yellow"
        gate = "raise but continue"
        basis_parts.append("active slice is not explicit")
        reason = "execution should refresh slice ownership before continuing"
    if total_tasks == 0:
        signal = "yellow"
        gate = "raise but continue"
        basis_parts.append("execution task board is missing")
        reason = "execution should restore a visible task board before continuing"

    if blockers:
        if any(keyword in lowered_blockers for keyword in ARCHITECTURE_DECISION_KEYWORDS):
            signal = "red"
            gate = "require user decision"
            basis_parts = ["open blockers mention a product, compatibility, release, or cost decision"]
            reason = "current blockers have crossed into user-decision territory"
        else:
            if signal != "red":
                signal = "yellow"
                gate = "raise but continue"
                basis_parts.append("open blockers or architectural risks are still recorded")
                reason = "the current direction can continue, but the supervision state should stay visible"

    if signal != "red" and any(keyword in f"{problem_class} {root_cause} {rejected_shortcut}".lower() for keyword in ARCHITECTURE_CAUTION_KEYWORDS):
        if not basis_parts:
            basis_parts.append("architecture supervision is guarding against local-only fixes")

    if automatic_review_trigger != "no automatic trigger is currently active" and signal != "red":
        signal = "yellow"
        gate = "raise but continue"
        basis_parts.append(automatic_review_trigger)
        reason = "the current direction can continue, but architecture review should stay visible because an automatic trigger fired"

    if signal == "green" and pending_capture in {"yes", "true", "pending"}:
        basis_parts.append("development-log capture is pending but does not yet block execution")

    if not root_cause:
        root_cause = "the repo can drift back to local fixes if the current slice loses a visible architectural checkpoint"
    if not correct_layer:
        correct_layer = "control surface, validators, and reporting"

    signal_basis = "; ".join(dedupe_preserve_order(basis_parts)) if basis_parts else "no blocker or escalation trigger is currently forcing a higher-level decision"

    existing_gate = labeled_bullet_value(escalation_text, "Current Gate").lower()
    if existing_gate == "require user decision" and signal != "red":
        signal = "yellow"
        gate = "raise but continue"
        signal_basis = "existing escalation state requested user attention earlier; keep review visible until it is deliberately cleared"
        reason = "the repo should acknowledge the earlier escalation before returning to silent execution"

    return {
        "signal": signal,
        "signal_basis": signal_basis,
        "problem_class": problem_class,
        "root_cause_hypothesis": root_cause,
        "correct_layer": correct_layer,
        "rejected_shortcut": rejected_shortcut,
        "automatic_review_trigger": automatic_review_trigger,
        "gate": gate,
        "reason": reason,
        "next_review_trigger": next_review_trigger,
        "active_slice": active_slice or "n/a",
        "current_execution_line": current_line or "n/a",
        "execution_progress": f"{done_tasks} / {total_tasks}",
    }


def repo_capabilities(repo: Path) -> list[tuple[str, str]]:
    status_text = read_text(repo / ".codex/status.md")
    capabilities: list[tuple[str, str]] = []
    if status_text:
        capabilities.append(("resume-status", "恢复当前状态与下一步"))
    if section(status_text, "Current Execution Line") and execution_task_lines(status_text):
        capabilities.append(("execution-board", "长任务执行线与可见任务板"))
    if section(status_text, "Architecture Supervision") and section(status_text, "Current Escalation State"):
        capabilities.append(("architecture-supervision", "默认架构监督与升级 gate"))
    if (repo / "scripts/sync_architecture_supervision.py").exists():
        capabilities.append(("architecture-auto-signal", "自动架构信号更新"))
    if (repo / "scripts/sync_architecture_retrofit.py").exists():
        capabilities.append(("architecture-retrofit", "架构整改审计与工作底稿"))
    if (repo / ".codex/doc-governance.json").exists() and (repo / "docs/README.md").exists():
        capabilities.append(("docs-retrofit", "文档整改与 Markdown 治理"))
    if (repo / "docs/devlog/README.md").exists():
        capabilities.append(("devlog", "开发日志索引与自动沉淀"))
    if (repo / ".codex/strategy.md").exists():
        capabilities.append(("strategy-surface", "战略评估层与 review contract"))
    if (repo / ".codex/program-board.md").exists():
        capabilities.append(("program-board", "程序编排层与 durable program board"))
    if (repo / ".codex/delivery-supervision.md").exists():
        capabilities.append(("delivery-supervision", "长期受监督交付层与 checkpoint rhythm"))
    if (repo / ".codex/ptl-supervision.md").exists():
        capabilities.append(("ptl-supervision", "PTL 监督环与持续巡检 contract"))
    if (repo / ".codex/worker-handoff.md").exists():
        capabilities.append(("worker-handoff", "worker 接续与回流 contract"))
    if (repo / ".codex/module-dashboard.md").exists():
        capabilities.append(("module-progress", "模块视角进展面板"))
    if (repo / "README.zh-CN.md").exists() and (repo / "docs/README.zh-CN.md").exists():
        capabilities.append(("bilingual-public-docs", "公开文档中英文切换"))
    if (repo / ".github/workflows/deep-gate.yml").exists():
        capabilities.append(("ci-deep-gate", "CI deep 门禁"))
    if (repo / ".github/workflows/release-readiness.yml").exists():
        capabilities.append(("ci-release-readiness", "CI release readiness 门禁"))
    if (repo / ".github/workflows/release-protection.yml").exists():
        capabilities.append(("ci-release-protection", "CI 更严格发布保护门禁"))
    if (repo / "VERSION").exists() and (repo / "install.sh").exists():
        capabilities.append(("release-flow", "版本发布与 tag 安装地址"))
    return capabilities


def primary_human_windows(language: str = "zh") -> list[str]:
    if language.startswith("en"):
        return [
            "project assistant menu",
            "project assistant progress",
            "project assistant architecture",
            "project assistant devlog",
        ]
    return [
        "项目助手 菜单",
        "项目助手 进展",
        "项目助手 架构",
        "项目助手 开发日志",
    ]


def extract_slice_titles(plan_text: str) -> list[str]:
    titles: list[str] = []
    for line in plan_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Slice:"):
            titles.append(stripped.split(":", 1)[1].strip().strip("`"))
    return titles


def execution_task_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in section(text, "Execution Tasks").splitlines()
        if re.match(r"^\s*-\s+\[[ xX]\]\s+", line)
    ]


def display_execution_task(line: str) -> str:
    return re.sub(r"^\s*-\s+", "", line).strip()


def execution_task_kind(line: str) -> str:
    lowered = display_execution_task(line).lower()
    if any(token in lowered for token in ("并行:", "parallel:", "[parallel]", "(parallel)")):
        return "parallel"
    return "mainline"


def normalized_execution_task_body(line: str) -> str:
    content = display_execution_task(line)
    match = re.match(r"^\[[ xX]\]\s*EL-\d+\s*(?P<body>.*)$", content)
    if match:
        content = match.group("body").strip()
    content = re.sub(r"^(并行|主线|parallel|mainline)\s*:\s*", "", content, flags=re.IGNORECASE).strip()
    content = re.sub(r"^\[(parallel|mainline)\]\s*", "", content, flags=re.IGNORECASE).strip()
    content = re.sub(r"^\((parallel|mainline)\)\s*", "", content, flags=re.IGNORECASE).strip()
    return content or display_execution_task(line)


def execution_task_progress(task_lines: list[str]) -> tuple[int, int]:
    total = len(task_lines)
    done = sum(1 for line in task_lines if "[x]" in line.lower())
    return done, total


def validate_commands_doc(text: str) -> list[str]:
    warnings: list[str] = []
    lowered = text.lower()
    if "项目助手" not in text:
        warnings.append(".codex/COMMANDS.md missing Chinese simple commands")
    if "project assistant" not in lowered:
        warnings.append(".codex/COMMANDS.md missing English simple commands")
    for required in ["项目助手 菜单", "项目助手 进展", "项目助手 架构", "项目助手 开发日志"]:
        if required not in text:
            warnings.append(f".codex/COMMANDS.md missing primary window command: {required}")
    for required in ["project assistant menu", "project assistant progress", "project assistant architecture", "project assistant devlog"]:
        if required not in lowered:
            warnings.append(f".codex/COMMANDS.md missing primary window command: {required}")
    return warnings


def validate_repo(repo: Path) -> ValidationResult:
    tier = parse_tier(repo)
    official_modules = parse_official_modules(repo)
    version_state = control_surface_version_state(repo, tier=tier)
    missing: list[str] = []
    warnings: list[str] = []

    required = control_surface_required_files(tier) + [DOC_GOVERNANCE]
    if strategy_surface_expected(repo):
        required.append(".codex/strategy.md")
    if program_board_expected(repo):
        required.append(".codex/program-board.md")
    if delivery_supervision_expected(repo):
        required.append(".codex/delivery-supervision.md")
    if ptl_supervision_expected(repo):
        required.append(".codex/ptl-supervision.md")
    if worker_handoff_expected(repo):
        required.append(".codex/worker-handoff.md")
    if tier == "large":
        required.append(".codex/module-dashboard.md")

    for rel in required:
        if not (repo / rel).exists():
            missing.append(rel)

    if version_state["managed"]:
        if version_state["managedBy"] != CONTROL_SURFACE_MANAGED_BY:
            warnings.append(".codex/control-surface.json missing managedBy: project-assistant")
        if version_state["currentVersion"] < CONTROL_SURFACE_VERSION:
            warnings.append(
                f".codex/control-surface.json controlSurfaceVersion is stale ({version_state['currentVersion']} < {CONTROL_SURFACE_VERSION})"
            )
        for component in version_state["missingComponents"]:
            warnings.append(
                f".codex/control-surface.json missing current surface version for {component} ({version_state['storedSurfaceVersions'].get(component, 0)} < {version_state['requiredSurfaceVersions'][component]})"
            )

    status_text = read_text(repo / ".codex/status.md")
    plan_text = read_text(repo / ".codex/plan.md")
    current_phase = first_line(section(status_text, "Current Phase")).lower()
    active_slice = first_line(section(status_text, "Active Slice")).lower()
    if tier == "large" and ("retrofit" in current_phase or "retrofit" in active_slice):
        warnings.append("status still contains retrofit-oriented language")

    if tier in {"medium", "large"}:
        if "## Current Execution Line" not in status_text:
            warnings.append(".codex/status.md missing Current Execution Line section")
        if "## Execution Tasks" not in status_text:
            warnings.append(".codex/status.md missing Execution Tasks section")
        if "## Development Log Capture" not in status_text:
            warnings.append(".codex/status.md missing Development Log Capture section")
        if "## Architecture Supervision" not in status_text:
            warnings.append(".codex/status.md missing Architecture Supervision section")
        if "## Current Escalation State" not in status_text:
            warnings.append(".codex/status.md missing Current Escalation State section")
        if "## Current Execution Line" not in plan_text:
            warnings.append(".codex/plan.md missing Current Execution Line section")
        if "## Execution Tasks" not in plan_text:
            warnings.append(".codex/plan.md missing Execution Tasks section")
        if "## Development Log Capture" not in plan_text:
            warnings.append(".codex/plan.md missing Development Log Capture section")
        if "## Architecture Supervision" not in plan_text:
            warnings.append(".codex/plan.md missing Architecture Supervision section")
        if "## Escalation Model" not in plan_text:
            warnings.append(".codex/plan.md missing Escalation Model section")
        status_execution = section(status_text, "Current Execution Line")
        plan_execution = section(plan_text, "Current Execution Line")
        status_devlog = section(status_text, "Development Log Capture")
        plan_devlog = section(plan_text, "Development Log Capture")
        status_arch = section(status_text, "Architecture Supervision")
        plan_arch = section(plan_text, "Architecture Supervision")
        status_escalation = section(status_text, "Current Escalation State")
        plan_escalation = section(plan_text, "Escalation Model")
        if "Plan Link:" not in status_execution:
            warnings.append(".codex/status.md missing Plan Link in Current Execution Line")
        if "Progress:" not in status_execution:
            warnings.append(".codex/status.md missing Progress in Current Execution Line")
        if "Plan Link:" not in plan_execution:
            warnings.append(".codex/plan.md missing Plan Link in Current Execution Line")
        if "Progress:" not in plan_execution:
            warnings.append(".codex/plan.md missing Progress in Current Execution Line")
        for label in ["Signal", "Signal Basis", "Root Cause Hypothesis", "Correct Layer", "Automatic Review Trigger", "Escalation Gate"]:
            if not has_labeled_bullet(status_arch, label):
                warnings.append(f".codex/status.md missing {label} in Architecture Supervision")
        for label in ["Signal", "Signal Basis", "Problem Class", "Root Cause Hypothesis", "Correct Layer", "Rejected Shortcut", "Automatic Review Trigger", "Escalation Gate"]:
            if not has_labeled_bullet(plan_arch, label):
                warnings.append(f".codex/plan.md missing {label} in Architecture Supervision")
        for label in ["Trigger Level", "Pending Capture", "Last Entry"]:
            if not has_bullet_label(status_devlog, label):
                warnings.append(f".codex/status.md missing {label} in Development Log Capture")
        for label in ["Trigger Level", "Auto-Capture When", "Skip When"]:
            if not has_bullet_label(plan_devlog, label):
                warnings.append(f".codex/plan.md missing {label} in Development Log Capture")
        for label in ["Current Gate", "Reason", "Next Review Trigger"]:
            if not has_labeled_bullet(status_escalation, label):
                warnings.append(f".codex/status.md missing {label} in Current Escalation State")
        for label in ["Continue Automatically", "Raise But Continue", "Require User Decision"]:
            if not has_labeled_bullet(plan_escalation, label):
                warnings.append(f".codex/plan.md missing {label} in Escalation Model")
        slice_titles = extract_slice_titles(plan_text)
        status_plan_link = next((item.split(":", 1)[1].strip().strip("`") for item in status_execution.splitlines() if item.strip().startswith("- Plan Link:")), "")
        plan_plan_link = next((item.split(":", 1)[1].strip().strip("`") for item in plan_execution.splitlines() if item.strip().startswith("- Plan Link:")), "")
        if status_plan_link and status_plan_link not in slice_titles:
            warnings.append(".codex/status.md Plan Link does not match any plan slice")
        if plan_plan_link and plan_plan_link not in slice_titles:
            warnings.append(".codex/plan.md Plan Link does not match any plan slice")
        for rel, text in [(".codex/status.md", status_text), (".codex/plan.md", plan_text)]:
            task_lines = execution_task_lines(text)
            if not task_lines:
                warnings.append(f"{rel} missing execution task checkboxes")
            elif not all(re.search(r"\bEL-\d+\b", line) for line in task_lines):
                warnings.append(f"{rel} execution tasks missing EL-* task ids")

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
    user_customized = bool(existing.get("userCustomized"))
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
            if user_customized and key in {"rootKeep", "requiredPaths", "publicDocIncludeGlobs", "publicDocExcludeGlobs", "questionExcludeGlobs", "officialModules"}:
                merged[key] = unique_list(value)
            else:
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
                "docs/devlog/README.md",
                "docs/devlog/README.zh-CN.md",
            ],
            "docsHomeLinks": {
                "en": ["../SKILL.md", "../references/README.md", "devlog/README.md"],
                "zh": ["../SKILL.md", "../references/README.zh-CN.md", "devlog/README.zh-CN.md"],
            },
            "publicDocIncludeGlobs": [
                "README.md",
                "docs/*.md",
                "docs/**/*.md",
                "references/README.md",
            ],
            "publicDocExcludeGlobs": [
                ".codex/**",
                "docs/devlog/20*.md",
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
                    "allowedGlobs": [
                        "references/*architecture*.md",
                        "references/**/*architecture*.md",
                    ],
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
                "docs/devlog/**",
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
                "docs/devlog/README.md",
                "docs/devlog/README.zh-CN.md",
                "reports/generated/README.md",
            ],
        "docsHomeLinks": {
            "en": [
                "reference/README.md",
                "workstreams/README.md",
                "archive/README.md",
                "devlog/README.md",
            ],
            "zh": [
                "reference/README.zh-CN.md",
                "workstreams/README.zh-CN.md",
                "archive/README.zh-CN.md",
                "devlog/README.zh-CN.md",
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
            "docs/devlog/README.md",
            "integrations/**/README.md",
        ],
        "publicDocExcludeGlobs": [
            ".codex/**",
            "docs/devlog/20*.md",
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
            "docs/devlog/**",
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
    existing = load_control_surface_config(repo)
    payload = {
        **existing,
        "managedBy": CONTROL_SURFACE_MANAGED_BY,
        "controlSurfaceVersion": CONTROL_SURFACE_VERSION,
        "tier": tier,
        "officialModules": official_modules,
        "surfaceVersions": required_control_surface_surface_versions(tier),
        "requiredFiles": [
            ".codex/brief.md",
            ".codex/plan.md" if tier in {"medium", "large"} else None,
            ".codex/status.md",
            ".codex/COMMANDS.md",
            ".codex/control-surface.json",
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
