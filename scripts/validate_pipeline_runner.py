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


def seed_control_surface(repo: Path, *, gate: str = "continue automatically") -> None:
    write(repo / ".codex/brief.md", "# Brief\n")
    write(repo / ".codex/COMMANDS.md", "# Commands\n")
    plan = f"""# Plan

## Current Phase

`pipeline fixture`

## Current Execution Line
- Objective: prove pipeline fixture behavior
- Plan Link: pipeline-fixture
- Progress: 1 / 1 tasks complete

## Architecture Supervision
- Signal: `green`
- Escalation Gate: {gate}

## Execution Tasks
- [x] EL-1 fixture control task complete
"""
    status = f"""# Status

## Current Phase

`pipeline fixture`

## Active Slice
`pipeline-fixture`

## Current Execution Line
- Objective: prove pipeline fixture behavior
- Plan Link: pipeline-fixture
- Progress: 1 / 1 tasks complete

## Architecture Supervision
- Signal: `green`
- Escalation Gate: {gate}

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


def seed_pipeline(repo: Path, tasks: list[dict[str, object]]) -> None:
    payload = {
        "schema": "project-assistant.task-pipeline.v1",
        "project": repo.name,
        "objective": "fixture objective",
        "status": "active",
        "activeTaskId": None,
        "repairStack": [],
        "tasks": tasks,
        "history": [],
    }
    write(repo / ".codex/task-pipeline.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def run_pipeline(repo: Path, *extra: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "pipeline_runner.py"), "run", str(repo), "--json", *extra],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 2}:
        raise AssertionError(f"pipeline_runner.py failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return json.loads(result.stdout)


def resolve_pipeline(repo: Path, *extra: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "pipeline_runner.py"), "resolve", str(repo), "--json", *extra],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 2}:
        raise AssertionError(f"pipeline_runner.py resolve failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return json.loads(result.stdout)


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


def task_statuses(payload: dict[str, object]) -> dict[str, str]:
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    tasks = state.get("tasks") if isinstance(state.get("tasks"), list) else []
    return {str(task.get("id")): str(task.get("status")) for task in tasks if isinstance(task, dict)}


def assert_pipeline_status(payload: dict[str, object], expected: str) -> None:
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    actual = state.get("status")
    if actual != expected:
        raise AssertionError(f"expected pipeline status {expected}, got {actual}: {json.dumps(payload, ensure_ascii=False, indent=2)}")


def validate_command_loop_fixture(root: Path) -> None:
    repo = root / "command-loop"
    seed_control_surface(repo)
    seed_pipeline(
        repo,
        [
            {
                "id": "T1",
                "title": "write output",
                "kind": "command",
                "status": "pending",
                "command": [sys.executable, "-c", "from pathlib import Path; Path('out.txt').write_text('ok', encoding='utf-8')"],
            },
            {
                "id": "T2",
                "title": "verify output",
                "kind": "command",
                "status": "pending",
                "dependsOn": ["T1"],
                "command": [sys.executable, "-c", "from pathlib import Path; raise SystemExit(0 if Path('out.txt').read_text(encoding='utf-8') == 'ok' else 1)"],
            },
        ],
    )
    payload = run_pipeline(repo, "--max-steps", "5")
    assert_pipeline_status(payload, "complete")
    statuses = task_statuses(payload)
    if statuses.get("T1") != "done" or statuses.get("T2") != "done":
        raise AssertionError(f"expected both tasks done, got {statuses}")


def validate_repair_loop_fixture(root: Path) -> None:
    repo = root / "repair-loop"
    seed_control_surface(repo)
    seed_pipeline(
        repo,
        [
            {
                "id": "T1",
                "title": "command that needs repair",
                "kind": "command",
                "status": "pending",
                "maxAttempts": 2,
                "command": [sys.executable, "-c", "from pathlib import Path; raise SystemExit(0 if Path('fixed.txt').exists() else 1)"],
                "repairCommand": [sys.executable, "-c", "from pathlib import Path; Path('fixed.txt').write_text('fixed', encoding='utf-8')"],
            }
        ],
    )
    payload = run_pipeline(repo, "--max-steps", "6")
    assert_pipeline_status(payload, "complete")
    statuses = task_statuses(payload)
    if statuses.get("T1") != "done":
        raise AssertionError(f"expected original task done after repair, got {statuses}")
    if not any(task_id.startswith("repair-T1") and status == "done" for task_id, status in statuses.items()):
        raise AssertionError(f"expected completed repair task, got {statuses}")


def validate_llm_pause_fixture(root: Path) -> None:
    repo = root / "llm-pause"
    seed_control_surface(repo)
    seed_pipeline(repo, [{"id": "T1", "title": "needs model work", "kind": "llm", "status": "pending"}])
    payload = run_pipeline(repo, "--max-steps", "3")
    assert_pipeline_status(payload, "awaiting-llm")
    statuses = task_statuses(payload)
    if statuses.get("T1") != "awaiting-llm":
        raise AssertionError(f"expected llm task awaiting-llm, got {statuses}")


def validate_llm_resolve_run_next_fixture(root: Path) -> None:
    repo = root / "llm-resolve-run-next"
    seed_control_surface(repo)
    seed_pipeline(
        repo,
        [
            {"id": "T1", "title": "model work", "kind": "llm", "status": "pending"},
            {
                "id": "T2",
                "title": "verify after model work",
                "kind": "command",
                "status": "pending",
                "dependsOn": ["T1"],
                "command": [sys.executable, "-c", "print('verified')"],
            },
        ],
    )
    first = run_pipeline(repo, "--max-steps", "3")
    assert_pipeline_status(first, "awaiting-llm")
    resolved = resolve_pipeline(repo, "--summary", "fixture model work completed", "--run-next", "--max-steps", "5")
    assert_pipeline_status(resolved, "complete")
    statuses = task_statuses(resolved)
    if statuses.get("T1") != "done" or statuses.get("T2") != "done":
        raise AssertionError(f"expected resolved llm task and follow-up command done, got {statuses}")
    events = resolved.get("events") if isinstance(resolved.get("events"), list) else []
    if not events or events[0].get("event") != "task-resolved":
        raise AssertionError(f"expected task-resolved event first, got {events}")


def validate_no_runnable_diagnostic_fixture(root: Path) -> None:
    repo = root / "no-runnable-diagnostic"
    seed_control_surface(repo)
    seed_pipeline(repo, [{"id": "T1", "title": "old model work", "kind": "llm", "status": "awaiting-llm"}])
    payload = run_pipeline(repo, "--max-steps", "1")
    events = payload.get("events") if isinstance(payload.get("events"), list) else []
    event = events[-1] if events and isinstance(events[-1], dict) else {}
    if event.get("event") != "no-runnable-task":
        raise AssertionError(f"expected no-runnable-task diagnostic, got {events}")
    if event.get("nonTerminalTaskCount") != 1:
        raise AssertionError(f"expected non-terminal task count in no-runnable diagnostic, got {event}")
    summary = event.get("taskStatusSummary") if isinstance(event.get("taskStatusSummary"), dict) else {}
    if summary.get("awaiting-llm") != 1:
        raise AssertionError(f"expected awaiting-llm count in no-runnable diagnostic, got {event}")


def validate_run_argument_enqueue_fixture(root: Path) -> None:
    repo = root / "run-argument-enqueue"
    seed_control_surface(repo)
    seed_pipeline(repo, [])
    payload = run_pipeline(repo, "--max-steps", "3", "--task", "Implement the user-requested feature as a pipeline task")
    assert_pipeline_status(payload, "awaiting-llm")
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    tasks = state.get("tasks") if isinstance(state.get("tasks"), list) else []
    if not tasks or not isinstance(tasks[0], dict):
        raise AssertionError("expected run --task to enqueue a task")
    if tasks[0].get("origin") != "run-argument":
        raise AssertionError(f"expected run-argument origin, got {tasks[0]}")


def validate_human_decision_fixture(root: Path) -> None:
    repo = root / "human-decision"
    seed_control_surface(repo, gate="require user decision")
    seed_pipeline(repo, [{"id": "T1", "title": "blocked by human decision", "kind": "command", "status": "pending", "command": [sys.executable, "-c", "print('should not run')"]}])
    payload = run_pipeline(repo, "--max-steps", "3")
    assert_pipeline_status(payload, "requires-human-decision")
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    if state.get("activeTaskId") != "PTL-PREFLIGHT-REVIEW":
        raise AssertionError(f"expected explicit PTL review task, got {state.get('activeTaskId')}")
    statuses = task_statuses(payload)
    if statuses.get("PTL-PREFLIGHT-REVIEW") != "requires-human-decision":
        raise AssertionError(f"expected PTL review task to require decision, got {statuses}")

    ptl_resolved = resolve_pipeline(
        repo,
        "--task-id",
        "PTL-PREFLIGHT-REVIEW",
        "--summary",
        "accepted PTL review",
        "--run-next",
        "--max-steps",
        "5",
    )
    assert_pipeline_status(ptl_resolved, "requires-human-decision")
    statuses = task_statuses(ptl_resolved)
    if statuses.get("T1") != "done" or statuses.get("COMPLETION-HUMAN-DECISION") != "requires-human-decision":
        raise AssertionError(f"expected command done and completion review pending, got {statuses}")

    completed = resolve_pipeline(
        repo,
        "--task-id",
        "COMPLETION-HUMAN-DECISION",
        "--summary",
        "accepted completion review",
        "--run-next",
        "--max-steps",
        "5",
    )
    assert_pipeline_status(completed, "complete")


def validate_resolve_final_text_follow_up_fixture(root: Path) -> None:
    repo = root / "resolve-final-text-follow-up"
    seed_control_surface(repo)
    seed_pipeline(repo, [{"id": "T1", "title": "diagnose issue", "kind": "llm", "status": "pending"}])
    first = run_pipeline(repo, "--max-steps", "2")
    assert_pipeline_status(first, "awaiting-llm")
    resolved = resolve_pipeline(
        repo,
        "--summary",
        "diagnosed issue",
        "--final-text",
        "下一步应该修复队列治理问题。",
        "--run-next",
        "--max-steps",
        "2",
    )
    assert_pipeline_status(resolved, "awaiting-llm")
    state = resolved.get("state") if isinstance(resolved.get("state"), dict) else {}
    tasks = state.get("tasks") if isinstance(state.get("tasks"), list) else []
    follow_ups = [task for task in tasks if isinstance(task, dict) and task.get("origin") == "completion-gate"]
    if not follow_ups:
        raise AssertionError(f"expected completion-gate follow-up task, got {tasks}")
    if follow_ups[0].get("status") != "awaiting-llm":
        raise AssertionError(f"expected follow-up to become next LLM task, got {follow_ups[0]}")


def validate_maintenance_archive_fixture(root: Path) -> None:
    repo = root / "maintenance-archive"
    seed_control_surface(repo)
    seed_pipeline(
        repo,
        [
            {"id": "T1", "title": "old imported message", "kind": "llm", "status": "pending", "origin": "message-ingress"},
            {"id": "T2", "title": "first resolved live message", "kind": "llm", "status": "done", "origin": "message-ingress"},
            {"id": "T3", "title": "new pending message", "kind": "llm", "status": "pending", "origin": "message-ingress"},
        ],
    )
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "pipeline_runner.py"),
            "maintain",
            str(repo),
            "--archive-stale-message-backlog",
            "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"pipeline maintain failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    payload = json.loads(result.stdout)
    statuses = task_statuses(payload)
    if statuses.get("T1") != "explicitly-deferred" or statuses.get("T3") != "pending":
        raise AssertionError(f"expected stale backlog archived and new pending preserved, got {statuses}")


def validate_generic_human_response_fixture(root: Path) -> None:
    repo = root / "generic-human-response"
    seed_control_surface(repo, gate="require user decision")
    seed_pipeline(repo, [{"id": "T1", "title": "blocked command", "kind": "command", "status": "pending", "command": [sys.executable, "-c", "print('ok')"]}])
    first = run_pipeline(repo, "--max-steps", "2")
    assert_pipeline_status(first, "requires-human-decision")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, sys; "
                f"sys.path.insert(0, {str(SCRIPT_DIR)!r}); "
                "from pathlib import Path; import pipeline_runner; "
                f"payload = pipeline_runner.apply_human_decision_response(Path({str(repo)!r}), response='继续 PTL-PREFLIGHT-REVIEW', max_steps=5); "
                "print(json.dumps(payload, ensure_ascii=False))"
            ),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"generic human response failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    payload = json.loads(result.stdout)
    if not payload.get("processed"):
        raise AssertionError(f"expected generic human response to be processed, got {payload}")
    pipeline = payload.get("pipeline") if isinstance(payload.get("pipeline"), dict) else {}
    statuses = task_statuses(pipeline)
    if statuses.get("PTL-PREFLIGHT-REVIEW") != "done" or statuses.get("T1") != "done":
        raise AssertionError(f"expected human response to acknowledge PTL gate and run command, got {statuses}")


def validate_generic_human_pause_fixture(root: Path) -> None:
    repo = root / "generic-human-pause"
    seed_control_surface(repo, gate="require user decision")
    seed_pipeline(repo, [{"id": "T1", "title": "blocked command", "kind": "command", "status": "pending", "command": [sys.executable, "-c", "print('should not run')"]}])
    first = run_pipeline(repo, "--max-steps", "2")
    assert_pipeline_status(first, "requires-human-decision")
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import json, sys; "
                f"sys.path.insert(0, {str(SCRIPT_DIR)!r}); "
                "from pathlib import Path; import pipeline_runner; "
                f"payload = pipeline_runner.apply_human_decision_response(Path({str(repo)!r}), response='先暂停 PTL-PREFLIGHT-REVIEW', max_steps=5); "
                "print(json.dumps(payload, ensure_ascii=False))"
            ),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"generic human pause failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    payload = json.loads(result.stdout)
    if not payload.get("processed"):
        raise AssertionError(f"expected generic human pause to be processed, got {payload}")
    pipeline = payload.get("pipeline") if isinstance(payload.get("pipeline"), dict) else {}
    assert_pipeline_status(pipeline, "explicitly-deferred")
    statuses = task_statuses(pipeline)
    if statuses.get("PTL-PREFLIGHT-REVIEW") != "explicitly-deferred" or statuses.get("T1") != "explicitly-deferred":
        raise AssertionError(f"expected pause to defer review and blocked task, got {statuses}")
    after = run_pipeline(repo, "--max-steps", "2")
    assert_pipeline_status(after, "explicitly-deferred")
    events = after.get("events") if isinstance(after.get("events"), list) else []
    if not events or events[-1].get("event") != "explicitly-deferred":
        raise AssertionError(f"expected paused pipeline not to recreate gate, got {events}")


def validate_entry_panel_fixture(root: Path) -> None:
    repo = root / "entry-panel"
    seed_control_surface(repo)
    seed_pipeline(repo, [{"id": "T1", "title": "visible task", "kind": "command", "status": "pending", "command": [sys.executable, "-c", "print('ok')"]}])
    continue_output = run_entry("continue_entry.py", repo)
    progress_output = run_entry("progress_entry.py", repo)
    if "## Task Pipeline" not in continue_output:
        raise AssertionError("continue_entry.py did not append Task Pipeline panel")
    if "## Task Pipeline" not in progress_output:
        raise AssertionError("progress_entry.py did not append Task Pipeline panel")


def validate_unified_execute_route_fixture(root: Path) -> None:
    repo = root / "unified-execute-route"
    seed_control_surface(repo)
    seed_pipeline(repo, [])
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "project_assistant_entry.py"),
            "execute",
            str(repo),
            "--task",
            "Execute this request through the task pipeline",
            "--max-steps",
            "2",
            "--json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"project_assistant_entry.py execute failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    payload = json.loads(result.stdout)
    assert_pipeline_status(payload, "awaiting-llm")
    state = payload.get("state") if isinstance(payload.get("state"), dict) else {}
    tasks = state.get("tasks") if isinstance(state.get("tasks"), list) else []
    if not tasks:
        raise AssertionError("expected unified execute route to enqueue a task")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate project-assistant task pipeline runner on isolated fixtures.")
    parser.add_argument("repo", nargs="?", default=".", help="Unused compatibility arg; fixtures are temporary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    checks = [
        ("command loop fixture", validate_command_loop_fixture),
        ("repair loop fixture", validate_repair_loop_fixture),
        ("llm pause fixture", validate_llm_pause_fixture),
        ("llm resolve run-next fixture", validate_llm_resolve_run_next_fixture),
        ("no runnable diagnostic fixture", validate_no_runnable_diagnostic_fixture),
        ("run argument enqueue fixture", validate_run_argument_enqueue_fixture),
        ("human decision fixture", validate_human_decision_fixture),
        ("resolve final text follow-up fixture", validate_resolve_final_text_follow_up_fixture),
        ("maintenance archive fixture", validate_maintenance_archive_fixture),
        ("generic human response fixture", validate_generic_human_response_fixture),
        ("generic human pause fixture", validate_generic_human_pause_fixture),
        ("entry panel fixture", validate_entry_panel_fixture),
        ("unified execute route fixture", validate_unified_execute_route_fixture),
    ]
    results: list[dict[str, object]] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="project-assistant-pipeline-runner-") as tmp:
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
