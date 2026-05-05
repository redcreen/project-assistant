#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback is not expected in Codex.
    tomllib = None  # type: ignore[assignment]

import message_ingress


SCHEMA = "project-assistant.codex-app-loop.v1"
REPO_LOOP_FILE = Path(".codex/codex-app-loop.json")
DEFAULT_SESSIONS_DIR = Path.home() / ".codex/sessions"
DEFAULT_STATE_PATH = Path.home() / ".codex/project-assistant/codex-app-loop-state.json"
DEFAULT_CONFIG_PATH = Path.home() / ".codex/config.toml"

PROJECT_MARKERS = [
    "项目助手",
    "ptl",
    "project assistant",
    "continue",
    "progress",
    "resume",
    "执行",
    "继续",
    "进展",
    "整改",
    "实现",
    "修复",
    "测试",
    "review",
    "implement",
    "fix",
    "test",
]


@dataclass(frozen=True)
class CodexUserEvent:
    event_id: str
    session_path: Path
    line_number: int
    timestamp: str
    cwd: Path | None
    message: str


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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


def event_id(path: Path, line_number: int, timestamp: str, message: str) -> str:
    raw = f"{path.resolve()}\0{line_number}\0{timestamp}\0{message}".encode("utf-8", errors="replace")
    return hashlib.sha256(raw).hexdigest()[:24]


def compact_message(message: str, limit: int = 160) -> str:
    compact = " ".join(message.strip().split())
    if len(compact) > limit:
        return compact[: limit - 3] + "..."
    return compact


def load_state(state_path: Path) -> dict[str, Any]:
    existing = read_json(state_path, {})
    if isinstance(existing, dict) and existing.get("schema") == SCHEMA:
        existing.setdefault("seenEventIds", [])
        existing.setdefault("lastEvents", [])
        existing.setdefault("counters", {})
        return existing
    return {
        "schema": SCHEMA,
        "createdAt": iso_now(),
        "updatedAt": iso_now(),
        "seenEventIds": [],
        "lastEvents": [],
        "counters": {},
    }


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    seen = [str(item) for item in state.get("seenEventIds", [])]
    state["seenEventIds"] = seen[-20000:]
    events = [item for item in state.get("lastEvents", []) if isinstance(item, dict)]
    state["lastEvents"] = events[-200:]
    state["schema"] = SCHEMA
    state["updatedAt"] = iso_now()
    write_json(state_path, state)


def bump_counter(state: dict[str, Any], name: str, amount: int = 1) -> None:
    counters = state.setdefault("counters", {})
    counters[name] = int(counters.get(name, 0)) + amount


def trusted_projects(config_path: Path) -> list[Path]:
    if tomllib is None or not config_path.exists():
        return []
    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    projects = data.get("projects")
    if not isinstance(projects, dict):
        return []
    trusted: list[Path] = []
    for raw_path, config in projects.items():
        if isinstance(config, dict) and config.get("trust_level") == "trusted":
            trusted.append(Path(str(raw_path)).expanduser().resolve())
    return trusted


def is_relative_to(path: Path, ancestor: Path) -> bool:
    try:
        path.relative_to(ancestor)
        return True
    except ValueError:
        return False


def nearest_control_surface(cwd: Path) -> Path | None:
    candidates = [cwd, *cwd.parents]
    home = Path.home().resolve()
    for candidate in candidates:
        if candidate == home.parent:
            break
        if (candidate / ".codex/control-surface.json").exists():
            return candidate
    return None


def matched_trusted_root(cwd: Path, trusted: list[Path]) -> Path | None:
    for project in trusted:
        if cwd == project or is_relative_to(cwd, project):
            return project
    return None


def project_marker_present(message: str) -> bool:
    lowered = message.lower()
    return any(marker.lower() in lowered for marker in PROJECT_MARKERS)


def resolve_target_repo(event: CodexUserEvent, trusted: list[Path], *, route_all_trusted: bool) -> tuple[Path | None, str]:
    if event.cwd is None:
        return None, "missing-cwd"
    cwd = event.cwd.expanduser().resolve()
    if not cwd.exists() or not cwd.is_dir():
        return None, "cwd-missing"

    control_root = nearest_control_surface(cwd)
    if control_root is not None:
        return control_root, "control-surface"

    trusted_root = matched_trusted_root(cwd, trusted)
    if trusted_root is not None and route_all_trusted:
        return trusted_root, "trusted-project"

    if project_marker_present(event.message):
        return trusted_root or cwd, "project-marker"

    return None, "not-project-assistant-context"


def list_session_files(sessions_dir: Path, max_files: int) -> list[Path]:
    if not sessions_dir.exists():
        return []
    files = [path for path in sessions_dir.rglob("*.jsonl") if path.is_file()]
    files.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    selected = files[:max(1, max_files)]
    return sorted(selected, key=lambda path: path.stat().st_mtime)


