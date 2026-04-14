#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from control_surface_lib import is_skill_repo
from daemon_validation_lib import enqueue_and_wait, read_task_output, start_clean_daemon, stop_daemon


REQUIRED_OUTPUTS = {
    "continue": "# 项目助手继续",
    "progress": "# 项目进展",
    "handoff": "# 项目助手交接",
}


def validate_concurrent_startup_edges(repo: Path) -> dict[str, object]:
    entry = repo / "scripts" / "project_assistant_entry.py"
    status_runs: list[dict[str, object]] = []
    queue_runs: list[dict[str, object]] = []
    for _ in range(8):
        subprocess.run([sys.executable, str(entry), "daemon", "kill", str(repo), "--json"], check=False, capture_output=True, text=True)
        start_proc = subprocess.Popen(
            [sys.executable, str(entry), "daemon", "start", str(repo), "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(0.02)
        status = subprocess.run(
            [sys.executable, str(entry), "daemon", "status", str(repo), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        queue = subprocess.run(
            [sys.executable, str(entry), "queue", str(repo), "--json"],
            check=False,
            capture_output=True,
            text=True,
        )
        start_stdout, start_stderr = start_proc.communicate(timeout=10)
        if start_proc.returncode != 0:
            raise AssertionError(f"daemon start failed during concurrency probe: {start_stderr or start_stdout}")
        if status.returncode != 0:
            raise AssertionError(f"daemon status failed during startup race: {status.stderr or status.stdout}")
        if queue.returncode != 0:
            raise AssertionError(f"daemon queue failed during startup race: {queue.stderr or queue.stdout}")
        status_payload = json.loads(status.stdout)
        queue_payload = json.loads(queue.stdout)
        status_runs.append(
            {
                "status": status_payload.get("status"),
                "resumeReady": status_payload.get("resumeReady"),
            }
        )
        queue_runs.append({"taskCount": len(queue_payload.get("tasks", []))})
    return {
        "ok": True,
        "statusRuns": status_runs,
        "queueRuns": queue_runs,
    }


def validate(repo: Path) -> dict[str, object]:
    repo = repo.resolve()
    if not is_skill_repo(repo):
        return {"ok": True, "repo": str(repo), "skipped": True, "reason": "non-skill repo"}

    _, started = start_clean_daemon(repo)
    results: dict[str, object] = {
        "ok": True,
        "repo": str(repo),
        "runtimeId": started["runtimeId"],
        "concurrency": validate_concurrent_startup_edges(repo),
        "tasks": {},
    }
    try:
        for task_type, heading in REQUIRED_OUTPUTS.items():
            task = enqueue_and_wait(repo, task_type)
            output = read_task_output(task)
            if str(task.get("status")) != "completed":
                raise AssertionError(f"{task_type} task did not complete")
            if heading not in output:
                raise AssertionError(f"{task_type} output missing heading {heading!r}")
            results["tasks"][task_type] = {
                "taskId": task["taskId"],
                "status": task["status"],
                "outputPath": task["outputPath"],
            }
        return results
    finally:
        stop_daemon(repo)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the PTL daemon runtime core against continue/progress/handoff tasks.")
    parser.add_argument("repo", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    result = validate(args.repo)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if result.get("skipped"):
            print(f"ok: True\nskip: {result['reason']}")
        else:
            print(f"runtime: {result['runtimeId']}")
            for task_type, task in result["tasks"].items():
                print(f"{task_type}: {task['status']} ({task['taskId']})")
            print(f"ok: {result['ok']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
