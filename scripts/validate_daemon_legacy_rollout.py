#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from control_surface_lib import control_surface_version_state, is_skill_repo, parse_tier
from daemon_validation_lib import downgrade_control_surface, enqueue_and_wait, read_task_output, start_clean_daemon, stop_daemon


def validate(repo: Path) -> dict[str, object]:
    repo = repo.resolve()
    if not is_skill_repo(repo):
        return {"ok": True, "repo": str(repo), "skipped": True, "reason": "non-skill repo"}

    with tempfile.TemporaryDirectory(prefix="project-assistant-legacy-rollout-") as temp_dir:
        legacy_repo = Path(temp_dir) / "legacy-fixture"
        legacy_repo.mkdir(parents=True, exist_ok=True)
        (legacy_repo / "README.md").write_text("# Legacy Fixture\n", encoding="utf-8")
        start_clean_daemon(legacy_repo)
        try:
            bootstrap = enqueue_and_wait(legacy_repo, "bootstrap", timeout_seconds=60)
            assert bootstrap["status"] == "completed", "bootstrap failed"
            downgrade_control_surface(legacy_repo)

            continue_task = enqueue_and_wait(legacy_repo, "continue", timeout_seconds=60)
            progress = enqueue_and_wait(legacy_repo, "progress", timeout_seconds=60)
            handoff = enqueue_and_wait(legacy_repo, "handoff", timeout_seconds=60)

            version_state = control_surface_version_state(legacy_repo, tier=parse_tier(legacy_repo))
            assert not version_state["needsConfigUpgrade"], "legacy repo did not auto-upgrade back to the current generation"
            assert (legacy_repo / ".codex/entry-routing.md").exists(), "entry-routing was not restored"
            assert "# 项目助手继续" in read_task_output(continue_task), "continue output missing heading"
            assert "# 项目进展" in read_task_output(progress), "progress output missing heading"
            assert "# 项目助手交接" in read_task_output(handoff), "handoff output missing heading"

            return {
                "ok": True,
                "repo": str(repo),
                "legacyRepo": str(legacy_repo),
                "continueTask": continue_task["taskId"],
                "progressTask": progress["taskId"],
                "handoffTask": handoff["taskId"],
            }
        finally:
            stop_daemon(legacy_repo)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate post-M16 rollout behavior on a downgraded legacy fixture repo through the daemon baseline.")
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
            print(f"legacyRepo: {result['legacyRepo']}")
            print(f"continue: {result['continueTask']}")
            print(f"progress: {result['progressTask']}")
            print(f"handoff: {result['handoffTask']}")
            print(f"ok: {result['ok']}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