def event_payload_text(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    message = payload.get("message")
    if isinstance(message, str):
        return message
    return ""


def iter_user_events(session_path: Path) -> list[CodexUserEvent]:
    events: list[CodexUserEvent] = []
    current_cwd: Path | None = None
    try:
        lines = session_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return events

    for index, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        item_type = item.get("type")
        payload_type = payload.get("type") if isinstance(payload, dict) else None

        if item_type in {"session_meta", "turn_context"}:
            raw_cwd = payload.get("cwd") if isinstance(payload, dict) else None
            if isinstance(raw_cwd, str) and raw_cwd.strip():
                current_cwd = Path(raw_cwd)
            continue

        if item_type == "event_msg" and payload_type == "user_message":
            message = event_payload_text(payload)
            if not message.strip():
                continue
            timestamp = str(item.get("timestamp") or "")
            events.append(
                CodexUserEvent(
                    event_id=event_id(session_path, index, timestamp, message),
                    session_path=session_path,
                    line_number=index,
                    timestamp=timestamp,
                    cwd=current_cwd,
                    message=message,
                )
            )
    return events


def recent_message_seen(repo: Path, message: str, window: int = 20) -> bool:
    ingress = read_json(repo / ".codex/message-ingress.json", {})
    if not isinstance(ingress, dict):
        return False
    messages = ingress.get("messages")
    if not isinstance(messages, list):
        return False
    normalized = " ".join(message.split())
    for item in messages[-window:]:
        if not isinstance(item, dict):
            continue
        existing = item.get("message")
        if isinstance(existing, str) and " ".join(existing.split()) == normalized:
            return True
    return False


def load_repo_loop(repo: Path) -> dict[str, Any]:
    existing = read_json(repo / REPO_LOOP_FILE, {})
    if isinstance(existing, dict) and existing.get("schema") == SCHEMA:
        existing.setdefault("lastEvents", [])
        existing.setdefault("counters", {})
        return existing
    return {
        "schema": SCHEMA,
        "project": repo.name,
        "createdAt": iso_now(),
        "updatedAt": iso_now(),
        "lastEvents": [],
        "counters": {},
    }


def write_repo_event(repo: Path, event: dict[str, Any]) -> None:
    payload = load_repo_loop(repo)
    payload["project"] = repo.name
    payload["updatedAt"] = iso_now()
    payload.setdefault("lastEvents", []).append(event)
    payload["lastEvents"] = [item for item in payload["lastEvents"] if isinstance(item, dict)][-50:]
    counters = payload.setdefault("counters", {})
    action = str(event.get("action") or "unknown")
    counters[action] = int(counters.get(action, 0)) + 1
    write_json(repo / REPO_LOOP_FILE, payload)


def record_global_event(state: dict[str, Any], event: dict[str, Any]) -> None:
    state.setdefault("lastEvents", []).append(event)
    action = str(event.get("action") or "unknown")
    bump_counter(state, action)


def scan_once(
    *,
    sessions_dir: Path,
    state_path: Path,
    config_path: Path,
    max_files: int,
    max_events: int,
    max_steps: int,
    route_all_trusted: bool,
    baseline: bool,
    dry_run: bool,
) -> dict[str, Any]:
    state = load_state(state_path)
    seen = {str(item) for item in state.get("seenEventIds", [])}
    trusted = trusted_projects(config_path)
    files = list_session_files(sessions_dir, max_files=max_files)

    candidates: list[CodexUserEvent] = []
    for session_file in files:
        candidates.extend(iter_user_events(session_file))
    candidates = [event for event in candidates if event.event_id not in seen]
    candidates.sort(key=lambda event: (event.timestamp, str(event.session_path), event.line_number))
    if not baseline:
        candidates = candidates[: max(1, max_events)]

    actions: list[dict[str, Any]] = []
    for event in candidates:
        summary: dict[str, Any] = {
            "eventId": event.event_id,
            "at": iso_now(),
            "timestamp": event.timestamp,
            "session": str(event.session_path),
            "line": event.line_number,
            "cwd": str(event.cwd) if event.cwd else None,
            "message": compact_message(event.message),
        }
        if baseline:
            summary["action"] = "baselined"
            seen.add(event.event_id)
            record_global_event(state, summary)
            actions.append(summary)
            continue

        repo, reason = resolve_target_repo(event, trusted, route_all_trusted=route_all_trusted)
        summary["routeReason"] = reason
        if repo is None:
            summary["action"] = "skipped"
            seen.add(event.event_id)
            record_global_event(state, summary)
            actions.append(summary)
            continue

        summary["repo"] = str(repo)
        if recent_message_seen(repo, event.message):
            summary["action"] = "deduped"
            seen.add(event.event_id)
            write_repo_event(repo, summary)
            record_global_event(state, summary)
            actions.append(summary)
            continue

        if dry_run:
            summary["action"] = "would-route"
            seen.add(event.event_id)
            record_global_event(state, summary)
            actions.append(summary)
            continue

        payload = message_ingress.ingest(
            repo,
            message=event.message,
            source="codex-app-loop",
            max_steps=max(1, max_steps),
            classify_only=False,
        )
        record = payload.get("record") if isinstance(payload.get("record"), dict) else {}
        summary["action"] = "routed"
        summary["taskId"] = record.get("taskId")
        seen.add(event.event_id)
        write_repo_event(repo, summary)
        record_global_event(state, summary)
        actions.append(summary)

    state["seenEventIds"] = list(seen)
    state["sessionsDir"] = str(sessions_dir)
    state["configPath"] = str(config_path)
    save_state(state_path, state)

    return {
        "ok": True,
        "schema": SCHEMA,
        "statePath": str(state_path),
        "sessionsDir": str(sessions_dir),
        "filesScanned": len(files),
        "eventsSeen": len(candidates),
        "actions": actions,
        "counters": state.get("counters", {}),
    }


def panel(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    payload = load_repo_loop(repo)
    return {
        "ok": True,
        "schema": SCHEMA,
        "project": repo.name,
        "path": REPO_LOOP_FILE.as_posix(),
        "counters": payload.get("counters", {}),
        "lastEvents": payload.get("lastEvents", [])[-5:],
    }


def render_panel(payload: dict[str, Any]) -> str:
    counters = payload.get("counters") if isinstance(payload.get("counters"), dict) else {}
    lines = [
        "## Codex App Loop",
        "",
        "| 项目 | 当前值 |",
        "| --- | --- |",
        f"| State | `{payload.get('path')}` |",
        f"| Routed | `{counters.get('routed', 0)}` |",
        f"| Deduped | `{counters.get('deduped', 0)}` |",
        f"| Skipped | `{counters.get('skipped', 0)}` |",
    ]
    last_events = payload.get("lastEvents") if isinstance(payload.get("lastEvents"), list) else []
    if last_events:
        lines.extend(["", "| Action | Reason | Message | Task |", "| --- | --- | --- | --- |"])
        for event in last_events:
            if not isinstance(event, dict):
                continue
            lines.append(
                f"| `{event.get('action', 'unknown')}` | `{event.get('routeReason', '')}` | {event.get('message', '')} | `{event.get('taskId') or '(none)'}` |"
            )
    return "\n".join(lines)


def watch(args: argparse.Namespace) -> int:
    while True:
        payload = scan_once(
            sessions_dir=args.sessions_dir,
            state_path=args.state,
            config_path=args.config,
            max_files=args.max_files,
            max_events=args.max_events,
            max_steps=args.max_steps,
            route_all_trusted=args.route_all_trusted,
            baseline=False,
            dry_run=args.dry_run,
        )
        if not args.quiet and payload.get("actions"):
            print(json.dumps(payload, ensure_ascii=False, sort_keys=True), flush=True)
        time.sleep(max(1.0, args.interval))


def add_common_scan_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--sessions-dir", type=Path, default=DEFAULT_SESSIONS_DIR)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--max-files", type=int, default=200)
    parser.add_argument("--max-events", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=1)
    parser.add_argument("--route-all-trusted", action="store_true", default=True)
    parser.add_argument("--no-route-all-trusted", dest="route_all_trusted", action="store_false")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bridge Codex Desktop App session logs into project-assistant message ingress.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan")
    add_common_scan_args(scan_parser)

    baseline_parser = subparsers.add_parser("baseline")
    add_common_scan_args(baseline_parser)

    watch_parser = subparsers.add_parser("watch")
    add_common_scan_args(watch_parser)
    watch_parser.add_argument("--interval", type=float, default=3.0)
    watch_parser.add_argument("--quiet", action="store_true")

    panel_parser = subparsers.add_parser("panel")
    panel_parser.add_argument("repo", type=Path)
    panel_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "watch":
        return watch(args)
    if args.command == "panel":
        payload = panel(args.repo)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_panel(payload))
        return 0

    payload = scan_once(
        sessions_dir=args.sessions_dir,
        state_path=args.state,
        config_path=args.config,
        max_files=args.max_files,
        max_events=args.max_events,
        max_steps=args.max_steps,
        route_all_trusted=args.route_all_trusted,
        baseline=args.command == "baseline",
        dry_run=args.dry_run,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"files scanned: {payload['filesScanned']}")
        print(f"events seen: {payload['eventsSeen']}")
        print(f"actions: {len(payload['actions'])}")
        print(f"ok: {payload['ok']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
