#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import codex_app_loop
import message_ingress

try:
    import pipeline_runner
except Exception:  # pragma: no cover - hook can still record messages without direct runner control.
    pipeline_runner = None  # type: ignore[assignment]

try:
    import ptl_learning
except Exception:  # pragma: no cover - hook must not fail if learning review is unavailable.
    ptl_learning = None  # type: ignore[assignment]


LOOP_HEADER_CONTEXT = (
    "Start every user-facing reply with a state-sensitive compact loop header: state the current loop/task id "
    "and the goal for this turn; include exit or pause options only when work is still running or waiting, "
    "include the active human-decision response format only when human input is actually required, and if there "
    "is no active task or human action needed, explicitly say no human action is needed instead of asking the user to stop or pause."
)
HUMAN_ACTION_CONTEXT = (
    "Whenever a human action is needed, restate a separate `需要人类做什么` section with numbered actions, "
    "the exact one-line reply format, and the current pending items; do not rely on prior context."
)


def read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"_decodeError": True, "_raw": raw}
    return payload if isinstance(payload, dict) else {}


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def current_human_decision_task(repo: Path) -> dict[str, Any] | None:
    if pipeline_runner is None:
        return None
    state = pipeline_runner.load_state(repo)
    active_id = str(state.get("activeTaskId") or "")
    for task in state.get("tasks", []):
        if not isinstance(task, dict):
            continue
        if task.get("id") == active_id and task.get("kind") == "human-decision":
            return task
    return None


def main() -> int:
    payload = read_stdin_json()
    prompt = payload.get("prompt")
    cwd = payload.get("cwd")
    session_id = payload.get("session_id")
    turn_id = payload.get("turn_id")

    if not isinstance(prompt, str) or not prompt.strip() or not isinstance(cwd, str) or not cwd.strip():
        emit({"continue": True})
        return 0

    repo, reason = codex_app_loop.resolve_target_repo(
        codex_app_loop.CodexUserEvent(
            event_id=f"hook:{session_id or ''}:{turn_id or ''}",
            session_path=Path(str(payload.get("transcript_path") or "")),
            line_number=0,
            timestamp="",
            cwd=Path(cwd),
            message=prompt,
        ),
        codex_app_loop.trusted_projects(codex_app_loop.DEFAULT_CONFIG_PATH),
        route_all_trusted=True,
    )
    if repo is None:
        emit({"continue": True})
        return 0

    human_task = current_human_decision_task(repo)
    if human_task and ptl_learning is not None and str(human_task.get("id")) == ptl_learning.HUMAN_REVIEW_TASK_ID:
        decision = ptl_learning.apply_human_review_response(repo, response=prompt)
        if decision.get("processed"):
            message_ingress.ingest(
                repo,
                message=prompt,
                source="codex-app-user-prompt-hook-human-decision",
                max_steps=1,
                classify_only=True,
            )
            remaining = decision.get("remaining") if isinstance(decision.get("remaining"), list) else []
            continuation = {}
            if not remaining and pipeline_runner is not None:
                continuation = pipeline_runner.run_pipeline(repo, max_steps=20)
            applied = decision.get("applied") if isinstance(decision.get("applied"), list) else []
            if remaining:
                prompt_items = [
                    {"title": str(item.get("title") or item.get("id") or "")}
                    for item in remaining
                    if isinstance(item, dict)
                ]
                context = (
                    f"{ptl_learning.render_human_prompt(prompt_items, title='还需要你确认')}\n\n"
                    "已处理："
                    f"{json.dumps(applied, ensure_ascii=False)}"
                )
            else:
                events = continuation.get("events") if isinstance(continuation.get("events"), list) else []
                context = (
                    "# 已确认完成\n\n"
                    f"已处理：{json.dumps(applied, ensure_ascii=False)}\n\n"
                    f"已继续执行 loop：{json.dumps(events[-3:], ensure_ascii=False)}。"
                )
            context = f"{LOOP_HEADER_CONTEXT} {HUMAN_ACTION_CONTEXT}\n\n{context}"
            emit(
                {
                    "continue": True,
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": context,
                    },
                }
            )
            return 0

    if human_task and pipeline_runner is not None:
        decision = pipeline_runner.apply_human_decision_response(repo, response=prompt)
        if decision.get("processed"):
            message_ingress.ingest(
                repo,
                message=prompt,
                source="codex-app-user-prompt-hook-human-decision",
                max_steps=1,
                classify_only=True,
            )
            pipeline = decision.get("pipeline") if isinstance(decision.get("pipeline"), dict) else {}
            events = pipeline.get("events") if isinstance(pipeline.get("events"), list) else []
            context = (
                f"{LOOP_HEADER_CONTEXT} {HUMAN_ACTION_CONTEXT}\n\n"
                "# Human Decision 已处理\n\n"
                f"- Task: `{decision.get('taskId')}`\n"
                f"- Outcome: `{decision.get('outcome')}`\n"
                f"- Loop events: `{json.dumps(events[-3:], ensure_ascii=False)}`"
            )
            emit(
                {
                    "continue": True,
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": context,
                    },
                }
            )
            return 0

    if codex_app_loop.recent_message_seen(repo, prompt):
        emit(
            {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": (
                        "Project Assistant ingress already recorded this user message; continue inside the existing bounded task loop. "
                        f"{LOOP_HEADER_CONTEXT} {HUMAN_ACTION_CONTEXT}"
                    ),
                },
            }
        )
        return 0

    result = message_ingress.ingest(
        repo,
        message=prompt,
        source="codex-app-user-prompt-hook",
        max_steps=1,
        classify_only=False,
    )
    record = result.get("record") if isinstance(result.get("record"), dict) else {}
    task_id = record.get("taskId") or "(none)"
    learning_context = ""
    if ptl_learning is not None:
        try:
            learning = ptl_learning.scan(repo)
            summary = learning.get("summary") if isinstance(learning.get("summary"), dict) else {}
            pending = int(summary.get("pending") or 0)
            if pending:
                learning_context = (
                    f" PTL learning review has `{pending}` pending candidate(s); inspect with "
                    "`python3 scripts/ptl_learning.py panel .` or use the host PTL review signal."
                )
        except Exception as exc:
            learning_context = f" PTL learning review scan failed: {exc}."
    codex_app_loop.write_repo_event(
        repo,
        {
            "action": "hook-routed",
            "routeReason": reason,
            "taskId": task_id,
            "message": codex_app_loop.compact_message(prompt),
            "sessionId": session_id,
            "turnId": turn_id,
        },
    )
    emit(
        {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": (
                    "Project Assistant has recorded this user message through the Codex App "
                    f"UserPromptSubmit hook as task `{task_id}`. Treat the turn as executing inside "
                    "that bounded loop task; do not re-ingest the same message unless the prior ingress failed. "
                    f"{LOOP_HEADER_CONTEXT} {HUMAN_ACTION_CONTEXT} "
                    "After completing the task, write back the result with "
                    f"`python3 scripts/pipeline_runner.py resolve . --task-id {task_id} "
                    '--outcome done --summary "<what changed>" --run-next`.'
                    " If the planned final answer contains a known required next step, keep working instead of finalizing, "
                    "or pass that answer through `--final-text` / `--final-text-file` so the completion gate can enqueue the follow-up."
                    f"{learning_context}"
                ),
            },
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
