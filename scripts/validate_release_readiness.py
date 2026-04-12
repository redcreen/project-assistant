#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from control_surface_lib import classify_architecture_signal, labeled_bullet_value, normalized_bullets, read_text, section


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate release readiness against architecture and devlog gates.")
    parser.add_argument("repo", type=Path, help="Repository root")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    repo = args.repo.resolve()
    status_text = read_text(repo / ".codex/status.md")
    warnings: list[str] = []

    architecture_state = classify_architecture_signal(repo)
    architecture_signal = architecture_state["signal"].lower()
    escalation_gate = architecture_state["gate"].lower()
    pending_capture = labeled_bullet_value(section(status_text, "Development Log Capture"), "Pending Capture").lower()
    blockers = normalized_bullets(section(status_text, "Blockers / Open Decisions"))
    if architecture_signal != "green":
        warnings.append(f"release blocked: architecture signal is {architecture_signal}")
    if escalation_gate and escalation_gate != "continue automatically":
        warnings.append(f"release blocked: escalation gate is {escalation_gate}")
    if pending_capture in {"yes", "true", "pending"}:
        warnings.append("release blocked: development-log capture is still pending")
    if blockers:
        warnings.append("release blocked: blockers or open decisions are still recorded")

    payload = {"ok": not warnings, "warnings": warnings}
    if args.format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if warnings:
            print("warnings:")
            for item in warnings:
                print(f"- {item}")
        print(f"ok: {payload['ok']}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
