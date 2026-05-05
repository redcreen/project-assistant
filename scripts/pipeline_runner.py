#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


SCHEMA = "project-assistant.task-pipeline.v1"
PIPELINE_FILE = Path(".codex/task-pipeline.json")
SCRIPT_DIR = Path(__file__).resolve().parent

TERMINAL_TASK_STATES = {"done", "skipped", "explicitly-deferred"}
PIPELINE_TERMINAL_STATES = {"complete", "blocked", "requires-human-decision", "awaiting-llm", "explicitly-deferred"}
PTL_PREFLIGHT_REVIEW_TASK_ID = "PTL-PREFLIGHT-REVIEW"
COMPLETION_REVIEW_TASK_ID = "COMPLETION-HUMAN-DECISION"
PTL_REVIEW_ACKS = "ptlReviewAcknowledgements"
COMPLETION_REVIEW_ACKS = "completionReviewAcknowledgements"


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def section(text: str, heading: str) -> str:
    target = f"## {heading}".lower()
    capture = False
    body: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            if capture:
                break
            capture = stripped.lower() == target
            continue
        if capture:
            body.append(line)
    return "\n".join(body).strip()


def labeled_value(text: str, label: str) -> str:
    prefix = f"- {label}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(prefix.lower()):
            return stripped[len(prefix) :].strip().strip("`")
    return ""


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug[:64] or "task"


def task_body(line: str) -> str:
    stripped = line.strip()
    stripped = re.sub(r"^- \[[ xX]\]\s*", "", stripped)
    return stripped.strip()


