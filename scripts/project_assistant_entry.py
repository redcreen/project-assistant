#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


MODE_ALIASES = {
    "continue": {"continue", "resume", "继续", "恢复"},
    "progress": {"progress", "进展"},
    "handoff": {"handoff", "交接", "压缩上下文"},
    "resume-readiness": {"resume-readiness", "readiness", "继续前升级", "升级检查"},
}

BACKEND_SCRIPTS = {
    "continue": "continue_entry.py",
    "progress": "progress_entry.py",
    "handoff": "handoff_entry.py",
    "resume-readiness": "sync_resume_readiness.py",
}


def canonical_mode(raw: str) -> str:
    token = raw.strip().lower()
    for mode, aliases in MODE_ALIASES.items():
        if token in {alias.lower() for alias in aliases}:
            return mode
    raise KeyError(raw)


def run_backend(script_path: Path, repo: Path) -> int:
    result = subprocess.run([sys.executable, str(script_path), str(repo.resolve())])
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canonical project-assistant front door. Route continue/progress/handoff through one hard entry."
    )
    parser.add_argument("mode", help="Mode: continue, progress, handoff, or resume-readiness")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root; defaults to the current working directory")
    args = parser.parse_args()

    try:
        mode = canonical_mode(args.mode)
    except KeyError:
        choices = ", ".join(sorted(BACKEND_SCRIPTS))
        raise SystemExit(f"unsupported project-assistant mode: {args.mode!r}. supported modes: {choices}")

    scripts_dir = Path(__file__).resolve().parent
    backend = scripts_dir / BACKEND_SCRIPTS[mode]
    return run_backend(backend, Path(args.repo))


if __name__ == "__main__":
    raise SystemExit(main())
