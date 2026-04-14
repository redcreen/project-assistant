#!/usr/bin/env python3
from __future__ import annotations

import argparse
import errno
import hashlib
import json
import os
import signal
import socket
import socketserver
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from control_surface_lib import bullet_lines, first_line, labeled_bullet_value, read_text, section


RUNTIME_VERSION = 1
DEFAULT_HOST = "127.0.0.1"
DEFAULT_FOREGROUND_TTL_SECONDS = 60
STARTUP_LOCK_STALE_SECONDS = 10
TRANSIENT_SOCKET_ERRNOS = {
    errno.ENOENT,
    errno.ECONNREFUSED,
    errno.ECONNRESET,
    errno.ENOTCONN,
    errno.EPIPE,
}

TASK_DEFINITIONS: dict[str, dict[str, Any]] = {
    "bootstrap": {
        "lane": "background-long",
        "etaBand": "10-30s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [".codex", "docs", "README.md", "README.zh-CN.md"],
    },
    "retrofit": {
        "lane": "background-long",
        "etaBand": "10-30s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [".codex", "docs", "README.md", "README.zh-CN.md"],
    },
    "docs-retrofit": {
        "lane": "background-long",
        "etaBand": "10-30s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [".codex", "docs", "README.md", "README.zh-CN.md"],
    },
    "resume-readiness": {
        "lane": "background-checkpoint",
        "etaBand": "0-10s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [".codex"],
    },
    "continue": {
        "lane": "background-checkpoint",
        "etaBand": "0-10s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [".codex"],
    },
    "progress": {
        "lane": "background-checkpoint",
        "etaBand": "0-10s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [],
    },
    "handoff": {
        "lane": "background-checkpoint",
        "etaBand": "0-10s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [],
    },
    "validate-fast": {
        "lane": "background-checkpoint",
        "etaBand": "0-10s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [],
    },
    "validate-deep": {
        "lane": "background-long",
        "etaBand": "10-30s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [],
    },
    "capability-snapshot": {
        "lane": "background-checkpoint",
        "etaBand": "0-10s",
        "checkpointPolicy": "after-task",
        "touchedPaths": [],
    },
}


@dataclass(frozen=True)
class RuntimePaths:
    repo: Path
    runtime_id: str
    runtime_dir: Path
    socket_path: Path
    endpoint_file: Path
    state_file: Path
    queue_file: Path
    events_file: Path
    pid_file: Path
    startup_lock_file: Path
    stdout_log: Path
    stderr_log: Path
    tasks_dir: Path


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    items: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        items.append(json.loads(line))
    return items


def repo_runtime_paths(repo: Path) -> RuntimePaths:
    repo = repo.resolve()
    digest = hashlib.sha1(str(repo).encode("utf-8")).hexdigest()[:10]
    slug = "".join(ch if ch.isalnum() else "-" for ch in repo.name.lower()).strip("-") or "repo"
    runtime_id = f"{slug}-{digest}"
    runtime_dir = Path.home() / ".codex" / "daemon" / runtime_id
    return RuntimePaths(
        repo=repo,
        runtime_id=runtime_id,
        runtime_dir=runtime_dir,
        socket_path=runtime_dir / "ptl.sock",
        endpoint_file=runtime_dir / "endpoint.json",
        state_file=runtime_dir / "state.json",
        queue_file=runtime_dir / "queue.json",
        events_file=runtime_dir / "events.jsonl",
        pid_file=runtime_dir / "daemon.pid",
        startup_lock_file=runtime_dir / "startup.lock",
        stdout_log=runtime_dir / "daemon.stdout.log",
        stderr_log=runtime_dir / "daemon.stderr.log",
        tasks_dir=runtime_dir / "tasks",
    )


def endpoint_payload(paths: RuntimePaths) -> dict[str, Any]:
    if hasattr(socket, "AF_UNIX"):
        return {"transport": "unix", "socketPath": str(paths.socket_path), "host": None, "port": None}
    return {"transport": "tcp", "socketPath": None, "host": DEFAULT_HOST, "port": 0}


def pid_from_file(paths: RuntimePaths) -> int | None:
    if not paths.pid_file.exists():
        return None
    try:
        return int(paths.pid_file.read_text(encoding="utf-8").strip())
    except Exception:
        return None


