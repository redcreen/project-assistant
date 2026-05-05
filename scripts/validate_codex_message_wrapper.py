#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_repo(repo: Path) -> None:
    write(repo / ".codex/brief.md", "# Brief\n")
    write(repo / ".codex/COMMANDS.md", "# Commands\n")
    plan = """# Plan

## Current Phase

`codex wrapper fixture`

## Current Execution Line
- Objective: validate codex message wrapper
- Plan Link: codex-wrapper-fixture
- Progress: 1 / 1 tasks complete

## Architecture Supervision
- Signal: `green`
- Escalation Gate: continue automatically

## Execution Tasks
- [x] EL-1 fixture control task complete
"""
    write(repo / ".codex/plan.md", plan)
    write(repo / ".codex/status.md", plan.replace("# Plan", "# Status"))
    write(
        repo / ".codex/control-surface.json",
        json.dumps(
            {
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
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )


def fake_codex(path: Path, args_file: Path) -> None:
    write(
        path,
        f"""#!/usr/bin/env bash
printf '%s\\n' "$@" > {str(args_file)!r}
exit 0
""",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def run_wrapper(repo: Path, fake: Path, *args: str, disabled: bool = False) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PROJECT_ASSISTANT_CODEX_REAL"] = str(fake)
    env["PROJECT_ASSISTANT_DIR"] = str(SKILL_DIR)
    if disabled:
        env["PROJECT_ASSISTANT_CODEX_WRAPPER_DISABLE"] = "1"
    else:
        env.pop("PROJECT_ASSISTANT_CODEX_WRAPPER_DISABLE", None)
    return subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "codex_message_wrapper.py"), *args],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        check=False,
    )


def read_ingress(repo: Path) -> dict[str, object]:
    return json.loads((repo / ".codex/message-ingress.json").read_text(encoding="utf-8"))


def validate_initial_prompt(root: Path) -> None:
    repo = root / "initial-prompt"
    seed_repo(repo)
    args_file = root / "fake-args.txt"
    fake = root / "fake-codex"
    fake_codex(fake, args_file)
    result = run_wrapper(repo, fake, "--cd", str(repo), "请实现轻量 wrapper")
    if result.returncode != 0:
        raise AssertionError(f"wrapper failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    ingress = read_ingress(repo)
    messages = ingress.get("messages", [])
    if not messages or messages[-1].get("message") != "请实现轻量 wrapper":
        raise AssertionError("initial prompt was not recorded in message ingress")
    if messages[-1].get("source") != "codex-wrapper":
        raise AssertionError("expected codex-wrapper source")
    if not (repo / ".codex/task-pipeline.json").exists():
        raise AssertionError("initial prompt should enqueue into task pipeline")
    if "--cd" not in args_file.read_text(encoding="utf-8"):
        raise AssertionError("wrapper did not forward original arguments to real codex")


def validate_exec_prompt(root: Path) -> None:
    repo = root / "exec-prompt"
    seed_repo(repo)
    args_file = root / "fake-exec-args.txt"
    fake = root / "fake-codex-exec"
    fake_codex(fake, args_file)
    result = run_wrapper(repo, fake, "exec", "--cd", str(repo), "fix failing tests")
    if result.returncode != 0:
        raise AssertionError(f"wrapper exec failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    messages = read_ingress(repo).get("messages", [])
    if not messages or messages[-1].get("message") != "fix failing tests":
        raise AssertionError("exec prompt was not recorded")


def validate_skipped_app_server(root: Path) -> None:
    repo = root / "app-server"
    seed_repo(repo)
    args_file = root / "fake-app-server-args.txt"
    fake = root / "fake-codex-app-server"
    fake_codex(fake, args_file)
    result = run_wrapper(repo, fake, "app-server", "--analytics-default-enabled")
    if result.returncode != 0:
        raise AssertionError(f"wrapper app-server failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    if (repo / ".codex/message-ingress.json").exists():
        raise AssertionError("app-server should not be recorded as a user message")


def validate_disable_flag(root: Path) -> None:
    repo = root / "disabled"
    seed_repo(repo)
    args_file = root / "fake-disabled-args.txt"
    fake = root / "fake-codex-disabled"
    fake_codex(fake, args_file)
    result = run_wrapper(repo, fake, "disabled prompt", disabled=True)
    if result.returncode != 0:
        raise AssertionError(f"wrapper disabled failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    if (repo / ".codex/message-ingress.json").exists():
        raise AssertionError("disable flag should skip message ingress")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the lightweight codex message wrapper.")
    parser.add_argument("repo", nargs="?", default=".", help="Unused compatibility arg; fixtures are temporary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    checks = [
        ("initial prompt fixture", validate_initial_prompt),
        ("exec prompt fixture", validate_exec_prompt),
        ("app-server skip fixture", validate_skipped_app_server),
        ("disable flag fixture", validate_disable_flag),
    ]
    results: list[dict[str, object]] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="project-assistant-codex-wrapper-") as tmp:
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
