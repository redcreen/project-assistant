#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from control_surface_lib import (
    CONTROL_SURFACE_COMPONENT_PATHS,
    control_surface_required_files,
    control_surface_version_state,
    ensure_roadmap_stage_links,
    parse_tier,
    read_text,
    relative_markdown_target,
    slugify,
    unwrap_markdown_label,
)


README_TEMPLATE = """# {project_name}

[English](README.md) | [中文](README.zh-CN.md)

> One-line value proposition.

## Who This Is For

## Quick Start

## Core Capabilities

## Common Workflows

## Documentation Map
- [Docs Home](docs/README.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Test Plan](docs/test-plan.md)

## Development

## License
"""


README_ZH_TEMPLATE = """# {project_name}

[English](README.md) | [中文](README.zh-CN.md)

> 一句话说明这个项目解决什么问题。

## 适用对象

## 快速开始

## 核心能力

## 常见工作流

## 文档导航
- [文档首页](docs/README.zh-CN.md)
- [架构](docs/architecture.zh-CN.md)
- [路线图](docs/roadmap.zh-CN.md)
- [测试计划](docs/test-plan.zh-CN.md)

## 开发

## 许可
"""


DOCS_HOME_TEMPLATE = """# Docs Home

[English](README.md) | [中文](README.zh-CN.md)

## Start Here
- Getting started: [README](../README.md)
- Testing: [test-plan.md](test-plan.md)

## By Goal
| Goal | Read This |
| --- | --- |
| Try the project quickly | [README](../README.md) |
| Verify correctness | [test-plan.md](test-plan.md) |
"""


DOCS_HOME_ZH_TEMPLATE = """# 文档首页

[English](README.md) | [中文](README.zh-CN.md)

## 从这里开始
- 快速了解项目：[README](../README.zh-CN.md)
- 测试：[test-plan.zh-CN.md](test-plan.zh-CN.md)

## 按目标阅读
| 目标 | 阅读这里 |
| --- | --- |
| 快速试用项目 | [README](../README.zh-CN.md) |
| 了解验证方式 | [test-plan.zh-CN.md](test-plan.zh-CN.md) |
"""


ARCHITECTURE_TEMPLATE = """# Architecture

[English](architecture.md) | [中文](architecture.zh-CN.md)

## Purpose and Scope

## System Context

```mermaid
flowchart TB
```

## Module Inventory
| Module | Responsibility | Key Interfaces |
| --- | --- | --- |

## Core Flow

```mermaid
flowchart LR
```

## Interfaces and Contracts

## State and Data Model

## Operational Concerns

## Tradeoffs and Non-Goals

## Related ADRs
"""


ARCHITECTURE_ZH_TEMPLATE = """# 架构

[English](architecture.md) | [中文](architecture.zh-CN.md)

## 目的与范围

## 系统上下文

```mermaid
flowchart TB
```

## 模块清单
| 模块 | 职责 | 关键接口 |
| --- | --- | --- |

## 核心流程

```mermaid
flowchart LR
```

## 接口与契约

## 状态与数据模型

## 运维关注点

## 取舍与非目标

## 相关 ADR
"""


ROADMAP_TEMPLATE = """# Roadmap

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## Scope

## Now / Next / Later
| Horizon | Focus | Exit Signal |
| --- | --- | --- |
| Now | | |
| Next | | |
| Later | | |

## Milestone Rules

- one milestone = one clear theme-level goal
- `done` means the milestone is actually complete
- do not split the same work theme across multiple top-level milestones
- put sub-steps in the development plan, not in overlapping roadmap rows

## Milestones
| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |

## Milestone Flow

```mermaid
flowchart LR
```

## Risks and Dependencies
"""


ROADMAP_ZH_TEMPLATE = """# 路线图

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## 范围

## 当前 / 下一步 / 更后面
| 时间层级 | 重点 | 退出信号 |
| --- | --- | --- |
| 当前 | | |
| 下一步 | | |
| 更后面 | | |

## 里程碑规则

- 一个里程碑只对应一个清晰的主题目标
- 标成 `done` / `已完成` 就表示这一项真的已经完整完成
- 不要把同一条工作主题拆到多个顶层里程碑里
- 细分步骤放进 development plan，不要塞进彼此重叠的 roadmap 顶层行

## 里程碑
| 里程碑 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |

## 里程碑流转

```mermaid
flowchart LR
```

## 风险与依赖
"""


TEST_PLAN_TEMPLATE = """# Test Plan

[English](test-plan.md) | [中文](test-plan.zh-CN.md)

## Scope and Risk

## Acceptance Cases
| Case | Setup | Action | Expected Result |
| --- | --- | --- | --- |

## Automation Coverage

## Manual Checks

## Test Data and Fixtures

## Release Gate
"""


TEST_PLAN_ZH_TEMPLATE = """# 测试计划

[English](test-plan.md) | [中文](test-plan.zh-CN.md)

## 范围与风险

## 验收用例
| 用例 | 前置条件 | 操作 | 预期结果 |
| --- | --- | --- | --- |

## 自动化覆盖

## 手工检查

## 测试数据与夹具

## 发布门禁
"""


ADR_TEMPLATE = """# ADR 0001: Title

[English](0001-template.md) | [中文](0001-template.zh-CN.md)

## Status

## Context

## Decision

## Consequences

## Alternatives Considered
"""


ADR_ZH_TEMPLATE = """# ADR 0001：标题

[English](0001-template.md) | [中文](0001-template.zh-CN.md)

## 状态

## 背景

## 决策

## 结果与影响

## 备选方案
"""


ADR_INDEX_TEMPLATE = """# ADR

[English](README.md) | [中文](README.zh-CN.md)

This directory records durable architecture and governance decisions.
"""


ADR_INDEX_ZH_TEMPLATE = """# ADR

[English](README.md) | [中文](README.zh-CN.md)

这里记录持久化的架构与治理决策。
"""


PROJECT_REFERENCE_HOME_TEMPLATE = """# {project_name} Reference Pack

[English](README.md) | [中文](README.zh-CN.md)

## Purpose

This directory holds the durable maintainer-facing reference stack that sits below `docs/roadmap.md` and above live control-surface notes.

## Read Here

- [development-plan.md](development-plan.md): detailed execution queue and milestone drill-down
"""


PROJECT_REFERENCE_HOME_ZH_TEMPLATE = """# {project_name} 参考资料包

[English](README.md) | [中文](README.zh-CN.md)

## 目的

这个目录存放给维护者看的长期参考资料，位置在 `docs/roadmap.md` 之下、`.codex/*` 控制面之上。

## 建议从这里读

- [development-plan.zh-CN.md](development-plan.zh-CN.md)：详细执行队列与里程碑下钻入口
"""