def pid_is_alive(pid: int | None) -> bool:
    if not pid:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def synthesized_runtime_status(paths: RuntimePaths) -> dict[str, Any]:
    state = read_json(paths.state_file, {})
    queue = read_json(paths.queue_file, {"tasks": []})
    queue_tasks = list(queue.get("tasks", []))
    counts = {"queued": 0, "running": 0, "completed": 0, "failed": 0, "cancelled": 0}
    for task in queue_tasks:
        status = str(task.get("status", "queued"))
        counts[status] = counts.get(status, 0) + 1

    truth = control_truth_snapshot(paths.repo)
    continuity = continuity_snapshot(paths.repo)
    pid = pid_from_file(paths)
    alive = pid_is_alive(pid)
    stored_status = str(state.get("status", "stopped") or "stopped")
    if paths.startup_lock_file.exists():
        runtime_status = "starting"
    elif stored_status == "stopping" and alive:
        runtime_status = "stopping"
    elif alive and not paths.socket_path.exists():
        runtime_status = "starting"
    elif alive:
        runtime_status = "running"
    elif stored_status == "starting":
        runtime_status = "stopped"
    elif stored_status == "stopping":
        runtime_status = "stopped"
    else:
        runtime_status = stored_status if stored_status in {"running", "stopped"} else "stopped"

    gate = str(truth["gate"]).strip().lower()
    lease = state.get("foregroundLease")
    resume_ready = runtime_status == "running" and gate not in {"require user decision", "require-user-decision"} and not isinstance(lease, dict)
    endpoint = read_json(paths.endpoint_file, endpoint_payload(paths))
    return {
        "version": RUNTIME_VERSION,
        "repo": str(paths.repo),
        "runtimeId": paths.runtime_id,
        "runtimeDir": str(paths.runtime_dir),
        "socketPath": str(paths.socket_path) if endpoint.get("transport") == "unix" else None,
        "endpoint": endpoint,
        "pid": pid,
        "status": runtime_status,
        "startedAt": state.get("startedAt", iso_now()),
        "updatedAt": iso_now(),
        "currentPhase": truth["currentPhase"],
        "activeSlice": truth["activeSlice"],
        "gate": truth["gate"],
        "currentCheckpoint": continuity["currentCheckpoint"],
        "nextAction": continuity["nextAction"],
        "nextActionSource": continuity["nextActionSource"],
        "remainingExecutionTasks": continuity["remainingExecutionTasks"],
        "resumeReady": resume_ready,
        "foregroundLease": lease,
        "queueSummary": counts,
        "lastEventId": int(state.get("lastEventId", 0)),
        "tasksPath": str(paths.tasks_dir),
    }


def synthesized_queue_snapshot(paths: RuntimePaths) -> dict[str, Any]:
    snapshot = read_json(paths.queue_file, {"tasks": []})
    tasks = list(snapshot.get("tasks", []))
    counts = {"queued": 0, "running": 0, "completed": 0, "failed": 0, "cancelled": 0}
    for task in tasks:
        status = str(task.get("status", "queued"))
        counts[status] = counts.get(status, 0) + 1
    return {"tasks": tasks, "counts": counts}


