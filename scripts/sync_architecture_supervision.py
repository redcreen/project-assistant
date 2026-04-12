#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import classify_architecture_signal, read_text


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    replacement = rf"\1{body.rstrip()}\n\n"
    updated, count = re.subn(pattern, replacement, text, flags=re.MULTILINE | re.DOTALL)
    if count:
        return updated.rstrip() + "\n"
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def plan_architecture_body(state: dict[str, str]) -> str:
    return "\n".join(
        [
            f"- Signal: `{state['signal']}`",
            f"- Signal Basis: {state['signal_basis']}",
            f"- Problem Class: {state['problem_class']}",
            f"- Root Cause Hypothesis: {state['root_cause_hypothesis']}",
            f"- Correct Layer: {state['correct_layer']}",
            f"- Rejected Shortcut: {state['rejected_shortcut']}",
            f"- Automatic Review Trigger: {state['automatic_review_trigger']}",
            f"- Escalation Gate: {state['gate']}",
        ]
    )


def status_architecture_body(state: dict[str, str]) -> str:
    return "\n".join(
        [
            f"- Signal: `{state['signal']}`",
            f"- Signal Basis: {state['signal_basis']}",
            f"- Root Cause Hypothesis: {state['root_cause_hypothesis']}",
            f"- Correct Layer: {state['correct_layer']}",
            f"- Automatic Review Trigger: {state['automatic_review_trigger']}",
            f"- Escalation Gate: {state['gate']}",
        ]
    )


def escalation_body(state: dict[str, str]) -> str:
    return "\n".join(
        [
            f"- Current Gate: {state['gate']}",
            f"- Reason: {state['reason']}",
            f"- Next Review Trigger: {state['next_review_trigger']}",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh the architecture supervision and escalation state from repo context.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    plan_path = repo / ".codex/plan.md"
    status_path = repo / ".codex/status.md"
    plan_text = read_text(plan_path)
    status_text = read_text(status_path)
    if not plan_text or not status_text:
        raise SystemExit("plan.md and status.md must exist before syncing architecture supervision")

    state = classify_architecture_signal(repo)
    plan_text = replace_section(plan_text, "Architecture Supervision", plan_architecture_body(state))
    status_text = replace_section(status_text, "Architecture Supervision", status_architecture_body(state))
    status_text = replace_section(status_text, "Current Escalation State", escalation_body(state))

    plan_path.write_text(plan_text, encoding="utf-8")
    status_path.write_text(status_text, encoding="utf-8")
    print(f"signal: {state['signal']}")
    print(f"gate: {state['gate']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
