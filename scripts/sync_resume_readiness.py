#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from control_surface_lib import (
    CONTROL_SURFACE_COMPONENT_VERSIONS,
    DELIVERY_SUPERVISION_REQUIRED_SECTIONS,
    PROGRAM_BOARD_REQUIRED_SECTIONS,
    PTL_SUPERVISION_REQUIRED_SECTIONS,
    STRATEGY_REQUIRED_SECTIONS,
    WORKER_HANDOFF_REQUIRED_SECTIONS,
    control_surface_required_files,
    control_surface_version_state,
    parse_tier,
    read_text,
)


@dataclass(frozen=True)
class SurfaceSync:
    name: str
    path: str
    script: str
    component: str
    required_sections: tuple[str, ...]


@dataclass(frozen=True)
class ResumeReadinessResult:
    repo: Path
    tier: str
    detected_version: int
    current_version: int
    target_version: int
    required_surface_versions: dict[str, int]
    detected_surface_versions: dict[str, int]
    stored_surface_versions: dict[str, int]
    reasons: tuple[str, ...]
    syncs_run: tuple[str, ...]

    @property
    def upgrade_needed(self) -> bool:
        return bool(self.reasons)


SURFACE_SYNCS: tuple[SurfaceSync, ...] = (
    SurfaceSync(
        name="strategy surface",
        path=".codex/strategy.md",
        script="sync_strategy_surface.py",
        component="strategy",
        required_sections=tuple(STRATEGY_REQUIRED_SECTIONS),
    ),
    SurfaceSync(
        name="program board",
        path=".codex/program-board.md",
        script="sync_program_board.py",
        component="programBoard",
        required_sections=tuple(PROGRAM_BOARD_REQUIRED_SECTIONS),
    ),
    SurfaceSync(
        name="delivery supervision",
        path=".codex/delivery-supervision.md",
        script="sync_delivery_supervision.py",
        component="deliverySupervision",
        required_sections=tuple(DELIVERY_SUPERVISION_REQUIRED_SECTIONS),
    ),
    SurfaceSync(
        name="PTL supervision",
        path=".codex/ptl-supervision.md",
        script="sync_ptl_supervision.py",
        component="ptlSupervision",
        required_sections=tuple(PTL_SUPERVISION_REQUIRED_SECTIONS),
    ),
    SurfaceSync(
        name="worker handoff",
        path=".codex/worker-handoff.md",
        script="sync_worker_handoff.py",
        component="workerHandoff",
        required_sections=tuple(WORKER_HANDOFF_REQUIRED_SECTIONS),
    ),
)


def has_required_sections(path: Path, required_sections: tuple[str, ...]) -> bool:
    text = read_text(path)
    if not text:
        return False
    return all(f"## {heading}" in text for heading in required_sections)


def control_surface_sync_reasons(repo: Path, version_state: dict[str, object]) -> list[str]:
    tier = str(version_state["tier"])
    reasons: list[str] = []
    for rel in control_surface_required_files(tier):
        if not (repo / rel).exists():
            reasons.append(f"missing {rel}")
    if bool(version_state["needsConfigUpgrade"]):
        current_version = version_state["currentVersion"]
        target_version = version_state["targetVersion"]
        reasons.append(f"control-surface version {current_version} -> {target_version}")
    missing_components = list(version_state["missingComponents"])
    if missing_components:
        reasons.append(f"surface versions outdated: {', '.join(missing_components)}")
    return reasons


def needed_surface_syncs(repo: Path, version_state: dict[str, object]) -> list[SurfaceSync]:
    required_components = set(version_state["requiredSurfaceVersions"])
    needed: list[SurfaceSync] = []
    for surface in SURFACE_SYNCS:
        path = repo / surface.path
        if surface.component not in required_components:
            continue
        if not path.exists() or not has_required_sections(path, surface.required_sections):
            needed.append(surface)
    return needed


def run_sync(script_path: Path, repo: Path) -> None:
    subprocess.run(
        [sys.executable, str(script_path), str(repo)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def ensure_resume_ready(repo: Path, check_only: bool = False) -> ResumeReadinessResult:
    repo = repo.resolve()
    scripts_dir = Path(__file__).resolve().parent
    reasons: list[str] = []
    ran: list[str] = []
    tier = parse_tier(repo)
    version_state = control_surface_version_state(repo, tier=tier)
    detected_version = int(version_state["currentVersion"])
    detected_surface_versions = dict(version_state["storedSurfaceVersions"])

    control_surface_reasons = control_surface_sync_reasons(repo, version_state)
    if control_surface_reasons:
        reasons.extend(control_surface_reasons)
        if not check_only:
            run_sync(scripts_dir / "sync_control_surface.py", repo)
            ran.append("sync_control_surface.py")
        version_state = control_surface_version_state(repo, tier=parse_tier(repo))

    for surface in needed_surface_syncs(repo, version_state):
        reasons.append(surface.name)
        if not check_only:
            run_sync(scripts_dir / surface.script, repo)
            ran.append(surface.script)

    if not check_only:
        version_state = control_surface_version_state(repo, tier=parse_tier(repo))

    return ResumeReadinessResult(
        repo=repo,
        tier=str(version_state["tier"]),
        detected_version=detected_version,
        current_version=int(version_state["currentVersion"]),
        target_version=int(version_state["targetVersion"]),
        required_surface_versions=dict(version_state["requiredSurfaceVersions"]),
        detected_surface_versions=detected_surface_versions,
        stored_surface_versions=dict(version_state["storedSurfaceVersions"]),
        reasons=tuple(reasons),
        syncs_run=tuple(ran),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether a repo needs an automatic control-surface generation upgrade before continue/resume, and run the minimum safe sync path when needed."
    )
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--check", action="store_true", help="Inspect only; do not run syncs")
    args = parser.parse_args()

    result = ensure_resume_ready(args.repo.resolve(), check_only=args.check)

    print("# Resume Readiness\n")
    print(f"- Repo: `{result.repo}`")
    print(f"- Tier: `{result.tier}`")
    if args.check or result.detected_version == result.current_version:
        print(f"- Control Surface Version: `{result.detected_version} / {result.target_version}`")
    else:
        print(f"- Control Surface Version: `{result.detected_version} -> {result.current_version} / {result.target_version}`")
    if result.required_surface_versions:
        expected = ", ".join(
            f"{name}:{CONTROL_SURFACE_COMPONENT_VERSIONS[name]}" for name in result.required_surface_versions
        )
        stored = ", ".join(
            f"{name}:{result.detected_surface_versions.get(name, 0)}"
            for name in result.required_surface_versions
        )
        current = ", ".join(
            f"{name}:{result.stored_surface_versions.get(name, 0)}"
            for name in result.required_surface_versions
        )
        print(f"- Required Surface Versions: `{expected}`")
        if args.check or stored == current:
            print(f"- Stored Surface Versions: `{stored}`")
        else:
            print(f"- Stored Surface Versions: `{stored} -> {current}`")
    print(f"- Upgrade Needed: `{'yes' if result.upgrade_needed else 'no'}`")
    print(f"- Upgrade Reasons: {', '.join(result.reasons) if result.reasons else 'none'}")
    if args.check:
        print("- Mode: check-only")
    else:
        print(f"- Syncs Run: {', '.join(result.syncs_run) if result.syncs_run else 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
