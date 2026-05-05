#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from typing import Any


SCHEMA = "project-assistant.completion-gate.v1"
OUTPUT_FILE = Path(".codex/completion-gate.json")

STOP_REASONS = {"complete", "blocked", "requires-human-decision", "explicitly-deferred"}
REQUIRED_NEXT_MARKERS = [
    "下一步",
    "还需要",
    "仍需",
    "需要继续",
    "后续需要",
    "next step",
    "still need",
    "still needs",
    "remaining",
    "not yet",
    "pending",
]
DEFERRED_MARKERS = [
    "optional",
    "deferred",
    "explicitly deferred",
    "later",
    "candidate",
    "backlog",
    "evidence-gated",
    "可选",
    "延期",
    "显式延期",
    "候选",
    "后续可选",
    "证据驱动",
    "不是本轮",
]


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def rel(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def is_deferred_line(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in DEFERRED_MARKERS)


def section(text: str, heading: str) -> str:
    target = f"## {heading}".lower()
    lines = text.splitlines()
    capture = False
    body: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## "):
            if capture:
                break
            capture = stripped.lower() == target
            continue
        if capture:
            body.append(line)
    return "\n".join(body).strip()


def labeled_value(text: str, label: str) -> str:
    prefix = f"- {label}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(prefix.lower()):
            return stripped[len(prefix) :].strip().strip("`")
    return ""


def current_phase(text: str) -> str:
    body = section(text, "Current Phase")
    for line in body.splitlines():
        stripped = line.strip().strip("`")
        if stripped:
            return stripped
    return "unknown"


def parse_open_tasks(text: str) -> list[str]:
    tasks: list[str] = []
    in_execution_tasks = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## "):
            in_execution_tasks = stripped == "## Execution Tasks"
            continue
        if in_execution_tasks and stripped.startswith("- [ ] "):
            task = stripped[6:].strip()
            if not is_deferred_line(task):
                tasks.append(task)
    return tasks


def parse_progress_hits(text: str, source: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    current_execution = section(text, "Current Execution Line")
    progress = labeled_value(current_execution, "Progress")
    if not progress:
        return hits
    match = re.search(r"(\d+)\s*/\s*(\d+)", progress)
    if not match:
        return hits
    done, total = int(match.group(1)), int(match.group(2))
    if total > done:
        hits.append(
            {
                "ruleId": "project-assistant.completion.progress-incomplete",
                "decision": "require-continue",
                "reason": "current execution progress is incomplete",
                "evidence": [f"{source}: {done} / {total}"],
            }
        )
    return hits


def escalation_requires_human(*texts: str) -> list[dict[str, Any]]:
    joined = "\n".join(texts)
    gate = labeled_value(joined, "Escalation Gate") or labeled_value(joined, "Current Gate")
    signal = labeled_value(joined, "Signal")
    if "require user" in gate.lower() or "require-review" in gate.lower() or signal.lower() == "red":
        return [
            {
                "ruleId": "project-assistant.completion.requires-human-decision",
                "decision": "requires-human-decision",
                "reason": "current escalation state requires human decision before stopping as complete",
                "evidence": [f"signal={signal or 'unknown'}", f"gate={gate or 'unknown'}"],
            }
        ]
    return []


def final_text_hits(final_text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for line in final_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lowered = stripped.lower()
        if any(marker in lowered for marker in REQUIRED_NEXT_MARKERS) and not is_deferred_line(stripped):
            hits.append(
                {
                    "ruleId": "project-assistant.completion.final-answer-known-next-step",
                    "decision": "require-continue",
                    "reason": "final answer contains a known required next step; continue instead of declaring completion",
                    "evidence": [stripped[:220]],
                }
            )
    return hits


def required_continuation_hits(repo: Path, plan_text: str, status_text: str, final_text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for source, text in [(".codex/plan.md", plan_text), (".codex/status.md", status_text)]:
        open_tasks = parse_open_tasks(text)
        if open_tasks:
            hits.append(
                {
                    "ruleId": "project-assistant.completion.open-execution-tasks",
                    "decision": "require-continue",
                    "reason": "execution task board still contains required open tasks",
                    "evidence": [f"{source}: {task}" for task in open_tasks[:8]],
                }
            )
        hits.extend(parse_progress_hits(text, source))
    hits.extend(final_text_hits(final_text))
    return hits


def evaluate(repo: Path, *, mode: str, stop_reason: str | None = None, final_text: str = "") -> dict[str, Any]:
    repo = repo.resolve()
    plan_text = read_text(repo / ".codex/plan.md")
    status_text = read_text(repo / ".codex/status.md")
    human_hits = escalation_requires_human(plan_text, status_text)
    continuation_hits = required_continuation_hits(repo, plan_text, status_text, final_text)

    if stop_reason and stop_reason not in STOP_REASONS:
        raise ValueError(f"unsupported stop reason: {stop_reason}")

    if stop_reason == "blocked":
        decision = "blocked"
        hits = [
            {
                "ruleId": "project-assistant.completion.blocked-stop",
                "decision": "blocked",
                "reason": "stop reason is an explicit blocker",
                "evidence": [],
            }
        ]
    elif stop_reason == "requires-human-decision" or human_hits:
        decision = "requires-human-decision"
        hits = human_hits
    elif continuation_hits and stop_reason != "explicitly-deferred":
        decision = "require-continue"
        hits = continuation_hits
    elif stop_reason == "explicitly-deferred":
        decision = "explicitly-deferred"
        hits = [
            {
                "ruleId": "project-assistant.completion.explicitly-deferred-stop",
                "decision": "explicitly-deferred",
                "reason": "remaining work was explicitly deferred by the user or objective contract",
                "evidence": [],
            }
        ]
    else:
        decision = "allow"
        hits = []

    payload = {
        "schema": SCHEMA,
        "generatedAt": iso_now(),
        "project": repo.name,
        "mode": mode,
        "decision": decision,
        "signal": "red" if decision == "blocked" else "yellow" if decision != "allow" else "green",
        "stopReason": stop_reason or "not-provided",
        "currentPhase": current_phase(status_text) if status_text else current_phase(plan_text),
        "policy": "No known required next step may be left as a final-answer follow-up unless it is blocked, requires human decision, or explicitly deferred.",
        "outputPath": OUTPUT_FILE.as_posix(),
        "sourceDocuments": [rel(path, repo) for path in [repo / ".codex/plan.md", repo / ".codex/status.md"] if path.exists()],
        "hits": hits,
    }
    write_json(repo / OUTPUT_FILE, payload)
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    hits = payload.get("hits") if isinstance(payload.get("hits"), list) else []
    lines = [
        "## Completion Gate",
        "",
        "| 项目 | 当前值 |",
        "| --- | --- |",
        f"| Decision | `{payload.get('decision')}` |",
        f"| Signal | `{payload.get('signal')}` |",
        f"| Stop Reason | `{payload.get('stopReason')}` |",
        f"| Current Phase | `{payload.get('currentPhase')}` |",
        f"| Output | `{payload.get('outputPath')}` |",
    ]
    if not hits:
        lines.extend(["", "没有发现会阻止本轮停下的已知必要下一步。"])
        return "\n".join(lines)
    lines.extend(["", "| Rule | Decision | Evidence |", "| --- | --- | --- |"])
    for hit in hits:
        evidence = "; ".join(str(item) for item in hit.get("evidence", [])[:4])
        lines.append(f"| `{hit.get('ruleId')}` | `{hit.get('decision')}` | {evidence or hit.get('reason', '')} |")
    return "\n".join(lines)


def exit_code(payload: dict[str, Any]) -> int:
    return 2 if payload.get("decision") == "require-continue" else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check whether project-assistant is allowed to stop instead of continuing known required work.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Inspect the current control surface for required continuation.")
    check_parser.add_argument("repo", type=Path)
    check_parser.add_argument("--json", action="store_true")

    final_parser = subparsers.add_parser("final-check", help="Validate a planned final response against the stop taxonomy.")
    final_parser.add_argument("repo", type=Path)
    final_parser.add_argument("--stop-reason", required=True, choices=sorted(STOP_REASONS))
    final_parser.add_argument("--final-text", default="")
    final_parser.add_argument("--final-text-file", type=Path)
    final_parser.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "check":
        payload = evaluate(args.repo, mode="check")
    elif args.command == "final-check":
        final_text = args.final_text
        if args.final_text_file:
            final_text = read_text(args.final_text_file)
        payload = evaluate(args.repo, mode="final-check", stop_reason=args.stop_reason, final_text=final_text)
    else:
        raise SystemExit(f"unsupported command: {args.command}")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(payload))
    return exit_code(payload)


if __name__ == "__main__":
    raise SystemExit(main())
