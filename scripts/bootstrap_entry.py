#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from control_surface_lib import parse_tier


@dataclass(frozen=True)
class StepResult:
    label: str
    seconds: float


def run_step(script_path: Path, repo: Path, *extra_args: str) -> StepResult:
    started = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(script_path), str(repo), *extra_args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    elapsed = time.perf_counter() - started
    if result.returncode != 0:
        output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part).strip()
        detail = f"\n{output}" if output else ""
        raise SystemExit(f"{script_path.name} failed for {repo}{detail}")
    return StepResult(label=script_path.name, seconds=elapsed)


def render(results: tuple[StepResult, ...], repo: Path, profile: str) -> str:
    total = sum(item.seconds for item in results)
    tier = parse_tier(repo)
    lines = [
        "# 项目助手启动",
        "",
        "## 结果",
        "",
        "| 项目 | 当前值 |",
        "| --- | --- |",
        f"| 仓库 | `{repo}` |",
        f"| 前门模式 | `bootstrap` |",
        f"| Tier | `{tier}` |",
        f"| 验证档位 | `{profile}` |",
        f"| 宿主直连次数 | `1` |",
        f"| 替代旧链路 | `sync_control_surface -> sync_docs_system -> validate_gate_set({profile})` |",
        f"| 总耗时 | `{total:.3f}s` |",
        "",
        "## 本轮动作",
        "",
        "| 步骤 | 耗时 |",
        "| --- | ---: |",
    ]
    for item in results:
        lines.append(f"| `{item.label}` | `{item.seconds:.3f}s` |")
    lines.extend(
        [
            "",
            "## 下一检查点",
            "",
            "1. 填完 `.codex/brief.md` 里的 Outcome / Scope / DoD。",
            "2. 把 `README`、`docs/architecture`、`docs/roadmap`、`docs/test-plan` 的模板段落替换成项目真实内容。",
            "3. 用 `project-assistant continue <repo>` 或 `python3 scripts/project_assistant_entry.py continue <repo>` 进入下一条执行线。",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the canonical bootstrap fast path: control surface, durable docs, and a fast structural gate in one transaction."
    )
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--profile", choices=["fast"], default="fast", help="Validation profile; bootstrap currently uses the fast gate")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    scripts_dir = Path(__file__).resolve().parent
    results = (
        run_step(scripts_dir / "sync_control_surface.py", repo),
        run_step(scripts_dir / "sync_docs_system.py", repo),
        run_step(scripts_dir / "validate_gate_set.py", repo, "--profile", args.profile),
    )
    print(render(results, repo, args.profile), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
