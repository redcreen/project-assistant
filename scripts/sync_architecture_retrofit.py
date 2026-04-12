#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from control_surface_lib import (
    classify_architecture_signal,
    load_doc_governance_config,
    match_glob,
    normalized_bullets,
    parse_official_modules,
    parse_tier,
    read_text,
    repo_capabilities,
    section,
)


IGNORED_DIRS = {".git", "node_modules", ".obsidian", "__pycache__"}


def inventory_markdown(repo: Path) -> list[str]:
    items: list[str] = []
    for path in repo.rglob("*.md"):
        if any(part in IGNORED_DIRS for part in path.relative_to(repo).parts):
            continue
        items.append(path.relative_to(repo).as_posix())
    return sorted(items)


def architecture_doc_sets(repo: Path, governance: dict) -> tuple[list[str], list[str]]:
    owners = governance.get("questionOwners", {}).get("architecture", {})
    allowed = [str(item) for item in owners.get("allowed", [])]
    allowed_globs = [str(item) for item in owners.get("allowedGlobs", [])]
    tokens = [str(item).lower() for item in owners.get("tokens", ["architecture"])]
    exclude_globs = [str(item) for item in governance.get("questionExcludeGlobs", [])]

    canonical: list[str] = []
    extras: list[str] = []
    for rel in inventory_markdown(repo):
        if any(match_glob(rel, pattern) for pattern in exclude_globs):
            continue
        lowered = rel.lower()
        if "architecture-retrofit" in lowered:
            continue
        if rel in allowed or any(match_glob(rel, pattern) for pattern in allowed_globs):
            canonical.append(rel)
            continue
        if any(token in lowered for token in tokens):
            extras.append(rel)
    return canonical, extras


def root_markdown_clutter(repo: Path, governance: dict) -> list[str]:
    allowed = {str(item) for item in governance.get("rootKeep", [])}
    clutter: list[str] = []
    for path in sorted(repo.glob("*.md")):
        if path.name not in allowed:
            clutter.append(path.name)
    return clutter


def primary_symptoms(repo: Path, governance: dict, architecture_state: dict[str, str]) -> list[str]:
    symptoms: list[str] = []
    canonical, extras = architecture_doc_sets(repo, governance)
    if extras:
        symptoms.append(f"duplicate architecture-like docs exist outside the canonical owner set: {', '.join(extras[:4])}")
    if not canonical:
        symptoms.append("the repo has no canonical architecture owner doc declared by doc-governance")
    clutter = root_markdown_clutter(repo, governance)
    if clutter:
        symptoms.append(f"root markdown clutter is still present: {', '.join(clutter[:4])}")
    blockers = normalized_bullets(section(read_text(repo / ".codex/status.md"), "Blockers / Open Decisions"))
    if blockers:
        symptoms.append(f"blockers or open decisions are still recorded: {blockers[0]}")
    official_modules = parse_official_modules(repo)
    if parse_tier(repo) == "large" and official_modules and not (repo / ".codex/module-dashboard.md").exists():
        symptoms.append("large-project module dashboard is missing while official modules exist")
    if architecture_state["signal"] != "green":
        symptoms.append(f"architecture signal is {architecture_state['signal']}: {architecture_state['signal_basis']}")
    return symptoms or ["architecture direction is viable, but the repo still benefits from an explicit retrofit plan before structural changes"]


def affected_boundaries(repo: Path, governance: dict) -> list[str]:
    boundaries = [
        "control surface (`.codex/plan.md`, `.codex/status.md`, `.codex/brief.md`)",
        "canonical architecture ownership (`docs/architecture*.md` and doc-governance question owners)",
        "execution slices and architecture supervision state",
        "tests and validation gates that enforce the intended architecture",
    ]
    if (repo / ".github/workflows").exists():
        boundaries.append("CI and release workflows that should enforce the corrected architecture path")
    official_modules = parse_official_modules(repo)
    if official_modules:
        boundaries.append("module layer (`.codex/module-dashboard.md` and `.codex/modules/*.md`)")
    _, extras = architecture_doc_sets(repo, governance)
    if extras:
        boundaries.append("legacy or competing architecture documents that need demotion, merge, move, or archive")
    return boundaries


def retrofit_scope(repo: Path, governance: dict) -> list[str]:
    scope = [
        "move the architectural source of truth to one canonical owner set and demote duplicates to reference or archive",
        "replace local-only fixes with a reusable mechanism in the correct layer",
        "align execution slices, documentation, tests, and gates with the corrected architecture direction",
        "refresh progress and handoff outputs so the corrected architecture remains visible during execution",
    ]
    official_modules = parse_official_modules(repo)
    if official_modules:
        scope.append("realign module boundaries, ownership, and module progress artifacts to the target architecture")
    if (repo / ".github/workflows").exists():
        scope.append("align CI and release protection with the corrected architecture assumptions")
    return scope


