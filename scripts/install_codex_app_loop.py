#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import plistlib
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path


LABEL = "com.redcreen.project-assistant.codex-app-loop"
BEGIN_MARKER = "<!-- project-assistant-codex-app-loop:begin -->"
END_MARKER = "<!-- project-assistant-codex-app-loop:end -->"
DEFAULT_AGENTS_PATH = Path.home() / ".codex/AGENTS.md"
DEFAULT_CONFIG_PATH = Path.home() / ".codex/config.toml"
DEFAULT_HOOKS_PATH = Path.home() / ".codex/hooks.json"
DEFAULT_PLIST_PATH = Path.home() / "Library/LaunchAgents" / f"{LABEL}.plist"
DEFAULT_LOG_DIR = Path.home() / ".codex/project-assistant"
HOOK_STATUS = "Project Assistant loop ingress"


AGENTS_BLOCK = f"""{BEGIN_MARKER}
# Project Assistant Loop Front Door

When a user message arrives in a project-assistant context, before doing substantial work:

1. Treat the user message as a task entering the project-assistant loop.
2. If the repository contains `scripts/project_assistant_entry.py`, run:
   `python3 scripts/project_assistant_entry.py message . --message "<user message>" --max-steps 1 --json`
3. If that script is unavailable but `scripts/message_ingress.py` exists, run:
   `python3 scripts/message_ingress.py ingest . --message "<user message>" --max-steps 1 --json`
4. Then execute inside the resulting bounded task and keep going until checkpoint, blocker, human decision, or completion gate.
5. If the task depends on uncertain host/API/plugin/protocol/binary behavior, run the smallest feasibility probe before broad implementation.

This prompt rule is a model-level front door, not a physical transport interceptor. The Codex App session watcher remains the filesystem-level fallback.
{END_MARKER}
"""


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def loop_script() -> Path:
    return Path(__file__).resolve().with_name("codex_app_loop.py")


def user_prompt_hook_script() -> Path:
    return Path(__file__).resolve().with_name("codex_app_user_prompt_hook.py")


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def install_agents_block(path: Path, *, dry_run: bool) -> bool:
    existing = read_text(path)
    if BEGIN_MARKER in existing and END_MARKER in existing:
        before = existing.split(BEGIN_MARKER, 1)[0].rstrip()
        after = existing.split(END_MARKER, 1)[1].lstrip()
        updated = "\n\n".join(part for part in [before, AGENTS_BLOCK.strip(), after] if part).rstrip() + "\n"
    elif existing.strip():
        updated = existing.rstrip() + "\n\n" + AGENTS_BLOCK
    else:
        updated = AGENTS_BLOCK

    changed = updated != existing
    if changed and not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            backup = path.with_suffix(path.suffix + f".bak-{time.strftime('%Y%m%d%H%M%S')}")
            shutil.copy2(path, backup)
        path.write_text(updated, encoding="utf-8")
    return changed


def read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def hook_command() -> str:
    return f"{shlex.quote(sys.executable)} {shlex.quote(str(user_prompt_hook_script()))}"


def project_assistant_hook_group() -> dict[str, object]:
    return {
        "hooks": [
            {
                "type": "command",
                "command": hook_command(),
                "timeoutSec": 10,
                "async": False,
                "statusMessage": HOOK_STATUS,
            }
        ]
    }


def is_project_assistant_hook_group(group: object) -> bool:
    if not isinstance(group, dict):
        return False
    hooks = group.get("hooks")
    if not isinstance(hooks, list):
        return False
    for hook in hooks:
        if not isinstance(hook, dict):
            continue
        command = str(hook.get("command") or "")
        status = str(hook.get("statusMessage") or "")
        if "codex_app_user_prompt_hook.py" in command or status == HOOK_STATUS:
            return True
    return False


