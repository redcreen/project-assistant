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


INTENT_TITLES = {
    "retrofit": "项目助手整改",
    "docs-retrofit": "项目助手文档整改",
}


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


def render(results: tuple[StepResult, ...], repo: Path, intent: str, profile: str) -> str:
    total = sum(item.seconds for item in results)
    tier = parse_tier(repo)
    title = INTENT_TITLES[intent]
    lines = [
        f"# {title}",
        "",
        "## 结果",
        "",
        "| 项目 | 当前值 |",
        "| --- | --- |",
        f"| 仓库 | `{repo}` |",
        f"| 前门模式 | `{intent}` |",
        f"| Tier | `{tier}` |",
        f"| 验证档位 | `{profile}` |",
        f"| 宿主直连次数 | `1` |",
        f"| 替代旧链路 | `sync_control_surface -> sync_docs_system -> sync_markdown_governance -> validate_gate_set({profile})` |",
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
            "## 说明",
            "",
            "- 当前前门默认跑 `fast` 结构门禁，优先把 control-surface / docs / markdown governance 收成一次事务。",
            "- 如果这轮要把整改宣告完成，后续仍应补跑 `python3 scripts/validate_gate_set.py <repo> --profile deep`。",
            "",
            "## 下一检查点",
            "",
            "1. 如果还有 maintainer-facing 文案或真实项目事实要补，直接继续当前切片，不要再手工串 sync 脚本。",
            "2. 结构整改收敛后，再补 `deep` 门禁确认质量层已经关闭。",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the canonical retrofit fast path: control surface, docs, markdown governance, and the fast structural gate in one transaction."
    )
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--intent", choices=["retrofit", "docs-retrofit"], default="retrofit")
    parser.add_argument("--profile", choices=["fast", "deep"], default="fast")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    scripts_dir = Path(__file__).resolve().parent
    results = (
        run_step(scripts_dir / "sync_control_surface.py", repo),
        run_step(scripts_dir / "sync_docs_system.py", repo),
        run_step(scripts_dir / "sync_markdown_governance.py", repo),
        run_step(scripts_dir / "validate_gate_set.py", repo, "--profile", args.profile),
    )
    print(render(results, repo, args.intent, args.profile), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