def execution_strategy(repo: Path, governance: dict) -> list[str]:
    canonical, extras = architecture_doc_sets(repo, governance)
    strategy = [
        "audit the current architecture signal, canonical owner docs, and duplicate architecture-like documents",
        "write down the target boundaries, correct layer, and rejected shortcuts before editing implementation details",
        "slice the retrofit so each slice changes one meaningful boundary and has explicit validation",
        "run `deep` gates during convergence and `release` gates before any architecture-sensitive release",
    ]
    if extras:
        strategy.insert(1, "merge, move, or archive duplicate architecture owners so one primary architecture surface remains")
    if not canonical:
        strategy.insert(1, "create or elevate a canonical architecture owner document before expanding implementation work")
    return strategy


def validation_rules(repo: Path) -> list[str]:
    rules = [
        "`python3 scripts/validate_gate_set.py /path/to/repo --profile deep` passes",
        "architecture signal is green or explicitly justified before closing the retrofit",
        "release-sensitive changes also pass `python3 scripts/validate_gate_set.py /path/to/repo --profile release`",
        "progress and handoff reflect the corrected architecture signal and active execution line",
    ]
    if parse_official_modules(repo):
        rules.append("module dashboard and module files still match the corrected architecture boundaries")
    return rules


def exit_conditions(repo: Path, governance: dict) -> list[str]:
    canonical, extras = architecture_doc_sets(repo, governance)
    conditions = [
        "one canonical architecture owner set answers the main architecture question",
        "duplicate or conflicting architecture docs no longer compete as active owners",
        "execution slices and control-surface artifacts reflect the corrected layer and root cause",
        "the retrofit leaves behind fewer local-only fixes and clearer boundaries than it started with",
    ]
    if not canonical:
        conditions[0] = "a canonical architecture owner document has been established and linked"
    if parse_official_modules(repo):
        conditions.append("module boundaries, ownership, and progress artifacts match the target architecture")
    return conditions


def render_report(repo: Path) -> str:
    tier = parse_tier(repo)
    governance = load_doc_governance_config(repo)
    architecture_state = classify_architecture_signal(repo)
    canonical, extras = architecture_doc_sets(repo, governance)
    blockers = normalized_bullets(section(read_text(repo / ".codex/status.md"), "Blockers / Open Decisions"))
    current_slice = section(read_text(repo / ".codex/status.md"), "Active Slice").strip().strip("`")
    current_execution = architecture_state["current_execution_line"]
    capabilities = [label for _, label in repo_capabilities(repo)]

    def bullets(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items) if items else "- none"

    return f"""# Architecture Retrofit

## Trigger

- Tier: `{tier}`
- Active Slice: `{current_slice or 'n/a'}`
- Current Execution Line: {current_execution}
- Architecture Signal: `{architecture_state['signal']}`
- Escalation Gate: `{architecture_state['gate']}`

## Primary Symptoms

{bullets(primary_symptoms(repo, governance, architecture_state))}

## Root-Cause Drivers

- Root Cause Hypothesis: {architecture_state['root_cause_hypothesis']}
- Signal Basis: {architecture_state['signal_basis']}
- Correct Layer: {architecture_state['correct_layer']}
- Rejected Shortcut: {architecture_state['rejected_shortcut']}

## Affected Boundaries

{bullets(affected_boundaries(repo, governance))}

## Current Architecture Sources

- Canonical Owners:
{bullets(canonical)}
- Additional Architecture-Like Docs:
{bullets(extras)}

## Current Risks / Open Decisions

{bullets(blockers)}

## Target Architecture

- Keep one canonical architecture owner set and make all other architecture-like docs either reference, workstream, or archive material.
- Ensure execution, validation, and reporting all reflect the same root-cause hypothesis and correct layer.
- When the repo has first-class modules, keep the module layer aligned with the target architecture instead of letting module docs drift away from the source of truth.
- Treat architecture retrofit as a boundary correction exercise, not a chain of local bug fixes.

## Retrofit Scope

{bullets(retrofit_scope(repo, governance))}

## Execution Strategy

{bullets(execution_strategy(repo, governance))}

## Validation

{bullets(validation_rules(repo))}

## Exit Conditions

{bullets(exit_conditions(repo, governance))}

## Usable Now

{bullets(capabilities)}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or refresh a repo-local architecture-retrofit working note.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["markdown", "text"], default="markdown")
    args = parser.parse_args()

    repo = args.repo.resolve()
    output_path = repo / ".codex/architecture-retrofit.md"
    report = render_report(repo)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    if args.format == "text":
        print(report)
    else:
        print(output_path.relative_to(repo).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
