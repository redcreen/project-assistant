#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from control_surface_lib import is_skill_repo
from daemon_validation_lib import enqueue_and_wait, read_task_output, start_clean_daemon, stop_daemon


def validate(repo: Path) -> dict[str, object]:
    repo = repo.resolve()
    if not is_skill_repo(repo):
        return {"ok": True, "repo": str(repo), "skipped": True, "reason": "non-skill repo"}

    with tempfile.TemporaryDirectory(prefix="project-assistant-daemon-host-") as temp_dir:
        test_repo = Path(temp_dir) / "fixture"
        test_repo.mkdir(parents=True, exist_ok=True)
        (test_repo / "README.md").write_text("# Fixture\n", encoding="utf-8")
        start_clean_daemon(test_repo)
        try:
            bootstrap = enqueue_and_wait(test_repo, "bootstrap", timeout_seconds=60)
            assert bootstrap["status"] == "completed", "bootstrap failed"
            assert (test_repo / ".codex/status.md").exists(), "bootstrap did not create control surface"

            retrofit = enqueue_and_wait(test_repo, "retrofit", timeout_seconds=60)
            docs_retrofit = enqueue_and_wait(test_repo, "docs-retrofit", timeout_seconds=60)
            validate_fast = enqueue_and_wait(test_repo, "validate-fast", timeout_seconds=60)
            progress = enqueue_and_wait(test_repo, "progress", timeout_seconds=60)
            continue_task = enqueue_and_wait(test_repo, "continue", timeout_seconds=60)
            handoff = enqueue_and_wait(test_repo, "handoff", timeout_seconds=60)

            assert "ok: True" in read_task_output(validate_fast), "validate-fast did not pass"
            assert "# 项目进展" in read_task_output(progress), "progress output missing heading"
            assert "# 项目助手继续" in read_task_output(continue_task), "continue output missing heading"
            assert "# 项目助手交接" in read_task_output(handoff), "handoff output missing heading"

            return {
                "ok": True,
                "repo": str(repo),
                "fixtureRepo": str(test_repo),
                "tasks": {
                    "bootstrap": bootstrap["taskId"],
                    "retrofit": retrofit["taskId"],
                    "docs-retrofit": docs_retrofit["taskId"],
                    "validate-fast": validate_fast["taskId"],
                    "progress": progress["taskId"],
                    "continue": continue_task["taskId"],
                    "handoff": handoff["taskId"],
                },
            }
        finally:
            stop_daemon(test_repo)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the daemon-host MVP baseline on a local fixture workspace.")
    parser.add_argument("repo", type=Path)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    result = validate(args.repo)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if result.get("skipped"):
            print(f"ok: True\nskip: {result['reason']}")
        else:
            print(f"fixture: {result['fixtureRepo']}")
            for name, task_id in result["tasks"].items():
                print(f"{name}: {task_id}")
            print(f"ok: {result['ok']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
