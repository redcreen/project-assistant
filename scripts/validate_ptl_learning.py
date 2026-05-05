#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_json(command: list[str], *, env: dict[str, str] | None = None, allow_block: bool = False) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, *command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        env=env,
    )
    allowed = {0, 2} if allow_block else {0}
    if result.returncode not in allowed:
        raise AssertionError(f"command failed: {command}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return json.loads(result.stdout)


def run_text(command: list[str], *, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        [sys.executable, *command],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        raise AssertionError(f"command failed: {command}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.stdout


def seed_control_surface(repo: Path) -> None:
    write(repo / ".codex/brief.md", "# Brief\n")
    write(
        repo / ".codex/plan.md",
        "# Plan\n\n## Architecture Supervision\n- Signal: `green`\n- Escalation Gate: continue automatically\n",
    )
    write(
        repo / ".codex/status.md",
        "# Status\n\n## Architecture Supervision\n- Signal: `green`\n- Escalation Gate: continue automatically\n",
    )
    write(repo / ".codex/COMMANDS.md", "# Commands\n")
    write(
        repo / ".codex/control-surface.json",
        json.dumps(
            {
                "managedBy": "project-assistant",
                "controlSurfaceVersion": 3,
                "tier": "medium",
                "requiredFiles": [
                    ".codex/brief.md",
                    ".codex/plan.md",
                    ".codex/status.md",
                    ".codex/COMMANDS.md",
                    ".codex/control-surface.json",
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )


def seed_learning_messages(repo: Path) -> None:
    messages = [
        ("msg-0001", "你不做最基础的可行性验证就干了一堆事，最后发现根本不可行。"),
        ("msg-0002", "不确定的 host/API/plugin/protocol/binary 行为要先验证，做最小 probe。"),
        ("msg-0003", "开发任务不能做一步停一步，需要一口气继续，直到 completion gate。"),
        ("msg-0004", "任务应该进入 loop / pipeline，能自动继续就自动继续。"),
        ("msg-0005", "style engine 经常出现 workaround，出图 prompt/mask/fallback 做短期不可复用行为。"),
        ("msg-0006", "不要用硬编码和短期 fallback 代替可复用主线。"),
    ]
    payload = {
        "schema": "project-assistant.message-ingress.v1",
        "project": repo.name,
        "updatedAt": "2026-05-05T00:00:00Z",
        "messages": [
            {
                "id": message_id,
                "message": message,
                "receivedAt": f"2026-05-05T00:0{index}:00Z",
                "source": "fixture",
                "taskId": f"T{index}",
            }
            for index, (message_id, message) in enumerate(messages, start=1)
        ],
    }
    write(repo / ".codex/message-ingress.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def seed_semantic_learning_messages(repo: Path) -> None:
    messages = [
        ("msg-0101", "需要人类回答时，需要给出明确的提示，回复格式要简单。"),
        ("msg-0102", "每次需要人类做什么，一定要把 pending items 和一行回复格式列清楚。"),
        ("msg-0103", "人类确认结束后，要回到 loop 里自动继续，不能让 pipeline 停住。"),
        ("msg-0104", "所有 human decision 都应该是 loop 中的 task，处理后 run-next。"),
    ]
    payload = {
        "schema": "project-assistant.message-ingress.v1",
        "project": repo.name,
        "updatedAt": "2026-05-05T00:00:00Z",
        "messages": [
            {
                "id": message_id,
                "message": message,
                "receivedAt": f"2026-05-05T01:0{index}:00Z",
                "source": "fixture",
                "taskId": f"T-semantic-{index}",
            }
            for index, (message_id, message) in enumerate(messages, start=1)
        ],
    }
    write(repo / ".codex/message-ingress.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def candidate_by_key(payload: dict[str, object], stable_key: str) -> dict[str, object]:
    for item in payload.get("candidates", []):
        if isinstance(item, dict) and item.get("stableKey") == stable_key:
            return item
    raise AssertionError(f"missing candidate: {stable_key}")


def validate_learning_review(root: Path) -> None:
    repo = root / "learning-project"
    registry = root / "persistent" / "learned-registry.json"
    seed_control_surface(repo)
    seed_learning_messages(repo)
    write(
        repo / ".codex/task-pipeline.json",
        json.dumps(
            {
                "schema": "project-assistant.task-pipeline.v1",
                "project": repo.name,
                "status": "active",
                "activeTaskId": None,
                "tasks": [],
                "history": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )

    scan = run_json([str(SCRIPT_DIR / "ptl_learning.py"), "scan", str(repo), "--registry", str(registry), "--json"])
    pending = [item for item in scan.get("candidates", []) if isinstance(item, dict) and item.get("status") == "candidate"]
    if len(pending) < 3:
        raise AssertionError(f"expected at least 3 pending candidates, got {len(pending)}")
    pipeline = json.loads((repo / ".codex/task-pipeline.json").read_text(encoding="utf-8"))
    review_task = next((item for item in pipeline.get("tasks", []) if item.get("id") == "PTL-LEARNING-REVIEW"), None)
    if not review_task or review_task.get("kind") != "human-decision" or review_task.get("status") != "pending":
        raise AssertionError("PTL learning scan did not create a pending human-decision task")
    run_result = run_json([str(SCRIPT_DIR / "pipeline_runner.py"), "run", str(repo), "--max-steps", "1", "--json"])
    if run_result.get("state", {}).get("status") != "requires-human-decision":
        raise AssertionError("human review task did not pause the pipeline for human decision")
    brief = run_result.get("events", [{}])[-1].get("brief", "")
    if "# 需要你确认" not in brief or "## 需要人类做什么" not in brief or "## 待确认规则" not in brief or "全部接受" not in brief:
        raise AssertionError("human review prompt is not clear enough")
    pending_panel = run_text([str(SCRIPT_DIR / "ptl_learning.py"), "panel", str(repo), "--registry", str(registry)])
    if "# 需要你确认" not in pending_panel or "## 需要人类做什么" not in pending_panel or "`全部接受`" not in pending_panel or "## 详情（可选）" not in pending_panel:
        raise AssertionError("pending review panel did not render a clear human prompt")

    feasibility = candidate_by_key(scan, "correction.feasibility-first")
    pipeline_candidate = candidate_by_key(scan, "correction.pipeline-continuity")
    workaround = candidate_by_key(scan, "correction.anti-workaround-reuse")

    run_json(
        [
            str(SCRIPT_DIR / "ptl_learning.py"),
            "accept",
            str(repo),
            "--registry",
            str(registry),
            "--id",
            str(feasibility["id"]),
            "--decision",
            "warn",
            "--scope",
            "user-global",
            "--json",
        ]
    )
    run_json(
        [
            str(SCRIPT_DIR / "ptl_learning.py"),
            "reject",
            str(repo),
            "--registry",
            str(registry),
            "--id",
            str(workaround["id"]),
            "--reason",
            "fixture reject",
            "--json",
        ]
    )
    run_json(
        [
            str(SCRIPT_DIR / "ptl_learning.py"),
            "snooze",
            str(repo),
            "--registry",
            str(registry),
            "--id",
            str(pipeline_candidate["id"]),
            "--days",
            "7",
            "--json",
        ]
    )
    pipeline = json.loads((repo / ".codex/task-pipeline.json").read_text(encoding="utf-8"))
    review_task = next((item for item in pipeline.get("tasks", []) if item.get("id") == "PTL-LEARNING-REVIEW"), None)
    if not review_task or review_task.get("status") != "done":
        raise AssertionError("PTL learning human-decision task was not closed after all candidates were reviewed")

    if not registry.exists():
        raise AssertionError("accepted rule did not write persistent learned registry")
    if repo.resolve() in registry.resolve().parents:
        raise AssertionError("learned registry should not be inside the project repo")
    registry_payload = json.loads(registry.read_text(encoding="utf-8"))
    accepted = [item for item in registry_payload.get("rules", []) if item.get("status") == "accepted"]
    if len(accepted) != 1:
        raise AssertionError(f"expected 1 accepted registry rule, got {len(accepted)}")

    review = json.loads((repo / ".codex/ptl-policy/learning-review.json").read_text(encoding="utf-8"))
    statuses = {item["stableKey"]: item["status"] for item in review.get("candidates", [])}
    if statuses.get("correction.feasibility-first") != "accepted":
        raise AssertionError("accepted candidate did not persist in local review")
    if statuses.get("correction.anti-workaround-reuse") != "rejected":
        raise AssertionError("rejected candidate did not persist in local review")
    if statuses.get("correction.pipeline-continuity") != "snoozed":
        raise AssertionError("snoozed candidate did not persist in local review")

    pipeline["activeTaskId"] = "T-feasible"
    pipeline["tasks"].append(
        {
            "id": "T-feasible",
            "title": "execute: uncertain host behavior",
            "metadata": {"rawMessage": "这个任务有可行性风险，先做最小 probe。"},
        }
    )
    write(repo / ".codex/task-pipeline.json", json.dumps(pipeline, ensure_ascii=False, indent=2) + "\n")
    env = {**os.environ, "PROJECT_ASSISTANT_LEARNED_REGISTRY": str(registry)}
    preflight = run_json([str(SCRIPT_DIR / "ptl_gate.py"), "preflight", str(repo), "--mode", "continue", "--json"], env=env, allow_block=True)
    if preflight.get("learnedRuleCount") != 1:
        raise AssertionError(f"expected learned rule injection, got {preflight.get('learnedRuleCount')}")
    hits = [item for item in preflight.get("hits", []) if isinstance(item, dict)]
    if not any(str(item.get("ruleId", "")).startswith("learned.") for item in hits):
        raise AssertionError("accepted learned rule did not produce a PTL preflight hit")

    panel = run_text([str(SCRIPT_DIR / "ptl_learning.py"), "panel", str(repo), "--registry", str(registry)])
    if "PTL Learning Review" not in panel or "Accepted Learned Rules" not in panel:
        raise AssertionError("review panel did not render learning review and accepted rules")


def validate_accept_all_fixture(root: Path) -> None:
    repo = root / "accept-all-project"
    registry = root / "persistent-all" / "learned-registry.json"
    seed_control_surface(repo)
    seed_learning_messages(repo)
    write(
        repo / ".codex/task-pipeline.json",
        json.dumps(
            {
                "schema": "project-assistant.task-pipeline.v1",
                "project": repo.name,
                "status": "active",
                "activeTaskId": None,
                "tasks": [],
                "history": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    scan = run_json([str(SCRIPT_DIR / "ptl_learning.py"), "scan", str(repo), "--registry", str(registry), "--json"])
    pending_count = len([item for item in scan.get("candidates", []) if isinstance(item, dict) and item.get("status") == "candidate"])
    if pending_count < 3:
        raise AssertionError("accept-all fixture did not create enough pending candidates")
    result = run_json([str(SCRIPT_DIR / "ptl_learning.py"), "accept-all", str(repo), "--registry", str(registry), "--json"])
    if result.get("accepted") != pending_count:
        raise AssertionError(f"accept-all accepted {result.get('accepted')} instead of {pending_count}")
    pipeline = json.loads((repo / ".codex/task-pipeline.json").read_text(encoding="utf-8"))
    review_task = next((item for item in pipeline.get("tasks", []) if item.get("id") == "PTL-LEARNING-REVIEW"), None)
    if not review_task or review_task.get("status") != "done":
        raise AssertionError("accept-all did not close the PTL human-decision task")


def validate_partial_response_fixture(root: Path) -> None:
    repo = root / "partial-response-project"
    registry = root / "persistent-partial" / "learned-registry.json"
    seed_control_surface(repo)
    seed_learning_messages(repo)
    write(
        repo / ".codex/task-pipeline.json",
        json.dumps(
            {
                "schema": "project-assistant.task-pipeline.v1",
                "project": repo.name,
                "status": "active",
                "activeTaskId": None,
                "tasks": [],
                "history": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    scan = run_json([str(SCRIPT_DIR / "ptl_learning.py"), "scan", str(repo), "--registry", str(registry), "--json"])
    pending_count = len([item for item in scan.get("candidates", []) if isinstance(item, dict) and item.get("status") == "candidate"])
    if pending_count < 3:
        raise AssertionError("partial response fixture did not create enough pending candidates")
    result = run_json(
        [
            str(SCRIPT_DIR / "ptl_learning.py"),
            "apply-response",
            str(repo),
            "--registry",
            str(registry),
            "--response",
            "接受 1，2 稍后",
            "--json",
        ]
    )
    if not result.get("processed") or len(result.get("remaining", [])) != pending_count - 2:
        raise AssertionError("partial human response did not leave the expected remaining decisions")
    pipeline = json.loads((repo / ".codex/task-pipeline.json").read_text(encoding="utf-8"))
    review_task = next((item for item in pipeline.get("tasks", []) if item.get("id") == "PTL-LEARNING-REVIEW"), None)
    if not review_task or review_task.get("status") not in {"pending", "requires-human-decision"}:
        raise AssertionError("partial response should keep the PTL human-decision task open")
    result = run_json(
        [
            str(SCRIPT_DIR / "ptl_learning.py"),
            "apply-response",
            str(repo),
            "--registry",
            str(registry),
            "--response",
            "全部拒绝",
            "--json",
        ]
    )
    if result.get("remaining"):
        raise AssertionError("final human response did not close all remaining decisions")
    pipeline = json.loads((repo / ".codex/task-pipeline.json").read_text(encoding="utf-8"))
    review_task = next((item for item in pipeline.get("tasks", []) if item.get("id") == "PTL-LEARNING-REVIEW"), None)
    if not review_task or review_task.get("status") != "done":
        raise AssertionError("final human response did not close the PTL human-decision task")


def validate_semantic_induction_fixture(root: Path) -> None:
    repo = root / "semantic-induction-project"
    registry = root / "persistent-semantic" / "learned-registry.json"
    seed_control_surface(repo)
    seed_semantic_learning_messages(repo)
    write(
        repo / ".codex/task-pipeline.json",
        json.dumps(
            {
                "schema": "project-assistant.task-pipeline.v1",
                "project": repo.name,
                "status": "active",
                "activeTaskId": None,
                "tasks": [],
                "history": [],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )
    scan = run_json([str(SCRIPT_DIR / "ptl_learning.py"), "scan", str(repo), "--registry", str(registry), "--json"])
    clear_human = candidate_by_key(scan, "semantic.clear-response.human-decision")
    loop_human = candidate_by_key(scan, "semantic.human-decision.loop-continuity")
    for candidate in [clear_human, loop_human]:
        if candidate.get("origin") != "semantic-induction":
            raise AssertionError("semantic candidate did not record semantic-induction origin")
        concepts = candidate.get("semanticConcepts")
        if not isinstance(concepts, list) or len(concepts) != 2:
            raise AssertionError("semantic candidate did not record the concept pair")
        if int(candidate.get("occurrenceCount", 0)) < 2:
            raise AssertionError("semantic induction should require repeated evidence")
    panel = run_text([str(SCRIPT_DIR / "ptl_learning.py"), "panel", str(repo), "--registry", str(registry)])
    if "人类确认提示必须列清待办项和一行回复格式" not in panel or "人类确认必须作为 loop task，确认后自动继续" not in panel:
        raise AssertionError("semantic candidates were not visible in the governed review panel")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate governed PTL learning review, registry, and gate injection.")
    parser.add_argument("repo", nargs="?", default=".", help="Unused compatibility arg; fixtures are temporary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    results: list[dict[str, object]] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="project-assistant-ptl-learning-") as tmp:
        checks = [
            ("learning review registry fixture", validate_learning_review),
            ("accept-all human-decision fixture", validate_accept_all_fixture),
            ("partial human response fixture", validate_partial_response_fixture),
            ("semantic induction fixture", validate_semantic_induction_fixture),
        ]
        for name, check in checks:
            try:
                check(Path(tmp))
                results.append({"name": name, "ok": True})
            except Exception as exc:
                ok = False
                results.append({"name": name, "ok": False, "error": str(exc)})

    if args.format == "json":
        print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for result in results:
            print(f"[{result['name']}] ok: {result['ok']}")
            if not result["ok"]:
                print(f"  error: {result.get('error')}")
        print(f"ok: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
