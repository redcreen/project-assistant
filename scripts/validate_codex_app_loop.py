#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
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

`codex app loop fixture`

## Current Execution Line
- Objective: prove Codex App loop bridge
- Plan Link: codex-app-loop-fixture
- Progress: 1 / 1 tasks complete

## Architecture Supervision
- Signal: `green`
- Escalation Gate: continue automatically

## Execution Tasks
- [x] EL-1 fixture control task complete
"""
    status = """# Status

## Current Phase

`codex app loop fixture`

## Active Slice
`codex-app-loop-fixture`

## Current Execution Line
- Objective: prove Codex App loop bridge
- Plan Link: codex-app-loop-fixture
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


def write_session(path: Path, cwd: Path, message: str) -> None:
    rows = [
        {"timestamp": "2026-05-04T00:00:00.000Z", "type": "session_meta", "payload": {"cwd": str(cwd)}},
        {"timestamp": "2026-05-04T00:00:01.000Z", "type": "event_msg", "payload": {"type": "user_message", "message": message}},
    ]
    write(path, "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n")


def run_json(args: list[str], cwd: Path | None = None) -> dict[str, object]:
    result = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if result.returncode != 0:
        raise AssertionError(f"command failed: {' '.join(args)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"expected JSON output from {' '.join(args)}\nSTDOUT:\n{result.stdout}") from exc


def pipeline_tasks(repo: Path) -> list[dict[str, object]]:
    payload = json.loads((repo / ".codex/task-pipeline.json").read_text(encoding="utf-8"))
    return [task for task in payload.get("tasks", []) if isinstance(task, dict)]


def message_ingress(repo: Path) -> dict[str, object]:
    return json.loads((repo / ".codex/message-ingress.json").read_text(encoding="utf-8"))


def validate_user_prompt_hook_fixture(root: Path) -> None:
    repo = root / "hook-repo"
    seed_control_surface(repo)
    hook_input = {
        "session_id": "session-fixture",
        "turn_id": "turn-fixture",
        "cwd": str(repo),
        "prompt": "请通过 UserPromptSubmit hook 进入 loop",
        "transcript_path": str(root / "transcript.jsonl"),
        "hook_event_name": "UserPromptSubmit",
        "model": "fixture-model",
    }
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "codex_app_user_prompt_hook.py")],
        input=json.dumps(hook_input, ensure_ascii=False),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"user prompt hook fixture failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"user prompt hook must emit JSON, got: {result.stdout}") from exc
    if output.get("continue") is not True:
        raise AssertionError(f"user prompt hook should continue, got {output}")
    hook_specific = output.get("hookSpecificOutput") if isinstance(output.get("hookSpecificOutput"), dict) else {}
    if hook_specific.get("hookEventName") != "UserPromptSubmit" or "additionalContext" not in hook_specific:
        raise AssertionError(f"user prompt hook should emit UserPromptSubmit additionalContext, got {output}")
    if "pipeline_runner.py resolve" not in str(hook_specific.get("additionalContext")):
        raise AssertionError(f"user prompt hook should include LLM task resolve protocol, got {output}")
    if "state-sensitive compact loop header" not in str(hook_specific.get("additionalContext")) or "no human action is needed" not in str(hook_specific.get("additionalContext")):
        raise AssertionError(f"user prompt hook should include user-facing loop header protocol, got {output}")
    if "需要人类做什么" not in str(hook_specific.get("additionalContext")) or "exact one-line reply format" not in str(hook_specific.get("additionalContext")):
        raise AssertionError(f"user prompt hook should include explicit human-action prompt protocol, got {output}")
    ingress = message_ingress(repo)
    messages = ingress.get("messages") if isinstance(ingress.get("messages"), list) else []
    if not any(isinstance(item, dict) and item.get("source") == "codex-app-user-prompt-hook" for item in messages):
        raise AssertionError("expected codex-app-user-prompt-hook message ingress record")
    tasks = pipeline_tasks(repo)
    if not any(task.get("origin") == "message-ingress" and task.get("metadata", {}).get("source") == "codex-app-user-prompt-hook" for task in tasks):
        raise AssertionError("expected codex-app-user-prompt-hook task metadata")


def validate_session_watcher_fixture(root: Path) -> None:
    repo = root / "watcher-repo"
    seed_control_surface(repo)
    sessions = root / "sessions"
    write_session(sessions / "2026/05/04/rollout-fixture.jsonl", repo, "请实现 Codex App loop watcher")
    state = root / "state.json"
    payload = run_json(
        [
            sys.executable,
            str(SCRIPT_DIR / "codex_app_loop.py"),
            "scan",
            "--sessions-dir",
            str(sessions),
            "--state",
            str(state),
            "--max-files",
            "10",
            "--max-events",
            "10",
            "--json",
        ]
    )
    actions = payload.get("actions") if isinstance(payload.get("actions"), list) else []
    if not any(isinstance(action, dict) and action.get("action") == "routed" for action in actions):
        raise AssertionError(f"expected routed action, got {actions}")
    tasks = pipeline_tasks(repo)
    if not any(task.get("origin") == "message-ingress" and task.get("metadata", {}).get("source") == "codex-app-loop" for task in tasks):
        raise AssertionError("expected codex-app-loop task metadata")


