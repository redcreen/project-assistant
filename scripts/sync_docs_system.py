#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from control_surface_lib import ensure_roadmap_stage_links, parse_tier, read_text, relative_markdown_target, slugify, unwrap_markdown_label


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


def parse_roadmap_milestones(text: str, chinese: bool) -> list[dict[str, str]]:
    body = section_body(text, ["Milestones"] if not chinese else ["里程碑"])
    rows: list[dict[str, str]] = []
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
                "label": unwrap_markdown_label(cells[0]),
                "status": cells[1],
                "goal": cells[2],
                "depends": unwrap_markdown_label(cells[3]),
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
            item[key.lower().replace(" ", "_").replace("-", "_")] = value.strip().strip("`")
        slices.append(item)
    return slices


def render_milestone_overview_table(rows: list[dict[str, str]], chinese: bool) -> str:
    header = "| 阶段 | 状态 | 目标 | 依赖 | 退出条件 |\n| --- | --- | --- | --- | --- |" if chinese else "| Milestone | Status | Goal | Depends On | Exit Criteria |\n| --- | --- | --- | --- | --- |"
    lines = [header]
    for row in rows:
        lines.append(f"| {row['label']} | {row['status']} | {row['goal']} | {row['depends']} | {row['exit']} |")
    return "\n".join(lines)


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
            f"| {index} | `{item.get('name', 'n/a')}` | {status} | {item.get('objective', 'n/a')} | {item.get('validation', 'n/a')} |"
        )
    return "\n".join(lines)


