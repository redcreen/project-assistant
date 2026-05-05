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


def seed_control_surface(repo: Path) -> None:
    write(repo / ".codex/brief.md", "# Brief\n")
    write(repo / ".codex/COMMANDS.md", "# Commands\n")
    plan = """# Plan

## Current Phase

`message ingress fixture`

## Current Execution Line
- Objective: prove message ingress behavior
- Plan Link: message-ingress-fixture
- Progress: 1 / 1 tasks complete

## Architecture Supervision
- Signal: `green`
- Escalation Gate: continue automatically

## Execution Tasks
- [x] EL-1 fixture control task complete
"""
    status = """# Status

## Current Phase

`message ingress fixture`

## Active Slice
`message-ingress-fixture`

## Current Execution Line
- Objective: prove message ingress behavior
- Plan Link: message-ingress-fixture
- Progress: 1 / 1 tasks complete

## Architecture Supervision
- Signal: `green`
- Escalation Gate: continue automatically

## Execution Tasks
- [x] EL-1 fixture control task complete
"""
    write(repo / ".codex/plan.md", plan)
    write(repo / ".codex/status.md", status)
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
    write(repo / ".codex/control-surface.json", json.dumps(control, ensure_ascii=False, indent=2) + "\n")


def run_ingress(repo: Path, message: str, *extra: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "message_ingress.py"), "ingest", str(repo), "--message", message, "--json", *extra],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"message_ingress.py failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return json.loads(result.stdout)


def run_front_door(repo: Path, message: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "project_assistant_entry.py"), "message", str(repo), "--message", message, "--json"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"project_assistant_entry.py message failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return json.loads(result.stdout)


def pipeline_tasks(repo: Path) -> list[dict[str, object]]:
    payload = json.loads((repo / ".codex/task-pipeline.json").read_text(encoding="utf-8"))
    return [task for task in payload.get("tasks", []) if isinstance(task, dict)]


def validate_execution_message_fixture(root: Path) -> None:
    repo = root / "execution-message"
    seed_control_surface(repo)
    payload = run_ingress(repo, "请一口气实现 pipeline runner")
    record = payload.get("record") if isinstance(payload.get("record"), dict) else {}
    classification = record.get("classification") if isinstance(record.get("classification"), dict) else {}
    if classification.get("intent") != "execute":
        raise AssertionError(f"expected execute intent, got {classification}")
    tasks = pipeline_tasks(repo)
    if not any(task.get("origin") == "message-ingress" and task.get("metadata", {}).get("rawMessage") == "请一口气实现 pipeline runner" for task in tasks):
        raise AssertionError("expected message-ingress task with raw message metadata")
    if not (repo / ".codex/message-ingress.json").exists():
        raise AssertionError("expected message ingress state file")


def validate_discussion_message_fixture(root: Path) -> None:
    repo = root / "discussion-message"
    seed_control_surface(repo)
    payload = run_ingress(repo, "这个方案是否正确？")
    record = payload.get("record") if isinstance(payload.get("record"), dict) else {}
    classification = record.get("classification") if isinstance(record.get("classification"), dict) else {}
    if classification.get("intent") != "analysis":
        raise AssertionError(f"expected analysis intent, got {classification}")
    if not record.get("taskId"):
        raise AssertionError("discussion message should still enter the pipeline")


def validate_classify_only_fixture(root: Path) -> None:
    repo = root / "classify-only"
    seed_control_surface(repo)
    payload = run_ingress(repo, "只是分类，不入队", "--classify-only")
    record = payload.get("record") if isinstance(payload.get("record"), dict) else {}
    if record.get("taskId") is not None:
        raise AssertionError("classify-only should not enqueue a task")
    if (repo / ".codex/task-pipeline.json").exists():
        raise AssertionError("classify-only should not create task pipeline")


def validate_front_door_fixture(root: Path) -> None:
    repo = root / "front-door"
    seed_control_surface(repo)
    payload = run_front_door(repo, "实现 message ingress 统一入口")
    record = payload.get("record") if isinstance(payload.get("record"), dict) else {}
    if not record.get("taskId"):
        raise AssertionError("front door should enqueue message as task")


def validate_entry_panel_fixture(root: Path) -> None:
    repo = root / "entry-panel"
    seed_control_surface(repo)
    run_ingress(repo, "记录一条用于面板展示的消息", "--classify-only")
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "continue_entry.py"), str(repo)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"continue_entry.py failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    if "## Message Ingress" not in result.stdout:
        raise AssertionError("continue entry should include Message Ingress panel")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate host/message ingress into the project-assistant task pipeline.")
    parser.add_argument("repo", nargs="?", default=".", help="Unused compatibility arg; fixtures are temporary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    checks = [
        ("execution message fixture", validate_execution_message_fixture),
        ("discussion message fixture", validate_discussion_message_fixture),
        ("classify-only fixture", validate_classify_only_fixture),
        ("front door fixture", validate_front_door_fixture),
        ("entry panel fixture", validate_entry_panel_fixture),
    ]
    results: list[dict[str, object]] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="project-assistant-message-ingress-") as tmp:
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
