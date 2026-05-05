#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def run_preflight(repo: Path, *extra: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "ptl_gate.py"), "preflight", str(repo), "--json", *extra],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 2}:
        raise AssertionError(f"ptl_gate.py failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return json.loads(result.stdout)


def run_entry(script_name: str, repo: Path) -> str:
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / script_name), str(repo)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(f"{script_name} failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    return result.stdout


def seed_control_surface(repo: Path, *, tier: str = "medium", modules: list[str] | None = None) -> None:
    write(repo / ".codex/brief.md", "# Project Brief\n\n## Outcome\n\nFixture.\n")
    write(
        repo / ".codex/plan.md",
        "# Project Plan\n\n## Architecture Supervision\n- Signal: `green`\n- Escalation Gate: continue automatically\n",
    )
    write(
        repo / ".codex/status.md",
        "# Project Status\n\n## Architecture Supervision\n- Signal: `green`\n- Escalation Gate: continue automatically\n",
    )
    write(repo / ".codex/COMMANDS.md", "# Commands\n")
    control = {
        "managedBy": "project-assistant",
        "controlSurfaceVersion": 3,
        "tier": tier,
        "officialModules": modules or [],
        "requiredFiles": [
            ".codex/brief.md",
            ".codex/plan.md",
            ".codex/status.md",
            ".codex/COMMANDS.md",
            ".codex/control-surface.json",
        ],
    }
    write(repo / ".codex/control-surface.json", json.dumps(control, ensure_ascii=False, indent=2) + "\n")


def assert_hit(payload: dict[str, object], rule_id: str) -> None:
    hits = payload.get("hits")
    if not isinstance(hits, list) or not any(isinstance(item, dict) and item.get("ruleId") == rule_id for item in hits):
        raise AssertionError(f"missing expected hit {rule_id}: {json.dumps(payload, ensure_ascii=False, indent=2)}")


def validate_generic_fixture(root: Path) -> None:
    repo = root / "generic"
    seed_control_surface(repo)
    payload = run_preflight(repo)
    if payload.get("decision") != "allow":
        raise AssertionError(f"expected allow for generic fixture, got {payload.get('decision')}")
    if not (repo / ".codex/ptl-policy/project-policy.json").exists():
        raise AssertionError("expected generated project policy")


def validate_missing_control_fixture(root: Path) -> None:
    repo = root / "missing-control"
    seed_control_surface(repo)
    (repo / ".codex/status.md").unlink()
    payload = run_preflight(repo)
    if payload.get("decision") != "block":
        raise AssertionError(f"expected block for missing control fixture, got {payload.get('decision')}")
    assert_hit(payload, "project-assistant.control-surface.required-files")


def validate_image_generation_fixture(root: Path) -> None:
    repo = root / "style-engine-like"
    seed_control_surface(repo)
    write(
        repo / "docs/reference/style-engine/vision55-surface-pipeline-current-goal.zh-CN.md",
        "# Vision Pipeline\n\n主线出图必须生成 product_surface_spec 和 mask_refinement_audit，不能只靠 prompt 或历史 mask。\n",
    )
    payload = run_preflight(repo, "--changed-path", "apps/product-restyle-lab/scripts/run_case.py")
    if payload.get("decision") != "warn":
        raise AssertionError(f"expected warn for image-generation fixture, got {payload.get('decision')}")
    assert_hit(payload, "domain.image-generation.reusable-mainline-contract")


def validate_openclaw_fixture(root: Path) -> None:
    repo = root / "openclaw-skills-like"
    seed_control_surface(repo, tier="large", modules=["health", "order"])
    write(repo / "openclaw.plugin.json", "{}\n")
    write(repo / "order/scripts/order_runtime_api.py", "# runtime api\n")
    write(repo / "order/runtime/command_manifest.json", "{}\n")
    write(repo / ".codex/modules/order.md", "# Module Status\n\nAdapters must call order_runtime_api.py.\n")
    write(repo / ".codex/modules/health.md", "# Module Status\n\nhealth_runtime_guard uses before_dispatch and unified intake.\n")
    payload = run_preflight(repo, "--changed-path", "plugins/openclaw-order/index.js", "--changed-path", "order/scripts/bridge.py")
    if payload.get("decision") != "warn":
        raise AssertionError(f"expected warn for openclaw fixture, got {payload.get('decision')}")
    assert_hit(payload, "domain.plugin-runtime.release-and-runtime-smoke")
    assert_hit(payload, "domain.order-runtime.adapter-boundary")


def validate_entry_activation_fixture(root: Path) -> None:
    repo = root / "entry-activation"
    seed_control_surface(repo)
    continue_output = run_entry("continue_entry.py", repo)
    progress_output = run_entry("progress_entry.py", repo)
    if "## PTL Preflight" not in continue_output:
        raise AssertionError("continue_entry.py did not append PTL Preflight panel")
    if "## PTL Preflight" not in progress_output:
        raise AssertionError("progress_entry.py did not append PTL Preflight panel")
    if not (repo / ".codex/ptl-policy/project-policy.json").exists():
        raise AssertionError("entry activation did not generate PTL project policy")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate PTL policy sync and preflight on isolated fixtures.")
    parser.add_argument("repo", nargs="?", default=".", help="Unused compatibility arg; fixtures are temporary.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    checks = [
        ("generic fixture", validate_generic_fixture),
        ("missing control fixture", validate_missing_control_fixture),
        ("image-generation fixture", validate_image_generation_fixture),
        ("openclaw-skills fixture", validate_openclaw_fixture),
        ("entry activation fixture", validate_entry_activation_fixture),
    ]
    results: list[dict[str, object]] = []
    ok = True
    with tempfile.TemporaryDirectory(prefix="project-assistant-ptl-gate-") as tmp:
        root = Path(tmp)
        for name, check in checks:
            try:
                check(root)
                results.append({"name": name, "ok": True})
            except Exception as exc:
                ok = False
                results.append({"name": name, "ok": False, "error": str(exc)})

    if args.format == "json":
        print(json.dumps({"ok": ok, "results": results}, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"[{result['name']}] ok: {result['ok']}")
            if not result["ok"]:
                print(f"  error: {result.get('error')}")
        print(f"ok: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
