#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run(args: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def must_run(args: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    result = run(args, cwd=cwd, env=env)
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        raise AssertionError(f"command failed: {' '.join(args)}\n{detail}")
    return result


def seed_source_repo(root: Path) -> Path:
    source = root / "source"
    source.mkdir(parents=True)
    must_run(["git", "init", "-b", "main"], cwd=source)
    must_run(["git", "config", "user.email", "fixture@example.invalid"], cwd=source)
    must_run(["git", "config", "user.name", "Fixture"], cwd=source)

    write(source / "VERSION", "tag\n")
    write(source / "bin" / "project-assistant", "#!/usr/bin/env bash\nexit 0\n")
    (source / "bin" / "project-assistant").chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    write(source / "install-vscode-tools.sh", "#!/usr/bin/env bash\nexit 0\n")
    write(
        source / "integrations" / "vscode-host" / "package.json",
        json.dumps(
            {
                "name": "project-assistant-host",
                "displayName": "Project Assistant Host",
                "version": "0.0.1",
                "publisher": "redcreen",
                "engines": {"vscode": "^1.100.0"},
                "main": "./extension.js",
            },
            indent=2,
        )
        + "\n",
    )
    write(source / "integrations" / "vscode-host" / "extension.js", "module.exports = {};\n")
    must_run(["git", "add", "."], cwd=source)
    must_run(["git", "commit", "-m", "tag fixture"], cwd=source)
    must_run(["git", "tag", "v1.0.0"], cwd=source)

    must_run(["git", "checkout", "-b", "release-candidate"], cwd=source)
    write(source / "VERSION", "branch\n")
    payload = json.loads((source / "integrations" / "vscode-host" / "package.json").read_text(encoding="utf-8"))
    payload["version"] = "0.0.2"
    write(source / "integrations" / "vscode-host" / "package.json", json.dumps(payload, indent=2) + "\n")
    must_run(["git", "add", "."], cwd=source)
    must_run(["git", "commit", "-m", "branch fixture"], cwd=source)
    must_run(["git", "checkout", "main"], cwd=source)
    return source


def install_env(source: Path, target: Path, bin_dir: Path, ref: str) -> dict[str, str]:
    env = dict(os.environ)
    env.update(
        {
            "PROJECT_ASSISTANT_REPO": str(source),
            "PROJECT_ASSISTANT_REF": ref,
            "PROJECT_ASSISTANT_DIR": str(target),
            "PROJECT_ASSISTANT_BIN_DIR": str(bin_dir),
            "PROJECT_ASSISTANT_AUTO_VSCODE_COMPONENTS": "none",
        }
    )
    return env


def validate_tag_install(root: Path) -> None:
    source = seed_source_repo(root / "tag")
    target = root / "tag-target"
    bin_dir = root / "tag-bin"
    result = must_run(["bash", str(ROOT / "install.sh")], env=install_env(source, target, bin_dir, "v1.0.0"))
    if "Installed to" not in result.stdout:
        raise AssertionError("install.sh did not complete tag install")
    if (target / "VERSION").read_text(encoding="utf-8").strip() != "tag":
        raise AssertionError("tag install did not checkout the requested tag")
    if not (bin_dir / "project-assistant").exists():
        raise AssertionError("tag install did not create CLI symlink")


def validate_branch_install(root: Path) -> None:
    source = seed_source_repo(root / "branch")
    target = root / "branch-target"
    bin_dir = root / "branch-bin"
    must_run(["bash", str(ROOT / "install.sh")], env=install_env(source, target, bin_dir, "release-candidate"))
    if (target / "VERSION").read_text(encoding="utf-8").strip() != "branch":
        raise AssertionError("branch install did not checkout the requested ref")


def validate_vscode_tools_branch_ref(root: Path) -> None:
    source = seed_source_repo(root / "vscode")
    extensions_dir = root / "extensions"
    env = dict(os.environ)
    env.update(
        {
            "PROJECT_ASSISTANT_REPO": str(source),
            "PROJECT_ASSISTANT_REF": "release-candidate",
            "PROJECT_ASSISTANT_VSCODE_EXTENSIONS_DIR": str(extensions_dir),
            "PROJECT_ASSISTANT_VSCODE_COMPONENTS": "project-assistant-host",
        }
    )
    must_run(["bash", str(ROOT / "install-vscode-tools.sh")], env=env)
    installed = extensions_dir / "redcreen.project-assistant-host-0.0.2"
    if not installed.exists():
        raise AssertionError("install-vscode-tools.sh did not install the requested branch package")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate project-assistant install scripts against tag and branch refs.")
    parser.add_argument("repo", nargs="?", default=".", help="Unused compatibility arg; fixtures are temporary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    checks = [
        ("tag install fixture", validate_tag_install),
        ("branch install fixture", validate_branch_install),
        ("vscode tools branch fixture", validate_vscode_tools_branch_ref),
    ]
    results: list[dict[str, object]] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="project-assistant-install-") as tmp:
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
