#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from daemon_runtime import ensure_daemon, kill_daemon, repo_runtime_paths, send_request, send_request_or_snapshot


def render_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def render_status_text(status: dict[str, object]) -> None:
    queue_summary = status.get("queueSummary", {})
    remaining = list(status.get("remainingExecutionTasks", []))
    print("# PTL Daemon")
    print("")
    print("| 项目 | 当前值 |")
    print("| --- | --- |")
    print(f"| 仓库 | `{status.get('repo')}` |")
    print(f"| Runtime | `{status.get('runtimeId')}` |")
    print(f"| 状态 | `{status.get('status')}` |")
    print(f"| 当前阶段 | `{status.get('currentPhase')}` |")
    print(f"| 当前切片 | `{status.get('activeSlice')}` |")
    print(f"| 当前检查点 | `{status.get('currentCheckpoint')}` |")
    print(f"| 下一动作 | `{status.get('nextAction')}` |")
    print(f"| 下一动作来源 | `{status.get('nextActionSource')}` |")
    print(f"| Gate | `{status.get('gate')}` |")
    print(f"| Resume Ready | `{status.get('resumeReady')}` |")
    print(f"| Socket | `{status.get('socketPath') or 'n/a'}` |")
    if remaining:
        print(f"| 剩余执行任务 | `{ ' / '.join(str(item) for item in remaining) }` |")
    print("")
    print("| 队列状态 | 数量 |")
    print("| --- | ---: |")
    for key in ["queued", "running", "completed", "failed", "cancelled"]:
        print(f"| `{key}` | `{queue_summary.get(key, 0)}` |")


def render_queue_text(snapshot: dict[str, object]) -> None:
    tasks = list(snapshot.get("tasks", []))
    print("# PTL Queue")
    print("")
    print("| Task | Type | Status | Lane | ETA | Output |")
    print("| --- | --- | --- | --- | --- | --- |")
    if not tasks:
        print("| `(empty)` |  |  |  |  |  |")
        return
    for task in tasks:
        print(
            f"| `{task.get('taskId')}` | `{task.get('taskType')}` | `{task.get('status')}` | "
            f"`{task.get('lane')}` | `{task.get('etaBand')}` | `{task.get('outputPath')}` |"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="project-assistant daemon / queue control surface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ["start", "status", "stop", "kill", "queue", "events"]:
        sub = subparsers.add_parser(name)
        sub.add_argument("repo", nargs="?", default=".", type=Path)
        sub.add_argument("--json", action="store_true")
        if name == "events":
            sub.add_argument("--since-id", type=int, default=0)
            sub.add_argument("--limit", type=int, default=100)

    enqueue = subparsers.add_parser("enqueue")
    enqueue.add_argument("task_type")
    enqueue.add_argument("repo", nargs="?", default=".", type=Path)
    enqueue.add_argument("--owner", default="daemon")
    enqueue.add_argument("--json", action="store_true")

    task = subparsers.add_parser("task")
    task.add_argument("task_id")
    task.add_argument("repo", nargs="?", default=".", type=Path)
    task.add_argument("--json", action="store_true")

    acquire = subparsers.add_parser("acquire-foreground")
    acquire.add_argument("repo", nargs="?", default=".", type=Path)
    acquire.add_argument("--owner", default="host")
    acquire.add_argument("--ttl-seconds", type=int, default=60)
    acquire.add_argument("--json", action="store_true")

    heartbeat = subparsers.add_parser("heartbeat-foreground")
    heartbeat.add_argument("lease_id")
    heartbeat.add_argument("repo", nargs="?", default=".", type=Path)
    heartbeat.add_argument("--ttl-seconds", type=int, default=60)
    heartbeat.add_argument("--json", action="store_true")

    release = subparsers.add_parser("release-foreground")
    release.add_argument("lease_id")
    release.add_argument("repo", nargs="?", default=".", type=Path)
    release.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    repo = args.repo.resolve() if hasattr(args, "repo") else Path(".").resolve()
    paths = repo_runtime_paths(repo)

    if args.command == "start":
        result = ensure_daemon(paths)
        if args.json:
            render_json(result)
        else:
            render_status_text(result)
        return 0

    if args.command == "status":
        result = send_request_or_snapshot(paths, "status")
        if args.json:
            render_json(result)
        else:
            render_status_text(result)
        return 0

    if args.command == "stop":
        result = send_request(paths, "stop")
        if args.json:
            render_json(result)
        else:
            render_status_text(result)
        return 0

    if args.command == "kill":
        result = kill_daemon(paths)
        if args.json:
            render_json(result)
        else:
            print(f"killed: {result['killed']}")
            print(f"runtimeDir: {result['runtimeDir']}")
        return 0

    if args.command == "queue":
        result = send_request_or_snapshot(paths, "queue")
        if args.json:
            render_json(result)
        else:
            render_queue_text(result)
        return 0

    if args.command == "events":
        result = send_request_or_snapshot(paths, "events", sinceId=args.since_id, limit=args.limit)
        if args.json:
            render_json(result)
        else:
            print("# PTL Events")
            print("")
            for item in result:
                print(f"- `{item['id']}` `{item['timestamp']}` `{item['type']}`")
        return 0

    if args.command == "enqueue":
        ensure_daemon(paths)
        result = send_request(paths, "enqueue", taskType=args.task_type, owner=args.owner)
        if args.json:
            render_json(result)
        else:
            print(f"queued: {result['taskId']} ({result['taskType']})")
            print(f"output: {result['outputPath']}")
        return 0

    if args.command == "task":
        result = send_request_or_snapshot(paths, "task", taskId=args.task_id)
        if args.json:
            render_json(result)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    if args.command == "acquire-foreground":
        ensure_daemon(paths)
        result = send_request(paths, "acquire-foreground", owner=args.owner, ttlSeconds=args.ttl_seconds)
        if args.json:
            render_json(result)
        else:
            print(f"lease: {result['leaseId']}")
        return 0

    if args.command == "heartbeat-foreground":
        result = send_request(paths, "heartbeat-foreground", leaseId=args.lease_id, ttlSeconds=args.ttl_seconds)
        if args.json:
            render_json(result)
        else:
            print(f"lease: {result['leaseId']}")
        return 0

    if args.command == "release-foreground":
        result = send_request(paths, "release-foreground", leaseId=args.lease_id)
        if args.json:
            render_json(result)
        else:
            print("released: True")
        return 0

    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
