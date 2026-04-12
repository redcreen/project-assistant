#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from control_surface_lib import primary_human_windows, repo_capabilities


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize which project-assistant capabilities are currently usable in a repo.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    capabilities = repo_capabilities(repo)
    windows = primary_human_windows("zh")
    payload = {
        "ok": True,
        "capabilities": [{"id": key, "label": label} for key, label in capabilities],
        "human_windows": windows,
    }
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if capabilities:
            print("usable now:")
            for _, label in capabilities:
                print(f"- {label}")
        else:
            print("usable now:")
            print("- no explicit project-assistant capabilities detected yet")
        print("human windows:")
        for item in windows:
            print(f"- {item}")
        print("ok: True")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
