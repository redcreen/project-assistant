#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from control_surface_lib import ensure_roadmap_stage_links, load_doc_governance_config, match_glob, slugify
IGNORED_DIRS = {".git", "node_modules", ".obsidian", "__pycache__"}
DURABLE_TOKENS = ("architecture", "roadmap", "policy", "strategy", "blueprint", "design", "workstream")
ARCHIVE_TOKENS = ("todo", "journal", "candidate", "scope", "note", "notes", "scratch", "investigation", "smoke-test", "testsuite")
LEGACY_DOC_BUCKETS = {"architecture", "roadmaps", "blueprints", "testing", "todo"}
CANONICAL_DOC_DIRS = {"adr", "reference", "workstreams", "archive", "how-to", "devlog"}

SKILL_REFERENCE_HOME = """# Reference Pack

[English](README.md) | [中文](README.zh-CN.md)

## Purpose

This directory contains the durable operating references behind the skill.

## Read First

- [../SKILL.md](../SKILL.md)
- [usage.md](usage.md)
- [retrofit.md](retrofit.md)
- [document-standards.md](document-standards.md)
- [governance.md](governance.md)
"""

SKILL_REFERENCE_HOME_ZH = """# 参考资料包

[English](README.md) | [中文](README.zh-CN.md)

## 目的

这个目录存放支撑 skill 的长期参考资料。

## 建议先读

- [../SKILL.md](../SKILL.md)
- [usage.md](usage.md)
- [retrofit.md](retrofit.md)
- [document-standards.md](document-standards.md)
- [governance.md](governance.md)
"""

REFERENCE_HOME = """# Reference Docs

[English](README.md) | [中文](README.zh-CN.md)

## Purpose

This directory contains stable reference material that supports the project but is not part of the primary landing stack.

## Contents

- configuration and policy references
- deeper architecture notes
- durable design references that are too specific for the top-level docs stack
"""

REFERENCE_HOME_ZH = """# 参考文档

[English](README.md) | [中文](README.zh-CN.md)

## 目的

这个目录存放稳定参考资料。它们支持项目理解，但不属于主入口文档栈。

## 内容

- 配置与策略参考
- 更深的架构说明
- 过于细节化、不适合放进顶层主栈的长期设计参考
"""

WORKSTREAMS_HOME = """# Workstreams

[English](README.md) | [中文](README.zh-CN.md)

## Purpose

This directory contains durable workstream documentation that used to be mixed into root docs or reports.

## Workstreams

- [memory-search/README.md](memory-search/README.md)
- [self-learning/README.md](self-learning/README.md)
"""

WORKSTREAMS_HOME_ZH = """# 工作流文档

[English](README.md) | [中文](README.zh-CN.md)

## 目的

这个目录存放长期有效的专项工作流文档，它们以前散落在根目录或 `reports/` 里。

## 工作流

- [memory-search/README.md](memory-search/README.md)
- [self-learning/README.md](self-learning/README.md)
"""

DEVLOG_HOME = """# Development Log

[English](README.md) | [中文](README.zh-CN.md)

## Purpose

This directory records durable implementation narratives: what went wrong, what we considered, what we changed, and how we verified it.

## When To Write Here

- a retrofit or bugfix produced a non-obvious conclusion
- an implementation path changed because of evidence or constraints
- future maintainers would benefit from the reasoning, not only the final diff

## Entry Expectations

- record the problem
- capture the key thinking path
- explain the chosen solution
- note the validation and follow-up

## Entries

- add date-based entries such as `2026-04-12-control-surface-convergence.md`
"""

DEVLOG_HOME_ZH = """# 开发日志

[English](README.md) | [中文](README.zh-CN.md)

## 目的

这个目录记录值得长期保留的实现过程：问题是什么、思考过程是什么、最后怎么解决、又是如何验证的。

## 什么时候写

- 一次整改或 bugfix 产出了非显然结论
- 方案因为证据或约束发生了关键转向
- 未来维护者不仅需要看最终 diff，还需要看推理过程

## 条目要求

- 记录问题
- 记录关键思考路径
- 解释最终方案
- 记录验证与后续动作

## 条目

- 建议按日期命名，例如 `2026-04-12-control-surface-convergence.md`
"""

