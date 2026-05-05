#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import stat
from pathlib import Path


MARKER = "project-assistant codex message wrapper"


def default_install_path() -> Path:
    return Path("~/.local/bin/codex").expanduser()


def default_skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_real_codex(install_path: Path) -> Path:
    explicit = os.environ.get("PROJECT_ASSISTANT_CODEX_REAL") or os.environ.get("CODEX_REAL")
    if explicit:
        return Path(explicit).expanduser().resolve()

    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(path_dir) / "codex"
        if not candidate.exists():
            continue
        resolved = candidate.resolve()
        if resolved == install_path.resolve():
            continue
        return resolved

    found = shutil.which("codex")
    if found:
        return Path(found).resolve()
    raise SystemExit("could not locate real codex; set PROJECT_ASSISTANT_CODEX_REAL")


def wrapper_text(skill_dir: Path, real_codex: Path) -> str:
    wrapper = skill_dir / "scripts/codex_message_wrapper.py"
    return f"""#!/usr/bin/env bash
# {MARKER}
set -euo pipefail
export PROJECT_ASSISTANT_DIR={str(skill_dir)!r}
if [[ -z "${{PROJECT_ASSISTANT_CODEX_REAL:-}}" ]]; then
  export PROJECT_ASSISTANT_CODEX_REAL={str(real_codex)!r}
else
  export PROJECT_ASSISTANT_CODEX_REAL
fi
exec python3 {str(wrapper)!r} "$@"
"""


def path_has_precedence(install_path: Path) -> bool:
    path_dirs = [Path(item).expanduser().resolve() for item in os.environ.get("PATH", "").split(os.pathsep) if item]
    install_dir = install_path.parent.expanduser().resolve()
    real_seen = False
    for path_dir in path_dirs:
        candidate = path_dir / "codex"
        if candidate.exists() and candidate.resolve() != install_path.resolve():
            real_seen = True
        if path_dir == install_dir:
            return not real_seen
    return False


def install(install_path: Path, *, skill_dir: Path, real_codex: Path, force: bool, dry_run: bool) -> dict[str, object]:
    install_path = install_path.expanduser()
    existing = install_path.read_text(encoding="utf-8") if install_path.exists() and install_path.is_file() else ""
    if install_path.exists() and MARKER not in existing and not force:
        raise SystemExit(f"refusing to overwrite non-project-assistant wrapper at {install_path}; pass --force")

    content = wrapper_text(skill_dir.resolve(), real_codex.resolve())
    if not dry_run:
        install_path.parent.mkdir(parents=True, exist_ok=True)
        install_path.write_text(content, encoding="utf-8")
        mode = install_path.stat().st_mode
        install_path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return {
        "installed": not dry_run,
        "path": str(install_path),
        "realCodex": str(real_codex),
        "skillDir": str(skill_dir),
        "takesPrecedenceInCurrentPath": path_has_precedence(install_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Install a lightweight codex CLI wrapper that records initial prompts into project-assistant message ingress.")
    parser.add_argument("--install-path", type=Path, default=default_install_path())
    parser.add_argument("--skill-dir", type=Path, default=default_skill_dir())
    parser.add_argument("--real-codex", type=Path)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    real_codex = args.real_codex.expanduser().resolve() if args.real_codex else resolve_real_codex(args.install_path)
    payload = install(args.install_path, skill_dir=args.skill_dir, real_codex=real_codex, force=args.force, dry_run=args.dry_run)
    for key, value in payload.items():
        print(f"{key}: {value}")
    if not payload["takesPrecedenceInCurrentPath"]:
        print(f"note: {args.install_path.parent} is not before the real codex in this shell PATH")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
