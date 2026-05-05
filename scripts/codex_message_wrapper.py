#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


COMMANDS = {
    "exec",
    "e",
    "review",
    "login",
    "logout",
    "mcp",
    "mcp-server",
    "app-server",
    "app",
    "completion",
    "sandbox",
    "debug",
    "apply",
    "a",
    "resume",
    "fork",
    "cloud",
    "features",
    "help",
}

PROMPT_COMMANDS = {"exec", "e", "review"}
SKIP_COMMANDS = {
    "login",
    "logout",
    "mcp",
    "mcp-server",
    "app-server",
    "app",
    "completion",
    "sandbox",
    "debug",
    "apply",
    "a",
    "resume",
    "fork",
    "cloud",
    "features",
    "help",
}

GLOBAL_OPTIONS_WITH_VALUE = {
    "-c",
    "--config",
    "--remote",
    "--remote-auth-token-env",
    "-i",
    "--image",
    "-m",
    "--model",
    "--local-provider",
    "-p",
    "--profile",
    "-s",
    "--sandbox",
    "-a",
    "--ask-for-approval",
    "-C",
    "--cd",
    "--add-dir",
}

SUBCOMMAND_OPTIONS_WITH_VALUE = GLOBAL_OPTIONS_WITH_VALUE | {
    "--output-last-message",
    "--schema",
    "--base",
    "--head",
}

NO_VALUE_OPTIONS = {
    "--help",
    "-h",
    "--version",
    "-V",
    "--oss",
    "--full-auto",
    "--dangerously-bypass-approvals-and-sandbox",
    "--search",
    "--no-alt-screen",
}


def option_takes_value(token: str, options_with_value: set[str]) -> bool:
    if "=" in token:
        return False
    return token in options_with_value


def capture_cd(argv: list[str]) -> Path:
    cwd = Path.cwd()
    idx = 0
    while idx < len(argv):
        token = argv[idx]
        if token in {"-C", "--cd"} and idx + 1 < len(argv):
            return Path(argv[idx + 1]).expanduser().resolve()
        if token.startswith("--cd="):
            return Path(token.split("=", 1)[1]).expanduser().resolve()
        idx += 1
    return cwd.resolve()


def strip_options(argv: list[str], options_with_value: set[str]) -> list[str]:
    remaining: list[str] = []
    idx = 0
    while idx < len(argv):
        token = argv[idx]
        if token == "--":
            remaining.extend(argv[idx + 1 :])
            break
        if token.startswith("-"):
            if option_takes_value(token, options_with_value):
                idx += 2
            else:
                idx += 1
            continue
        remaining.append(token)
        idx += 1
    return remaining


def extract_message(argv: list[str]) -> str | None:
    if not argv or any(token in {"--help", "-h", "--version", "-V"} for token in argv):
        return None

    remaining = strip_options(argv, GLOBAL_OPTIONS_WITH_VALUE)
    if not remaining:
        return None

    first = remaining[0]
    if first in SKIP_COMMANDS:
        return None
    if first in PROMPT_COMMANDS:
        prompt_parts = strip_options(remaining[1:], SUBCOMMAND_OPTIONS_WITH_VALUE)
        return " ".join(prompt_parts).strip() or None
    if first in COMMANDS:
        return None
    return " ".join(remaining).strip() or None


def resolve_real_codex(wrapper_path: Path) -> Path:
    explicit = os.environ.get("PROJECT_ASSISTANT_CODEX_REAL") or os.environ.get("CODEX_REAL")
    if explicit:
        return Path(explicit).expanduser().resolve()

    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(path_dir) / "codex"
        if not candidate.exists():
            continue
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved == wrapper_path.resolve():
            continue
        return resolved

    found = shutil.which("codex")
    if found:
        return Path(found).resolve()
    raise SystemExit("codex wrapper could not locate the real codex binary; set PROJECT_ASSISTANT_CODEX_REAL")


def maybe_ingest(repo: Path, message: str) -> None:
    if os.environ.get("PROJECT_ASSISTANT_CODEX_WRAPPER_DISABLE") == "1":
        return
    if os.environ.get("PROJECT_ASSISTANT_CODEX_WRAPPER_ACTIVE") == "1":
        return

    skill_dir = Path(os.environ.get("PROJECT_ASSISTANT_DIR", "~/.codex/skills/project-assistant")).expanduser()
    entry = skill_dir / "scripts/project_assistant_entry.py"
    if not entry.exists():
        return

    env = dict(os.environ)
    env["PROJECT_ASSISTANT_CODEX_WRAPPER_ACTIVE"] = "1"
    command = [
        sys.executable,
        str(entry),
        "message",
        str(repo),
        "--message",
        message,
        "--source",
        "codex-wrapper",
        "--max-steps",
        "1",
        "--json",
    ]
    debug = os.environ.get("PROJECT_ASSISTANT_CODEX_WRAPPER_DEBUG") == "1"
    result = subprocess.run(
        command,
        stdout=None if debug else subprocess.DEVNULL,
        stderr=None if debug else subprocess.DEVNULL,
        text=True,
        env=env,
        check=False,
    )
    if result.returncode != 0 and os.environ.get("PROJECT_ASSISTANT_CODEX_WRAPPER_STRICT") == "1":
        raise SystemExit(result.returncode)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    wrapper_path = Path(sys.argv[0]).resolve()
    real_codex = resolve_real_codex(wrapper_path)
    message = extract_message(argv)
    if message:
        maybe_ingest(capture_cd(argv), message)
    os.execv(str(real_codex), [str(real_codex), *argv])
    return 127


if __name__ == "__main__":
    raise SystemExit(main())