def synthesized_events_snapshot(paths: RuntimePaths, since_id: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    events = [item for item in read_jsonl(paths.events_file) if int(item.get("id", 0)) > since_id]
    return events[-limit:]


def synthesized_task_snapshot(paths: RuntimePaths, task_id: str) -> dict[str, Any]:
    for task in synthesized_queue_snapshot(paths)["tasks"]:
        if str(task.get("taskId")) == task_id:
            return task
    raise KeyError(task_id)


def scripts_dir() -> Path:
    return Path(__file__).resolve().parent


def task_command(task_type: str, repo: Path) -> list[str]:
    base = scripts_dir()
    python = sys.executable
    if task_type == "bootstrap":
        return [python, str(base / "bootstrap_entry.py"), str(repo)]
    if task_type == "retrofit":
        return [python, str(base / "retrofit_entry.py"), str(repo)]
    if task_type == "docs-retrofit":
        return [python, str(base / "retrofit_entry.py"), str(repo), "--intent", "docs-retrofit"]
    if task_type == "resume-readiness":
        return [python, str(base / "sync_resume_readiness.py"), str(repo)]
    if task_type == "continue":
        return [python, str(base / "continue_entry.py"), str(repo)]
    if task_type == "progress":
        return [python, str(base / "progress_entry.py"), str(repo)]
    if task_type == "handoff":
        return [python, str(base / "handoff_entry.py"), str(repo)]
    if task_type == "validate-fast":
        return [python, str(base / "validate_gate_set.py"), str(repo), "--profile", "fast"]
    if task_type == "validate-deep":
        return [python, str(base / "validate_gate_set.py"), str(repo), "--profile", "deep"]
    if task_type == "capability-snapshot":
        return [python, str(base / "capability_snapshot.py"), str(repo), "--format", "text"]
    raise ValueError(f"unsupported task type: {task_type}")


def markdown_checkbox_items(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("- [ ] "):
            items.append({"status": "open", "text": stripped[6:].strip().strip("`")})
        elif stripped.startswith("- [x] ") or stripped.startswith("- [X] "):
            items.append({"status": "done", "text": stripped[6:].strip().strip("`")})
    return items


def continuity_snapshot(repo: Path) -> dict[str, Any]:
    status_text = read_text(repo / ".codex/status.md")
    plan_text = read_text(repo / ".codex/plan.md")
    status_execution = section(status_text, "Current Execution Line")
    plan_execution = section(plan_text, "Current Execution Line")
    status_next_actions = section(status_text, "Next 3 Actions")
    plan_tasks = section(plan_text, "Execution Tasks")

    checkpoint = (
        labeled_bullet_value(status_execution, "Runway")
        or labeled_bullet_value(plan_execution, "Runway")
        or labeled_bullet_value(status_execution, "Objective")
        or labeled_bullet_value(plan_execution, "Objective")
        or "n/a"
    )

    open_tasks = [item["text"] for item in markdown_checkbox_items(plan_tasks) if item["status"] == "open" and item["text"]]
    next_three = [item.strip().strip("`") for item in bullet_lines(status_next_actions) if item.strip()]
    next_action = open_tasks[0] if open_tasks else (next_three[0] if next_three else "n/a")
    next_action_source = "plan.execution-tasks" if open_tasks else ("status.next-3" if next_three else "none")

    return {
        "currentCheckpoint": checkpoint,
        "nextAction": next_action,
        "nextActionSource": next_action_source,
        "remainingExecutionTasks": open_tasks[:3],
    }


def control_truth_snapshot(repo: Path) -> dict[str, str]:
    status_text = read_text(repo / ".codex/status.md")
    plan_text = read_text(repo / ".codex/plan.md")
    phase = first_line(section(status_text, "Current Phase")) or first_line(section(plan_text, "Current Phase")) or "n/a"
    active_slice = first_line(section(status_text, "Active Slice")) or "n/a"
    gate = labeled_bullet_value(section(status_text, "Current Escalation State"), "Current Gate") or labeled_bullet_value(
        section(plan_text, "Escalation Model"),
        "Require User Decision",
    )
    return {
        "currentPhase": phase,
        "activeSlice": active_slice,
        "gate": gate or "n/a",
    }


class RuntimeStore:
    def __init__(self, paths: RuntimePaths) -> None:
        self.paths = paths
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.task_threads: dict[str, threading.Thread] = {}
        self.state = read_json(paths.state_file, {})
        self.queue = read_json(paths.queue_file, {"tasks": []})
        self.state.setdefault("version", RUNTIME_VERSION)
        self.state.setdefault("repo", str(paths.repo))
        self.state.setdefault("runtimeId", paths.runtime_id)
        self.state.setdefault("runtimeDir", str(paths.runtime_dir))
        self.state.setdefault("startedAt", iso_now())
        self.state.setdefault("lastEventId", 0)
        self.state.setdefault("foregroundLease", None)
        self.state.setdefault("status", "starting")
        self.queue.setdefault("tasks", [])
        paths.runtime_dir.mkdir(parents=True, exist_ok=True)
        paths.tasks_dir.mkdir(parents=True, exist_ok=True)
        self._reconcile_inflight_tasks_after_restart_locked()

    def _reconcile_inflight_tasks_after_restart_locked(self) -> None:
        reconciled = False
        finished_at = iso_now()
        for task in self.queue["tasks"]:
            if str(task.get("status")) not in {"queued", "running"}:
                continue
            task["status"] = "cancelled"
            task["lastEvent"] = "cancelled"
            task["finishedAt"] = task.get("finishedAt") or finished_at
            task["durationSeconds"] = task.get("durationSeconds")
            task["returnCode"] = task.get("returnCode")
            self._append_event_locked(
                "task_cancelled",
                taskId=task.get("taskId"),
                taskType=task.get("taskType"),
                reason="daemon restarted before task finished",
            )
            reconciled = True
        if reconciled:
            self.state["foregroundLease"] = None
            self.state["status"] = "starting"
            self.persist_locked()

    def persist_locked(self) -> None:
        snapshot = self._status_snapshot_locked()
        write_json(self.paths.state_file, snapshot)
        write_json(self.paths.queue_file, {"tasks": self.queue["tasks"]})

    def _append_event_locked(self, event_type: str, **data: Any) -> dict[str, Any]:
        event_id = int(self.state.get("lastEventId", 0)) + 1
        self.state["lastEventId"] = event_id
        event = {"id": event_id, "timestamp": iso_now(), "type": event_type, **data}
        with self.paths.events_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event

    def _cleanup_expired_lease_locked(self) -> None:
        lease = self.state.get("foregroundLease")
        if not isinstance(lease, dict):
            return
        expires_at = float(lease.get("expiresAt", 0))
        if expires_at and expires_at < time.time():
            self.state["foregroundLease"] = None
            self._append_event_locked("session_stopped", reason="foreground lease expired")

    def _resume_ready_locked(self) -> bool:
        self._cleanup_expired_lease_locked()
        gate = str(control_truth_snapshot(self.paths.repo)["gate"]).strip().lower()
        if gate in {"require user decision", "require-user-decision"}:
            return False
        lease = self.state.get("foregroundLease")
        if isinstance(lease, dict):
            return False
        return True

    def _queue_counts_locked(self) -> dict[str, int]:
        counts = {"queued": 0, "running": 0, "completed": 0, "failed": 0, "cancelled": 0}
        for task in self.queue["tasks"]:
            status = str(task.get("status", "queued"))
            if status not in counts:
                counts[status] = 0
            counts[status] += 1
        return counts

    def _status_snapshot_locked(self) -> dict[str, Any]:
        truth = control_truth_snapshot(self.paths.repo)
        continuity = continuity_snapshot(self.paths.repo)
        self._cleanup_expired_lease_locked()
        endpoint = endpoint_payload(self.paths)
        return {
            "version": RUNTIME_VERSION,
            "repo": str(self.paths.repo),
            "runtimeId": self.paths.runtime_id,
            "runtimeDir": str(self.paths.runtime_dir),
            "socketPath": str(self.paths.socket_path) if endpoint["transport"] == "unix" else None,
            "endpoint": endpoint,
            "pid": os.getpid(),
            "status": self.state.get("status", "running"),
            "startedAt": self.state.get("startedAt", iso_now()),
            "updatedAt": iso_now(),
            "currentPhase": truth["currentPhase"],
            "activeSlice": truth["activeSlice"],
            "gate": truth["gate"],
            "currentCheckpoint": continuity["currentCheckpoint"],
            "nextAction": continuity["nextAction"],
            "nextActionSource": continuity["nextActionSource"],
            "remainingExecutionTasks": continuity["remainingExecutionTasks"],
            "resumeReady": self._resume_ready_locked(),
            "foregroundLease": self.state.get("foregroundLease"),
            "queueSummary": self._queue_counts_locked(),
            "lastEventId": int(self.state.get("lastEventId", 0)),
            "tasksPath": str(self.paths.tasks_dir),
        }

    def status_snapshot(self) -> dict[str, Any]:
        with self.lock:
            self.state["status"] = "running"
            self.persist_locked()
            return self._status_snapshot_locked()

    def queue_snapshot(self) -> dict[str, Any]:
        with self.lock:
            self.persist_locked()
            return {"tasks": list(self.queue["tasks"]), "counts": self._queue_counts_locked()}

    def events_since(self, since_id: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        with self.lock:
            if not self.paths.events_file.exists():
                return []
            events: list[dict[str, Any]] = []
            for line in self.paths.events_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                payload = json.loads(line)
                if int(payload.get("id", 0)) > since_id:
                    events.append(payload)
            return events[-limit:]

    def acquire_foreground(self, owner: str, ttl_seconds: int = DEFAULT_FOREGROUND_TTL_SECONDS) -> dict[str, Any]:
        with self.lock:
            lease = {
                "leaseId": str(uuid.uuid4()),
                "owner": owner,
                "acquiredAt": iso_now(),
                "expiresAt": time.time() + ttl_seconds,
            }
            self.state["foregroundLease"] = lease
            self._append_event_locked("session_started", owner=owner, leaseId=lease["leaseId"])
            self.persist_locked()
            return lease

    def heartbeat_foreground(self, lease_id: str, ttl_seconds: int = DEFAULT_FOREGROUND_TTL_SECONDS) -> dict[str, Any]:
        with self.lock:
            lease = self.state.get("foregroundLease")
            if not isinstance(lease, dict) or lease.get("leaseId") != lease_id:
                raise ValueError("foreground lease not found")
            lease["expiresAt"] = time.time() + ttl_seconds
            lease["heartbeatAt"] = iso_now()
            self.persist_locked()
            return lease

    def release_foreground(self, lease_id: str) -> None:
        with self.lock:
            lease = self.state.get("foregroundLease")
            if isinstance(lease, dict) and lease.get("leaseId") == lease_id:
                self.state["foregroundLease"] = None
                self._append_event_locked("session_stopped", leaseId=lease_id, reason="released")
                if self._resume_ready_locked():
                    self._append_event_locked("resume_ready", gate=control_truth_snapshot(self.paths.repo)["gate"])
                self.persist_locked()

    def task_snapshot(self, task_id: str) -> dict[str, Any]:
        with self.lock:
            for task in self.queue["tasks"]:
                if task.get("taskId") == task_id:
                    return dict(task)
        raise KeyError(task_id)

    def enqueue_task(self, task_type: str, owner: str = "daemon") -> dict[str, Any]:
        if task_type not in TASK_DEFINITIONS:
            raise ValueError(f"unsupported task type: {task_type}")
        definition = TASK_DEFINITIONS[task_type]
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        output_path = self.paths.tasks_dir / f"{task_id}.log"
        task = {
            "taskId": task_id,
            "taskType": task_type,
            "lane": definition["lane"],
            "status": "queued",
            "etaBand": definition["etaBand"],
            "owner": owner,
            "touchedPaths": definition["touchedPaths"],
            "checkpointPolicy": definition["checkpointPolicy"],
            "lastEvent": "queued",
            "createdAt": iso_now(),
            "startedAt": None,
            "finishedAt": None,
            "durationSeconds": None,
            "returnCode": None,
            "outputPath": str(output_path),
            "command": task_command(task_type, self.paths.repo),
        }
        with self.lock:
            self.queue["tasks"].append(task)
            self._append_event_locked("task_queued", taskId=task_id, taskType=task_type, lane=definition["lane"])
            self.persist_locked()
            thread = threading.Thread(target=self._run_task, args=(task_id,), daemon=True)
            self.task_threads[task_id] = thread
            thread.start()
            return dict(task)

    def _run_task(self, task_id: str) -> None:
        with self.lock:
            task = next(task for task in self.queue["tasks"] if task["taskId"] == task_id)
            task["status"] = "running"
            task["startedAt"] = iso_now()
            task["lastEvent"] = "running"
            self._append_event_locked("task_running", taskId=task_id, taskType=task["taskType"])
            self.persist_locked()
            command = list(task["command"])
            output_path = Path(task["outputPath"])

        started = time.perf_counter()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as handle:
            result = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT, text=True)
        elapsed = time.perf_counter() - started

        with self.lock:
            task = next(item for item in self.queue["tasks"] if item["taskId"] == task_id)
            task["finishedAt"] = iso_now()
            task["durationSeconds"] = round(elapsed, 3)
            task["returnCode"] = result.returncode
            task["status"] = "completed" if result.returncode == 0 else "failed"
            task["lastEvent"] = task["status"]
            self._append_event_locked(
                f"task_{task['status']}",
                taskId=task_id,
                taskType=task["taskType"],
                returnCode=result.returncode,
                outputPath=task["outputPath"],
            )
            if self._resume_ready_locked():
                self._append_event_locked("resume_ready", gate=control_truth_snapshot(self.paths.repo)["gate"])
            self.persist_locked()

    def stop(self) -> dict[str, Any]:
        with self.lock:
            self.state["status"] = "stopping"
            self._append_event_locked("daemon_stopping")
            self.persist_locked()
            self.stop_event.set()
            return self._status_snapshot_locked()


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        raw = self.rfile.readline().decode("utf-8").strip()
        if not raw:
            return
        request = json.loads(raw)
        action = request.get("action")
        store: RuntimeStore = self.server.store  # type: ignore[attr-defined]
        try:
            if action == "ping":
                response = {"ok": True, "result": store.status_snapshot()}
            elif action == "status":
                response = {"ok": True, "result": store.status_snapshot()}
            elif action == "queue":
                response = {"ok": True, "result": store.queue_snapshot()}
            elif action == "task":
                response = {"ok": True, "result": store.task_snapshot(str(request["taskId"]))}
            elif action == "events":
                response = {
                    "ok": True,
                    "result": store.events_since(int(request.get("sinceId", 0)), int(request.get("limit", 100))),
                }
            elif action == "enqueue":
                response = {
                    "ok": True,
                    "result": store.enqueue_task(str(request["taskType"]), str(request.get("owner", "daemon"))),
                }
            elif action == "acquire-foreground":
                response = {
                    "ok": True,
                    "result": store.acquire_foreground(
                        str(request.get("owner", "host")),
                        int(request.get("ttlSeconds", DEFAULT_FOREGROUND_TTL_SECONDS)),
                    ),
                }
            elif action == "heartbeat-foreground":
                response = {
                    "ok": True,
                    "result": store.heartbeat_foreground(
                        str(request["leaseId"]),
                        int(request.get("ttlSeconds", DEFAULT_FOREGROUND_TTL_SECONDS)),
                    ),
                }
            elif action == "release-foreground":
                store.release_foreground(str(request["leaseId"]))
                response = {"ok": True, "result": {"released": True}}
            elif action == "stop":
                response = {"ok": True, "result": store.stop()}
                threading.Thread(target=self.server.shutdown, daemon=True).start()  # type: ignore[attr-defined]
            else:
                response = {"ok": False, "error": f"unsupported action: {action}"}
        except Exception as exc:  # pragma: no cover - exercised by CLI validation
            response = {"ok": False, "error": str(exc)}
        self.wfile.write((json.dumps(response, ensure_ascii=False) + "\n").encode("utf-8"))


class ThreadingUnixServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    allow_reuse_address = True


def send_request(paths: RuntimePaths, action: str, **payload: Any) -> dict[str, Any]:
    request = {"action": action, **payload}
    deadline = time.time() + 1.5
    last_error: Exception | None = None
    while True:
        endpoint = read_json(paths.endpoint_file, endpoint_payload(paths))
        transport = endpoint.get("transport")
        client: socket.socket | None = None
        try:
            if transport == "unix":
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                client.connect(endpoint["socketPath"])
            else:
                client = socket.create_connection((endpoint["host"], int(endpoint["port"])))
            client.sendall((json.dumps(request, ensure_ascii=False) + "\n").encode("utf-8"))
            data = b""
            while not data.endswith(b"\n"):
                chunk = client.recv(65536)
                if not chunk:
                    break
                data += chunk
            if not data:
                raise RuntimeError("daemon returned no data")
            response = json.loads(data.decode("utf-8"))
            if not response.get("ok"):
                raise RuntimeError(str(response.get("error", "daemon request failed")))
            return response["result"]
        except (FileNotFoundError, ConnectionRefusedError, ConnectionResetError, BrokenPipeError, RuntimeError, OSError) as exc:
            err_no = getattr(exc, "errno", None)
            is_transient = isinstance(exc, (FileNotFoundError, ConnectionRefusedError, ConnectionResetError, BrokenPipeError))
            if isinstance(exc, OSError) and err_no in TRANSIENT_SOCKET_ERRNOS:
                is_transient = True
            if isinstance(exc, RuntimeError) and str(exc) == "daemon returned no data":
                is_transient = True
            last_error = exc
            if not is_transient or time.time() >= deadline:
                break
            time.sleep(0.05)
        finally:
            if client is not None:
                client.close()
    if last_error is not None:
        raise last_error
    raise RuntimeError("daemon request failed")


def send_request_or_snapshot(paths: RuntimePaths, action: str, **payload: Any) -> dict[str, Any] | list[dict[str, Any]]:
    try:
        return send_request(paths, action, **payload)
    except Exception:
        if action == "status":
            return synthesized_runtime_status(paths)
        if action == "queue":
            return synthesized_queue_snapshot(paths)
        if action == "events":
            return synthesized_events_snapshot(paths, int(payload.get("sinceId", 0)), int(payload.get("limit", 100)))
        if action == "task":
            return synthesized_task_snapshot(paths, str(payload["taskId"]))
        raise


def daemon_alive(paths: RuntimePaths) -> bool:
    try:
        send_request(paths, "ping")
        return True
    except Exception:
        return False


def start_daemon_process(paths: RuntimePaths) -> dict[str, Any]:
    paths.runtime_dir.mkdir(parents=True, exist_ok=True)
    write_json(paths.endpoint_file, endpoint_payload(paths))
    with paths.stdout_log.open("a", encoding="utf-8") as stdout, paths.stderr_log.open("a", encoding="utf-8") as stderr:
        subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "serve", str(paths.repo)],
            cwd=str(scripts_dir().parent),
            stdout=stdout,
            stderr=stderr,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    if wait_for_daemon(paths, timeout_seconds=5):
        return send_request(paths, "status")
    raise RuntimeError("daemon failed to start within 5s")


def wait_for_daemon(paths: RuntimePaths, timeout_seconds: float) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if daemon_alive(paths):
            return True
        time.sleep(0.1)
    return False


def acquire_startup_lock(paths: RuntimePaths) -> bool:
    paths.runtime_dir.mkdir(parents=True, exist_ok=True)
    while True:
        try:
            fd = os.open(paths.startup_lock_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            try:
                age_seconds = time.time() - paths.startup_lock_file.stat().st_mtime
            except FileNotFoundError:
                continue
            if age_seconds > STARTUP_LOCK_STALE_SECONDS:
                try:
                    paths.startup_lock_file.unlink()
                except FileNotFoundError:
                    pass
                continue
            return False
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(str(os.getpid()))
            return True


def release_startup_lock(paths: RuntimePaths) -> None:
    try:
        paths.startup_lock_file.unlink()
    except FileNotFoundError:
        pass


def ensure_daemon(paths: RuntimePaths) -> dict[str, Any]:
    if daemon_alive(paths):
        return send_request(paths, "status")
    if acquire_startup_lock(paths):
        try:
            if daemon_alive(paths):
                return send_request(paths, "status")
            return start_daemon_process(paths)
        finally:
            release_startup_lock(paths)
    if wait_for_daemon(paths, timeout_seconds=5):
        return send_request(paths, "status")
    raise RuntimeError("daemon failed to become reachable within 5s")


def kill_daemon(paths: RuntimePaths) -> dict[str, Any]:
    if paths.pid_file.exists():
        pid = int(paths.pid_file.read_text(encoding="utf-8").strip())
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    if paths.socket_path.exists():
        try:
            paths.socket_path.unlink()
        except FileNotFoundError:
            pass
    release_startup_lock(paths)
    return {"killed": True, "runtimeDir": str(paths.runtime_dir)}


def serve(repo: Path) -> int:
    paths = repo_runtime_paths(repo)
    paths.runtime_dir.mkdir(parents=True, exist_ok=True)
    paths.tasks_dir.mkdir(parents=True, exist_ok=True)
    if paths.socket_path.exists():
        paths.socket_path.unlink()
    store = RuntimeStore(paths)
    write_json(paths.endpoint_file, endpoint_payload(paths))
    paths.pid_file.write_text(str(os.getpid()), encoding="utf-8")
    with ThreadingUnixServer(str(paths.socket_path), RequestHandler) as server:
        server.store = store  # type: ignore[attr-defined]
        store.state["status"] = "running"
        store._append_event_locked("daemon_started", pid=os.getpid(), repo=str(repo.resolve()))
        store.persist_locked()
        try:
            server.serve_forever(poll_interval=0.25)
        finally:
            with store.lock:
                store.state["status"] = "stopped"
                store._append_event_locked("daemon_stopped")
                store.persist_locked()
            try:
                paths.socket_path.unlink()
            except FileNotFoundError:
                pass
            try:
                paths.pid_file.unlink()
            except FileNotFoundError:
                pass
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PTL daemon runtime")
    subparsers = parser.add_subparsers(dest="command", required=True)

    serve_parser = subparsers.add_parser("serve")
    serve_parser.add_argument("repo", type=Path)

    args = parser.parse_args(argv)
    if args.command == "serve":
        return serve(args.repo.resolve())
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
