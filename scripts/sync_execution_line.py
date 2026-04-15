#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from control_surface_lib import classify_architecture_signal, labeled_bullet_value, latest_devlog_entry, read_text, section


def replace_section(text: str, heading: str, body: str) -> str:
    pattern = rf"(^## {re.escape(heading)}\n)(.*?)(?=^## |\Z)"
    replacement = rf"\1{body.rstrip()}\n\n"
    updated, count = re.subn(pattern, replacement, text, flags=re.MULTILINE | re.DOTALL)
    if count:
        return updated.rstrip() + "\n"
    return text.rstrip() + f"\n\n## {heading}\n{body.rstrip()}\n"


def parse_slices(plan_text: str) -> dict[str, dict[str, str]]:
    slices_section = section(plan_text, "Slices")
    result: dict[str, dict[str, str]] = {}
    current_name = ""
    current_lines: list[str] = []
    for raw_line in slices_section.splitlines():
        line = raw_line.rstrip()
        if line.strip().startswith("- Slice:"):
            if current_name:
                result[current_name] = parse_slice_block(current_lines)
            current_name = line.strip().split(":", 1)[1].strip().strip("`")
            current_lines = []
        elif current_name:
            current_lines.append(line)
    if current_name:
        result[current_name] = parse_slice_block(current_lines)
    return result