ARCHIVE_HOME = """# Archive

[English](README.md) | [中文](README.zh-CN.md)

## Purpose

This directory holds superseded, exploratory, or legacy Markdown documents that should remain available for history but no longer act as active docs.
"""

ARCHIVE_HOME_ZH = """# 归档文档

[English](README.md) | [中文](README.zh-CN.md)

## 目的

这个目录存放已被替代、探索性、或历史遗留的 Markdown 文档。它们保留历史价值，但不再作为当前主文档使用。
"""

GENERATED_HOME = """# Generated Reports

This directory contains evidence, audits, evaluations, and generated outputs. These files are not the source of truth for active planning or durable architecture.
"""

SELF_LEARNING_HOME = """# Self-Learning

This workstream groups the durable self-learning architecture and roadmap references.

- [architecture.md](architecture.md)
- [roadmap.md](roadmap.md)
"""

MEMORY_SEARCH_HOME = """# Memory Search

This workstream groups the durable memory-search documents that should not live under `reports/`.

- [architecture.md](architecture.md)
- [roadmap.md](roadmap.md)
- [retrieval-policy.md](retrieval-policy.md)
- [governance.md](governance.md)
- [session-memory-shape-strategy.md](session-memory-shape-strategy.md)
- [next-blueprint.md](next-blueprint.md)
"""

LINK_RE = re.compile(r"(?P<prefix>\[[^\]]+\]\()(?P<target>[^)]+)(?P<suffix>\))")


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content + "\n", encoding="utf-8")
    return True


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def inventory_markdown(repo: Path) -> list[Path]:
    items: list[Path] = []
    for path in repo.rglob("*.md"):
        if any(part in IGNORED_DIRS for part in path.relative_to(repo).parts):
            continue
        items.append(path)
    return sorted(items)


