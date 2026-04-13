#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import subprocess
import sys
from pathlib import Path


MODE_ALIASES = {
    "bootstrap": {"bootstrap", "start", "启动"},
    "retrofit": {"retrofit", "整改"},
    "docs-retrofit": {"docs-retrofit", "docs retrofit", "文档整改", "文档整理"},
    "continue": {"continue", "resume", "继续", "恢复"},
    "progress": {"progress", "进展"},
    "handoff": {"handoff", "交接", "压缩上下文"},
    "resume-readiness": {"resume-readiness", "readiness", "继续前升级", "升级检查"},
}

BACKEND_SCRIPTS = {
    "bootstrap": "bootstrap_entry.py",
    "retrofit": "retrofit_entry.py",
    "docs-retrofit": "retrofit_entry.py",
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


DEFAULT_BACKEND_ARGS = {
    "docs-retrofit": ("--intent", "docs-retrofit"),
}


def run_backend(script_path: Path, repo: Path, extra_args: list[str]) -> int:
    module = importlib.import_module(script_path.stem)
    backend_main = getattr(module, "main", None)
    if not callable(backend_main):
        result = subprocess.run([sys.executable, str(script_path), str(repo.resolve()), *extra_args])
        return result.returncode
    return int(backend_main([str(repo.resolve()), *extra_args]) or 0)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Canonical project-assistant front door. Route bootstrap/retrofit/continue/progress/handoff through one hard entry."
    )
    parser.add_argument("mode", help="Mode: bootstrap, retrofit, docs-retrofit, continue, progress, handoff, or resume-readiness")
    parser.add_argument("repo", nargs="?", default=".", help="Repository root; defaults to the current working directory")
    args, extra_args = parser.parse_known_args()

    try:
        mode = canonical_mode(args.mode)
    except KeyError:
        choices = ", ".join(sorted(BACKEND_SCRIPTS))
        raise SystemExit(f"unsupported project-assistant mode: {args.mode!r}. supported modes: {choices}")

    scripts_dir = Path(__file__).resolve().parent
    backend = scripts_dir / BACKEND_SCRIPTS[mode]
    return run_backend(backend, Path(args.repo), [*DEFAULT_BACKEND_ARGS.get(mode, ()), *extra_args])


if __name__ == "__main__":
    raise SystemExit(main())