def install_user_prompt_hook(path: Path, *, dry_run: bool) -> bool:
    existing = read_json(path)
    updated: dict[str, object] = dict(existing)
    hooks = updated.get("hooks")
    if not isinstance(hooks, dict):
        hooks = {}
    hooks = dict(hooks)
    groups = hooks.get("UserPromptSubmit")
    if not isinstance(groups, list):
        groups = []
    retained = [group for group in groups if not is_project_assistant_hook_group(group)]
    retained.append(project_assistant_hook_group())
    hooks["UserPromptSubmit"] = retained
    updated["hooks"] = hooks

    changed = updated != existing
    if changed and not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            backup = path.with_suffix(path.suffix + f".bak-{time.strftime('%Y%m%d%H%M%S')}")
            shutil.copy2(path, backup)
        path.write_text(json.dumps(updated, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return changed


def codex_hooks_enabled(path: Path) -> bool:
    text = read_text(path)
    in_features = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_features = stripped == "[features]"
            continue
        if not in_features or not stripped.startswith("codex_hooks"):
            continue
        _, _, value = stripped.partition("=")
        return value.strip().lower() == "true"
    return False


def enable_codex_hooks(path: Path, *, dry_run: bool) -> bool:
    existing = read_text(path)
    lines = existing.splitlines()
    out: list[str] = []
    in_features = False
    features_seen = False
    codex_hooks_seen = False
    inserted = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            if in_features and not codex_hooks_seen:
                out.append("codex_hooks = true")
                inserted = True
            in_features = stripped == "[features]"
            features_seen = features_seen or in_features
            codex_hooks_seen = False if in_features else codex_hooks_seen
            out.append(line)
            continue
        if in_features and stripped.startswith("codex_hooks"):
            out.append("codex_hooks = true")
            codex_hooks_seen = True
            continue
        out.append(line)

    if in_features and not codex_hooks_seen:
        out.append("codex_hooks = true")
        inserted = True

    if not features_seen:
        if out and out[-1].strip():
            out.append("")
        out.extend(["[features]", "codex_hooks = true"])
        inserted = True

    updated = "\n".join(out).rstrip() + "\n"
    changed = updated != existing or inserted
    if changed and not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            backup = path.with_suffix(path.suffix + f".bak-{time.strftime('%Y%m%d%H%M%S')}")
            shutil.copy2(path, backup)
        path.write_text(updated, encoding="utf-8")
    return changed


def plist_payload(plist_path: Path, *, interval: float, max_files: int, max_events: int, max_steps: int) -> dict[str, object]:
    log_dir = DEFAULT_LOG_DIR
    state_path = log_dir / "codex-app-loop-state.json"
    return {
        "Label": LABEL,
        "ProgramArguments": [
            sys.executable,
            str(loop_script()),
            "watch",
            "--state",
            str(state_path),
            "--interval",
            str(interval),
            "--max-files",
            str(max_files),
            "--max-events",
            str(max_events),
            "--max-steps",
            str(max_steps),
            "--quiet",
        ],
        "RunAtLoad": True,
        "KeepAlive": True,
        "StandardOutPath": str(log_dir / "codex-app-loop.stdout.log"),
        "StandardErrorPath": str(log_dir / "codex-app-loop.stderr.log"),
        "WorkingDirectory": str(skill_root()),
    }


def install_launch_agent(
    plist_path: Path,
    *,
    interval: float,
    max_files: int,
    max_events: int,
    max_steps: int,
    dry_run: bool,
) -> bool:
    payload = plist_payload(plist_path, interval=interval, max_files=max_files, max_events=max_events, max_steps=max_steps)
    current = plist_path.read_bytes() if plist_path.exists() else b""
    rendered = plistlib.dumps(payload, sort_keys=True)
    changed = current != rendered
    if changed and not dry_run:
        plist_path.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        plist_path.write_bytes(rendered)
    return changed


def run_baseline(*, max_files: int, max_events: int, dry_run: bool) -> int:
    if dry_run:
        return 0
    result = subprocess.run(
        [
            sys.executable,
            str(loop_script()),
            "baseline",
            "--max-files",
            str(max_files),
            "--max-events",
            str(max_events),
        ],
        cwd=skill_root(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return result.returncode


def load_launch_agent(plist_path: Path, *, dry_run: bool, no_load: bool) -> int:
    if dry_run or no_load:
        return 0
    uid = os.getuid()
    subprocess.run(["launchctl", "bootout", f"gui/{uid}", str(plist_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    bootstrap = subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(plist_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    if bootstrap.returncode != 0:
        return bootstrap.returncode
    kickstart = subprocess.run(["launchctl", "kickstart", "-k", f"gui/{uid}/{LABEL}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    return kickstart.returncode


def status(agents_path: Path, plist_path: Path, hooks_path: Path, config_path: Path) -> dict[str, object]:
    agents_text = read_text(agents_path)
    hooks_payload = read_json(hooks_path)
    hook_groups = {}
    if isinstance(hooks_payload.get("hooks"), dict):
        hook_groups = hooks_payload["hooks"]  # type: ignore[assignment]
    user_prompt_groups = hook_groups.get("UserPromptSubmit") if isinstance(hook_groups, dict) else None
    launchctl = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/{LABEL}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
    return {
        "label": LABEL,
        "agentsPath": str(agents_path),
        "agentsBlockInstalled": BEGIN_MARKER in agents_text and END_MARKER in agents_text,
        "configPath": str(config_path),
        "codexHooksEnabled": codex_hooks_enabled(config_path),
        "hooksPath": str(hooks_path),
        "userPromptSubmitHookInstalled": isinstance(user_prompt_groups, list) and any(is_project_assistant_hook_group(group) for group in user_prompt_groups),
        "plistPath": str(plist_path),
        "plistInstalled": plist_path.exists(),
        "launchAgentLoaded": launchctl.returncode == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Codex Desktop App loop bridge for project-assistant.")
    parser.add_argument("--agents-path", type=Path, default=DEFAULT_AGENTS_PATH)
    parser.add_argument("--config-path", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--hooks-path", type=Path, default=DEFAULT_HOOKS_PATH)
    parser.add_argument("--plist-path", type=Path, default=DEFAULT_PLIST_PATH)
    parser.add_argument("--interval", type=float, default=3.0)
    parser.add_argument("--max-files", type=int, default=300)
    parser.add_argument("--max-events", type=int, default=1000)
    parser.add_argument("--max-steps", type=int, default=1)
    parser.add_argument("--skip-hooks", action="store_true")
    parser.add_argument("--skip-baseline", action="store_true")
    parser.add_argument("--no-load", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()

    if args.status:
        print(json.dumps(status(args.agents_path, args.plist_path, args.hooks_path, args.config_path), ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    agents_changed = install_agents_block(args.agents_path, dry_run=args.dry_run)
    hooks_changed = False
    config_changed = False
    if not args.skip_hooks:
        hooks_changed = install_user_prompt_hook(args.hooks_path, dry_run=args.dry_run)
        config_changed = enable_codex_hooks(args.config_path, dry_run=args.dry_run)
    baseline_code = 0 if args.skip_baseline else run_baseline(max_files=args.max_files, max_events=args.max_events, dry_run=args.dry_run)
    plist_changed = install_launch_agent(
        args.plist_path,
        interval=args.interval,
        max_files=args.max_files,
        max_events=args.max_events,
        max_steps=args.max_steps,
        dry_run=args.dry_run,
    )
    load_code = load_launch_agent(args.plist_path, dry_run=args.dry_run, no_load=args.no_load)

    print(f"agents_changed: {agents_changed}")
    print(f"hooks_changed: {hooks_changed}")
    print(f"config_changed: {config_changed}")
    print(f"baseline_ok: {baseline_code == 0}")
    print(f"plist_changed: {plist_changed}")
    print(f"launch_loaded: {load_code == 0 and not args.no_load and not args.dry_run}")
    print(f"status: {status(args.agents_path, args.plist_path, args.hooks_path, args.config_path)}")
    return 0 if baseline_code == 0 and load_code == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
