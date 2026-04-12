#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from control_surface_lib import load_doc_governance_config, match_glob


EN_COMMAND_RE = re.compile(
    r"(?im)(?:^|[`>\-\s])(?:\$project-assistant|project assistant\s+(?:menu|start|continue|resume|progress|retrofit|docs retrofit|devlog|handoff|release))\b"
)
ZH_COMMAND_RE = re.compile(
    r"(?im)(?:^|[`>\-\s])项目助手(?:\s+(?:菜单|启动这个项目|继续|恢复当前状态|进展|整改|文档整改|开发日志|压缩上下文|发布))?"
)

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def actual_path(path: Path) -> Path:
    if not path.exists():
        return path
    for child in path.parent.iterdir():
        if child.name == path.name:
            return child
    lowered = path.name.lower()
    for child in path.parent.iterdir():
        if child.name.lower() == lowered:
            return child
    return path


def append_unique_path(paths: list[Path], candidate: Path) -> None:
    candidate = actual_path(candidate)
    for existing in paths:
        try:
            if existing.samefile(candidate):
                return
        except FileNotFoundError:
            pass
    paths.append(candidate)


def english_public_docs(repo: Path) -> list[Path]:
    governance = load_doc_governance_config(repo)
    include_globs = [str(item) for item in governance.get("publicDocIncludeGlobs", [])]
    exclude_globs = [str(item) for item in governance.get("publicDocExcludeGlobs", [])]
    docs: list[Path] = []
    for path in sorted(repo.rglob("*.md")):
        rel = path.relative_to(repo).as_posix()
        if path.name.endswith(".zh-CN.md"):
            continue
        if include_globs and not any(match_glob(rel, pattern) for pattern in include_globs):
            continue
        if any(match_glob(rel, pattern) for pattern in exclude_globs):
            continue
        append_unique_path(docs, path)
    return docs


def chinese_public_docs(repo: Path) -> list[Path]:
    governance = load_doc_governance_config(repo)
    include_globs = [str(item) for item in governance.get("publicDocIncludeGlobs", [])]
    exclude_globs = [str(item) for item in governance.get("publicDocExcludeGlobs", [])]
    docs: list[Path] = []
    for path in sorted(repo.rglob("*.zh-CN.md")):
        rel = path.relative_to(repo).as_posix()
        base_rel = rel.replace(".zh-CN.md", ".md")
        if include_globs and not any(match_glob(base_rel, pattern) for pattern in include_globs):
            continue
        if any(match_glob(base_rel, pattern) for pattern in exclude_globs):
            continue
        append_unique_path(docs, path)
    return docs


def counterpart(path: Path) -> Path:
    return actual_path(path.with_name(f"{path.stem}.zh-CN{path.suffix}"))


def english_counterpart(path: Path) -> Path:
    return actual_path(path.with_name(path.name.replace(".zh-CN.md", ".md")))


def expected_switch_pair(english: Path, chinese: Path, current: Path) -> str:
    if current == english:
        return f"[English]({english.name}) | [中文]({chinese.name})"
    return f"[English]({english.name}) | [中文]({chinese.name})"


def has_switch_line(text: str, english: Path, chinese: Path) -> bool:
    first_lines = "\n".join(text.splitlines()[:5])
    expected = expected_switch_pair(english, chinese, english)
    return english.name in first_lines and chinese.name in first_lines and "[English]" in first_lines and "[中文]" in first_lines


def command_language_warning(path: Path, text: str, english_doc: bool) -> str | None:
    has_chinese_command = bool(ZH_COMMAND_RE.search(text))
    has_english_command = bool(EN_COMMAND_RE.search(text))
    if english_doc and has_chinese_command and not has_english_command:
        return f"{path} uses Chinese-only command examples in an English public doc"
    if not english_doc and has_english_command and not has_chinese_command:
        return f"{path} uses English-only command examples in a Chinese public doc"
    return None


def mixed_language_structure_warning(path: Path, text: str, english_doc: bool) -> str | None:
    lowered = text.lower()
    if english_doc and ("[中文](#中文)" in lowered or "\n## 中文" in text or "\n### 中文" in text):
        return f"{path} mixes Chinese anchor sections into an English public doc"
    if not english_doc and ("[english](#english)" in lowered or "\n## English" in text or "\n### English" in text):
        return f"{path} mixes English anchor sections into a Chinese public doc"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate switchable bilingual public docs.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    missing: list[str] = []
    warnings: list[str] = []

    for english in english_public_docs(repo):
        chinese = counterpart(english)
        if not chinese.exists():
            missing.append(str(chinese.relative_to(repo)))
            continue

        en_text = read_text(english)
        zh_text = read_text(chinese)
        if not has_switch_line(en_text, english, chinese):
            warnings.append(f"{english.relative_to(repo)} missing language switch line")
        if not has_switch_line(zh_text, english, chinese):
            warnings.append(f"{chinese.relative_to(repo)} missing language switch line")
        en_warning = command_language_warning(english.relative_to(repo), en_text, True)
        zh_warning = command_language_warning(chinese.relative_to(repo), zh_text, False)
        en_mix_warning = mixed_language_structure_warning(english.relative_to(repo), en_text, True)
        zh_mix_warning = mixed_language_structure_warning(chinese.relative_to(repo), zh_text, False)
        if en_warning:
            warnings.append(en_warning)
        if zh_warning:
            warnings.append(zh_warning)
        if en_mix_warning:
            warnings.append(en_mix_warning)
        if zh_mix_warning:
            warnings.append(zh_mix_warning)

    for chinese in chinese_public_docs(repo):
        english = english_counterpart(chinese)
        if not english.exists():
            missing.append(str(english.relative_to(repo)))

    ok = not missing and not warnings
    payload = {"ok": ok, "missing": missing, "warnings": warnings}

    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if missing:
            print("missing:")
            for item in missing:
                print(f"- {item}")
        if warnings:
            print("warnings:")
            for item in warnings:
                print(f"- {item}")
        print(f"ok: {ok}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
