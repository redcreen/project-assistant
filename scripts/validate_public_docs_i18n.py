#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def english_public_docs(repo: Path) -> list[Path]:
    docs: list[Path] = []
    readme = repo / "README.md"
    if readme.exists():
        docs.append(readme)
    docs_dir = repo / "docs"
    if docs_dir.exists():
        for path in sorted(docs_dir.rglob("*.md")):
            if path.name.endswith(".zh-CN.md"):
                continue
            docs.append(path)
    return docs


def counterpart(path: Path) -> Path:
    return path.with_name(f"{path.stem}.zh-CN{path.suffix}")


def expected_switch_pair(english: Path, chinese: Path, current: Path) -> str:
    if current == english:
        return f"[English]({english.name}) | [中文]({chinese.name})"
    return f"[English]({english.name}) | [中文]({chinese.name})"


def has_switch_line(text: str, english: Path, chinese: Path) -> bool:
    first_lines = "\n".join(text.splitlines()[:5])
    expected = expected_switch_pair(english, chinese, english)
    return english.name in first_lines and chinese.name in first_lines and "[English]" in first_lines and "[中文]" in first_lines


def command_language_warning(path: Path, text: str, english_doc: bool) -> str | None:
    has_chinese_command = "项目助手" in text
    has_english_command = "project assistant" in text.lower() or "$project-assistant" in text
    if english_doc and has_chinese_command and not has_english_command:
        return f"{path} uses Chinese-only command examples in an English public doc"
    if not english_doc and has_english_command and not has_chinese_command:
        return f"{path} uses English-only command examples in a Chinese public doc"
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
        if en_warning:
            warnings.append(en_warning)
        if zh_warning:
            warnings.append(zh_warning)

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