def render_development_plan(repo: Path, chinese: bool) -> str:
    slug = project_doc_slug(repo)
    docs_dir = repo / "docs"
    plan_path = repo / ".codex/plan.md"
    roadmap_path = docs_dir / ("roadmap.zh-CN.md" if chinese else "roadmap.md")
    architecture_path = docs_dir / ("architecture.zh-CN.md" if chinese else "architecture.md")
    test_plan_path = docs_dir / ("test-plan.zh-CN.md" if chinese else "test-plan.md")
    plan_text = read_text(plan_path)
    roadmap_text = read_text(roadmap_path)
    milestones = parse_roadmap_milestones(roadmap_text, chinese=chinese)
    current_phase = parse_current_phase(plan_text)
    execution = parse_current_execution_fields(plan_text)
    slices = parse_slices(plan_text)
    title = f"# {project_name(repo)} Development Plan" if not chinese else f"# {project_name(repo)} 开发计划"
    switch = "[English](development-plan.md) | [中文](development-plan.zh-CN.md)"
    if chinese:
        related_lines = ["- [../../roadmap.zh-CN.md](../../roadmap.zh-CN.md)"]
    else:
        related_lines = ["- [../../roadmap.md](../../roadmap.md)"]
    if architecture_path.exists():
        target = "../../architecture.md" if not chinese else "../../architecture.zh-CN.md"
        related_lines.append(f"- [{target}]({target})")
    if test_plan_path.exists():
        target = "../../test-plan.md" if not chinese else "../../test-plan.zh-CN.md"
        related_lines.append(f"- [{target}]({target})")
    if chinese:
        current_position = (
            "| 项目 | 当前值 | 说明 |\n| --- | --- | --- |\n"
            f"| 当前阶段 | {current_phase} | 来自 `.codex/plan.md` 的当前维护阶段 |\n"
            f"| 当前切片 | `{execution['plan_link']}` | 当前执行线绑定的切片 |\n"
            f"| 当前执行线 | {execution['objective']} | 当前这轮真正要收口的工作 |\n"
            f"| 当前验证 | {execution['validation']} | 继续前如何证明这条线已收口 |"
        )
    else:
        current_position = (
            "| Item | Current Value | Meaning |\n| --- | --- | --- |\n"
            f"| Current Phase | {current_phase} | Current maintainer-facing phase from `.codex/plan.md` |\n"
            f"| Active Slice | `{execution['plan_link']}` | The slice tied to the current execution line |\n"
            f"| Current Execution Line | {execution['objective']} | What the repo is trying to finish now |\n"
            f"| Validation | {execution['validation']} | How this line proves itself before moving on |"
        )
    if chinese:
        return (
            f"{title}\n\n{switch}\n\n"
            "## 目的\n\n"
            "这份文档是给维护者看的 durable 详细执行计划，位置在 `docs/roadmap` 之下、`.codex/plan.md` 之上。\n\n"
            "它回答的不是“今天聊天里说了什么”，而是：\n\n"
            "`接下来先做什么、从哪里恢复、每个里程碑下面到底落什么细节。`\n\n"
            "## 相关文档\n\n"
            + "\n".join(related_lines)
            + "\n\n## 怎么使用这份计划\n\n"
            "1. 先看 roadmap，理解整体路线和当前里程碑。\n"
            "2. 再看这里的“当前位置”和“顺序执行队列”，理解今天该从哪里恢复。\n"
            "3. 需要具体约束时，再回到 `.codex/plan.md` 看实时执行控制面。\n\n"
            "## 当前位置\n\n"
            f"{current_position}\n\n"
            "## 阶段总览\n\n"
            f"{render_milestone_overview_table(milestones, chinese=True) if milestones else '| 阶段 | 状态 | 目标 | 依赖 | 退出条件 |\\n| --- | --- | --- | --- | --- |'}\n\n"
            "## 顺序执行队列\n\n"
            f"{render_slice_queue(slices, execution['plan_link'], execution['progress'], chinese=True) if slices else '| 顺序 | 切片 | 当前状态 | 目标 | 验证 |\\n| --- | --- | --- | --- | --- |'}\n\n"
            "## 里程碑细节\n\n"
            f"{render_milestone_details(milestones, chinese=True) if milestones else '当前还没有从 roadmap 里解析出可下钻的里程碑。'}\n\n"
            "## 当前下一步\n\n"
            "| 下一步 | 为什么做 |\n| --- | --- |\n"
            f"| 继续从 `{execution['plan_link']}` 之后恢复 | 当前执行线已经把真实恢复点固定在 `.codex/plan.md` 里 |"
        )
    return (
        f"{title}\n\n{switch}\n\n"
        "## Purpose\n\n"
        "This document is the durable maintainer-facing execution plan that sits below `docs/roadmap.md` and above `.codex/plan.md`.\n\n"
        "It answers one practical question:\n\n"
        "`what should happen next, where should maintainers resume, and what detail sits underneath each roadmap milestone?`\n\n"
        "## Related Documents\n\n"
        + "\n".join(related_lines)
        + "\n\n## How To Use This Plan\n\n"
        "1. Read the roadmap first to understand milestone order.\n"
        "2. Read `Current Position` and `Ordered Execution Queue` here to know where to resume.\n"
        "3. Drop into `.codex/plan.md` only when you need the live control-surface detail.\n\n"
        "## Current Position\n\n"
        f"{current_position}\n\n"
        "## Milestone Overview\n\n"
        f"{render_milestone_overview_table(milestones, chinese=False) if milestones else '| Milestone | Status | Goal | Depends On | Exit Criteria |\\n| --- | --- | --- | --- | --- |'}\n\n"
        "## Ordered Execution Queue\n\n"
        f"{render_slice_queue(slices, execution['plan_link'], execution['progress'], chinese=False) if slices else '| Order | Slice | Status | Objective | Validation |\\n| --- | --- | --- | --- | --- |'}\n\n"
        "## Milestone Details\n\n"
        f"{render_milestone_details(milestones, chinese=False) if milestones else 'No milestone drill-down could be derived from the roadmap yet.'}\n\n"
        "## Current Next Step\n\n"
        "| Next Move | Why |\n| --- | --- |\n"
        f"| Continue from `{execution['plan_link']}` onward | The live execution line already fixes the real resume point in `.codex/plan.md` |"
    )


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