def parse_slice_block(lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_key = ""
    buffer: list[str] = []
    for line in lines:
        stripped = line.strip()
        match = re.match(r"^- ([A-Za-z /-]+):\s*(.*)$", stripped)
        if match:
            if current_key:
                fields[current_key] = "\n".join(buffer).strip()
            current_key = match.group(1).strip()
            first_value = match.group(2).strip()
            buffer = [first_value] if first_value else []
        elif current_key:
            buffer.append(stripped)
    if current_key:
        fields[current_key] = "\n".join(buffer).strip()
    return fields


def choose_slice_name(plan_text: str, status_text: str, explicit_slice: str | None) -> str:
    if explicit_slice:
        return explicit_slice
    link = labeled_bullet_value(section(status_text, "Current Execution Line"), "Plan Link")
    if link:
        return link
    active_slice = section(status_text, "Active Slice").strip().strip("`")
    return active_slice


STOP_WORDS = {
    "slice",
    "the",
    "and",
    "or",
    "for",
    "to",
    "of",
    "next",
    "current",
    "plan",
    "advance",
    "implement",
    "add",
    "align",
    "define",
    "stabilize",
    "unify",
}


def normalize_words(text: str) -> set[str]:
    return {
        word
        for word in re.findall(r"[a-z0-9]+", text.lower())
        if word and word not in STOP_WORDS
    }


def resolve_slice_name(candidate: str, slices: dict[str, dict[str, str]]) -> str | None:
    if candidate in slices:
        return candidate
    candidate_words = normalize_words(candidate)
    if not candidate_words:
        return None
    best_name = None
    best_score = 0
    for name in slices:
        words = normalize_words(name)
        score = len(candidate_words & words)
        if score > best_score:
            best_name = name
            best_score = score
    if best_name and best_score >= 2:
        return best_name
    return None


def default_validation_text(fields: dict[str, str]) -> str:
    return fields.get("Validation") or "run the primary validation for the slice"


def build_tasks(slice_name: str, fields: dict[str, str]) -> list[str]:
    objective = fields.get("Objective", slice_name)
    validation = default_validation_text(fields)
    dependencies = fields.get("Dependencies", "affected boundaries and required inputs")
    risks = fields.get("Risks", "local fixes drifting away from the intended direction")
    return [
        f"[ ] EL-1 confirm the checkpoint and objective for `{slice_name}`: {objective}",
        f"[ ] EL-2 verify dependencies and affected boundaries: {dependencies}",
        "[ ] EL-3 confirm architecture signal, root-cause hypothesis, and correct layer still hold",
        f"[ ] EL-4 implement the highest-value change for `{slice_name}`",
        f"[ ] EL-5 address the main execution risk: {risks}",
        "[ ] EL-6 update docs, control-surface notes, or contracts touched by this slice",
        f"[ ] EL-7 run validation: {validation}",
        "[ ] EL-8 refresh progress, capabilities, next checkpoint, and next 3 actions",
        "[ ] EL-9 capture a devlog entry if the root cause, tradeoff, or rejected shortcut changed",
    ]


def build_execution_line_body(slice_name: str, fields: dict[str, str]) -> str:
    objective = fields.get("Objective", slice_name)
    validation = default_validation_text(fields)
    return "\n".join(
        [
            f"- Objective: {objective}",
            f"- Plan Link: {slice_name}",
            "- Runway: one active-slice checkpoint covering implementation, validation, and state refresh",
            "- Progress: 0 / 9 tasks complete",
            "- Stop Conditions:",
            "  - blocker requires human direction",
            "  - validation fails and changes the direction",
            "  - business, compatibility, or cost decision requires user judgment",
            f"- Validation: {validation}",
        ]
    )


def build_status_execution_line_body(slice_name: str, fields: dict[str, str]) -> str:
    objective = fields.get("Objective", slice_name)
    return "\n".join(
        [
            f"- Objective: {objective}",
            f"- Plan Link: {slice_name}",
            "- Runway: one active-slice checkpoint covering implementation, validation, and state refresh",
            "- Progress: 0 / 9 tasks complete",
            "- Stop Conditions:",
            "  - blocker requires human direction",
            "  - validation fails and changes the direction",
            "  - business, compatibility, or cost decision requires user judgment",
        ]
    )


def build_devlog_plan_body() -> str:
    return "\n".join(
        [
            "- Trigger Level: high",
            "- Auto-Capture When:",
            "  - the root-cause hypothesis changes",
            "  - a reusable mechanism replaces repeated local fixes",
            "  - a retrofit changes governance, architecture, or release policy",
            "  - a tradeoff or rejected shortcut is likely to matter in future work",
            "- Skip When:",
            "  - the change is mechanical or formatting-only",
            "  - no durable reasoning changed",
            "  - the work simply followed an already-approved path",
            "  - the change stayed local and introduced no durable tradeoff",
        ]
    )


def build_devlog_status_body(repo: Path) -> str:
    latest_name = latest_devlog_entry(repo) or "none"
    return "\n".join(
        [
            "- Trigger Level: high",
            "- Pending Capture: no",
            f"- Last Entry: {latest_name}",
        ]
    )


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
    parser = argparse.ArgumentParser(description="Generate a longer execution-line task board from the active slice.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--slice", help="Explicit slice name to generate from")
    parser.add_argument("--force", action="store_true", help="Replace the current execution board even if one already exists")
    args = parser.parse_args()

    repo = args.repo.resolve()
    plan_path = repo / ".codex/plan.md"
    status_path = repo / ".codex/status.md"
    plan_text = read_text(plan_path)
    status_text = read_text(status_path)
    if not plan_text or not status_text:
        raise SystemExit("plan.md and status.md must exist before generating an execution line")

    current_tasks = section(status_text, "Execution Tasks")
    if current_tasks.strip() and not args.force:
        raise SystemExit("execution task board already exists; rerun with --force to replace it")

    slices = parse_slices(plan_text)
    slice_name = choose_slice_name(plan_text, status_text, args.slice)
    resolved_name = resolve_slice_name(slice_name, slices)
    fields = slices.get(resolved_name or slice_name)
    if not fields:
        available = ", ".join(sorted(slices)) or "(none)"
        raise SystemExit(f"could not find slice '{slice_name}'. available slices: {available}")
    slice_name = resolved_name or slice_name

    tasks = build_tasks(slice_name, fields)
    plan_text = replace_section(plan_text, "Current Execution Line", build_execution_line_body(slice_name, fields))
    plan_text = replace_section(plan_text, "Execution Tasks", "\n".join(f"- {task}" if not task.startswith("- ") else task for task in tasks))
    if "## Development Log Capture" in plan_text:
        plan_text = replace_section(plan_text, "Development Log Capture", build_devlog_plan_body())

    status_text = replace_section(status_text, "Active Slice", f"`{slice_name}`")
    status_text = replace_section(status_text, "Current Execution Line", build_status_execution_line_body(slice_name, fields))
    status_text = replace_section(status_text, "Execution Tasks", "\n".join(f"- {task}" if not task.startswith("- ") else task for task in tasks))
    if "## Development Log Capture" in status_text:
        status_text = replace_section(status_text, "Development Log Capture", build_devlog_status_body(repo))

    plan_path.write_text(plan_text, encoding="utf-8")
    status_path.write_text(status_text, encoding="utf-8")
    subprocess.run([sys.executable, str(Path(__file__).with_name("sync_plan_docs.py")), str(repo)], check=True)
    state = classify_architecture_signal(repo)
    plan_text = replace_section(plan_text, "Architecture Supervision", plan_architecture_body(state))
    status_text = replace_section(status_text, "Architecture Supervision", status_architecture_body(state))
    status_text = replace_section(status_text, "Current Escalation State", escalation_body(state))
    plan_path.write_text(plan_text, encoding="utf-8")
    status_path.write_text(status_text, encoding="utf-8")
    print(f"generated execution board for slice: {slice_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