def move_file(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        return False
    shutil.move(str(src), str(dst))
    return True


def relpath(from_dir: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, start=from_dir).replace(os.sep, "/")


def resolved_target(path: Path, target: str) -> Path | None:
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    clean = target.split("#", 1)[0]
    if not clean:
        return None
    return (path.parent / clean).resolve(strict=False)


def is_skill_repo(repo: Path) -> bool:
    return (repo / "SKILL.md").exists() and (repo / "references").exists()


def bootstrap_control_surface(repo: Path) -> None:
    script = Path(__file__).with_name("sync_control_surface.py")
    result = subprocess.run(
        [sys.executable, str(script), str(repo)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def remove_line_block(lines: list[str], start_marker: str, stop_markers: set[str]) -> list[str]:
    cleaned: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if not skipping and stripped == start_marker:
            skipping = True
            continue
        if skipping and stripped in stop_markers:
            skipping = False
        if not skipping:
            cleaned.append(line)
    return cleaned


def ensure_blank_before_heading(text: str, headings: set[str]) -> str:
    lines = text.splitlines()
    normalized: list[str] = []
    for line in lines:
        if line in headings and normalized and normalized[-1].strip():
            normalized.append("")
        normalized.append(line)
    return "\n".join(normalized).rstrip() + "\n"


def governance_link_line(link: str, chinese: bool = False) -> str:
    normalized = link.replace("\\", "/")
    label_map_en = {
        "../SKILL.md": "skill contract",
        "../references/README.md": "reference pack",
        "reference/README.md": "reference docs",
        "workstreams/README.md": "workstreams",
        "archive/README.md": "archive",
        "devlog/README.md": "development log",
    }
    label_map_zh = {
        "../SKILL.md": "skill 合约",
        "../references/README.zh-CN.md": "参考资料包",
        "reference/README.zh-CN.md": "参考文档",
        "workstreams/README.zh-CN.md": "工作流文档",
        "archive/README.zh-CN.md": "归档文档",
        "devlog/README.zh-CN.md": "开发日志",
    }
    label = (label_map_zh if chinese else label_map_en).get(normalized)
    if not label:
        label = Path(normalized).stem.replace(".zh-CN", "").replace("-", " ")
    separator = "：" if chinese else ": "
    return f"- {label}{separator}[{link}]({link})"


def inferred_workstream_parts(name: str) -> tuple[str, str] | None:
    lowered = name.lower().removesuffix(".md")
    for token in DURABLE_TOKENS:
        suffix = f"-{token}"
        if lowered.endswith(suffix):
            prefix = lowered[: -len(suffix)].strip("-")
            if prefix and prefix not in {"docs", "report", "generated", "current", "new"}:
                if token == "workstream":
                    return slugify(prefix), "README.md"
                return slugify(prefix), f"{token}.md"
    return None


def legacy_tree_destination(rel_path: str, skill_repo: bool) -> str | None:
    if skill_repo:
        return None
    path = Path(rel_path)
    parts = path.parts
    if len(parts) < 3 or parts[0] != "docs":
        return None
    legacy_root = parts[1]
    if legacy_root in CANONICAL_DOC_DIRS:
        return None
    third = parts[2]
    tail = parts[3:]
    if third in {"README.md", "README.zh-CN.md"}:
        return f"docs/reference/{legacy_root}/{third}"
    if third in {"todo"}:
        suffix = "/".join(parts[2:])
        return f"docs/archive/{legacy_root}/{suffix}"
    if third in {"architecture", "roadmaps", "blueprints", "testing"}:
        suffix = "/".join(parts[2:])
        return f"docs/reference/{legacy_root}/{suffix}"
    if third.endswith(".md"):
        lowered = third.lower()
        if any(token in lowered for token in ARCHIVE_TOKENS):
            return f"docs/archive/{legacy_root}/{third}"
        return f"docs/reference/{legacy_root}/{third}"
    return None


def infer_destination(rel_path: str, governance: dict, skill_repo: bool) -> str | None:
    path = Path(rel_path)
    name = path.name
    lowered = name.lower()
    root_keep = {str(item) for item in governance.get("rootKeep", [])}
    if rel_path in root_keep:
        return None

    legacy = legacy_tree_destination(rel_path, skill_repo)
    if legacy:
        return legacy

    if path.parts and path.parts[0] == "reports":
        if path.parent.name == "generated" or name == "README.md":
            return None
        workstream = inferred_workstream_parts(name)
        if workstream:
            slug, target_name = workstream
            return f"docs/workstreams/{slug}/{target_name}"
        if any(token in lowered for token in DURABLE_TOKENS):
            return f"docs/reference/{name}"
        return f"reports/generated/{name}"

    if len(path.parts) == 1:
        if any(token in lowered for token in ARCHIVE_TOKENS):
            return f"docs/archive/{name}"
        workstream = inferred_workstream_parts(name)
        if workstream and not skill_repo:
            slug, target_name = workstream
            return f"docs/workstreams/{slug}/{target_name}"
        if any(token in lowered for token in DURABLE_TOKENS):
            return f"docs/reference/{name}"
        if name.endswith(".md") and name not in root_keep:
            return f"docs/archive/{name}"

    return None


def ensure_directory_indexes(root: Path, repo: Path, public: bool) -> list[str]:
    touched: list[str] = []
    if not root.exists():
        return touched
    for subdir in sorted(root.rglob("*")):
        if not subdir.is_dir():
            continue
        if any(part in IGNORED_DIRS for part in subdir.relative_to(repo).parts):
            continue
        readme = subdir / "README.md"
        readme_zh = subdir / "README.zh-CN.md"
        entries = sorted(
            p.name
            for p in subdir.glob("*.md")
            if p.name not in {"README.md", "README.zh-CN.md"}
        )
        if not entries:
            continue
        title = subdir.name.replace("-", " ").title()
        lines = [f"# {title}", "", "[English](README.md) | [中文](README.zh-CN.md)", "", "## Docs", ""]
        lines.extend(f"- [{entry}]({entry})" for entry in entries)
        zh_lines = [f"# {title}", "", "[English](README.md) | [中文](README.zh-CN.md)", "", "## 文档", ""]
        zh_lines.extend(f"- [{entry}]({entry})" for entry in entries)
        if not readme.exists():
            readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
            touched.append(str(readme.relative_to(repo)))
        if public and not readme_zh.exists():
            readme_zh.write_text("\n".join(zh_lines) + "\n", encoding="utf-8")
            touched.append(str(readme_zh.relative_to(repo)))
    return touched


def extract_mixed_bilingual_sections(text: str) -> tuple[str, str, str] | None:
    match = re.search(
        r"(?s)^(.*?)\n## English\s*\n(.*?)\n## (?:中文|Chinese)\s*\n(.*)$",
        text,
    )
    if not match:
        return None
    preamble = match.group(1).strip()
    english_body = match.group(2).strip()
    chinese_body = match.group(3).strip()
    cleaned_lines: list[str] = []
    for line in preamble.splitlines():
        lowered = line.lower()
        if "(#english)" in lowered or "(#中文)" in line or "(#chinese)" in lowered:
            continue
        cleaned_lines.append(line)
    header = "\n".join(cleaned_lines).strip()
    if not english_body or not chinese_body:
        return None
    return header, english_body, chinese_body


def ensure_switch_line(path: Path, english: Path, chinese: Path) -> bool:
    text = read_text(path)
    if not text:
        return False
    first_lines = "\n".join(text.splitlines()[:5])
    if english.name in first_lines and chinese.name in first_lines and "[English]" in first_lines and "[中文]" in first_lines:
        return False
    switch = f"[English]({english.name}) | [中文]({chinese.name})\n\n"
    path.write_text(switch + text.lstrip(), encoding="utf-8")
    return True


def bilingual_groups(repo: Path, governance: dict) -> dict[str, dict[str, Path]]:
    include_globs = [str(item) for item in governance.get("publicDocIncludeGlobs", [])]
    exclude_globs = [str(item) for item in governance.get("publicDocExcludeGlobs", [])]
    groups: dict[str, dict[str, Path]] = {}
    for path in inventory_markdown(repo):
        rel = path.relative_to(repo).as_posix()
        base_rel = rel.replace(".zh-CN.md", ".md") if rel.endswith(".zh-CN.md") else rel
        if include_globs and not any(match_glob(base_rel, pattern) for pattern in include_globs):
            continue
        if any(match_glob(base_rel, pattern) for pattern in exclude_globs):
            continue
        entry = groups.setdefault(base_rel, {})
        entry["zh" if rel.endswith(".zh-CN.md") else "en"] = path
    return groups


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def stub_content(source: Path, target: Path, chinese: bool) -> str:
    source_text = read_text(source)
    title = first_heading(source_text, target.stem.replace(".zh-CN", "").replace("-", " "))
    intro = (
        f"> TODO: 把 [{source.name}]({source.name}) 的事实同步翻译到这个文档。\n"
        if chinese
        else f"> TODO: translate the facts from [{source.name}]({source.name}) into this document.\n"
    )
    source_heading = "## Source of Truth" if not chinese else "## 事实来源"
    source_line = f"- [{source.name}]({source.name})"
    return (
        f"# {title}\n\n"
        f"[English]({target.with_name(target.stem.replace('.zh-CN', '') + target.suffix).name}) | [中文]({target.with_name(target.stem.replace('.zh-CN', '') + '.zh-CN' + target.suffix).name})\n\n"
        f"{intro}\n"
        f"{source_heading}\n\n"
        f"{source_line}\n"
    )


def ensure_public_doc_pairs(repo: Path, governance: dict) -> tuple[list[str], list[str]]:
    created: list[str] = []
    touched: list[str] = []
    for base_rel, pair in bilingual_groups(repo, governance).items():
        en_path = pair.get("en", repo / base_rel)
        zh_path = pair.get("zh", en_path.with_name(f"{en_path.stem}.zh-CN{en_path.suffix}"))
        source_path = pair.get("en") or pair.get("zh")
        if source_path is None:
            continue

        mixed_source = pair.get("en") or pair.get("zh")
        if mixed_source is not None:
            split = extract_mixed_bilingual_sections(read_text(mixed_source))
            if split:
                header, english_body, chinese_body = split
                shared = f"{header}\n\n" if header else ""
                en_text = f"{shared}[English]({en_path.name}) | [中文]({zh_path.name})\n\n{english_body.strip()}\n"
                zh_text = f"{shared}[English]({en_path.name}) | [中文]({zh_path.name})\n\n{chinese_body.strip()}\n"
                if read_text(en_path).rstrip() != en_text.rstrip():
                    en_path.parent.mkdir(parents=True, exist_ok=True)
                    en_path.write_text(en_text, encoding="utf-8")
                    touched.append(str(en_path.relative_to(repo)))
                if read_text(zh_path).rstrip() != zh_text.rstrip():
                    zh_exists = zh_path.exists()
                    zh_path.parent.mkdir(parents=True, exist_ok=True)
                    zh_path.write_text(zh_text, encoding="utf-8")
                    if zh_exists:
                        touched.append(str(zh_path.relative_to(repo)))
                    else:
                        created.append(str(zh_path.relative_to(repo)))

        if not en_path.exists():
            en_path.parent.mkdir(parents=True, exist_ok=True)
            en_path.write_text(stub_content(zh_path, en_path, chinese=False), encoding="utf-8")
            created.append(str(en_path.relative_to(repo)))
        if not zh_path.exists():
            zh_path.parent.mkdir(parents=True, exist_ok=True)
            zh_path.write_text(stub_content(en_path, zh_path, chinese=True), encoding="utf-8")
            created.append(str(zh_path.relative_to(repo)))

        if ensure_switch_line(en_path, en_path, zh_path):
            rel = str(en_path.relative_to(repo))
            if rel not in touched and rel not in created:
                touched.append(rel)
        if ensure_switch_line(zh_path, en_path, zh_path):
            rel = str(zh_path.relative_to(repo))
            if rel not in touched and rel not in created:
                touched.append(rel)
    return created, touched


def rewrite_links(repo: Path, moves: dict[Path, Path]) -> int:
    changed = 0
    for md in inventory_markdown(repo):
        text = md.read_text(encoding="utf-8")
        original = text

        def repl(match: re.Match[str]) -> str:
            target = match.group("target")
            resolved = resolved_target(md, target)
            if resolved is None:
                return match.group(0)
            for old_abs, new_abs in moves.items():
                if resolved == old_abs.resolve(strict=False):
                    new_target = relpath(md.parent, new_abs)
                    return f"{match.group('prefix')}{new_target}{match.group('suffix')}"
            return match.group(0)

        text = LINK_RE.sub(repl, text)
        if text != original:
            md.write_text(text, encoding="utf-8")
            changed += 1
    return changed


def relativize_repo_local_target(doc_path: Path, repo: Path, target: str) -> str | None:
    raw = target.strip()
    wrapped = raw.startswith("<") and raw.endswith(">")
    inner = raw[1:-1] if wrapped else raw
    if inner.startswith("file://"):
        inner = inner[len("file://") :]
    if not inner.startswith("/"):
        return None
    resolved = Path(inner).resolve(strict=False)
    try:
        rel = resolved.relative_to(repo.resolve())
    except ValueError:
        return None
    rewritten = relpath(doc_path.parent, repo / rel)
    if wrapped or " " in rewritten:
        rewritten = f"<{rewritten}>"
    return rewritten


def rewrite_repo_local_links(repo: Path) -> int:
    changed = 0
    repo_resolved = repo.resolve()

    for md in inventory_markdown(repo):
        text = md.read_text(encoding="utf-8")
        original = text

        def link_repl(match: re.Match[str]) -> str:
            target = match.group("target")
            rewritten = relativize_repo_local_target(md, repo_resolved, target)
            if not rewritten:
                return match.group(0)
            return f"{match.group('prefix')}{rewritten}{match.group('suffix')}"

        text = LINK_RE.sub(link_repl, text)

        normalized_lines: list[str] = []
        for line in text.splitlines():
            stripped = line.strip()
            candidate = stripped
            prefix = ""
            suffix = ""

            if stripped.startswith("- "):
                prefix = line[: line.index("- ") + 2]
                candidate = stripped[2:].strip()
            if candidate.startswith("`") and candidate.endswith("`"):
                suffix = "`"
                candidate = candidate[1:-1].strip()
                prefix = prefix + "`"

            if candidate.startswith("file://"):
                candidate = candidate[len("file://") :]

            if candidate.startswith("/"):
                resolved = Path(candidate).resolve(strict=False)
                try:
                    rel = resolved.relative_to(repo_resolved)
                except ValueError:
                    normalized_lines.append(line)
                    continue
                relative = relpath(md.parent, repo / rel)
                normalized_lines.append(f"{prefix}{relative}{suffix}")
            else:
                normalized_lines.append(line)

        text = "\n".join(normalized_lines)
        if original.endswith("\n"):
            text += "\n"

        if text != original:
            md.write_text(text, encoding="utf-8")
            changed += 1

    return changed


def normalize_docs_home(repo: Path, additions: list[str], heading: str) -> bool:
    path = repo / "docs/README.md"
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = remove_line_block(
        lines,
        "- Reference docs: [reference/README.md](reference/README.md)",
        {
            "## Markdown Governance",
            "## Maintainer Resume Boundary",
        },
    )
    lines = remove_line_block(
        lines,
        "- Workstreams: [workstreams/README.md](workstreams/README.md)",
        {
            "## Markdown Governance",
            "## Maintainer Resume Boundary",
        },
    )
    lines = remove_line_block(
        lines,
        "- Archive: [archive/README.md](archive/README.md)",
        {
            "## Markdown Governance",
            "## Maintainer Resume Boundary",
        },
    )
    filtered: list[str] = []
    seen = set()
    for line in lines:
        key = line.strip()
        if key in seen and key.startswith("- "):
            continue
        if key:
            seen.add(key)
        filtered.append(line)

    text = "\n".join(filtered).rstrip() + "\n"
    changed = False
    if heading not in text:
        block = f"\n\n{heading}\n\n" + "\n".join(additions) + "\n"
        marker = "## Maintainer Resume Boundary"
        if marker in text:
            text = text.replace(marker, block + "\n" + marker, 1)
        else:
            text = text.rstrip() + block + "\n"
        changed = True
    else:
        for addition in additions:
            if addition not in text:
                text = text.rstrip() + "\n" + addition + "\n"
                changed = True
    text = ensure_blank_before_heading(text, {"## Markdown Governance", "## Skill References"})
    if changed or text != path.read_text(encoding="utf-8"):
        path.write_text(text, encoding="utf-8")
        return True
    return False


def normalize_docs_home_zh(repo: Path, additions: list[str], heading: str) -> bool:
    path = repo / "docs/README.zh-CN.md"
    if not path.exists():
        return False
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = remove_line_block(
        lines,
        "- 参考文档：[reference/README.zh-CN.md](reference/README.zh-CN.md)",
        {
            "## Markdown 治理",
            "## 维护者恢复边界",
        },
    )
    lines = remove_line_block(
        lines,
        "- 工作流文档：[workstreams/README.zh-CN.md](workstreams/README.zh-CN.md)",
        {
            "## Markdown 治理",
            "## 维护者恢复边界",
        },
    )
    lines = remove_line_block(
        lines,
        "- 归档文档：[archive/README.zh-CN.md](archive/README.zh-CN.md)",
        {
            "## Markdown 治理",
            "## 维护者恢复边界",
        },
    )
    filtered: list[str] = []
    seen = set()
    for line in lines:
        key = line.strip()
        if key in seen and key.startswith("- "):
            continue
        if key:
            seen.add(key)
        filtered.append(line)

    text = "\n".join(filtered).rstrip() + "\n"
    changed = False
    if heading not in text:
        block = f"\n\n{heading}\n\n" + "\n".join(additions) + "\n"
        marker = "## 维护者恢复边界"
        if marker in text:
            text = text.replace(marker, block + "\n" + marker, 1)
        else:
            text = text.rstrip() + block + "\n"
        changed = True
    else:
        for addition in additions:
            if addition not in text:
                text = text.rstrip() + "\n" + addition + "\n"
                changed = True
    text = ensure_blank_before_heading(text, {"## Markdown 治理", "## Skill 参考"})
    if changed or text != path.read_text(encoding="utf-8"):
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Converge the full Markdown tree to a governed structure.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    bootstrap_control_surface(repo)
    skill_repo = is_skill_repo(repo)
    governance = load_doc_governance_config(repo)
    moved: list[str] = []
    created: list[str] = []
    touched: list[str] = []
    moves: dict[Path, Path] = {}

    if skill_repo:
        write_targets = [
            (repo / "references/README.md", SKILL_REFERENCE_HOME),
            (repo / "references/README.zh-CN.md", SKILL_REFERENCE_HOME_ZH),
            (repo / "docs/devlog/README.md", DEVLOG_HOME),
            (repo / "docs/devlog/README.zh-CN.md", DEVLOG_HOME_ZH),
        ]
    else:
        write_targets = [
            (repo / "docs/reference/README.md", REFERENCE_HOME),
            (repo / "docs/reference/README.zh-CN.md", REFERENCE_HOME_ZH),
            (repo / "docs/workstreams/README.md", WORKSTREAMS_HOME),
            (repo / "docs/workstreams/README.zh-CN.md", WORKSTREAMS_HOME_ZH),
            (repo / "docs/archive/README.md", ARCHIVE_HOME),
            (repo / "docs/archive/README.zh-CN.md", ARCHIVE_HOME_ZH),
            (repo / "docs/devlog/README.md", DEVLOG_HOME),
            (repo / "docs/devlog/README.zh-CN.md", DEVLOG_HOME_ZH),
            (repo / "reports/generated/README.md", GENERATED_HOME),
            (repo / "docs/workstreams/self-learning/README.md", SELF_LEARNING_HOME),
            (repo / "docs/workstreams/memory-search/README.md", MEMORY_SEARCH_HOME),
        ]
    for path, content in write_targets:
        if write_if_missing(path, content):
            created.append(str(path.relative_to(repo)))

    explicit_moves: dict[str, str] = {}
    configured_moves = governance.get("explicitMoves", {})
    if isinstance(configured_moves, dict):
        explicit_moves.update({str(k): str(v) for k, v in configured_moves.items()})

    for old_rel, new_rel in explicit_moves.items():
        old_path = repo / old_rel
        new_path = repo / new_rel
        if old_path.exists() and old_path != new_path:
            if not move_file(old_path, new_path):
                continue
            moves[old_path.resolve(strict=False)] = new_path.resolve(strict=False)
            moved.append(f"{old_rel} -> {new_rel}")

    for path in inventory_markdown(repo):
        rel = path.relative_to(repo).as_posix()
        destination = infer_destination(rel, governance, skill_repo)
        if not destination:
            continue
        target = repo / destination
        if path == target or target.exists():
            continue
        if not move_file(path, target):
            continue
        moves[path.resolve(strict=False)] = target.resolve(strict=False)
        moved.append(f"{rel} -> {destination}")

    rewritten = rewrite_links(repo, moves)
    if rewritten:
        touched.append(f"rewrote-links:{rewritten}")
    local_rewritten = rewrite_repo_local_links(repo)
    if local_rewritten:
        touched.append(f"rewrote-local-paths:{local_rewritten}")
    touched.extend(ensure_directory_indexes(repo / "docs/workstreams", repo, public=True))
    touched.extend(ensure_directory_indexes(repo / "docs/reference", repo, public=True))
    touched.extend(ensure_directory_indexes(repo / "docs/archive", repo, public=False))
    pair_created, pair_touched = ensure_public_doc_pairs(repo, governance)
    created.extend(item for item in pair_created if item not in created)
    touched.extend(item for item in pair_touched if item not in touched)
    docs_home_links = governance.get("docsHomeLinks", {})
    en_additions = []
    zh_additions = []
    en_heading = "## Skill References" if skill_repo else "## Markdown Governance"
    zh_heading = "## Skill 参考" if skill_repo else "## Markdown 治理"
    for link in docs_home_links.get("en", []):
        en_additions.append(governance_link_line(str(link), chinese=False))
    for link in docs_home_links.get("zh", []):
        zh_additions.append(governance_link_line(str(link), chinese=True))
    release_en = repo / "RELEASE.md"
    release_zh = repo / "RELEASE.zh-CN.md"
    if release_en.exists():
        en_additions.append(f"- release process: [../{release_en.name}](../{release_en.name})")
        zh_name = release_zh.name if release_zh.exists() else f"{release_en.stem}.zh-CN{release_en.suffix}"
        zh_additions.append(f"- 发布说明：[../{zh_name}](../{zh_name})")
    if normalize_docs_home(repo, en_additions, en_heading):
        touched.append("docs/README.md")
    if normalize_docs_home_zh(repo, zh_additions, zh_heading):
        touched.append("docs/README.zh-CN.md")
    for rel in ensure_roadmap_stage_links(repo):
        if rel not in touched:
            touched.append(rel)

    print(f"moved: {', '.join(moved) if moved else '(none)'}")
    print(f"created: {', '.join(created) if created else '(none)'}")
    print(f"touched: {', '.join(touched) if touched else '(none)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
