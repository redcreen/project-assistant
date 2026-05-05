#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_repo(repo: Path, *, open_task: bool = False, progress: str = "2 / 2 tasks complete", gate: str = "continue automatically") -> None:
    tasks = (
        "- [x] EL-1 implement the first step\n"
        "- [ ] EL-2 finish the required second step\n"
        if open_task
        else "- [x] EL-1 implement the first step\n- [x] EL-2 finish the required second step\n"
    )
    plan = f"""# Plan

## Current Phase

`fixture phase`

## Current Execution Line
- Objective: finish the fixture objective
- Plan Link: fixture-slice
- Progress: {progress}
- Stop Conditions:
  - validation fails

## Architecture Supervision
- Signal: `green`
- Escalation Gate: {gate}

## Execution Tasks
{tasks}
"""
    status = f"""# Status

## Current Phase

`fixture phase`

## Active Slice
`fixture-slice`

## Current Execution Line
- Objective: finish the fixture objective
- Plan Link: fixture-slice
- Progress: {progress}

## Architecture Supervision
- Signal: `green`
- Escalation Gate: {gate}

## Execution Tasks
{tasks}
"""
    write(repo / ".codex/plan.md", plan)
    write(repo / ".codex/status.md", status)


def run_gate(repo: Path, *args: str) -> tuple[int, dict[str, object]]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "completion_gate.py"), *args, str(repo), "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 2}:
        raise AssertionError(f"completion_gate.py failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.returncode, json.loads(result.stdout)


def run_final(repo: Path, stop_reason: str, final_text: str) -> tuple[int, dict[str, object]]:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "completion_gate.py"),
            "final-check",
            str(repo),
            "--stop-reason",
            stop_reason,
            "--final-text",
            final_text,
            "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 2}:
        raise AssertionError(f"completion_gate.py failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.returncode, json.loads(result.stdout)


def run_entry(script_name: str, repo: Path) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script_name), str(repo)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"{script_name} failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.stdout


def assert_decision(payload: dict[str, object], expected: str) -> None:
    actual = payload.get("decision")
    if actual != expected:
        raise AssertionError(f"expected decision {expected}, got {actual}: {json.dumps(payload, ensure_ascii=False, indent=2)}")


def validate_complete_fixture(root: Path) -> None:
    repo = root / "complete"
    seed_repo(repo)
    code, payload = run_final(repo, "complete", "All required work is complete and validation passed.")
    if code != 0:
        raise AssertionError(f"expected exit 0, got {code}")
    assert_decision(payload, "allow")
    if not (repo / ".codex/completion-gate.json").exists():
        raise AssertionError("expected completion gate output file")


def validate_open_task_fixture(root: Path) -> None:
    repo = root / "open-task"
    seed_repo(repo, open_task=True, progress="1 / 2 tasks complete")
    code, payload = run_final(repo, "complete", "All done.")
    if code != 2:
        raise AssertionError(f"expected exit 2 for required continuation, got {code}")
    assert_decision(payload, "require-continue")


def validate_final_text_fixture(root: Path) -> None:
    repo = root / "final-text-next-step"
    seed_repo(repo)
    code, payload = run_final(repo, "complete", "下一步仍需接入宿主 review，accepted rules 还需要写入 registry。")
    if code != 2:
        raise AssertionError(f"expected exit 2 for final-answer next step, got {code}")
    assert_decision(payload, "require-continue")


def validate_explicit_deferred_fixture(root: Path) -> None:
    repo = root / "explicit-deferred"
    seed_repo(repo, open_task=True, progress="1 / 2 tasks complete")
    code, payload = run_final(repo, "explicitly-deferred", "后续可选：再扩一层 UI。")
    if code != 0:
        raise AssertionError(f"expected exit 0 for explicitly deferred stop, got {code}")
    assert_decision(payload, "explicitly-deferred")


def validate_human_decision_fixture(root: Path) -> None:
    repo = root / "human-decision"
    seed_repo(repo, gate="require user decision")
    code, payload = run_final(repo, "complete", "Implementation is ready, but release direction needs user decision.")
    if code != 0:
        raise AssertionError(f"expected exit 0 for human-decision stop, got {code}")
    assert_decision(payload, "requires-human-decision")


def validate_entry_visibility_fixture(root: Path) -> None:
    repo = root / "entry-visibility"
    seed_repo(repo)
    control = {
        "managedBy": "project-assistant",
        "controlSurfaceVersion": 3,
        "tier": "medium",
        "officialModules": [],
        "requiredFiles": [
            ".codex/brief.md",
            ".codex/plan.md",
            ".codex/status.md",
            ".codex/COMMANDS.md",
            ".codex/control-surface.json",
        ],
    }
    write(repo / ".codex/brief.md", "# Brief\n")
    write(repo / ".codex/COMMANDS.md", "# Commands\n")
    write(repo / ".codex/control-surface.json", json.dumps(control, ensure_ascii=False, indent=2) + "\n")
    continue_output = run_entry("continue_entry.py", repo)
    progress_output = run_entry("progress_entry.py", repo)
    if "## Completion Gate" not in continue_output:
        raise AssertionError("continue_entry.py did not append Completion Gate panel")
    if "## Completion Gate" not in progress_output:
        raise AssertionError("progress_entry.py did not append Completion Gate panel")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the no-known-required-next-step completion gate on isolated fixtures.")
    parser.add_argument("repo", nargs="?", default=".", help="Unused compatibility arg; fixtures are temporary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    checks = [
        ("complete fixture", validate_complete_fixture),
        ("open task fixture", validate_open_task_fixture),
        ("final text next-step fixture", validate_final_text_fixture),
        ("explicit deferred fixture", validate_explicit_deferred_fixture),
        ("human decision fixture", validate_human_decision_fixture),
        ("entry visibility fixture", validate_entry_visibility_fixture),
    ]
    results: list[dict[str, object]] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="project-assistant-completion-gate-") as tmp:
        root = Path(tmp)
        for name, check in checks:
            try:
                check(root)
                results.append({"name": name, "ok": True})
            except Exception as exc:
                ok = False
                results.append({"name": name, "ok": False, "error": str(exc)})

    if args.format == "json":
        print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"[{result['name']}] ok: {result['ok']}")
            if not result["ok"]:
                print(f"  error: {result.get('error')}")
        print(f"ok: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
