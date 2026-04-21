#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_STATE_PATH = Path.home() / ".openclaw" / "openclaw-codex-app-server" / "state.json"


@dataclass(frozen=True)
class Binding:
    raw: dict[str, Any]

    @property
    def conversation(self) -> dict[str, Any]:
        value = self.raw.get("conversation")
        return value if isinstance(value, dict) else {}

    @property
    def channel(self) -> str:
        return str(self.conversation.get("channel") or "")

    @property
    def account_id(self) -> str:
        return str(self.conversation.get("accountId") or "")

    @property
    def conversation_id(self) -> str:
        return str(self.conversation.get("conversationId") or "")

    @property
    def thread_id(self) -> str:
        return str(self.raw.get("threadId") or "")

    @property
    def thread_title(self) -> str:
        return str(self.raw.get("threadTitle") or "")

    @property
    def workspace_dir(self) -> str:
        return str(self.raw.get("workspaceDir") or "")

    @property
    def updated_at_ms(self) -> int:
        value = self.raw.get("updatedAt")
        if isinstance(value, (int, float)):
            return int(value)
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Resume the Codex thread currently bound in openclaw-codex-app-server. "
            "Use this instead of a fresh terminal session when you want the same "
            "shared thread as Telegram / Codex App / VS Code."
        )
    )
    parser.add_argument(
        "--state-file",
        default=str(DEFAULT_STATE_PATH),
        help=f"Path to openclaw-codex-app-server state.json (default: {DEFAULT_STATE_PATH})",
    )
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List active OpenClaw -> Codex bindings")
    add_selection_flags(list_parser)

    resume_parser = subparsers.add_parser("resume", help="Resume the selected binding in local Codex")
    add_selection_flags(resume_parser)
    resume_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved binding and codex command without executing it",
    )
    resume_parser.add_argument(
        "prompt",
        nargs=argparse.REMAINDER,
        help="Optional prompt appended to `codex resume <threadId> <prompt>`",
    )

    return parser


def add_selection_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--channel", help="Match a binding by channel, for example `telegram`")
    parser.add_argument("--account-id", help="Match a binding by account id")
    parser.add_argument("--conversation-id", help="Match a binding by conversation id")
    parser.add_argument("--thread-id", help="Match a binding by Codex thread id")
    parser.add_argument("--title-contains", help="Match a binding whose thread title contains this text")
    parser.add_argument(
        "--index",
        type=int,
        default=1,
        help="1-based index into the filtered bindings sorted by latest updatedAt first (default: 1)",
    )


def load_bindings(state_file: Path) -> list[Binding]:
    if not state_file.is_file():
        raise SystemExit(f"OpenClaw state file not found: {state_file}")
    try:
        snapshot = json.loads(state_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Failed to parse {state_file}: {exc}") from exc
    bindings_raw = snapshot.get("bindings")
    if not isinstance(bindings_raw, list):
        raise SystemExit(f"Unexpected bindings format in {state_file}")
    bindings = [Binding(entry) for entry in bindings_raw if isinstance(entry, dict)]
    bindings.sort(key=lambda binding: binding.updated_at_ms, reverse=True)
    return bindings


def matches(binding: Binding, args: argparse.Namespace) -> bool:
    if args.channel and binding.channel != args.channel:
        return False
    if args.account_id and binding.account_id != args.account_id:
        return False
    if args.conversation_id and binding.conversation_id != args.conversation_id:
        return False
    if args.thread_id and binding.thread_id != args.thread_id:
        return False
    if args.title_contains and args.title_contains.lower() not in binding.thread_title.lower():
        return False
    return True


def select_binding(bindings: list[Binding], args: argparse.Namespace) -> Binding:
    filtered = [binding for binding in bindings if matches(binding, args)]
    if not filtered:
        raise SystemExit("No matching OpenClaw -> Codex binding found. Run `openclaw-codex list` first.")
    if args.index < 1 or args.index > len(filtered):
        raise SystemExit(
            f"Binding index {args.index} is out of range for {len(filtered)} matching binding(s)."
        )
    return filtered[args.index - 1]


def format_binding(binding: Binding, index: int) -> str:
    updated = (
        datetime.fromtimestamp(binding.updated_at_ms / 1000).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        if binding.updated_at_ms
        else "unknown"
    )
    lines = [
        f"[{index}] {binding.channel or '<none>'}/{binding.account_id or '<none>'}/{binding.conversation_id or '<none>'}",
        f"thread: {binding.thread_id or '<none>'}",
        f"title: {binding.thread_title or '<none>'}",
        f"cwd: {binding.workspace_dir or '<none>'}",
        f"updated: {updated}",
    ]
    return "\n".join(lines)


def run_list(bindings: list[Binding], args: argparse.Namespace) -> int:
    filtered = [binding for binding in bindings if matches(binding, args)]
    if not filtered:
        print("No matching bindings.")
        return 1
    for index, binding in enumerate(filtered, start=1):
        if index > 1:
            print()
        print(format_binding(binding, index))
    return 0


def run_resume(bindings: list[Binding], args: argparse.Namespace) -> int:
    binding = select_binding(bindings, args)
    if not binding.thread_id:
        raise SystemExit("Selected binding has no thread id.")

    prompt_parts = [part for part in args.prompt if part != "--"]
    prompt = " ".join(prompt_parts).strip()
    command = ["codex", "resume", binding.thread_id]
    if prompt:
        command.append(prompt)

    if args.dry_run:
        print(format_binding(binding, 1))
        print()
        print("command:", " ".join(command))
        return 0

    if binding.workspace_dir:
        os.chdir(os.path.expanduser(binding.workspace_dir))
    os.execvp(command[0], command)
    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    command = args.command or "resume"
    state_file = Path(os.path.expanduser(args.state_file)).resolve()
    bindings = load_bindings(state_file)

    if command == "list":
        return run_list(bindings, args)
    if command == "resume":
        return run_resume(bindings, args)

    parser.error(f"Unsupported command: {command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