def ensure_bilingual_pair(en_path: Path, zh_path: Path, en_template: str, zh_template: str, created: list[str], touched: list[str], repo: Path) -> None:
    if ensure_file(en_path, en_template):
        created.append(str(en_path.relative_to(repo)))
    if ensure_file(zh_path, zh_template):
        created.append(str(zh_path.relative_to(repo)))
    if ensure_switch_line(en_path, en_path, zh_path) and str(en_path.relative_to(repo)) not in touched:
        touched.append(str(en_path.relative_to(repo)))
    if ensure_switch_line(zh_path, en_path, zh_path) and str(zh_path.relative_to(repo)) not in touched:
        touched.append(str(zh_path.relative_to(repo)))


def project_name(repo: Path) -> str:
    package_json = repo / "package.json"
    if package_json.exists():
        try:
            payload = json.loads(package_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        name = payload.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    return repo.name


def project_doc_slug(repo: Path) -> str:
    slug = slugify(project_name(repo))
    if slug:
        return slug
    fallback = re.sub(r"[^a-z0-9]+", "-", repo.name.lower()).strip("-")
    return fallback or "project"


def first_existing(repo: Path, names: list[str]) -> Path | None:
    for name in names:
        path = repo / name
        if path.exists():
            return path
    return None


def ensure_file(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


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


def scaffold_like(text: str) -> bool:
    markers = [
        "One-line value proposition.",
        "一句话说明这个项目解决什么问题。",
        "## Core Capabilities",
        "## 核心能力",
        "## Common Workflows",
        "## 常见工作流",
    ]
    return any(marker in text for marker in markers)


def normalize_split_bilingual_doc(en_path: Path, zh_path: Path, touched: list[str], created: list[str], repo: Path) -> None:
    en_text = read_text(en_path)
    if not en_text:
        return
    split = extract_mixed_bilingual_sections(en_text)
    if not split:
        return

    header, english_body, chinese_body = split
    if header:
        english_text = f"{header}\n\n[English]({en_path.name}) | [中文]({zh_path.name})\n\n{english_body.strip()}\n"
        chinese_text = f"{header}\n\n[English]({en_path.name}) | [中文]({zh_path.name})\n\n{chinese_body.strip()}\n"
    else:
        english_text = f"[English]({en_path.name}) | [中文]({zh_path.name})\n\n{english_body.strip()}\n"
        chinese_text = f"[English]({en_path.name}) | [中文]({zh_path.name})\n\n{chinese_body.strip()}\n"

    if en_text.rstrip() != english_text.rstrip():
        en_path.write_text(english_text, encoding="utf-8")
        rel = str(en_path.relative_to(repo))
        if rel not in touched:
            touched.append(rel)

    zh_exists = zh_path.exists()
    zh_text = read_text(zh_path)
    if not zh_exists or not zh_text.strip() or scaffold_like(zh_text):
        zh_path.parent.mkdir(parents=True, exist_ok=True)
        zh_path.write_text(chinese_text, encoding="utf-8")
        rel = str(zh_path.relative_to(repo))
        if zh_exists:
            if rel not in touched:
                touched.append(rel)
        else:
            created.append(rel)


def replace_when_stale(path: Path, content: str, markers: list[str]) -> bool:
    text = read_text(path)
    if not text:
        return False
    if not all(marker in text for marker in markers):
        return False
    normalized = content
    if text.rstrip() == normalized.rstrip():
        return False
    path.write_text(normalized, encoding="utf-8")
    return True


def replace_if_scaffold(path: Path, scaffolds: list[str], content: str) -> bool:
    text = read_text(path)
    if not text:
        return False
    normalized = text.rstrip()
    known = {item.rstrip() for item in scaffolds}
    if normalized not in known:
        return False
    if normalized == content.rstrip():
        return False
    path.write_text(content, encoding="utf-8")
    return True


def append_doc_map_if_missing(readme_path: Path) -> bool:
    text = read_text(readme_path)
    if not text:
        return False
    if "## Documentation Map" in text or "## Docs" in text:
        return False
    addition = """

## Documentation Map
- [Docs Home](docs/README.md)
- [Test Plan](docs/test-plan.md)
"""
    readme_path.write_text(text.rstrip() + addition + "\n", encoding="utf-8")
    return True


def append_quick_start_if_missing(readme_path: Path) -> bool:
    text = read_text(readme_path)
    if not text or "## Quick Start" in text:
        return False
    addition = """

## Quick Start

See [docs/README.md](docs/README.md) for the full documentation map.
"""
    readme_path.write_text(text.rstrip() + addition + "\n", encoding="utf-8")
    return True


def append_unique_lines(path: Path, lines: list[str]) -> bool:
    text = read_text(path)
    if not text:
        return False
    additions = [line for line in lines if line not in text]
    if not additions:
        return False
    path.write_text(text.rstrip() + "\n" + "\n".join(additions) + "\n", encoding="utf-8")
    return True


def section_body(text: str, headings: list[str]) -> str:
    pattern = "|".join(re.escape(heading) for heading in headings)
    match = re.search(rf"(?ms)^## (?:{pattern})\n(.*?)(?=^## |\Z)", text)
    return match.group(1).strip() if match else ""


def replace_section(text: str, headings: list[str], body: str) -> str:
    pattern = "|".join(re.escape(heading) for heading in headings)
    match = re.search(rf"(?ms)^(## (?:{pattern})\n)(.*?)(?=^## |\Z)", text)
    rendered = body.rstrip()
    if match:
        start, end = match.span()
        return text[:start] + match.group(1) + rendered + "\n\n" + text[end:]
    heading = headings[0]
    return text.rstrip() + f"\n\n## {heading}\n{rendered}\n"


def ensure_section_before(text: str, heading: str, body: str, before_headings: list[str]) -> str:
    rendered = f"## {heading}\n{body.rstrip()}\n\n"
    existing = re.search(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", text)
    if existing:
        updated = text[: existing.start()] + text[existing.end():]
    else:
        updated = text
    insert_at = len(updated)
    for candidate in before_headings:
        marker = f"## {candidate}"
        pos = updated.find(marker)
        if pos != -1:
            insert_at = min(insert_at, pos)
    if insert_at == len(updated):
        return updated.rstrip() + "\n\n" + rendered.rstrip() + "\n"
    prefix = updated[:insert_at].rstrip() + "\n\n"
    suffix = updated[insert_at:].lstrip()
    return prefix + rendered + suffix


def parse_roadmap_milestones(text: str, chinese: bool) -> list[dict[str, str]]:
    body = section_body(text, ["Milestones"] if not chinese else ["里程碑"])
    rows: list[dict[str, str]] = []

    def strip_embedded_markdown_links(value: str) -> str:
        return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value).strip()

    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 5:
            continue
        if cells[0] in {"Milestone", "里程碑", "---"}:
            continue
        rows.append(
            {
                "label": strip_embedded_markdown_links(unwrap_markdown_label(cells[0])),
                "status": cells[1],
                "goal": cells[2],
                "depends": strip_embedded_markdown_links(unwrap_markdown_label(cells[3])),
                "exit": cells[4],
            }
        )
    return rows


def parse_current_phase(plan_text: str) -> str:
    body = section_body(plan_text, ["Current Phase"])
    return body.replace("\n", " ").strip() if body else "n/a"


def parse_current_execution_fields(plan_text: str) -> dict[str, str]:
    body = section_body(plan_text, ["Current Execution Line"])
    fields = {
        "objective": "n/a",
        "plan_link": "n/a",
        "progress": "n/a",
        "validation": "n/a",
        "stop_conditions": "n/a",
    }
    if not body:
        return fields
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Objective:"):
            fields["objective"] = stripped.split(":", 1)[1].strip().strip("`")
        elif stripped.startswith("- Plan Link:"):
            fields["plan_link"] = stripped.split(":", 1)[1].strip().strip("`")
        elif stripped.startswith("- Progress:"):
            fields["progress"] = stripped.split(":", 1)[1].strip().strip("`")
        elif stripped.startswith("- Validation:"):
            fields["validation"] = stripped.split(":", 1)[1].strip().strip("`")
        elif stripped.startswith("- Stop Conditions:"):
            fields["stop_conditions"] = stripped.split(":", 1)[1].strip().strip("`")
    return fields


def parse_open_execution_tasks(plan_text: str) -> list[str]:
    body = section_body(plan_text, ["Execution Tasks"])
    if not body:
        return []
    tasks: list[str] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ] "):
            tasks.append(stripped[6:].strip().strip("`"))
    return tasks


def parse_execution_tasks(plan_text: str) -> list[dict[str, str]]:
    body = section_body(plan_text, ["Execution Tasks"])
    if not body:
        return []
    tasks: list[dict[str, str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [x] "):
            tasks.append({"status": "done", "label": stripped[6:].strip().strip("`")})
        elif stripped.startswith("- [ ] "):
            tasks.append({"status": "open", "label": stripped[6:].strip().strip("`")})
    return tasks


def parse_slices(plan_text: str) -> list[dict[str, str]]:
    body = section_body(plan_text, ["Slices"])
    if not body:
        return []
    blocks = re.split(r"\n(?=- Slice: )", body.strip())
    slices: list[dict[str, str]] = []
    for block in blocks:
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines or not lines[0].strip().startswith("- Slice:"):
            continue
        item: dict[str, str] = {"name": lines[0].split(":", 1)[1].strip().strip("`")}
        for line in lines[1:]:
            stripped = line.strip()
            if ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            normalized_key = key.lstrip("- ").strip().lower().replace(" ", "_").replace("-", "_")
            item[normalized_key] = value.strip().strip("`")
        slices.append(item)
    return slices


def render_milestone_overview_table(rows: list[dict[str, str]], chinese: bool) -> str:
    header = "| 阶段 | 状态 | 目标 | 依赖 | 退出条件 |\n| --- | --- | --- | --- | --- |" if chinese else "| Milestone | Status | Goal | Depends On | Exit Criteria |\n| --- | --- | --- | --- | --- |"
    lines = [header]
    for row in rows:
        lines.append(
            f"| {escape_table_cell(row['label'])} | {escape_table_cell(row['status'])} | {escape_table_cell(row['goal'])} | {escape_table_cell(row['depends'])} | {escape_table_cell(row['exit'])} |"
        )
    return "\n".join(lines)


def escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_milestone_details(rows: list[dict[str, str]], chinese: bool) -> str:
    sections: list[str] = []
    for row in rows:
        if chinese:
            table = "\n".join(
                [
                    "| 项目 | 当前值 |",
                    "| --- | --- |",
                    f"| 当前状态 | {row['status']} |",
                    f"| 目标 | {row['goal']} |",
                    f"| 依赖 | {row['depends']} |",
                    f"| 退出条件 | {row['exit']} |",
                ]
            )
        else:
            table = "\n".join(
                [
                    "| Item | Current Value |",
                    "| --- | --- |",
                    f"| Status | {row['status']} |",
                    f"| Goal | {row['goal']} |",
                    f"| Depends On | {row['depends']} |",
                    f"| Exit Criteria | {row['exit']} |",
                ]
            )
        sections.append(f"### {row['label']}\n\n{table}")
    return "\n\n".join(sections)


def render_slice_queue(slices: list[dict[str, str]], current_plan_link: str, current_progress: str, chinese: bool) -> str:
    if chinese:
        lines = ["| 顺序 | 切片 | 当前状态 | 目标 | 验证 |", "| --- | --- | --- | --- | --- |"]
    else:
        lines = ["| Order | Slice | Status | Objective | Validation |", "| --- | --- | --- | --- | --- |"]
    current_index = next((idx for idx, item in enumerate(slices) if item.get("name") == current_plan_link), None)
    current_done = False
    match = re.match(r"(\d+)\s*/\s*(\d+)", current_progress)
    if match:
        current_done = match.group(1) == match.group(2)
    for index, item in enumerate(slices, start=1):
        if current_index is None:
            status = "recorded" if not chinese else "已记录"
        elif index - 1 < current_index:
            status = "earlier slice" if not chinese else "较早切片"
        elif index - 1 == current_index:
            status = ("just completed" if current_done else "current") if not chinese else ("刚完成" if current_done else "当前")
        else:
            status = "next / queued" if not chinese else "下一步 / 已排队"
        lines.append(
            f"| {index} | `{escape_table_cell(item.get('name', 'n/a'))}` | {escape_table_cell(status)} | {escape_table_cell(item.get('objective', 'n/a'))} | {escape_table_cell(item.get('validation', 'n/a'))} |"
        )
    return "\n".join(lines)


def human_progress_counts(progress: str) -> tuple[str, str]:
    match = re.match(r"(\d+)\s*/\s*(\d+)", progress)
    if not match:
        return ("n/a", "n/a")
    return match.group(1), match.group(2)


def active_slice(slices: list[dict[str, str]], plan_link: str) -> dict[str, str] | None:
    return next((item for item in slices if item.get("name") == plan_link), None)


def render_execution_task_board(tasks: list[dict[str, str]], chinese: bool) -> str:
    if chinese:
        lines = ["| 顺序 | 任务 | 状态 |", "| --- | --- | --- |"]
        status_map = {"done": "已完成", "open": "下一步"}
    else:
        lines = ["| Order | Task | Status |", "| --- | --- | --- |"]
        status_map = {"done": "done", "open": "next"}
    for index, task in enumerate(tasks, start=1):
        lines.append(
            f"| {index} | {escape_table_cell(task['label'])} | {escape_table_cell(status_map.get(task['status'], task['status']))} |"
        )
    return "\n".join(lines)


def render_public_progress_snapshot(
    current_phase: str,
    execution: dict[str, str],
    tasks: list[dict[str, str]],
    slices: list[dict[str, str]],
    chinese: bool,
) -> str:
    done_count, total_count = human_progress_counts(execution["progress"])
    next_task = next((task["label"] for task in tasks if task["status"] == "open"), "")
    current_slice = active_slice(slices, execution["plan_link"]) or {}
    current_index = next((idx for idx, item in enumerate(slices) if item.get("name") == execution["plan_link"]), None)
    next_slice = slices[current_index + 1] if current_index is not None and current_index + 1 < len(slices) else None
    if chinese:
        return "\n".join(
            [
                "| 项目 | 当前值 |",
                "| --- | --- |",
                f"| 总体进度 | {escape_table_cell(f'{done_count} / {total_count} execution tasks 完成')} |",
                f"| 当前阶段 | {escape_table_cell(current_phase)} |",
                f"| 当前切片 | `{escape_table_cell(execution['plan_link'])}` |",
                f"| 当前目标 | {escape_table_cell(execution['objective'])} |",
                f"| 当前切片退出条件 | {escape_table_cell(current_slice.get('exit_condition', execution['validation']))} |",
                f"| 明确下一步动作 | {escape_table_cell(next_task if next_task else '当前 execution tasks 已完成，转向下一切片')} |",
                f"| 下一候选切片 | `{escape_table_cell(next_slice.get('name', 'n/a'))}` |" if next_slice else "| 下一候选切片 | n/a |",
            ]
        )
    return "\n".join(
        [
            "| Item | Current Value |",
            "| --- | --- |",
            f"| Overall Progress | {escape_table_cell(f'{done_count} / {total_count} execution tasks complete')} |",
            f"| Current Phase | {escape_table_cell(current_phase)} |",
            f"| Active Slice | `{escape_table_cell(execution['plan_link'])}` |",
            f"| Current Objective | {escape_table_cell(execution['objective'])} |",
            f"| Active Slice Exit Signal | {escape_table_cell(current_slice.get('exit_condition', execution['validation']))} |",
            f"| Clear Next Move | {escape_table_cell(next_task if next_task else 'Current execution tasks are complete; move to the next slice')} |",
            f"| Next Candidate Slice | `{escape_table_cell(next_slice.get('name', 'n/a'))}` |" if next_slice else "| Next Candidate Slice | n/a |",
        ]
    )


def roadmap_focus_rows(slices: list[dict[str, str]], execution: dict[str, str], chinese: bool) -> list[tuple[str, str, str]]:
    current_focus = execution["objective"]
    current_index = next((idx for idx, item in enumerate(slices) if item.get("name") == execution["plan_link"]), None)
    current_slice = slices[current_index] if current_index is not None else None
    current_exit = (
        current_slice.get("exit_condition", execution["validation"])
        if current_slice
        else (execution["stop_conditions"] if execution["stop_conditions"] not in {"", "n/a"} else execution["validation"])
    )

    next_slice = slices[current_index + 1] if current_index is not None and current_index + 1 < len(slices) else None
    later_slice = slices[current_index + 2] if current_index is not None and current_index + 2 < len(slices) else None

    if chinese:
        next_focus = next_slice.get("objective", next_slice.get("name", "暂无")) if next_slice else "暂无"
        next_exit = next_slice.get("exit_condition", next_slice.get("validation", "暂无")) if next_slice else "暂无"
        later_focus = later_slice.get("objective", later_slice.get("name", "暂无")) if later_slice else "暂无"
        later_exit = later_slice.get("exit_condition", later_slice.get("validation", "暂无")) if later_slice else "暂无"
        return [
            ("当前", current_focus, current_exit),
            ("下一步", next_focus, next_exit),
            ("更后面", later_focus, later_exit),
        ]

    next_focus = next_slice.get("objective", next_slice.get("name", "n/a")) if next_slice else "n/a"
    next_exit = next_slice.get("exit_condition", next_slice.get("validation", "n/a")) if next_slice else "n/a"
    later_focus = later_slice.get("objective", later_slice.get("name", "n/a")) if later_slice else "n/a"
    later_exit = later_slice.get("exit_condition", later_slice.get("validation", "n/a")) if later_slice else "n/a"
    return [
        ("Current", current_focus, current_exit),
        ("Next", next_focus, next_exit),
        ("Later", later_focus, later_exit),
    ]


def render_roadmap_focus_section(plan_text: str, chinese: bool) -> str:
    execution = parse_current_execution_fields(plan_text)
    slices = parse_slices(plan_text)
    rows = roadmap_focus_rows(slices, execution, chinese)
    if chinese:
        header = "| 时间层级 | 重点 | 退出信号 |\n| --- | --- | --- |"
    else:
        header = "| Horizon | Focus | Exit Signal |\n| --- | --- | --- |"
    lines = [header]
    for horizon, focus, exit_signal in rows:
        lines.append(f"| {escape_table_cell(horizon)} | {escape_table_cell(focus)} | {escape_table_cell(exit_signal)} |")
    return "\n".join(lines)


def render_roadmap_progress_section(plan_text: str, chinese: bool) -> str:
    current_phase = parse_current_phase(plan_text)
    execution = parse_current_execution_fields(plan_text)
    tasks = parse_execution_tasks(plan_text)
    slices = parse_slices(plan_text)
    snapshot = render_public_progress_snapshot(current_phase, execution, tasks, slices, chinese)
    if chinese:
        return snapshot + "\n\n查看详细执行计划：[project-assistant/development-plan.zh-CN.md](reference/project-assistant/development-plan.zh-CN.md)"
    return snapshot + "\n\nSee the detailed execution plan: [project-assistant/development-plan.md](reference/project-assistant/development-plan.md)"


def render_roadmap_integrity_section(chinese: bool) -> str:
    if chinese:
        return "\n".join(
            [
                "- 一个里程碑只对应一个清晰的主题目标",
                "- 标成 `done` / `已完成` 就表示这一项真的已经完整完成",
                "- 不要把同一条工作主题拆到多个顶层里程碑里",
                "- 细分步骤放进 development plan，不要塞进彼此重叠的 roadmap 顶层行",
            ]
        )
    return "\n".join(
        [
            "- one milestone = one clear theme-level goal",
            "- `done` means the milestone is actually complete",
            "- do not split the same work theme across multiple top-level milestones",
            "- put sub-steps in the development plan, not in overlapping roadmap rows",
        ]
    )


def render_development_plan(repo: Path, chinese: bool) -> str:
    docs_dir = repo / "docs"
    plan_text = read_text(repo / ".codex/plan.md")
    roadmap_text = read_text(docs_dir / ("roadmap.zh-CN.md" if chinese else "roadmap.md"))
    architecture_path = docs_dir / ("architecture.zh-CN.md" if chinese else "architecture.md")
    test_plan_path = docs_dir / ("test-plan.zh-CN.md" if chinese else "test-plan.md")
    milestones = parse_roadmap_milestones(roadmap_text, chinese=chinese)
    current_phase = parse_current_phase(plan_text)
    execution = parse_current_execution_fields(plan_text)
    open_execution_tasks = parse_open_execution_tasks(plan_text)
    execution_tasks = parse_execution_tasks(plan_text)
    slices = parse_slices(plan_text)
    progress_snapshot = render_public_progress_snapshot(current_phase, execution, execution_tasks, slices, chinese)

    title = f"# {project_name(repo)} Development Plan" if not chinese else f"# {project_name(repo)} 开发计划"
    switch = "[English](development-plan.md) | [中文](development-plan.zh-CN.md)"
    related_lines = ["- [../../roadmap.zh-CN.md](../../roadmap.zh-CN.md)"] if chinese else ["- [../../roadmap.md](../../roadmap.md)"]
    if architecture_path.exists():
        target = "../../architecture.zh-CN.md" if chinese else "../../architecture.md"
        related_lines.append(f"- [{target}]({target})")
    if test_plan_path.exists():
        target = "../../test-plan.zh-CN.md" if chinese else "../../test-plan.md"
        related_lines.append(f"- [{target}]({target})")

    if chinese:
        current_position = (
            "| 项目 | 当前值 | 说明 |\n| --- | --- | --- |\n"
            f"| 当前阶段 | {current_phase} | 当前维护阶段 |\n"
            f"| 当前切片 | `{execution['plan_link']}` | 当前执行线绑定的切片 |\n"
            f"| 当前执行线 | {execution['objective']} | 当前真正要收口的工作 |\n"
            f"| 当前验证 | {execution['validation']} | 这条线继续前需要保持为真的验证入口 |"
        )
        next_move = open_execution_tasks[0] if open_execution_tasks else "当前 execution tasks 已完成，转向下一切片或 release 决策"
        next_move_reason = (
            "这是当前第一条未完成 execution task；roadmap 与 development plan 都应把人带到同一个恢复点。"
            if open_execution_tasks
            else "当前 execution tasks 已完成，下一步应进入下一切片或下一轮 release 判断。"
        )
        return (
            f"{title}\n\n{switch}\n\n"
            "## 目的\n\n"
            "这份文档是给维护者看的 durable 详细执行计划，位置在 `docs/roadmap` 之下、AI 控制面之上。\n\n"
            "它回答的不是“今天聊天里说了什么”，而是：\n\n"
            "`接下来先做什么、从哪里恢复、每个里程碑下面到底落什么细节。`\n\n"
            "## 相关文档\n\n"
            + "\n".join(related_lines)
            + "\n\n## 怎么使用这份计划\n\n"
            "1. 先看 roadmap，理解总体进展与下一阶段。\n"
            "2. 再看这里的“总体进展”“执行任务进度”和“顺序执行队列”，理解今天该从哪里恢复。\n"
            "3. 只有在维护自动化本身时，才需要继续下钻到内部控制文档。\n\n"
            "## 总体进展\n\n"
            f"{progress_snapshot}\n\n"
            "## 当前位置\n\n"
            f"{current_position}\n\n"
            "## 执行任务进度\n\n"
            f"{render_execution_task_board(execution_tasks, chinese=True) if execution_tasks else '| 顺序 | 任务 | 状态 |\\n| --- | --- | --- |'}\n\n"
            "## 阶段总览\n\n"
            f"{render_milestone_overview_table(milestones, chinese=True) if milestones else '| 阶段 | 状态 | 目标 | 依赖 | 退出条件 |\\n| --- | --- | --- | --- | --- |'}\n\n"
            "## 顺序执行队列\n\n"
            f"{render_slice_queue(slices, execution['plan_link'], execution['progress'], chinese=True) if slices else '| 顺序 | 切片 | 当前状态 | 目标 | 验证 |\\n| --- | --- | --- | --- | --- |'}\n\n"
            "## 里程碑细节\n\n"
            f"{render_milestone_details(milestones, chinese=True) if milestones else '当前还没有从 roadmap 里解析出可下钻的里程碑。'}\n\n"
            "## 当前下一步\n\n"
            "| 下一步 | 为什么做 |\n| --- | --- |\n"
            f"| {next_move} | {next_move_reason} |"
        )

    current_position = (
        "| Item | Current Value | Meaning |\n| --- | --- | --- |\n"
        f"| Current Phase | {current_phase} | Current maintainer-facing phase |\n"
        f"| Active Slice | `{execution['plan_link']}` | The slice tied to the current execution line |\n"
        f"| Current Execution Line | {execution['objective']} | What the repo is trying to finish now |\n"
        f"| Validation | {execution['validation']} | The checks that must stay true before moving on |"
    )
    next_move = open_execution_tasks[0] if open_execution_tasks else "Current execution tasks are complete; move to the next slice or release decision"
    next_move_reason = (
        "This is the first unchecked execution task, so both the roadmap and this plan stay aligned to the same resume point."
        if open_execution_tasks
        else "The current execution tasks are complete, so the next move is to enter the next slice or release decision."
    )
    return (
        f"{title}\n\n{switch}\n\n"
        "## Purpose\n\n"
        "This document is the durable maintainer-facing execution plan that sits below `docs/roadmap.md` and above the AI control surfaces.\n\n"
        "It answers one practical question:\n\n"
        "`what should happen next, where should maintainers resume, and what detail sits underneath each roadmap milestone?`\n\n"
        "## Related Documents\n\n"
        + "\n".join(related_lines)
        + "\n\n## How To Use This Plan\n\n"
        "1. Read the roadmap first to understand overall progress and the next stage.\n"
        "2. Read `Overall Progress`, `Execution Task Progress`, and `Ordered Execution Queue` here to know where to resume.\n"
        "3. Only drop into the internal control docs when you are maintaining the automation itself.\n\n"
        "## Overall Progress\n\n"
        f"{progress_snapshot}\n\n"
        "## Current Position\n\n"
        f"{current_position}\n\n"
        "## Execution Task Progress\n\n"
        f"{render_execution_task_board(execution_tasks, chinese=False) if execution_tasks else '| Order | Task | Status |\\n| --- | --- | --- |'}\n\n"
        "## Milestone Overview\n\n"
        f"{render_milestone_overview_table(milestones, chinese=False) if milestones else '| Milestone | Status | Goal | Depends On | Exit Criteria |\\n| --- | --- | --- | --- | --- |'}\n\n"
        "## Ordered Execution Queue\n\n"
        f"{render_slice_queue(slices, execution['plan_link'], execution['progress'], chinese=False) if slices else '| Order | Slice | Status | Objective | Validation |\\n| --- | --- | --- | --- | --- |'}\n\n"
        "## Milestone Details\n\n"
        f"{render_milestone_details(milestones, chinese=False) if milestones else 'No milestone drill-down could be derived from the roadmap yet.'}\n\n"
        "## Current Next Step\n\n"
        "| Next Move | Why |\n| --- | --- |\n"
        f"| {next_move} | {next_move_reason} |"
    )


def sync_public_plan_surfaces(repo: Path) -> list[str]:
    touched: list[str] = []
    docs_dir = repo / "docs"
    reference_dir = docs_dir / "reference" / project_doc_slug(repo)
    development_plan = reference_dir / "development-plan.md"
    development_plan_zh = reference_dir / "development-plan.zh-CN.md"
    roadmap = docs_dir / "roadmap.md"
    roadmap_zh = docs_dir / "roadmap.zh-CN.md"
    plan_text = read_text(repo / ".codex/plan.md")

    if development_plan.exists():
        rendered = render_development_plan(repo, chinese=False).rstrip() + "\n"
        if read_text(development_plan).rstrip() != rendered.rstrip():
            development_plan.write_text(rendered, encoding="utf-8")
            touched.append(str(development_plan.relative_to(repo)))
    if development_plan_zh.exists():
        rendered = render_development_plan(repo, chinese=True).rstrip() + "\n"
        if read_text(development_plan_zh).rstrip() != rendered.rstrip():
            development_plan_zh.write_text(rendered, encoding="utf-8")
            touched.append(str(development_plan_zh.relative_to(repo)))

    if roadmap.exists() and plan_text:
        roadmap_text = read_text(roadmap)
        updated = ensure_section_before(
            roadmap_text,
            "Overall Progress",
            render_roadmap_progress_section(plan_text, chinese=False),
            ["Current / Next / Later", "Now / Next / Later"],
        )
        if updated.rstrip() != roadmap_text.rstrip():
            roadmap.write_text(updated.rstrip() + "\n", encoding="utf-8")
            touched.append(str(roadmap.relative_to(repo)))
        roadmap_text = read_text(roadmap)
        updated = ensure_section_before(
            roadmap_text,
            "Milestone Rules",
            render_roadmap_integrity_section(chinese=False),
            ["Milestones"],
        )
        if updated.rstrip() != roadmap_text.rstrip():
            roadmap.write_text(updated.rstrip() + "\n", encoding="utf-8")
            rel = str(roadmap.relative_to(repo))
            if rel not in touched:
                touched.append(rel)
        roadmap_text = read_text(roadmap)
        updated = replace_section(roadmap_text, ["Current / Next / Later", "Now / Next / Later"], render_roadmap_focus_section(plan_text, chinese=False))
        if updated.rstrip() != roadmap_text.rstrip():
            roadmap.write_text(updated.rstrip() + "\n", encoding="utf-8")
            rel = str(roadmap.relative_to(repo))
            if rel not in touched:
                touched.append(rel)
    if roadmap_zh.exists() and plan_text:
        roadmap_zh_text = read_text(roadmap_zh)
        updated = ensure_section_before(
            roadmap_zh_text,
            "总体进展",
            render_roadmap_progress_section(plan_text, chinese=True),
            ["当前 / 下一步 / 更后面"],
        )
        if updated.rstrip() != roadmap_zh_text.rstrip():
            roadmap_zh.write_text(updated.rstrip() + "\n", encoding="utf-8")
            touched.append(str(roadmap_zh.relative_to(repo)))
        roadmap_zh_text = read_text(roadmap_zh)
        updated = ensure_section_before(
            roadmap_zh_text,
            "里程碑规则",
            render_roadmap_integrity_section(chinese=True),
            ["里程碑"],
        )
        if updated.rstrip() != roadmap_zh_text.rstrip():
            roadmap_zh.write_text(updated.rstrip() + "\n", encoding="utf-8")
            rel = str(roadmap_zh.relative_to(repo))
            if rel not in touched:
                touched.append(rel)
        roadmap_zh_text = read_text(roadmap_zh)
        updated = replace_section(roadmap_zh_text, ["当前 / 下一步 / 更后面"], render_roadmap_focus_section(plan_text, chinese=True))
        if updated.rstrip() != roadmap_zh_text.rstrip():
            roadmap_zh.write_text(updated.rstrip() + "\n", encoding="utf-8")
            rel = str(roadmap_zh.relative_to(repo))
            if rel not in touched:
                touched.append(rel)

    return touched


def ensure_table_row_in_section(path: Path, heading: str, row: str) -> bool:
    text = read_text(path)
    if not text or row in text:
        return False
    marker = f"## {heading}"
    start = text.find(marker)
    if start == -1:
        return False
    section_end = text.find("\n## ", start + len(marker))
    section_text = text[start: section_end if section_end != -1 else len(text)]
    lines = section_text.splitlines()
    table_end = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("|"):
            table_end = idx
    if table_end is None:
        return False
    lines.insert(table_end + 1, row)
    rebuilt = "\n".join(lines)
    new_text = text[:start] + rebuilt + (text[section_end:] if section_end != -1 else "")
    path.write_text(new_text, encoding="utf-8")
    return True


def ensure_roadmap_detail_link(path: Path, link_line: str, chinese: bool) -> bool:
    text = read_text(path)
    if not text or link_line in text:
        return False
    section_title = "## 当前 / 下一步 / 更后面" if chinese else "## Now / Next / Later"
    block = ("\n详细执行队列看这里：\n\n" if chinese else "\nDetailed execution queue:\n\n") + f"- {link_line}\n\n"
    insert_at = text.find(section_title)
    if insert_at == -1:
        milestone_title = "## 里程碑" if chinese else "## Milestones"
        insert_at = text.find(milestone_title)
    if insert_at == -1:
        heading_matches = list(re.finditer(r"(?m)^##\s+.+$", text))
        if not heading_matches:
            return False
        if len(heading_matches) >= 2:
            insert_at = heading_matches[1].start()
        else:
            insert_at = len(text)
    new_text = text[:insert_at] + block + text[insert_at:]
    path.write_text(new_text, encoding="utf-8")
    return True


def docs_home_templates(tier: str) -> tuple[str, str]:
    if tier == "large":
        return (
            """# Docs Home

[English](README.md) | [中文](README.zh-CN.md)

## Start Here
- Getting started: [README](../README.md)
- Architecture: [architecture.md](architecture.md)
- Roadmap: [roadmap.md](roadmap.md)
- Testing: [test-plan.md](test-plan.md)
- ADRs: [adr/](adr/)

## By Goal
| Goal | Read This |
| --- | --- |
| Try the project quickly | [README](../README.md) |
| Understand the system | [architecture.md](architecture.md) |
| See what is next | [roadmap.md](roadmap.md) |
| Verify correctness | [test-plan.md](test-plan.md) |
""",
            """# 文档首页

[English](README.md) | [中文](README.zh-CN.md)

## 从这里开始
- 快速了解项目：[README](../README.zh-CN.md)
- 架构：[architecture.zh-CN.md](architecture.zh-CN.md)
- 路线图：[roadmap.zh-CN.md](roadmap.zh-CN.md)
- 测试：[test-plan.zh-CN.md](test-plan.zh-CN.md)
- ADR：[adr/README.zh-CN.md](adr/README.zh-CN.md)

## 按目标阅读
| 目标 | 阅读这里 |
| --- | --- |
| 快速试用项目 | [README](../README.zh-CN.md) |
| 理解系统结构 | [architecture.zh-CN.md](architecture.zh-CN.md) |
| 了解下一步计划 | [roadmap.zh-CN.md](roadmap.zh-CN.md) |
| 了解验证方式 | [test-plan.zh-CN.md](test-plan.zh-CN.md) |
""",
        )
    return DOCS_HOME_TEMPLATE, DOCS_HOME_ZH_TEMPLATE


def bootstrap_control_surface(repo: Path) -> None:
    tier = parse_tier(repo)
    version_state = control_surface_version_state(repo, tier=tier)
    missing_required_files = any(not (repo / rel).exists() for rel in control_surface_required_files(tier))
    missing_required_surfaces = any(
        not (repo / CONTROL_SURFACE_COMPONENT_PATHS[component]).exists()
        for component in version_state["requiredSurfaceVersions"]
    )
    if not version_state["needsConfigUpgrade"] and not missing_required_files and not missing_required_surfaces:
        return
    script = Path(__file__).with_name("sync_control_surface.py")
    result = subprocess.run(
        [sys.executable, str(script), str(repo)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or normalize the durable docs skeleton for a repo.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    bootstrap_control_surface(repo)
    tier = parse_tier(repo)
    docs_dir = repo / "docs"
    docs_dir.mkdir(exist_ok=True)
    adr_dir = docs_dir / "adr"
    adr_dir.mkdir(exist_ok=True)
    reference_dir = docs_dir / "reference" / project_doc_slug(repo)
    reference_dir.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    touched: list[str] = []

    readme = repo / "README.md"
    readme_zh = repo / "README.zh-CN.md"
    if ensure_file(readme, README_TEMPLATE.format(project_name=project_name(repo))):
        created.append("README.md")
    created_zh = ensure_file(readme_zh, README_ZH_TEMPLATE.format(project_name=project_name(repo)))
    if created_zh:
        created.append("README.zh-CN.md")
    if append_doc_map_if_missing(readme):
        touched.append("README.md")
    if append_quick_start_if_missing(readme) and "README.md" not in touched:
        touched.append("README.md")
    if ensure_switch_line(readme, readme, readme_zh) and "README.md" not in touched:
        touched.append("README.md")
    if ensure_switch_line(readme_zh, readme, readme_zh) and not created_zh:
        touched.append("README.zh-CN.md")
    normalize_split_bilingual_doc(readme, readme_zh, touched, created, repo)

    if tier in {"medium", "large"}:
        docs_home_template, docs_home_zh_template = docs_home_templates(tier)
        ensure_bilingual_pair(docs_dir / "README.md", docs_dir / "README.zh-CN.md", docs_home_template, docs_home_zh_template, created, touched, repo)
        docs_home_scaffolds = [
            """# Docs Home

[English](README.md) | [中文](README.zh-CN.md)

## Start Here
- Getting started: [README](../README.md)
- Architecture: [architecture.md](architecture.md)
- Roadmap: [roadmap.md](roadmap.md)
- Testing: [test-plan.md](test-plan.md)
- ADRs: [adr/](adr/)

## By Goal
| Goal | Read This |
| --- | --- |
| Try the project quickly | [README](../README.md) |
| Understand the system | [architecture.md](architecture.md) |
| See what is next | [roadmap.md](roadmap.md) |
| Verify correctness | [test-plan.md](test-plan.md) |
""",
            DOCS_HOME_TEMPLATE,
        ]
        if replace_if_scaffold(docs_dir / "README.md", docs_home_scaffolds, docs_home_template) and "docs/README.md" not in touched:
            touched.append("docs/README.md")
        docs_home_zh_scaffolds = [
            """# 文档首页

[English](README.md) | [中文](README.zh-CN.md)

## 从这里开始
- 快速了解项目：[README](../README.zh-CN.md)
- 架构：[architecture.zh-CN.md](architecture.zh-CN.md)
- 路线图：[roadmap.zh-CN.md](roadmap.zh-CN.md)
- 测试：[test-plan.zh-CN.md](test-plan.zh-CN.md)
- ADR：[adr/README.zh-CN.md](adr/README.zh-CN.md)

## 按目标阅读
| 目标 | 阅读这里 |
| --- | --- |
| 快速试用项目 | [README](../README.zh-CN.md) |
| 理解系统结构 | [architecture.zh-CN.md](architecture.zh-CN.md) |
| 了解下一步计划 | [roadmap.zh-CN.md](roadmap.zh-CN.md) |
| 了解验证方式 | [test-plan.zh-CN.md](test-plan.zh-CN.md) |
""",
            DOCS_HOME_ZH_TEMPLATE,
        ]
        if replace_if_scaffold(docs_dir / "README.zh-CN.md", docs_home_zh_scaffolds, docs_home_zh_template) and "docs/README.zh-CN.md" not in touched:
            touched.append("docs/README.zh-CN.md")
        extra_docs_home_lines: list[str] = []
        extra_docs_home_zh_lines: list[str] = []
        release_doc = first_existing(repo, ["RELEASE.md", "release.md"])
        release_doc_zh = first_existing(repo, ["RELEASE.zh-CN.md", "release.zh-CN.md"])
        if release_doc:
            extra_docs_home_lines.append(f"- Release process: [../{release_doc.name}](../{release_doc.name})")
            zh_name = release_doc_zh.name if release_doc_zh else f"{release_doc.stem}.zh-CN{release_doc.suffix}"
            extra_docs_home_zh_lines.append(f"- 发布说明：[../{zh_name}](../{zh_name})")
        if (docs_dir / "module-map.md").exists():
            extra_docs_home_lines.append("- Module map: [module-map.md](module-map.md)")
            extra_docs_home_zh_lines.append("- 模块地图：[module-map.zh-CN.md](module-map.zh-CN.md)")
        if append_unique_lines(docs_dir / "README.md", extra_docs_home_lines) and "docs/README.md" not in touched:
            touched.append("docs/README.md")
        if append_unique_lines(docs_dir / "README.zh-CN.md", extra_docs_home_zh_lines) and "docs/README.zh-CN.md" not in touched:
            touched.append("docs/README.zh-CN.md")
        ensure_bilingual_pair(docs_dir / "test-plan.md", docs_dir / "test-plan.zh-CN.md", TEST_PLAN_TEMPLATE, TEST_PLAN_ZH_TEMPLATE, created, touched, repo)

        development_plan = reference_dir / "development-plan.md"
        development_plan_zh = reference_dir / "development-plan.zh-CN.md"
        reference_home = reference_dir / "README.md"
        reference_home_zh = reference_dir / "README.zh-CN.md"
        reference_home_text = PROJECT_REFERENCE_HOME_TEMPLATE.format(project_name=project_name(repo))
        reference_home_zh_text = PROJECT_REFERENCE_HOME_ZH_TEMPLATE.format(project_name=project_name(repo))
        if ensure_file(reference_home, reference_home_text):
            created.append(str(reference_home.relative_to(repo)))
        if ensure_file(reference_home_zh, reference_home_zh_text):
            created.append(str(reference_home_zh.relative_to(repo)))
        if ensure_switch_line(reference_home, reference_home, reference_home_zh) and str(reference_home.relative_to(repo)) not in touched:
            touched.append(str(reference_home.relative_to(repo)))
        if ensure_switch_line(reference_home_zh, reference_home, reference_home_zh) and str(reference_home_zh.relative_to(repo)) not in touched:
            touched.append(str(reference_home_zh.relative_to(repo)))

        en_plan_text = render_development_plan(repo, chinese=False)
        zh_plan_text = render_development_plan(repo, chinese=True)
        if read_text(development_plan).rstrip() != en_plan_text.rstrip():
            development_plan.write_text(en_plan_text + "\n", encoding="utf-8")
            rel = str(development_plan.relative_to(repo))
            if rel not in created and rel not in touched:
                touched.append(rel)
        if read_text(development_plan_zh).rstrip() != zh_plan_text.rstrip():
            development_plan_zh.write_text(zh_plan_text + "\n", encoding="utf-8")
            rel = str(development_plan_zh.relative_to(repo))
            if rel not in created and rel not in touched:
                touched.append(rel)
        ensure_switch_line(development_plan, development_plan, development_plan_zh)
        ensure_switch_line(development_plan_zh, development_plan, development_plan_zh)

        dev_plan_rel = relative_markdown_target(docs_dir, development_plan)
        dev_plan_rel_zh = relative_markdown_target(docs_dir, development_plan_zh)
        if ensure_table_row_in_section(
            docs_dir / "README.md",
            "By Goal",
            f"| Drill into the detailed execution queue | [{reference_dir.name}/development-plan.md]({dev_plan_rel}) |",
        ) and "docs/README.md" not in touched:
            touched.append("docs/README.md")
        if ensure_table_row_in_section(
            docs_dir / "README.zh-CN.md",
            "按目标阅读",
            f"| 深入查看详细执行队列 | [{reference_dir.name}/development-plan.zh-CN.md]({dev_plan_rel_zh}) |",
        ) and "docs/README.zh-CN.md" not in touched:
            touched.append("docs/README.zh-CN.md")

    if tier == "large":
        architecture = docs_dir / "architecture.md"
        architecture_zh = docs_dir / "architecture.zh-CN.md"
        roadmap = docs_dir / "roadmap.md"
        roadmap_zh = docs_dir / "roadmap.zh-CN.md"
        adr_template = adr_dir / "0001-template.md"
        adr_template_zh = adr_dir / "0001-template.zh-CN.md"
        adr_index = adr_dir / "README.md"
        adr_index_zh = adr_dir / "README.zh-CN.md"

        ensure_bilingual_pair(architecture, architecture_zh, ARCHITECTURE_TEMPLATE, ARCHITECTURE_ZH_TEMPLATE, created, touched, repo)
        ensure_bilingual_pair(roadmap, roadmap_zh, ROADMAP_TEMPLATE, ROADMAP_ZH_TEMPLATE, created, touched, repo)
        ensure_bilingual_pair(adr_template, adr_template_zh, ADR_TEMPLATE, ADR_ZH_TEMPLATE, created, touched, repo)
        ensure_bilingual_pair(adr_index, adr_index_zh, ADR_INDEX_TEMPLATE, ADR_INDEX_ZH_TEMPLATE, created, touched, repo)

    optional_public_pairs = [
        (docs_dir / "architecture.md", docs_dir / "architecture.zh-CN.md", ARCHITECTURE_TEMPLATE, ARCHITECTURE_ZH_TEMPLATE),
        (docs_dir / "roadmap.md", docs_dir / "roadmap.zh-CN.md", ROADMAP_TEMPLATE, ROADMAP_ZH_TEMPLATE),
        (adr_dir / "README.md", adr_dir / "README.zh-CN.md", ADR_INDEX_TEMPLATE, ADR_INDEX_ZH_TEMPLATE),
    ]
    for en_path, zh_path, en_template, zh_template in optional_public_pairs:
        if en_path.exists() or zh_path.exists():
            ensure_bilingual_pair(en_path, zh_path, en_template, zh_template, created, touched, repo)

    for rel in sync_public_plan_surfaces(repo):
        if rel not in created and rel not in touched:
            touched.append(rel)

    release_doc = first_existing(repo, ["RELEASE.md", "release.md"])
    if release_doc:
        release_doc_zh = first_existing(repo, ["RELEASE.zh-CN.md", "release.zh-CN.md"])
        if not release_doc_zh:
            release_doc_zh = release_doc.with_name(f"{release_doc.stem}.zh-CN{release_doc.suffix}")
        normalize_split_bilingual_doc(release_doc, release_doc_zh, touched, created, repo)
    normalize_split_bilingual_doc(docs_dir / "module-map.md", docs_dir / "module-map.zh-CN.md", touched, created, repo)
    if tier in {"medium", "large"}:
        development_plan = reference_dir / "development-plan.md"
        development_plan_zh = reference_dir / "development-plan.zh-CN.md"
        if development_plan.exists() and ensure_roadmap_detail_link(
            docs_dir / "roadmap.md",
            f"[{reference_dir.name}/development-plan.md]({relative_markdown_target(docs_dir, development_plan)})",
            chinese=False,
        ):
            touched.append("docs/roadmap.md")
        if development_plan_zh.exists() and ensure_roadmap_detail_link(
            docs_dir / "roadmap.zh-CN.md",
            f"[{reference_dir.name}/development-plan.zh-CN.md]({relative_markdown_target(docs_dir, development_plan_zh)})",
            chinese=True,
        ):
            touched.append("docs/roadmap.zh-CN.md")
    for rel in ensure_roadmap_stage_links(repo):
        if rel not in touched:
            touched.append(rel)

    print(f"tier: {tier}")
    print(f"created: {', '.join(created) if created else '(none)'}")
    print(f"touched: {', '.join(touched) if touched else '(none)'}")
    print("docs sync complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