def task_id(title: str, index: int) -> str:
    match = re.match(r"(EL-\d+)\b", title.strip(), flags=re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return f"T{index:02d}-{slugify(title)}"


def parse_plan_tasks(repo: Path) -> list[dict[str, Any]]:
    text = read_text(repo / ".codex/plan.md")
    tasks: list[dict[str, Any]] = []
    in_execution_tasks = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            in_execution_tasks = stripped == "## Execution Tasks"
            continue
        if not in_execution_tasks or not stripped.startswith("- ["):
            continue
        done = stripped.lower().startswith("- [x]")
        title = task_body(stripped)
        tasks.append(
            {
                "id": task_id(title, len(tasks) + 1),
                "title": title,
                "kind": "llm",
                "status": "done" if done else "pending",
                "origin": "plan",
                "attempts": 0,
                "maxAttempts": 1,
                "createdAt": iso_now(),
                "updatedAt": iso_now(),
            }
        )
    return tasks


def current_objective(repo: Path) -> str:
    plan = read_text(repo / ".codex/plan.md")
    current = section(plan, "Current Execution Line")
    return labeled_value(current, "Objective") or "advance the active project-assistant execution line"


def default_state(repo: Path) -> dict[str, Any]:
    tasks = parse_plan_tasks(repo)
    return {
        "schema": SCHEMA,
        "generatedAt": iso_now(),
        "updatedAt": iso_now(),
        "project": repo.name,
        "objective": current_objective(repo),
        "status": "active" if any(task.get("status") == "pending" for task in tasks) else "complete",
        "activeTaskId": None,
        "repairStack": [],
        PTL_REVIEW_ACKS: {},
        COMPLETION_REVIEW_ACKS: {},
        "tasks": tasks,
        "history": [],
    }


def normalize_task(task: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(task)
    normalized.setdefault("kind", "llm")
    normalized.setdefault("status", "pending")
    normalized.setdefault("origin", "manual")
    normalized.setdefault("attempts", 0)
    normalized.setdefault("maxAttempts", 1)
    normalized.setdefault("createdAt", iso_now())
    normalized.setdefault("updatedAt", iso_now())
    return normalized


def load_state(repo: Path) -> dict[str, Any]:
    existing = read_json(repo / PIPELINE_FILE, None)
    if isinstance(existing, dict) and existing.get("schema") == SCHEMA:
        state = dict(existing)
        state["tasks"] = [normalize_task(task) for task in state.get("tasks", []) if isinstance(task, dict)]
        state.setdefault("repairStack", [])
        state.setdefault("history", [])
        state.setdefault(PTL_REVIEW_ACKS, {})
        state.setdefault(COMPLETION_REVIEW_ACKS, {})
        state["objective"] = current_objective(repo)
        state.setdefault("status", "active")
        return state
    return default_state(repo)


def next_generated_task_id(state: dict[str, Any]) -> str:
    existing = {str(task.get("id")) for task in state.get("tasks", []) if isinstance(task, dict)}
    idx = len(existing) + 1
    while True:
        candidate = f"T{idx:02d}"
        if candidate not in existing:
            return candidate
        idx += 1


def enqueue_task(
    state: dict[str, Any],
    *,
    title: str,
    kind: str = "llm",
    command: str | None = None,
    depends_on: list[str] | None = None,
    origin: str = "enqueue",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task: dict[str, Any] = {
        "id": next_generated_task_id(state),
        "title": title,
        "kind": kind,
        "status": "pending",
        "origin": origin,
        "attempts": 0,
        "maxAttempts": 1,
        "createdAt": iso_now(),
        "updatedAt": iso_now(),
    }
    if command:
        task["command"] = command
    if depends_on:
        task["dependsOn"] = depends_on
    if metadata:
        task["metadata"] = metadata
    state.setdefault("tasks", []).append(task)
    if state.get("status") in {"complete", "awaiting-llm", "explicitly-deferred"}:
        state["status"] = "active"
    append_history(state, "task-enqueued", taskId=task["id"], title=title, kind=kind)
    return task


def save_state(repo: Path, state: dict[str, Any]) -> None:
    state["schema"] = SCHEMA
    state["updatedAt"] = iso_now()
    state["project"] = repo.name
    write_json(repo / PIPELINE_FILE, state)


def task_map(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(task.get("id")): task for task in state.get("tasks", []) if isinstance(task, dict)}


def dependencies_done(state: dict[str, Any], task: dict[str, Any]) -> bool:
    tasks = task_map(state)
    deps = task.get("dependsOn") if isinstance(task.get("dependsOn"), list) else []
    for dep in deps:
        dep_task = tasks.get(str(dep))
        if not dep_task or dep_task.get("status") not in TERMINAL_TASK_STATES:
            return False
    return True


def select_task(state: dict[str, Any]) -> dict[str, Any] | None:
    tasks = task_map(state)
    repair_stack = [str(item) for item in state.get("repairStack", [])]
    while repair_stack:
        task = tasks.get(repair_stack[-1])
        if task and task.get("status") not in TERMINAL_TASK_STATES:
            state["repairStack"] = repair_stack
            return task
        repair_stack.pop()
    state["repairStack"] = repair_stack
    for task in state.get("tasks", []):
        if not isinstance(task, dict):
            continue
        if task.get("status") == "pending" and dependencies_done(state, task):
            return task
    return None


def current_human_decision(state: dict[str, Any]) -> dict[str, Any] | None:
    tasks = task_map(state)
    active_id = str(state.get("activeTaskId") or "")
    active = tasks.get(active_id)
    if active and active.get("kind") == "human-decision" and active.get("status") == "requires-human-decision":
        return active
    for task in state.get("tasks", []):
        if isinstance(task, dict) and task.get("kind") == "human-decision" and task.get("status") == "requires-human-decision":
            return task
    return None


def task_status_summary(state: dict[str, Any]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for task in state.get("tasks", []):
        if not isinstance(task, dict):
            continue
        status = str(task.get("status") or "unknown")
        summary[status] = summary.get(status, 0) + 1
    return summary


def no_runnable_event(state: dict[str, Any]) -> dict[str, Any]:
    summary = task_status_summary(state)
    non_terminal = sum(count for status, count in summary.items() if status not in TERMINAL_TASK_STATES)
    return {
        "event": "no-runnable-task",
        "detail": "No pending runnable task is available.",
        "activeTaskId": state.get("activeTaskId"),
        "nonTerminalTaskCount": non_terminal,
        "taskStatusSummary": summary,
    }


def should_stop_for_pipeline_status(state: dict[str, Any]) -> bool:
    status = str(state.get("status") or "")
    if status == "requires-human-decision":
        return current_human_decision(state) is not None
    if status == "awaiting-llm":
        return any(isinstance(task, dict) and task.get("status") == "awaiting-llm" for task in state.get("tasks", []))
    return status in {"complete", "blocked", "explicitly-deferred"}


def run_json_command(args: list[str], repo: Path) -> dict[str, Any]:
    result = subprocess.run(
        args,
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if not result.stdout.strip():
        return {"returncode": result.returncode, "stderr": result.stderr.strip()}
    try:
        payload = json.loads(result.stdout)
    except Exception:
        payload = {"stdout": result.stdout.strip()}
    payload["returncode"] = result.returncode
    if result.stderr.strip():
        payload["stderr"] = result.stderr.strip()
    return payload


def ptl_preflight(repo: Path) -> dict[str, Any]:
    script = SCRIPT_DIR / "ptl_gate.py"
    if not script.exists():
        return {"decision": "allow", "missing": "ptl_gate.py"}
    return run_json_command([sys.executable, str(script), "preflight", str(repo), "--mode", "execute", "--json"], repo)


def completion_check(repo: Path, *, final_text: str = "") -> dict[str, Any]:
    script = SCRIPT_DIR / "completion_gate.py"
    if not script.exists():
        return {"decision": "allow", "missing": "completion_gate.py"}
    args = [sys.executable, str(script), "final-check", str(repo), "--stop-reason", "complete", "--json"]
    if final_text:
        args.extend(["--final-text", final_text])
    return run_json_command(args, repo)


def command_args(task: dict[str, Any], key: str = "command") -> tuple[list[str] | str | None, bool]:
    command = task.get(key)
    if isinstance(command, list) and all(isinstance(item, str) for item in command):
        return command, False
    if isinstance(command, str) and command.strip():
        return command, True
    return None, False


def run_task_command(repo: Path, task: dict[str, Any]) -> dict[str, Any]:
    command, use_shell = command_args(task)
    if command is None:
        return {"returncode": 1, "stdout": "", "stderr": "task has no command"}
    result = subprocess.run(
        command,
        cwd=repo,
        shell=use_shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def append_history(state: dict[str, Any], event: str, **fields: Any) -> None:
    history = state.setdefault("history", [])
    history.append({"at": iso_now(), "event": event, **fields})
    del history[:-200]


def stable_key(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def preflight_review_key(preflight: dict[str, Any]) -> str:
    require_hits = [
        {
            "ruleId": hit.get("ruleId"),
            "reason": hit.get("reason"),
            "evidence": hit.get("evidence", []),
        }
        for hit in preflight.get("hits", [])
        if isinstance(hit, dict) and str(hit.get("decision") or "") == "require-review"
    ]
    return stable_key(
        {
            "kind": "ptl-preflight-review",
            "policyHash": preflight.get("policyHash"),
            "currentSignal": preflight.get("currentSignal"),
            "requireHits": require_hits,
        }
    )


def completion_review_key(completion: dict[str, Any]) -> str:
    require_hits = [
        {
            "ruleId": hit.get("ruleId"),
            "reason": hit.get("reason"),
            "evidence": hit.get("evidence", []),
        }
        for hit in completion.get("hits", [])
        if isinstance(hit, dict) and str(hit.get("decision") or "") == "requires-human-decision"
    ]
    return stable_key(
        {
            "kind": "completion-human-decision",
            "currentPhase": completion.get("currentPhase"),
            "requireHits": require_hits,
        }
    )


def review_acknowledged(state: dict[str, Any], store_name: str, key: str) -> bool:
    store = state.get(store_name)
    return isinstance(store, dict) and key in store


def record_review_acknowledgement(state: dict[str, Any], task: dict[str, Any], summary: str) -> None:
    metadata = task.get("metadata") if isinstance(task.get("metadata"), dict) else {}
    store_name = str(metadata.get("ackStore") or "")
    ack_key = str(metadata.get("ackKey") or "")
    if not store_name or not ack_key:
        return
    store = state.setdefault(store_name, {})
    if not isinstance(store, dict):
        state[store_name] = {}
        store = state[store_name]
    store[ack_key] = {
        "acknowledgedAt": iso_now(),
        "taskId": task.get("id"),
        "summary": summary,
    }
    append_history(state, "review-acknowledged", taskId=task.get("id"), ackStore=store_name, ackKey=ack_key)


def upsert_human_decision_task(
    state: dict[str, Any],
    *,
    task_id: str,
    title: str,
    required_action: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    now = iso_now()
    for task in state.get("tasks", []):
        if not isinstance(task, dict) or str(task.get("id") or "") != task_id:
            continue
        if task.get("status") in TERMINAL_TASK_STATES:
            break
        task["kind"] = "human-decision"
        task["status"] = "requires-human-decision"
        task["title"] = title
        task["updatedAt"] = now
        existing_metadata = task.get("metadata") if isinstance(task.get("metadata"), dict) else {}
        task["metadata"] = {**existing_metadata, **metadata, "requiredAction": required_action}
        state["status"] = "requires-human-decision"
        state["activeTaskId"] = task_id
        return task

    task = {
        "id": task_id,
        "title": title,
        "kind": "human-decision",
        "status": "requires-human-decision",
        "origin": "pipeline-gate",
        "attempts": 0,
        "maxAttempts": 1,
        "metadata": {**metadata, "requiredAction": required_action},
        "createdAt": now,
        "updatedAt": now,
    }
    state.setdefault("tasks", []).append(task)
    state["status"] = "requires-human-decision"
    state["activeTaskId"] = task_id
    append_history(state, "human-decision-created", taskId=task_id, title=title)
    return task


def ptl_review_required_action(preflight: dict[str, Any], blocked_task: dict[str, Any]) -> str:
    signal = preflight.get("currentSignal") if isinstance(preflight.get("currentSignal"), dict) else {}
    gate = signal.get("gate") or "PTL review required"
    blocked = f"{blocked_task.get('id')}: {blocked_task.get('title')}"
    return (
        "PTL 要求先确认后再继续执行。\n"
        f"当前 gate：{gate}\n"
        f"被拦截任务：{blocked}\n"
        f"一行回复格式：继续 {PTL_PREFLIGHT_REVIEW_TASK_ID} 或 先暂停 {PTL_PREFLIGHT_REVIEW_TASK_ID}"
    )


def ensure_ptl_review_task(state: dict[str, Any], *, preflight: dict[str, Any], blocked_task: dict[str, Any]) -> dict[str, Any]:
    key = preflight_review_key(preflight)
    return upsert_human_decision_task(
        state,
        task_id=PTL_PREFLIGHT_REVIEW_TASK_ID,
        title="human decision: review PTL preflight gate before continuing",
        required_action=ptl_review_required_action(preflight, blocked_task),
        metadata={
            "ackStore": PTL_REVIEW_ACKS,
            "ackKey": key,
            "blockedTaskId": blocked_task.get("id"),
            "decisionType": "ptl-preflight-review",
            "exactAcceptReply": f"继续 {PTL_PREFLIGHT_REVIEW_TASK_ID}",
            "exactPauseReply": f"先暂停 {PTL_PREFLIGHT_REVIEW_TASK_ID}",
            "preflight": preflight,
        },
    )


def completion_review_required_action(completion: dict[str, Any]) -> str:
    hits = completion.get("hits") if isinstance(completion.get("hits"), list) else []
    evidence = []
    for hit in hits:
        if not isinstance(hit, dict):
            continue
        evidence.extend(str(item) for item in hit.get("evidence", [])[:2])
    evidence_text = "；".join(evidence[:4]) or "completion gate requires human decision"
    return (
        "当前执行线已经没有可自动执行的任务，但完成门禁要求人类确认。\n"
        f"原因：{evidence_text}\n"
        f"一行回复格式：继续 {COMPLETION_REVIEW_TASK_ID} 或 先暂停 {COMPLETION_REVIEW_TASK_ID}"
    )


def ensure_completion_review_task(state: dict[str, Any], *, completion: dict[str, Any]) -> dict[str, Any]:
    key = completion_review_key(completion)
    return upsert_human_decision_task(
        state,
        task_id=COMPLETION_REVIEW_TASK_ID,
        title="human decision: review completion gate before closing the execution line",
        required_action=completion_review_required_action(completion),
        metadata={
            "ackStore": COMPLETION_REVIEW_ACKS,
            "ackKey": key,
            "decisionType": "completion-human-decision",
            "exactAcceptReply": f"继续 {COMPLETION_REVIEW_TASK_ID}",
            "exactPauseReply": f"先暂停 {COMPLETION_REVIEW_TASK_ID}",
            "completion": completion,
        },
    )


def response_matches_task(response: str, task_id: str) -> bool:
    lowered = response.casefold()
    return task_id.casefold() in lowered or "全部接受" in lowered


def classify_human_decision_response(response: str, task_id: str) -> str | None:
    text = response.strip().casefold()
    if not text:
        return None
    accept_markers = ("继续", "接受", "同意", "确认", "approve", "accept", "continue", "yes", "全部接受")
    pause_markers = ("先暂停", "暂停", "pause", "snooze", "defer", "稍后")
    reject_markers = ("拒绝", "不同意", "reject", "block")
    if any(marker in text for marker in pause_markers) and response_matches_task(response, task_id):
        return "explicitly-deferred"
    if any(marker in text for marker in reject_markers) and response_matches_task(response, task_id):
        return "blocked"
    if any(marker in text for marker in accept_markers) and response_matches_task(response, task_id):
        return "done"
    return None


def apply_human_decision_response(repo: Path, *, response: str, max_steps: int = 20) -> dict[str, Any]:
    repo = repo.resolve()
    state = load_state(repo)
    task = current_human_decision(state)
    if task is None:
        return {"processed": False, "reason": "no active human-decision task"}
    task_id = str(task.get("id") or "")
    outcome = classify_human_decision_response(response, task_id)
    if outcome is None:
        return {"processed": False, "reason": "response did not match active human-decision task", "taskId": task_id}
    summary = f"human response `{response.strip()}` resolved {task_id} as {outcome}"
    payload = resolve_pipeline_task(
        repo,
        task_id=task_id,
        outcome=outcome,
        summary=summary,
        run_next=outcome == "done",
        max_steps=max_steps,
    )
    return {"processed": True, "taskId": task_id, "outcome": outcome, "summary": summary, "pipeline": payload}


def create_repair_task(state: dict[str, Any], failed_task: dict[str, Any], result: dict[str, Any]) -> dict[str, Any] | None:
    repair_command, use_shell = command_args(failed_task, "repairCommand")
    repair_kind = "command" if repair_command is not None else "llm"
    attempts = int(failed_task.get("attempts") or 0)
    max_attempts = int(failed_task.get("maxAttempts") or 1)
    if attempts > max_attempts:
        return None
    repair_id = f"repair-{failed_task.get('id')}-{attempts}"
    if any(task.get("id") == repair_id for task in state.get("tasks", [])):
        return None
    repair_task: dict[str, Any] = {
        "id": repair_id,
        "title": f"Repair {failed_task.get('id')}: {failed_task.get('title')}",
        "kind": repair_kind,
        "status": "pending",
        "origin": "repair",
        "returnTo": failed_task.get("id"),
        "attempts": 0,
        "maxAttempts": 1,
        "failureEvidence": {
            "returncode": result.get("returncode"),
            "stdout": result.get("stdout", "")[-1000:],
            "stderr": result.get("stderr", "")[-1000:],
        },
        "createdAt": iso_now(),
        "updatedAt": iso_now(),
    }
    if repair_command is not None:
        repair_task["command"] = repair_command
        if use_shell:
            repair_task["commandMode"] = "shell"
    state.setdefault("tasks", []).append(repair_task)
    state.setdefault("repairStack", []).append(repair_id)
    return repair_task


def complete_repair_return(state: dict[str, Any], repair_task: dict[str, Any]) -> None:
    return_to = repair_task.get("returnTo")
    if not return_to:
        return
    original = task_map(state).get(str(return_to))
    if original and original.get("status") in {"failed", "waiting-repair"}:
        original["status"] = "pending"
        original["updatedAt"] = iso_now()
        append_history(state, "repair-return", repairTaskId=repair_task.get("id"), returnTo=return_to)


def llm_brief(task: dict[str, Any]) -> str:
    evidence = task.get("failureEvidence") if isinstance(task.get("failureEvidence"), dict) else {}
    lines = [
        f"Task `{task.get('id')}` requires LLM execution.",
        f"Title: {task.get('title')}",
    ]
    if evidence:
        lines.extend(
            [
                "Failure evidence:",
                f"- returncode: {evidence.get('returncode')}",
                f"- stderr: {evidence.get('stderr') or '(none)'}",
                f"- stdout: {evidence.get('stdout') or '(none)'}",
            ]
        )
    lines.append(
        "After completing it, run `pipeline_runner.py resolve <repo> "
        f"--task-id {task.get('id')} --outcome done --summary \"<what changed>\" --run-next`."
    )
    return "\n".join(lines)


def execute_one(repo: Path, state: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    if task.get("kind") == "human-decision":
        task["status"] = "requires-human-decision"
        task["updatedAt"] = iso_now()
        state["status"] = "requires-human-decision"
        state["activeTaskId"] = task.get("id")
        metadata = task.get("metadata") if isinstance(task.get("metadata"), dict) else {}
        brief = metadata.get("requiredAction") or task.get("title") or "Human decision required."
        append_history(state, "awaiting-human-decision", taskId=task.get("id"), brief=brief)
        return {"event": "requires-human-decision", "taskId": task.get("id"), "brief": brief}

    preflight = ptl_preflight(repo)
    preflight_decision = str(preflight.get("decision") or "allow")
    if preflight_decision == "block":
        state["status"] = "blocked"
        append_history(state, "ptl-blocked", taskId=task.get("id"), preflight=preflight)
        return {"event": "blocked", "taskId": task.get("id"), "preflight": preflight}
    if preflight_decision == "require-review":
        review_key = preflight_review_key(preflight)
        if not review_acknowledged(state, PTL_REVIEW_ACKS, review_key):
            review_task = ensure_ptl_review_task(state, preflight=preflight, blocked_task=task)
            append_history(state, "ptl-requires-human", taskId=review_task.get("id"), blockedTaskId=task.get("id"), preflight=preflight)
            return {
                "event": "requires-human-decision",
                "taskId": review_task.get("id"),
                "blockedTaskId": task.get("id"),
                "brief": (review_task.get("metadata") or {}).get("requiredAction"),
                "preflight": preflight,
            }
        append_history(state, "ptl-review-already-acknowledged", taskId=task.get("id"), ackKey=review_key)

    task["status"] = "running"
    task["updatedAt"] = iso_now()
    state["activeTaskId"] = task.get("id")
    append_history(state, "task-started", taskId=task.get("id"), kind=task.get("kind"))

    if task.get("kind") in {"command", "validation", "repair-command", "repair"}:
        result = run_task_command(repo, task)
        task["lastResult"] = result
        task["attempts"] = int(task.get("attempts") or 0) + 1
        task["updatedAt"] = iso_now()
        if result["returncode"] == 0:
            task["status"] = "done"
            append_history(state, "task-done", taskId=task.get("id"))
            complete_repair_return(state, task)
            return {"event": "task-done", "taskId": task.get("id"), "result": result}
        task["status"] = "failed"
        repair = create_repair_task(state, task, result)
        if repair:
            task["status"] = "waiting-repair"
            append_history(state, "repair-created", taskId=task.get("id"), repairTaskId=repair.get("id"))
            return {"event": "repair-created", "taskId": task.get("id"), "repairTaskId": repair.get("id"), "result": result}
        state["status"] = "blocked"
        append_history(state, "task-blocked", taskId=task.get("id"), result=result)
        return {"event": "blocked", "taskId": task.get("id"), "result": result}

    task["status"] = "awaiting-llm"
    task["updatedAt"] = iso_now()
    state["status"] = "awaiting-llm"
    brief = llm_brief(task)
    append_history(state, "awaiting-llm", taskId=task.get("id"), brief=brief)
    return {"event": "awaiting-llm", "taskId": task.get("id"), "brief": brief}


def finish_if_done(repo: Path, state: dict[str, Any]) -> dict[str, Any] | None:
    if any(task.get("status") not in TERMINAL_TASK_STATES for task in state.get("tasks", [])):
        return None
    completion = completion_check(repo)
    if completion.get("decision") == "require-continue":
        state["status"] = "active"
        append_history(state, "completion-requires-continue", completion=completion)
        return {"event": "completion-requires-continue", "completion": completion}
    if completion.get("decision") == "requires-human-decision":
        review_key = completion_review_key(completion)
        if not review_acknowledged(state, COMPLETION_REVIEW_ACKS, review_key):
            review_task = ensure_completion_review_task(state, completion=completion)
            append_history(state, "completion-requires-human", taskId=review_task.get("id"), completion=completion)
            return {
                "event": "requires-human-decision",
                "taskId": review_task.get("id"),
                "brief": (review_task.get("metadata") or {}).get("requiredAction"),
                "completion": completion,
            }
        append_history(state, "completion-review-already-acknowledged", ackKey=review_key)
    state["status"] = "complete"
    state["activeTaskId"] = None
    append_history(state, "pipeline-complete", completion=completion)
    return {"event": "complete", "completion": completion}


def run_pipeline(repo: Path, *, max_steps: int, task_titles: list[str] | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    state = load_state(repo)
    for title in task_titles or []:
        enqueue_task(state, title=title, kind="llm", origin="run-argument")
    events: list[dict[str, Any]] = []
    if not state.get("tasks"):
        state = default_state(repo)

    for _ in range(max_steps):
        if state.get("status") == "explicitly-deferred":
            events.append({"event": "explicitly-deferred"})
            break
        done_event = finish_if_done(repo, state)
        if done_event:
            events.append(done_event)
            break
        human_decision = current_human_decision(state)
        if human_decision is not None:
            state["status"] = "requires-human-decision"
            state["activeTaskId"] = human_decision.get("id")
            events.append({"event": "requires-human-decision", "taskId": human_decision.get("id"), "brief": (human_decision.get("metadata") or {}).get("requiredAction", human_decision.get("title"))})
            break
        if state.get("status") in PIPELINE_TERMINAL_STATES and should_stop_for_pipeline_status(state):
            events.append({"event": str(state.get("status"))})
            break
        task = select_task(state)
        if task is None:
            done_event = finish_if_done(repo, state) or no_runnable_event(state)
            events.append(done_event)
            break
        event = execute_one(repo, state, task)
        events.append(event)
        if event.get("event") in {"awaiting-llm", "blocked", "requires-human-decision"}:
            break
    else:
        state["status"] = "active"
        append_history(state, "max-steps-reached", maxSteps=max_steps)
        events.append({"event": "max-steps-reached", "maxSteps": max_steps})

    save_state(repo, state)
    return {"ok": state.get("status") == "complete", "state": state, "events": events, "path": PIPELINE_FILE.as_posix()}


def sync_pipeline(repo: Path) -> dict[str, Any]:
    state = load_state(repo.resolve())
    save_state(repo.resolve(), state)
    return {"ok": True, "state": state, "path": PIPELINE_FILE.as_posix()}


def enqueue_pipeline_task(repo: Path, *, title: str, kind: str, command: str | None = None) -> dict[str, Any]:
    state = load_state(repo.resolve())
    task = enqueue_task(state, title=title, kind=kind, command=command)
    save_state(repo.resolve(), state)
    return {"ok": True, "state": state, "task": task, "path": PIPELINE_FILE.as_posix()}


def resolve_task_id(state: dict[str, Any], task_id: str | None) -> str:
    if task_id:
        return task_id
    active = state.get("activeTaskId")
    if isinstance(active, str) and active.strip():
        return active
    for task in reversed(state.get("tasks", [])):
        if isinstance(task, dict) and task.get("status") == "awaiting-llm":
            return str(task.get("id"))
    raise ValueError("no task id provided and no active awaiting-llm task found")


def resolve_pipeline_task(
    repo: Path,
    *,
    task_id: str | None,
    outcome: str,
    summary: str,
    run_next: bool,
    max_steps: int,
    final_text: str = "",
) -> dict[str, Any]:
    repo = repo.resolve()
    state = load_state(repo)
    resolved_id = resolve_task_id(state, task_id)
    tasks = task_map(state)
    task = tasks.get(resolved_id)
    if task is None:
        raise ValueError(f"task not found: {resolved_id}")

    allowed_from = {"pending", "running", "awaiting-llm", "requires-human-decision", "failed", "waiting-repair"}
    current = str(task.get("status") or "pending")
    if current not in allowed_from and outcome not in {"skipped", "explicitly-deferred"}:
        raise ValueError(f"task {resolved_id} is already {current}")

    task["status"] = outcome
    task["updatedAt"] = iso_now()
    task["resolution"] = {
        "outcome": outcome,
        "summary": summary,
        "resolvedAt": task["updatedAt"],
    }
    if outcome in {"done", "explicitly-deferred"}:
        record_review_acknowledgement(state, task, summary)
    metadata = task.get("metadata") if isinstance(task.get("metadata"), dict) else {}
    if outcome == "explicitly-deferred" and task.get("kind") == "human-decision":
        blocked_task_id = str(metadata.get("blockedTaskId") or "")
        blocked_task = tasks.get(blocked_task_id)
        if blocked_task and blocked_task.get("status") not in TERMINAL_TASK_STATES:
            archive_task(blocked_task, summary=f"Deferred because human decision {resolved_id} was paused.")
            append_history(state, "blocked-task-deferred-by-human-decision", taskId=blocked_task_id, humanDecisionTaskId=resolved_id)
    if state.get("activeTaskId") == resolved_id:
        state["activeTaskId"] = None
    append_history(state, "task-resolved", taskId=resolved_id, outcome=outcome, summary=summary)

    events: list[dict[str, Any]] = [{"event": "task-resolved", "taskId": resolved_id, "outcome": outcome, "summary": summary}]
    if outcome == "blocked":
        state["status"] = "blocked"
    elif outcome == "requires-human-decision":
        state["status"] = "requires-human-decision"
    elif outcome == "explicitly-deferred":
        state["status"] = "explicitly-deferred"
    else:
        state["status"] = "active"

    if outcome in TERMINAL_TASK_STATES and final_text.strip():
        completion = completion_check(repo, final_text=final_text)
        if completion.get("decision") == "require-continue":
            follow_up = enqueue_task(
                state,
                title="follow-up: completion gate found a required next step in the final answer",
                kind="llm",
                origin="completion-gate",
                metadata={
                    "sourceTaskId": resolved_id,
                    "completionDecision": completion,
                    "finalTextExcerpt": final_text.strip()[:1000],
                },
            )
            state["status"] = "active"
            events.append(
                {
                    "event": "completion-follow-up-enqueued",
                    "taskId": follow_up.get("id"),
                    "sourceTaskId": resolved_id,
                    "completion": completion,
                }
            )
        elif completion.get("decision") == "requires-human-decision":
            review_key = completion_review_key(completion)
            if not review_acknowledged(state, COMPLETION_REVIEW_ACKS, review_key):
                review_task = ensure_completion_review_task(state, completion=completion)
                events.append(
                    {
                        "event": "requires-human-decision",
                        "taskId": review_task.get("id"),
                        "brief": (review_task.get("metadata") or {}).get("requiredAction"),
                        "completion": completion,
                    }
                )

    save_state(repo, state)
    payload: dict[str, Any] = {"ok": True, "state": state, "events": events, "path": PIPELINE_FILE.as_posix()}
    if run_next and outcome in TERMINAL_TASK_STATES:
        follow_up = run_pipeline(repo, max_steps=max(1, max_steps))
        follow_events = follow_up.get("events") if isinstance(follow_up.get("events"), list) else []
        payload = follow_up
        payload["events"] = events + follow_events
    return payload


def archive_task(task: dict[str, Any], *, summary: str) -> None:
    task["status"] = "explicitly-deferred"
    task["updatedAt"] = iso_now()
    task["resolution"] = {
        "outcome": "explicitly-deferred",
        "summary": summary,
        "resolvedAt": task["updatedAt"],
    }


def maintain_pipeline(
    repo: Path,
    *,
    archive_stale_message_backlog: bool,
    before_task_id: str | None,
    repair_stale_gate: bool,
) -> dict[str, Any]:
    repo = repo.resolve()
    state = load_state(repo)
    events: list[dict[str, Any]] = []

    if repair_stale_gate and state.get("status") == "requires-human-decision" and current_human_decision(state) is None:
        state["status"] = "active"
        state["activeTaskId"] = None
        append_history(state, "stale-human-gate-repaired")
        events.append({"event": "stale-human-gate-repaired"})

    if archive_stale_message_backlog:
        tasks = [task for task in state.get("tasks", []) if isinstance(task, dict)]
        cutoff_index: int | None = None
        if before_task_id:
            for index, task in enumerate(tasks):
                if str(task.get("id") or "") == before_task_id:
                    cutoff_index = index
                    break
            if cutoff_index is None:
                raise ValueError(f"before task not found: {before_task_id}")
        else:
            for index, task in enumerate(tasks):
                if task.get("origin") == "message-ingress" and task.get("status") in TERMINAL_TASK_STATES:
                    cutoff_index = index
                    break

        archived: list[str] = []
        if cutoff_index is not None:
            summary = (
                "Archived historical message-ingress backlog before the first resolved message task; "
                "these items were imported from prior Codex/App history and must not block new loop work."
            )
            for task in tasks[:cutoff_index]:
                if task.get("origin") != "message-ingress":
                    continue
                if task.get("status") in TERMINAL_TASK_STATES:
                    continue
                archive_task(task, summary=summary)
                archived.append(str(task.get("id")))
            if archived:
                append_history(state, "stale-message-backlog-archived", taskIds=archived, beforeTaskId=before_task_id)
                events.append({"event": "stale-message-backlog-archived", "taskIds": archived, "count": len(archived)})
            else:
                events.append({"event": "stale-message-backlog-archive-noop", "beforeTaskId": before_task_id})

    save_state(repo, state)
    return {"ok": True, "state": state, "events": events, "path": PIPELINE_FILE.as_posix()}


def render_panel(payload: dict[str, Any]) -> str:
    state = payload.get("state") if isinstance(payload.get("state"), dict) else load_state(Path(".").resolve())
    tasks = state.get("tasks", []) if isinstance(state.get("tasks"), list) else []
    done = sum(1 for task in tasks if isinstance(task, dict) and task.get("status") in TERMINAL_TASK_STATES)
    total = len(tasks)
    lines = [
        "## Task Pipeline",
        "",
        "| 项目 | 当前值 |",
        "| --- | --- |",
        f"| Status | `{state.get('status')}` |",
        f"| Objective | {state.get('objective', 'n/a')} |",
        f"| Active Task | `{state.get('activeTaskId') or '(none)'}` |",
        f"| Progress | `{done} / {total}` |",
        f"| State | `{PIPELINE_FILE.as_posix()}` |",
    ]
    if payload.get("events"):
        lines.extend(["", "| Event | Task | Detail |", "| --- | --- | --- |"])
        for event in payload.get("events", [])[:8]:
            if not isinstance(event, dict):
                continue
            detail = event.get("brief") or event.get("repairTaskId") or event.get("event")
            lines.append(f"| `{event.get('event')}` | `{event.get('taskId', '')}` | {str(detail).splitlines()[0][:160]} |")
    return "\n".join(lines)


def normalize_argv(argv: list[str]) -> list[str]:
    if not argv:
        return ["panel", "."]
    if argv[0] in {"sync", "enqueue", "run", "resolve", "maintain", "panel"}:
        return argv
    return ["run", *argv]


def main(argv: list[str] | None = None) -> int:
    argv = normalize_argv(list(sys.argv[1:] if argv is None else argv))
    parser = argparse.ArgumentParser(description="Run the project-assistant task pipeline loop.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync")
    sync_parser.add_argument("repo", type=Path)
    sync_parser.add_argument("--json", action="store_true")

    enqueue_parser = subparsers.add_parser("enqueue")
    enqueue_parser.add_argument("repo", type=Path)
    enqueue_parser.add_argument("--title", required=True)
    enqueue_parser.add_argument("--kind", choices=["llm", "command", "validation", "human-decision"], default="llm")
    enqueue_parser.add_argument("--command", dest="task_command")
    enqueue_parser.add_argument("--json", action="store_true")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("repo", type=Path)
    run_parser.add_argument("--max-steps", type=int, default=20)
    run_parser.add_argument("--task", action="append", default=[], help="Enqueue a new LLM task before entering the programmatic pipeline loop.")
    run_parser.add_argument("--json", action="store_true")

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("repo", type=Path)
    resolve_parser.add_argument("--task-id")
    resolve_parser.add_argument("--outcome", choices=["done", "skipped", "explicitly-deferred", "blocked", "requires-human-decision"], default="done")
    resolve_parser.add_argument("--summary", required=True)
    resolve_parser.add_argument("--run-next", action="store_true")
    resolve_parser.add_argument("--max-steps", type=int, default=20)
    resolve_parser.add_argument("--final-text", default="")
    resolve_parser.add_argument("--final-text-file", type=Path)
    resolve_parser.add_argument("--json", action="store_true")

    maintain_parser = subparsers.add_parser("maintain")
    maintain_parser.add_argument("repo", type=Path)
    maintain_parser.add_argument("--archive-stale-message-backlog", action="store_true")
    maintain_parser.add_argument("--before-task-id")
    maintain_parser.add_argument("--repair-stale-gate", action="store_true", default=True)
    maintain_parser.add_argument("--no-repair-stale-gate", action="store_false", dest="repair_stale_gate")
    maintain_parser.add_argument("--json", action="store_true")

    panel_parser = subparsers.add_parser("panel")
    panel_parser.add_argument("repo", type=Path)
    panel_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "sync":
        payload = sync_pipeline(args.repo)
    elif args.command == "enqueue":
        payload = enqueue_pipeline_task(args.repo, title=args.title, kind=args.kind, command=args.task_command)
    elif args.command == "run":
        payload = run_pipeline(args.repo, max_steps=max(1, args.max_steps), task_titles=args.task)
    elif args.command == "resolve":
        final_text = args.final_text
        if args.final_text_file:
            final_text = read_text(args.final_text_file)
        try:
            payload = resolve_pipeline_task(
                args.repo,
                task_id=args.task_id,
                outcome=args.outcome,
                summary=args.summary,
                run_next=args.run_next,
                max_steps=max(1, args.max_steps),
                final_text=final_text,
            )
        except ValueError as exc:
            payload = {"ok": False, "error": str(exc), "state": load_state(args.repo)}
    elif args.command == "maintain":
        try:
            payload = maintain_pipeline(
                args.repo,
                archive_stale_message_backlog=args.archive_stale_message_backlog,
                before_task_id=args.before_task_id,
                repair_stale_gate=args.repair_stale_gate,
            )
        except ValueError as exc:
            payload = {"ok": False, "error": str(exc), "state": load_state(args.repo)}
    elif args.command == "panel":
        payload = sync_pipeline(args.repo)
    else:
        raise SystemExit(f"unsupported command: {args.command}")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_panel(payload))
    state = payload.get("state", {}) if isinstance(payload.get("state"), dict) else {}
    if payload.get("ok") is False and payload.get("error"):
        return 2
    return 0 if state.get("status") not in {"blocked"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
