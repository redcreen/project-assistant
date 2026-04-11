#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from control_surface_lib import parse_tier, read_text


README_TEMPLATE = """# {project_name}

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


DOCS_HOME_TEMPLATE = """# Docs Home

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


ARCHITECTURE_TEMPLATE = """# Architecture

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


ROADMAP_TEMPLATE = """# Roadmap

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


TEST_PLAN_TEMPLATE = """# Test Plan

## Scope and Risk

## Acceptance Cases
| Case | Setup | Action | Expected Result |
| --- | --- | --- | --- |

## Automation Coverage

## Manual Checks

## Test Data and Fixtures

## Release Gate
"""


ADR_TEMPLATE = """# ADR 0001: Title

## Status

## Context

## Decision

## Consequences

## Alternatives Considered
"""


def project_name(repo: Path) -> str:
    return repo.name


def ensure_file(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
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

    if ensure_file(repo / "README.md", README_TEMPLATE.format(project_name=project_name(repo))):
        created.append("README.md")
    else:
        if append_doc_map_if_missing(repo / "README.md"):
            touched.append("README.md")
        if append_quick_start_if_missing(repo / "README.md") and "README.md" not in touched:
            touched.append("README.md")

    if tier in {"medium", "large"}:
        if ensure_file(docs_dir / "README.md", DOCS_HOME_TEMPLATE):
            created.append("docs/README.md")
        if ensure_file(docs_dir / "test-plan.md", TEST_PLAN_TEMPLATE):
            created.append("docs/test-plan.md")

    if tier == "large":
        if ensure_file(docs_dir / "architecture.md", ARCHITECTURE_TEMPLATE):
            created.append("docs/architecture.md")
        if ensure_file(docs_dir / "roadmap.md", ROADMAP_TEMPLATE):
            created.append("docs/roadmap.md")
        if ensure_file(adr_dir / "0001-template.md", ADR_TEMPLATE):
            created.append("docs/adr/0001-template.md")

    print(f"tier: {tier}")
    print(f"created: {', '.join(created) if created else '(none)'}")
    print(f"touched: {', '.join(touched) if touched else '(none)'}")
    print("docs sync complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
