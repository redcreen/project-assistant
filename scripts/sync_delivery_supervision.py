#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import (
    delivery_supervision_expected,
    first_line,
    labeled_bullet_value,
    parse_delivery_supervision,
    read_text,
    section,
)


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    updated, count = re.subn(
        pattern,
        lambda match: f"{match.group(1)}{body.rstrip()}\n\n",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if count:
        return updated.rstrip() + "\n"
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def delivery_direction(repo: Path) -> tuple[str, str, str]:
    plan_text = read_text(repo / ".codex/plan.md")
    status_text = read_text(repo / ".codex/status.md")
    current_phase = first_line(section(status_text, "Current Phase")) or first_line(section(plan_text, "Current Phase"))
    objective = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective") or labeled_bullet_value(
        section(plan_text, "Current Execution Line"), "Objective"
    )
    lowered = current_phase.lower()
    status = "active"
    if "closed" in lowered or "收口" in current_phase or "queued" in lowered or "排队" in current_phase:
        status = "done"
    elif "next" in lowered:
        status = "next"
    direction = "supervised long-run delivery"
    why_now = (
        "战略评估层和程序编排层已经把方向、边界和 workstreams 收口成 durable 真相；现在需要一套长期监督交付面来定义 checkpoint 节奏、自动继续边界和升级时机。"
    )
    if objective:
        why_now = objective
    return direction, status, why_now


def delivery_contract() -> list[str]:
    return [
        "长期监督交付必须同时引用 `.codex/strategy.md`、`.codex/program-board.md`、`.codex/plan.md`、`.codex/status.md` 和当前 durable 文档，而不是只凭聊天上下文继续。",
        "每个 checkpoint 都必须重新判断：当前工作是可以自动继续、提醒后继续，还是必须升级给人类裁决。",
        "长期交付只允许在已批准的业务方向内自动继续；不能自动改变产品方向、兼容性承诺、外部定位或显著成本 / 时间边界。",
        "每轮 checkpoint 都必须把验证结果、控制面真相、进展面和交接面刷新成同一套状态，而不是只更新其中一部分。",
        "重要的监督循环调整、升级边界变化或 supporting backlog 回流判断，应写入 devlog，避免只剩结论没有推理链。",
    ]


