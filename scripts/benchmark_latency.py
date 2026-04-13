#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StepResult:
    step: str
    seconds: float


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    total_seconds: float
    host_round_trips: int
    steps: tuple[StepResult, ...]


def run_step(script: Path, *args: Path | str) -> StepResult:
    started = time.perf_counter()
    subprocess.run(
        [sys.executable, str(script), *[str(arg) for arg in args]],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    elapsed = time.perf_counter() - started
    return StepResult(step=script.name, seconds=elapsed)


def make_blank_repo(root: Path) -> Path:
    repo = root / "blank-repo"
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    (repo / "README.md").write_text("# Blank Repo\n", encoding="utf-8")
    return repo


def make_retrofit_repo(root: Path) -> Path:
    repo = root / "retrofit-repo"
    (repo / "docs/legacy/sub").mkdir(parents=True, exist_ok=True)
    (repo / "docs/legacy/roadmaps").mkdir(parents=True, exist_ok=True)
    (repo / "reports").mkdir(parents=True, exist_ok=True)
    (repo / "notes").mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    (repo / "README.md").write_text("# Legacy Repo\n\nOld readme\n", encoding="utf-8")
    (repo / "docs/legacy/sub/arch.md").write_text("legacy architecture\n", encoding="utf-8")
    (repo / "docs/legacy/roadmaps/plan.md").write_text("legacy roadmap\n", encoding="utf-8")
    (repo / "reports/strategy.md").write_text("old report\n", encoding="utf-8")
    (repo / "notes/random.md").write_text("todo\n", encoding="utf-8")
    return repo


def benchmark_blank(scripts_dir: Path) -> ScenarioResult:
    temp_root = Path(tempfile.mkdtemp(prefix="project-assistant-bench-blank-"))
    try:
        repo = make_blank_repo(temp_root)
        steps = (
            run_step(scripts_dir / "sync_control_surface.py", repo),
            run_step(scripts_dir / "sync_docs_system.py", repo),
            run_step(scripts_dir / "validate_gate_set.py", repo, "--profile", "fast"),
        )
        total = sum(step.seconds for step in steps)
        return ScenarioResult(scenario="blank-bootstrap-baseline", total_seconds=total, host_round_trips=len(steps), steps=steps)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def benchmark_blank_front_door(scripts_dir: Path) -> ScenarioResult:
    temp_root = Path(tempfile.mkdtemp(prefix="project-assistant-bench-blank-front-door-"))
    try:
        repo = make_blank_repo(temp_root)
        steps = (
            run_step(scripts_dir / "project_assistant_entry.py", "bootstrap", repo),
        )
        total = sum(step.seconds for step in steps)
        return ScenarioResult(scenario="blank-bootstrap-front-door", total_seconds=total, host_round_trips=1, steps=steps)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def benchmark_retrofit(scripts_dir: Path) -> ScenarioResult:
    temp_root = Path(tempfile.mkdtemp(prefix="project-assistant-bench-retrofit-"))
    try:
        repo = make_retrofit_repo(temp_root)
        steps = (
            run_step(scripts_dir / "sync_control_surface.py", repo),
            run_step(scripts_dir / "sync_docs_system.py", repo),
            run_step(scripts_dir / "sync_markdown_governance.py", repo),
            run_step(scripts_dir / "validate_gate_set.py", repo, "--profile", "fast"),
        )
        total = sum(step.seconds for step in steps)
        return ScenarioResult(scenario="retrofit-baseline", total_seconds=total, host_round_trips=len(steps), steps=steps)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def benchmark_retrofit_front_door(scripts_dir: Path) -> ScenarioResult:
    temp_root = Path(tempfile.mkdtemp(prefix="project-assistant-bench-retrofit-front-door-"))
    try:
        repo = make_retrofit_repo(temp_root)
        steps = (
            run_step(scripts_dir / "project_assistant_entry.py", "retrofit", repo),
        )
        total = sum(step.seconds for step in steps)
        return ScenarioResult(scenario="retrofit-front-door", total_seconds=total, host_round_trips=1, steps=steps)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def to_payload(results: tuple[ScenarioResult, ...]) -> dict[str, object]:
    return {
        "results": [
            {
                "scenario": result.scenario,
                "total_seconds": round(result.total_seconds, 3),
                "host_round_trips": result.host_round_trips,
                "steps": [
                    {
                        "step": step.step,
                        "seconds": round(step.seconds, 3),
                    }
                    for step in result.steps
                ],
            }
            for result in results
        ]
    }


def render_text(results: tuple[ScenarioResult, ...]) -> str:
    lines = ["# Latency Benchmark", ""]
    for result in results:
        lines.append(f"## {result.scenario}")
        lines.append("| Step | Seconds |")
        lines.append("| --- | ---: |")
        for step in result.steps:
            lines.append(f"| {step.step} | {step.seconds:.3f} |")
        lines.append(f"| host round trips | {result.host_round_trips} |")
        lines.append(f"| total | {result.total_seconds:.3f} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark the script-level latency of blank bootstrap and retrofit flows.")
    parser.add_argument("--scenario", choices=["blank", "retrofit", "all"], default="all")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent
    results: list[ScenarioResult] = []
    if args.scenario in {"blank", "all"}:
        results.append(benchmark_blank(scripts_dir))
        results.append(benchmark_blank_front_door(scripts_dir))
    if args.scenario in {"retrofit", "all"}:
        results.append(benchmark_retrofit(scripts_dir))
        results.append(benchmark_retrofit_front_door(scripts_dir))

    payload = to_payload(tuple(results))
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_text(tuple(results)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
