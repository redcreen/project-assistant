#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from control_surface_lib import is_skill_repo


REQUIRED_COMMANDS = {
    "projectAssistant.startDaemon",
    "projectAssistant.stopDaemon",
    "projectAssistant.refresh",
    "projectAssistant.manualContinue",
    "projectAssistant.oneClickContinue",
    "projectAssistant.showProgress",
    "projectAssistant.showHandoff",
    "projectAssistant.resumeCodex",
    "projectAssistant.openRecentCodexSession",
    "projectAssistant.openProgressInTerminal",
    "projectAssistant.openHandoffInTerminal",
    "projectAssistant.openRetrofitInTerminal",
    "projectAssistant.copyStopInstruction",
    "projectAssistant.configureCliPath",
    "projectAssistant.showOutput",
    "projectAssistant.openTaskLog",
}


def validate(repo: Path) -> dict[str, object]:
    repo = repo.resolve()
    if not is_skill_repo(repo):
        return {"ok": True, "repo": str(repo), "skipped": True, "reason": "non-skill repo"}

    extension_dir = repo / "integrations/vscode-host"
    package_path = extension_dir / "package.json"
    extension_js = extension_dir / "extension.js"
    readme_path = extension_dir / "README.md"
    icon_path = extension_dir / "media/project-assistant.svg"

    payload = json.loads(package_path.read_text(encoding="utf-8"))
    commands = {item["command"] for item in payload["contributes"]["commands"]}
    views = payload["contributes"]["views"]["projectAssistant"]
    activation_events = set(payload.get("activationEvents", []))

    missing_commands = sorted(REQUIRED_COMMANDS - commands)
    assert not missing_commands, f"missing commands: {', '.join(missing_commands)}"
    assert extension_js.exists(), "extension.js missing"
    assert readme_path.exists(), "README.md missing"
    assert icon_path.exists(), "icon missing"
    assert any(view["id"] == "projectAssistantQueue" for view in views), "projectAssistantQueue view missing"
    assert "onView:projectAssistantQueue" in activation_events, "queue activation event missing"
    subprocess.run(["node", "--check", str(extension_js)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    return {
        "ok": True,
        "repo": str(repo),
        "extensionDir": str(extension_dir),
        "commands": sorted(commands),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the VS Code host extension package and entrypoint.")
    parser.add_argument("repo", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    result = validate(args.repo)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if result.get("skipped"):
            print(f"ok: True\nskip: {result['reason']}")
        else:
            print(f"extension: {result['extensionDir']}")
            print(f"commands: {len(result['commands'])}")
            print(f"ok: {result['ok']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
