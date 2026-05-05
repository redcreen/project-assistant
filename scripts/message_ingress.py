#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

import pipeline_runner


SCHEMA = "project-assistant.message-ingress.v1"
INGRESS_FILE = Path(".codex/message-ingress.json")

EXECUTION_MARKERS = [
    "实现",
    "修复",
    "修改",
    "加",
    "做掉",
    "完成",
    "落地",
    "跑",
    "测试",
    "一口气",
    "implement",
    "fix",
    "add",
    "update",
    "run",
    "test",
    "ship",
]
DISCUSSION_MARKERS = ["讨论", "怎么看", "是否", "为什么", "能否", "怎么", "分析", "review", "explain", "why", "how"]
PROGRESS_MARKERS = ["进展", "状态", "progress", "status"]


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def classify_message(message: str) -> dict[str, Any]:
    lowered = message.lower()
    if any(marker in lowered for marker in PROGRESS_MARKERS):
        intent = "progress"
        task_required = True
    elif any(marker in lowered for marker in EXECUTION_MARKERS):
        intent = "execute"
        task_required = True
    elif any(marker in lowered for marker in DISCUSSION_MARKERS) or message.strip().endswith(("?", "？")):
        intent = "analysis"
        task_required = True
    else:
        intent = "message"
        task_required = True
    return {
        "intent": intent,
        "taskRequired": task_required,
        "taskKind": "llm",
        "reason": "host/message ingress captures every non-empty user message as a pipeline task; command execution remains explicit.",
    }


def task_title(message: str, intent: str) -> str:
    compact = " ".join(message.strip().split())
    if len(compact) > 140:
        compact = compact[:137] + "..."
    return f"{intent}: {compact}"


def load_ingress(repo: Path) -> dict[str, Any]:
    existing = read_json(repo / INGRESS_FILE, {})
    if isinstance(existing, dict) and existing.get("schema") == SCHEMA:
        existing.setdefault("messages", [])
        return existing
    return {"schema": SCHEMA, "project": repo.name, "messages": []}


def save_ingress(repo: Path, ingress: dict[str, Any]) -> None:
    ingress["schema"] = SCHEMA
    ingress["project"] = repo.name
    ingress["updatedAt"] = iso_now()
    write_json(repo / INGRESS_FILE, ingress)


def next_message_id(messages: list[Any]) -> str:
    max_id = 0
    for item in messages:
        if not isinstance(item, dict):
            continue
        raw_id = str(item.get("id") or "")
        if not raw_id.startswith("msg-"):
            continue
        try:
            max_id = max(max_id, int(raw_id.removeprefix("msg-")))
        except ValueError:
            continue
    return f"msg-{max_id + 1:04d}"


def ingest(repo: Path, *, message: str, source: str, max_steps: int, classify_only: bool) -> dict[str, Any]:
    repo = repo.resolve()
    classification = classify_message(message)
    ingress = load_ingress(repo)
    messages = ingress.setdefault("messages", [])
    record = {
        "id": next_message_id(messages if isinstance(messages, list) else []),
        "receivedAt": iso_now(),
        "source": source,
        "message": message,
        "classification": classification,
        "taskId": None,
        "action": "classify-only" if classify_only else "enqueue-and-run",
    }

    pipeline_payload: dict[str, Any] | None = None
    if classification["taskRequired"] and not classify_only:
        state = pipeline_runner.load_state(repo)
        task = pipeline_runner.enqueue_task(
            state,
            title=task_title(message, str(classification["intent"])),
            kind=str(classification["taskKind"]),
            origin="message-ingress",
            metadata={
                "messageId": record["id"],
                "source": source,
                "intent": classification["intent"],
                "rawMessage": message,
            },
        )
        pipeline_runner.save_state(repo, state)
        record["taskId"] = task.get("id")
        pipeline_payload = pipeline_runner.run_pipeline(repo, max_steps=max_steps)

    messages = ingress.setdefault("messages", [])
    messages.append(record)
    del messages[:-200]
    save_ingress(repo, ingress)

    return {
        "ok": True,
        "schema": SCHEMA,
        "project": repo.name,
        "ingressPath": INGRESS_FILE.as_posix(),
        "pipelinePath": pipeline_runner.PIPELINE_FILE.as_posix(),
        "record": record,
        "pipeline": pipeline_payload,
    }


def panel(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    ingress = load_ingress(repo)
    return {
        "ok": True,
        "schema": SCHEMA,
        "project": repo.name,
        "ingressPath": INGRESS_FILE.as_posix(),
        "messageCount": len(ingress.get("messages", [])),
        "lastMessages": list(ingress.get("messages", []))[-5:],
    }


def render_panel(payload: dict[str, Any]) -> str:
    lines = [
        "## Message Ingress",
        "",
        "| 项目 | 当前值 |",
        "| --- | --- |",
        f"| Ingress | `{payload.get('ingressPath')}` |",
        f"| Message Count | `{payload.get('messageCount', 0)}` |",
    ]
    record = payload.get("record") if isinstance(payload.get("record"), dict) else None
    if record:
        classification = record.get("classification") if isinstance(record.get("classification"), dict) else {}
        lines.extend(
            [
                f"| Last Intent | `{classification.get('intent')}` |",
                f"| Task | `{record.get('taskId') or '(none)'}` |",
                f"| Action | `{record.get('action')}` |",
            ]
        )
    last_messages = payload.get("lastMessages") if isinstance(payload.get("lastMessages"), list) else []
    if last_messages:
        lines.extend(["", "| Message | Intent | Task |", "| --- | --- | --- |"])
        for item in last_messages:
            if not isinstance(item, dict):
                continue
            classification = item.get("classification") if isinstance(item.get("classification"), dict) else {}
            message = " ".join(str(item.get("message", "")).split())[:120]
            lines.append(f"| {message} | `{classification.get('intent', 'unknown')}` | `{item.get('taskId') or '(none)'}` |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture host/user messages into the project-assistant task pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest")
    ingest_parser.add_argument("repo", type=Path)
    ingest_parser.add_argument("--message", required=True)
    ingest_parser.add_argument("--source", default="chat")
    ingest_parser.add_argument("--max-steps", type=int, default=3)
    ingest_parser.add_argument("--classify-only", action="store_true")
    ingest_parser.add_argument("--json", action="store_true")

    panel_parser = subparsers.add_parser("panel")
    panel_parser.add_argument("repo", type=Path)
    panel_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "ingest":
        payload = ingest(args.repo, message=args.message, source=args.source, max_steps=max(1, args.max_steps), classify_only=args.classify_only)
    elif args.command == "panel":
        payload = panel(args.repo)
    else:
        raise SystemExit(f"unsupported command: {args.command}")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_panel(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
