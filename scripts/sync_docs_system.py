#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from control_surface_lib import parse_tier, read_text


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
"""


DOCS_HOME_ZH_TEMPLATE = """# 文档首页

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
    return repo.name


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


def append_doc_map_if_missing(readme_path: Path) -> bool:
    text = read_text(readme_path)
    if not text:
        return False
    if "## Documentation Map" in text or "## Docs" in text:
        return False
    addition = """

## Documentation Map
- [Docs Home](docs/README.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or normalize the durable docs skeleton for a repo.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    tier = parse_tier(repo)
    docs_dir = repo / "docs"
    docs_dir.mkdir(exist_ok=True)
    adr_dir = docs_dir / "adr"
    adr_dir.mkdir(exist_ok=True)

    created: list[str] = []
    touched: list[str] = []

    readme = repo / "README.md"
    readme_zh = repo / "README.zh-CN.md"
    if ensure_file(readme, README_TEMPLATE.format(project_name=project_name(repo))):
        created.append("README.md")
    if ensure_file(readme_zh, README_ZH_TEMPLATE.format(project_name=project_name(repo))):
        created.append("README.zh-CN.md")
    else:
        if append_doc_map_if_missing(readme):
            touched.append("README.md")
        if append_quick_start_if_missing(readme) and "README.md" not in touched:
            touched.append("README.md")
    if ensure_switch_line(readme, readme, readme_zh) and "README.md" not in touched:
        touched.append("README.md")
    if ensure_switch_line(readme_zh, readme, readme_zh):
        touched.append("README.zh-CN.md")

    if tier in {"medium", "large"}:
        ensure_bilingual_pair(docs_dir / "README.md", docs_dir / "README.zh-CN.md", DOCS_HOME_TEMPLATE, DOCS_HOME_ZH_TEMPLATE, created, touched, repo)
        ensure_bilingual_pair(docs_dir / "test-plan.md", docs_dir / "test-plan.zh-CN.md", TEST_PLAN_TEMPLATE, TEST_PLAN_ZH_TEMPLATE, created, touched, repo)

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

    print(f"tier: {tier}")
    print(f"created: {', '.join(created) if created else '(none)'}")
    print(f"touched: {', '.join(touched) if touched else '(none)'}")
    print("docs sync complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