def checkpoint_rhythm_table() -> str:
    rows = [
        ("1", "对齐方向与输入", "读取 strategy / program board / plan / status，确认当前工作流和 checkpoint 目标", "supervisor", "每轮开始前"),
        ("2", "推进执行线", "执行当前切片，保持任务板、验证入口和控制面一致", "delivery worker", "每轮主体"),
        ("3", "运行验证并刷新真相", "运行 gate / tests，并刷新 status / progress / continue / handoff", "delivery worker", "每轮验证后"),
        ("4", "决定继续 / 升级 / 暂停", "根据信号、blocker 和升级边界决定下一轮动作", "supervisor", "每轮收口时"),
        ("5", "记录 rollout 摩擦", "把跨 repo 的真实摩擦、supporting backlog 回流建议和下一里程碑候选沉淀出来", "supervisor + docs-and-release", "每个 adoption checkpoint"),
    ]
    lines = ["| Order | Checkpoint | What Happens | Owner | When |", "| --- | --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in rows)
    return "\n".join(lines)


def automatic_continue_table() -> str:
    rows = [
        ("已批准方向内的实现与验证", "continue automatically", "当前切片仍在既定方向内，验证通过，且没有新的用户级取舍"),
        ("黄色信号但可在既有方向内收口", "raise but continue", "保留风险可见性，继续当前 checkpoint，并要求下一轮复核"),
        ("出现新的 rollout 摩擦但尚未跨到业务裁决", "raise but continue", "先记进 strategy / program board / delivery-supervision，再继续"),
        ("方向、兼容性、定位、成本 / 时间边界变化", "require user decision", "立即停止自动继续，升级给人类"),
        ("验证失败或 release gate 退红", "raise but continue", "先停在当前 checkpoint，修复后再决定是否继续"),
    ]
    lines = ["| Situation | Gate | Why |", "| --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return "\n".join(lines)


def escalation_timing_table() -> str:
    rows = [
        ("开始新一轮长任务前", "检查是否仍在已批准方向内；否则升级", "supervisor"),
        ("每轮验证之后", "根据 gate / blocker / architecture signal 决定继续还是先提醒", "delivery worker + supervisor"),
        ("出现重复 rollout 摩擦时", "考虑是否需要新的 milestone、治理专项或 supporting backlog 回流", "supervisor"),
        ("准备 release / tag 之前", "必须重新确认 release gate、blockers、devlog capture 和 supervision state 都是绿色", "docs-and-release"),
    ]
    lines = ["| When | Required Decision | Owner |", "| --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return "\n".join(lines)


def executor_loop_table() -> str:
    rows = [
        ("supervisor", "strategy + program board + delivery supervision + status", "确认当前 checkpoint、升级边界和下一轮入口", "done"),
        ("delivery worker", "active slice + execution tasks + validator outputs", "推进当前长任务、运行验证、刷新真相", "done"),
        ("docs-and-release", "README + roadmap + development-plan + handoff + release gates", "保持维护者文档、交接和发布面一致", "done"),
    ]
    lines = ["| Executor | Current Input | Responsibility | Status |", "| --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return "\n".join(lines)


def backlog_reentry_table() -> str:
    rows = [
        ("M8 locale-aware internal output", "只有 rollout 证据证明中文优先维护流程仍被冗余英文显著拖慢，且不会分叉真相时，才允许回流", "先保持在 supporting backlog"),
        ("M9 slimmer continue snapshot", "只有 post-M14 rollout 仍显示 `continue` 输出过重，并且不损失恢复精度时，才允许回流", "先保持在 supporting backlog"),
        ("future rollout friction", "只有当同类摩擦跨多个 repo 反复出现时，才升级成新的正式里程碑", "先记录为 rollout evidence"),
    ]
    lines = ["| Topic | Re-entry Rule | Current Position |", "| --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return "\n".join(lines)


def next_checks(repo: Path) -> list[str]:
    existing = parse_delivery_supervision(repo).get("next_checks", [])
    if existing:
        return existing
    return [
        "在更多 medium / large 仓库上使用完整的 PTL supervision + worker handoff 工作模型，并记录 rollout 摩擦。",
        "根据真实 rollout 证据决定 `M8 / M9` 是否继续保持在 supporting backlog。",
        "当 cross-repo adoption 证据足够时，再决定是否需要 `M15` 或新的 post-M14 里程碑。",
    ]


def render_delivery_supervision(repo: Path) -> str:
    direction, status, why_now = delivery_direction(repo)
    lines = [
        "# Delivery Supervision",
        "",
        "## Current Delivery Direction",
        "",
        f"- Direction: `{direction}`",
        f"- Status: `{status}`",
        f"- Why Now: {why_now}",
        "",
        "## Supervised Delivery Contract",
        "",
    ]
    lines.extend(f"- {item}" for item in delivery_contract())
    lines.extend(
        [
            "",
            "## Checkpoint Rhythm",
            "",
            checkpoint_rhythm_table(),
            "",
            "## Automatic Continue Boundaries",
            "",
            automatic_continue_table(),
            "",
            "## Escalation Timing",
            "",
            escalation_timing_table(),
            "",
            "## Executor Supervision Loop",
            "",
            executor_loop_table(),
            "",
            "## Backlog Re-entry Policy",
            "",
            backlog_reentry_table(),
            "",
            "## Next Delivery Checks",
            "",
        ]
    )
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(next_checks(repo), start=1))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or refresh a durable delivery-supervision surface when M12 is expected.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/delivery-supervision.md"
    if not delivery_supervision_expected(repo):
        if path.exists():
            print(".codex/delivery-supervision.md already exists; no delivery sync needed")
        else:
            print("delivery supervision surface not expected for this repo")
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    text = read_text(path)
    if not text:
        path.write_text(render_delivery_supervision(repo), encoding="utf-8")
        print(".codex/delivery-supervision.md")
        return 0

    rendered = render_delivery_supervision(repo)
    always_refresh = {"Current Delivery Direction", "Next Delivery Checks"}
    for heading in [
        "Current Delivery Direction",
        "Supervised Delivery Contract",
        "Checkpoint Rhythm",
        "Automatic Continue Boundaries",
        "Escalation Timing",
        "Executor Supervision Loop",
        "Backlog Re-entry Policy",
        "Next Delivery Checks",
    ]:
        body = section(rendered, heading)
        if heading in always_refresh or not section(text, heading).strip():
            text = replace_section(text, heading, body)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(".codex/delivery-supervision.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
