#!/usr/bin/env python3
from __future__ import annotations

import argparse
import plistlib
import subprocess
import sys
from pathlib import Path

from nightly_project_audit import DEFAULT_CONFIG_PATH, ROOT, default_config


LAUNCH_AGENT_LABEL = "ai.redcreen.project-assistant.nightly-audit"


def write_default_config(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(__import__("json").dumps(default_config(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def launch_agent_path() -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{LAUNCH_AGENT_LABEL}.plist"


def build_plist(config_path: Path, hour: int, minute: int, log_dir: Path) -> dict:
    python = sys.executable
    return {
        "Label": LAUNCH_AGENT_LABEL,
        "ProgramArguments": [
            python,
            str(ROOT / "scripts" / "nightly_project_audit.py"),
            "--config",
            str(config_path),
        ],
        "WorkingDirectory": str(ROOT),
        "RunAtLoad": True,
        "StartCalendarInterval": {
            "Hour": hour,
            "Minute": minute,
        },
        "StandardOutPath": str(log_dir / "launchd.stdout.log"),
        "StandardErrorPath": str(log_dir / "launchd.stderr.log"),
    }


def launchctl(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["launchctl", *args], text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the nightly project-assistant audit as a macOS launch agent.")
    parser.add_argument("--hour", type=int, default=23)
    parser.add_argument("--minute", type=int, default=30)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()

    config_path = args.config.expanduser().resolve()
    write_default_config(config_path)

    agent_path = launch_agent_path()
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    log_dir = config_path.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    with agent_path.open("wb") as handle:
        plistlib.dump(build_plist(config_path, args.hour, args.minute, log_dir), handle, sort_keys=False)

    uid = str(__import__("os").getuid())
    domain = f"gui/{uid}"
    launchctl("bootout", domain, str(agent_path))
    bootstrap = launchctl("bootstrap", domain, str(agent_path))
    if bootstrap.returncode != 0:
        raise SystemExit(bootstrap.stderr.strip() or bootstrap.stdout.strip() or "launchctl bootstrap failed")
    launchctl("enable", f"{domain}/{LAUNCH_AGENT_LABEL}")
    kickstart = launchctl("kickstart", "-k", f"{domain}/{LAUNCH_AGENT_LABEL}")
    if kickstart.returncode != 0:
        raise SystemExit(kickstart.stderr.strip() or kickstart.stdout.strip() or "launchctl kickstart failed")

    print(agent_path)
    print(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
