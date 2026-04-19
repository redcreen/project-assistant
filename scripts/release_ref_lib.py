#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


RAW_INSTALL_URL_RE = re.compile(
    r"https://raw\.githubusercontent\.com/redcreen/project-assistant/v(?P<version>\d+\.\d+\.\d+)/(?P<script>install(?:-vscode-tools)?\.sh)"
)
CLONE_BRANCH_RE = re.compile(
    r"git clone --branch v(?P<version>\d+\.\d+\.\d+) https://github\.com/redcreen/project-assistant\.git"
)
ENV_REF_RE = re.compile(r"PROJECT_ASSISTANT_REF=v(?P<version>\d+\.\d+\.\d+)")
DEFAULT_REF_RE = re.compile(r"PROJECT_ASSISTANT_REF:-v(?P<version>\d+\.\d+\.\d+)")


def release_ref_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".sh"} and path.name not in {"install.sh", "install-vscode-tools.sh"}:
            continue
        files.append(path)
    return sorted(set(files))


def rewrite_release_refs(text: str, version: str) -> str:
    tag = f"v{version}"
    updated = RAW_INSTALL_URL_RE.sub(
        lambda match: f"https://raw.githubusercontent.com/redcreen/project-assistant/{tag}/{match.group('script')}",
        text,
    )
    updated = CLONE_BRANCH_RE.sub(
        f"git clone --branch {tag} https://github.com/redcreen/project-assistant.git",
        updated,
    )
    updated = ENV_REF_RE.sub(f"PROJECT_ASSISTANT_REF={tag}", updated)
    updated = DEFAULT_REF_RE.sub(f"PROJECT_ASSISTANT_REF:-{tag}", updated)
    return updated


def update_release_refs(root: Path, version: str) -> list[Path]:
    touched: list[Path] = []
    for path in release_ref_files(root):
        original = path.read_text(encoding="utf-8")
        updated = rewrite_release_refs(original, version)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            touched.append(path)
    return touched


def validate_release_refs(root: Path, version: str) -> list[str]:
    warnings: list[str] = []
    expected_tag = f"v{version}"
    patterns = [
        ("raw install link", RAW_INSTALL_URL_RE),
        ("clone branch", CLONE_BRANCH_RE),
        ("environment ref", ENV_REF_RE),
        ("default install ref", DEFAULT_REF_RE),
    ]
    for path in release_ref_files(root):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        for label, pattern in patterns:
            for match in pattern.finditer(text):
                actual_tag = f"v{match.group('version')}"
                if actual_tag != expected_tag:
                    warnings.append(f"{rel} has stale {label}: expected {expected_tag}, found {actual_tag}")
    return warnings
