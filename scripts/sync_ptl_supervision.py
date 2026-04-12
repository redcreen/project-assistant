#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import (
    first_line,
    labeled_bullet_value,
    parse_ptl_supervision,
    ptl_supervision_expected,
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


def ptl_direction(repo: Path) -> tuple[str, str, str]:
    plan_text = read_text(repo / ".codex/plan.md")
    status_text = read_text(repo / ".codex/status.md")
    current_phase = first_line(section(status_text, "Current Phase")) or first_line(section(plan_text, "Current Phase"))
    objective = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective") or labeled_bullet_value(
        section(plan_text, "Current Execution Line"), "Objective"
    )
    lowered = current_phase.lower()
    status = "active"
    if any(token in lowered for token in ["closed", "收口", "queued", "later", "later layer", "evidence-gated"]):
        status = "done"
    elif "next" in lowered:
        status = "next"
    direction = "PTL supervision loop"
    why_now = "M12 已经把长期受监督交付层变成 durable 真相；现在需要让 PTL 以周期性 / 事件驱动的监督环持续接管推进，而不是只在聊天里偶尔出现。"
    if objective:
        why_now = objective
    return direction, status, why_now


def supervision_contract() -> list[str]:
    return [
        "PTL 监督环必须读取 `.codex/strategy.md`、`.codex/program-board.md`、`.codex/delivery-supervision.md`、`.codex/plan.md` 和 `.codex/status.md`，不能只凭聊天上下文判断是否继续。",
        "PTL 负责决定何时继续、何时重排、何时先提醒后继续、何时必须升级给人类；它不负责越权修改业务方向。",
        "每次 worker 停下、checkpoint 结束、验证失败或超时后，PTL 都必须重新做一次监督判断。",
        "PTL 的监督循环必须把结论写回 durable 真相，而不是只在聊天里说一句“继续”。",
        "只要问题跨到业务方向、兼容性承诺、外部定位或显著成本 / 时间边界，PTL 就必须停止自动继续并升级给人类。",
    ]


def trigger_table() -> str:
    rows = [
        ("周期巡检", "到达下一次 checkpoint 节点", "读取 strategy / program-board / delivery-supervision / status", "确认继续还是重排"),
        ("worker 停下", "当前 worker 正常结束、超时、失败或显式交接", "接管剩余工作判断", "决定继续 / 回流 / 升级"),
        ("验证变化", "gate、tests、release readiness 或 architecture signal 变化", "重新判断升级边界", "决定是否继续当前线"),
        ("计划变化", "active slice 完成、主线切换或 supporting backlog 回流", "重读 program board", "决定下一条线"),
        ("用户裁决", "人类修改业务方向、优先级或重大取舍", "更新监督基线", "重新生成下一轮监督判断"),
    ]
    lines = ["| Trigger | 何时触发 | PTL 要做什么 | 产出 |", "| --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return "\n".join(lines)


def responsibilities_table() -> str:
    rows = [
        ("PTL", "strategy + program-board + delivery-supervision + status", "持续巡检项目、判断继续/重排/升级、把监督结论写回 durable 真相"),
        ("delivery worker", "active slice + execution tasks + validator outputs", "推进当前写入线并在 checkpoint 后把结果交回监督环"),
        ("docs-and-release", "README + roadmap + development-plan + gate outputs", "保持维护者文档、交接和门禁与 PTL 判断一致"),
    ]
    lines = ["| 角色 | 主要输入 | 责任 |", "| --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return "\n".join(lines)


def supervision_matrix() -> str:
    rows = [
        ("当前方向内、验证通过、无新 blocker", "继续", "自动继续当前线", "保持节奏不因人工缺席而中断"),
        ("黄色信号但仍在既定方向内", "提醒后继续", "记录风险并继续到下个 checkpoint", "保持可见性而不把项目停住"),
        ("active slice 完成或优先级变化", "重排", "切换 program-board 顺序并刷新当前执行线", "让主线和 supporting backlog 保持同一套调度真相"),
        ("出现业务方向 / 兼容性 / 成本边界变化", "升级", "停止自动继续并通知人类裁决", "防止 PTL 越权"),
    ]
    lines = ["| 情况 | PTL 动作 | 具体处理 | 为什么 |", "| --- | --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in rows)
    return "\n".join(lines)


def active_checks_table() -> str:
    rows = [
        ("监督输入完整", "green", "strategy / program-board / delivery-supervision / plan / status 都存在"),
        ("继续边界清楚", "green", "何时继续 / 提醒 / 升级已有 durable 规则"),
        ("worker 停下后的接管入口", "green", "M14 已经把 handoff / re-entry contract 收口成 durable 真相"),
        ("业务裁决越权防护", "green", "一旦跨到产品方向或兼容性承诺，PTL 只升级不代替决策"),
    ]
    lines = ["| 检查项 | 当前信号 | 说明 |", "| --- | --- | --- |"]
    lines.extend(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return "\n".join(lines)


def next_checks(repo: Path) -> list[str]:
    existing = parse_ptl_supervision(repo).get("next_checks", [])
    if existing:
        return existing
    return [
        "在真实 repo 上继续验证 PTL 监督判断会在 worker 停下后接住项目，而不是只在 skill 自己身上成立。",
        "继续观察 worker handoff / re-entry 是否还暴露新的 durable 缺口，需要回写到 supervision contract。",
        "继续收集跨 repo 证据，判断何时才值得打开 M15 多执行器层。",
    ]


def render_ptl_supervision(repo: Path) -> str:
    direction, status, why_now = ptl_direction(repo)
    lines = [
        "# PTL Supervision",
        "",
        "## Current PTL Direction",
        "",
        f"- Direction: `{direction}`",
        f"- Status: `{status}`",
        f"- Why Now: {why_now}",
        "",
        "## PTL Supervision Contract",
        "",
    ]
    lines.extend(f"- {item}" for item in supervision_contract())
    lines.extend(
        [
            "",
            "## Supervision Triggers",
            "",
            trigger_table(),
            "",
            "## Standing Responsibilities",
            "",
            responsibilities_table(),
            "",
            "## Continue / Resequence / Escalate Matrix",
            "",
            supervision_matrix(),
            "",
            "## Active Supervision Checks",
            "",
            active_checks_table(),
            "",
            "## Next PTL Checks",
            "",
        ]
    )
    lines.extend(f"{idx}. {item}" for idx, item in enumerate(next_checks(repo), start=1))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or refresh a durable PTL supervision surface when M13 is expected.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    path = repo / ".codex/ptl-supervision.md"
    if not ptl_supervision_expected(repo):
        if path.exists():
            print(".codex/ptl-supervision.md already exists; no PTL sync needed")
        else:
            print("ptl supervision surface not expected for this repo")
        return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    text = read_text(path)
    if not text:
        path.write_text(render_ptl_supervision(repo), encoding="utf-8")
        print(".codex/ptl-supervision.md")
        return 0

    rendered = render_ptl_supervision(repo)
    always_refresh = {"Current PTL Direction", "Next PTL Checks"}
    for heading in [
        "Current PTL Direction",
        "PTL Supervision Contract",
        "Supervision Triggers",
        "Standing Responsibilities",
        "Continue / Resequence / Escalate Matrix",
        "Active Supervision Checks",
        "Next PTL Checks",
    ]:
        body = section(rendered, heading)
        if heading in always_refresh or not section(text, heading).strip():
            text = replace_section(text, heading, body)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    print(".codex/ptl-supervision.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
