#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from pathlib import Path

from daemon_runtime import ensure_daemon, kill_daemon, repo_runtime_paths, send_request, send_request_or_snapshot


def start_clean_daemon(repo: Path) -> tuple[Path, dict[str, object]]:
    repo = repo.resolve()
    paths = repo_runtime_paths(repo)
    kill_daemon(paths)
    time.sleep(0.1)
    return repo, ensure_daemon(paths)


def stop_daemon(repo: Path) -> None:
    paths = repo_runtime_paths(repo.resolve())
    try:
        send_request(paths, "stop")
        time.sleep(0.3)
    except Exception:
        pass
    kill_daemon(paths)


def wait_for_task(repo: Path, task_id: str, timeout_seconds: float = 30.0) -> dict[str, object]:
    repo = repo.resolve()
    paths = repo_runtime_paths(repo)
    deadline = time.time() + timeout_seconds
    last = None
    while time.time() < deadline:
        last = send_request_or_snapshot(paths, "task", taskId=task_id)
        if str(last.get("status")) in {"completed", "failed", "cancelled"}:
            return last
        time.sleep(0.2)
    raise TimeoutError(f"task {task_id} did not finish within {timeout_seconds}s")


def enqueue_and_wait(repo: Path, task_type: str, timeout_seconds: float = 30.0) -> dict[str, object]:
    repo = repo.resolve()
    paths = repo_runtime_paths(repo)
    ensure_daemon(paths)
    task = send_request(paths, "enqueue", taskType=task_type, owner="validation")
    return wait_for_task(repo, str(task["taskId"]), timeout_seconds=timeout_seconds)


def read_task_output(task: dict[str, object]) -> str:
    output_path = Path(str(task["outputPath"]))
    return output_path.read_text(encoding="utf-8") if output_path.exists() else ""


def downgrade_control_surface(repo: Path) -> None:
    config_path = repo.resolve() / ".codex/control-surface.json"
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    payload["controlSurfaceVersion"] = 0
    payload["surfaceVersions"] = {}
    config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for rel in [
        ".codex/entry-routing.md",
        ".codex/strategy.md",
        ".codex/program-board.md",
        ".codex/delivery-supervision.md",
        ".codex/ptl-supervision.md",
        ".codex/worker-handoff.md",
    ]:
        path = repo / rel
        if path.exists():
            path.unlink()