def validate_dedupe_fixture(root: Path) -> None:
    repo = root / "dedupe-repo"
    seed_control_surface(repo)
    sessions = root / "dedupe-sessions"
    write_session(sessions / "2026/05/04/rollout-dedupe.jsonl", repo, "请测试 Codex App loop 去重")
    state = root / "dedupe-state.json"
    base_args = [
        sys.executable,
        str(SCRIPT_DIR / "codex_app_loop.py"),
        "scan",
        "--sessions-dir",
        str(sessions),
        "--state",
        str(state),
        "--max-files",
        "10",
        "--max-events",
        "10",
        "--json",
    ]
    first = run_json(base_args)
    second = run_json(base_args)
    if not first.get("actions"):
        raise AssertionError("first scan should process the fixture event")
    if second.get("actions"):
        raise AssertionError(f"second scan should have no new actions, got {second.get('actions')}")


def validate_trusted_project_fixture(root: Path) -> None:
    repo = root / "trusted-repo"
    repo.mkdir(parents=True)
    sessions = root / "trusted-sessions"
    write_session(sessions / "2026/05/04/rollout-trusted.jsonl", repo, "普通项目消息也要进入 loop")
    config = root / "config.toml"
    write(config, f'[projects."{repo}"]\ntrust_level = "trusted"\n')
    payload = run_json(
        [
            sys.executable,
            str(SCRIPT_DIR / "codex_app_loop.py"),
            "scan",
            "--sessions-dir",
            str(sessions),
            "--state",
            str(root / "trusted-state.json"),
            "--config",
            str(config),
            "--max-files",
            "10",
            "--max-events",
            "10",
            "--json",
        ]
    )
    actions = payload.get("actions") if isinstance(payload.get("actions"), list) else []
    if not any(isinstance(action, dict) and action.get("routeReason") == "trusted-project" for action in actions):
        raise AssertionError(f"expected trusted-project route, got {actions}")
    if not (repo / ".codex/message-ingress.json").exists():
        raise AssertionError("trusted project message should create message ingress")


def validate_installer_fixture(root: Path) -> None:
    agents = root / "AGENTS.md"
    hooks = root / "hooks.json"
    config = root / "config.toml"
    plist = root / "LaunchAgents/com.redcreen.project-assistant.codex-app-loop.plist"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_DIR / "install_codex_app_loop.py"),
            "--agents-path",
            str(agents),
            "--hooks-path",
            str(hooks),
            "--config-path",
            str(config),
            "--plist-path",
            str(plist),
            "--skip-baseline",
            "--no-load",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"installer fixture failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    text = agents.read_text(encoding="utf-8")
    if "project-assistant-codex-app-loop:begin" not in text or "message_ingress.py" not in text:
        raise AssertionError("AGENTS prompt block was not installed")
    hooks_payload = json.loads(hooks.read_text(encoding="utf-8"))
    groups = hooks_payload.get("hooks", {}).get("UserPromptSubmit", [])
    if not any("codex_app_user_prompt_hook.py" in json.dumps(group) for group in groups):
        raise AssertionError("UserPromptSubmit hook was not installed")
    if "codex_hooks = true" not in config.read_text(encoding="utf-8"):
        raise AssertionError("features.codex_hooks was not enabled")
    payload = plistlib.loads(plist.read_bytes())
    args = payload.get("ProgramArguments")
    if not isinstance(args, list) or "watch" not in args or str(SCRIPT_DIR / "codex_app_loop.py") not in args:
        raise AssertionError(f"plist does not launch codex_app_loop.py watch: {args}")


def validate_entry_panel_fixture(root: Path) -> None:
    repo = root / "panel-repo"
    seed_control_surface(repo)
    sessions = root / "panel-sessions"
    write_session(sessions / "2026/05/04/rollout-panel.jsonl", repo, "记录一条 app loop 面板消息")
    run_json(
        [
            sys.executable,
            str(SCRIPT_DIR / "codex_app_loop.py"),
            "scan",
            "--sessions-dir",
            str(sessions),
            "--state",
            str(root / "panel-state.json"),
            "--max-files",
            "10",
            "--max-events",
            "10",
            "--json",
        ]
    )
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "continue_entry.py"), str(repo)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"continue_entry.py failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    if "## Codex App Loop" not in result.stdout:
        raise AssertionError("continue entry should include Codex App Loop panel")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Codex Desktop App loop bridge fixtures.")
    parser.add_argument("repo", nargs="?", default=".", help="Unused compatibility arg; fixtures are temporary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    checks = [
        ("user prompt hook fixture", validate_user_prompt_hook_fixture),
        ("session watcher fixture", validate_session_watcher_fixture),
        ("dedupe fixture", validate_dedupe_fixture),
        ("trusted project fixture", validate_trusted_project_fixture),
        ("installer fixture", validate_installer_fixture),
        ("entry panel fixture", validate_entry_panel_fixture),
    ]
    results: list[dict[str, object]] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="project-assistant-codex-app-loop-") as tmp:
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
