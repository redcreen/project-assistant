#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import time
from pathlib import Path
from typing import Any

try:
    import ptl_learning
except Exception:  # pragma: no cover - preflight must remain usable without the optional learning layer.
    ptl_learning = None  # type: ignore[assignment]


POLICY_SCHEMA = "project-assistant.ptl-policy.v1"
PREFLIGHT_SCHEMA = "project-assistant.ptl-preflight.v1"
POLICY_DIR = Path(".codex/ptl-policy")
POLICY_FILE = POLICY_DIR / "project-policy.json"
PREFLIGHT_FILE = POLICY_DIR / "preflight.json"

DEFAULT_REQUIRED_FILES = [
    ".codex/brief.md",
    ".codex/plan.md",
    ".codex/status.md",
    ".codex/COMMANDS.md",
    ".codex/control-surface.json",
]

DECISION_RANK = {
    "allow": 0,
    "observe": 1,
    "warn": 2,
    "require-review": 3,
    "block": 4,
}


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def stable_hash(payload: Any) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def rel(path: Path, repo: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def parse_control_surface(repo: Path) -> dict[str, Any]:
    parsed = read_json(repo / ".codex/control-surface.json", {})
    return parsed if isinstance(parsed, dict) else {}


def configured_required_files(repo: Path) -> list[str]:
    control = parse_control_surface(repo)
    required = control.get("requiredFiles")
    if isinstance(required, list) and all(isinstance(item, str) for item in required):
        return list(dict.fromkeys([*DEFAULT_REQUIRED_FILES, *required]))
    return list(DEFAULT_REQUIRED_FILES)


def official_modules(repo: Path) -> list[str]:
    control = parse_control_surface(repo)
    modules = control.get("officialModules")
    if isinstance(modules, list):
        return [str(item) for item in modules if str(item).strip()]
    return []


def source_documents(repo: Path) -> list[Path]:
    paths: list[Path] = []
    for rel_path in [
        ".codex/brief.md",
        ".codex/plan.md",
        ".codex/status.md",
        ".codex/strategy.md",
        ".codex/program-board.md",
        ".codex/delivery-supervision.md",
        ".codex/ptl-supervision.md",
        ".codex/worker-handoff.md",
        "README.md",
        "README.zh-CN.md",
        "docs/README.md",
        "docs/README.zh-CN.md",
        "docs/architecture.md",
        "docs/architecture.zh-CN.md",
        "docs/roadmap.md",
        "docs/roadmap.zh-CN.md",
        "docs/test-plan.md",
        "docs/test-plan.zh-CN.md",
    ]:
        candidate = repo / rel_path
        if candidate.exists():
            paths.append(candidate)
    modules_dir = repo / ".codex/modules"
    if modules_dir.exists():
        paths.extend(sorted(modules_dir.glob("*.md"))[:20])
    reference_dir = repo / "docs/reference"
    if reference_dir.exists():
        paths.extend(sorted(reference_dir.glob("**/*.md"))[:60])
    return list(dict.fromkeys(paths))


def corpus_text(repo: Path) -> str:
    chunks: list[str] = []
    for path in source_documents(repo):
        text = read_text(path)
        if text:
            chunks.append(f"\n\n# SOURCE {rel(path, repo)}\n{text[:8000]}")
    return "\n".join(chunks).lower()


def detect_domain_packs(repo: Path, corpus: str) -> list[str]:
    packs: list[str] = []
    if any(
        token in corpus
        for token in [
            "product_surface_spec",
            "mask_refinement_audit",
            "generation brief",
            "white model",
            "白模",
            "出图",
            "sdxl",
            "prompt",
        ]
    ):
        packs.append("image-generation")
    if (repo / "openclaw.plugin.json").exists() or "openclaw" in corpus and "plugin" in corpus:
        packs.append("plugin-runtime")
    if (repo / "order/scripts/order_runtime_api.py").exists() or (repo / "order/runtime/command_manifest.json").exists():
        packs.append("order-runtime")
    if "health_runtime_guard" in corpus or "unified intake" in corpus or "before_dispatch" in corpus:
        packs.append("health-intake")
    return packs


def existing_rule_overrides(repo: Path) -> dict[str, dict[str, Any]]:
    existing = read_json(repo / POLICY_FILE, {})
    rules = existing.get("rules") if isinstance(existing, dict) else None
    if not isinstance(rules, list):
        return {}
    overrides: dict[str, dict[str, Any]] = {}
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        rule_id = str(rule.get("id") or "")
        if not rule_id:
            continue
        overrides[rule_id] = {
            key: rule[key]
            for key in ["status", "decision", "severity", "scope", "acceptedAt", "acceptedBy", "notes"]
            if key in rule
        }
    return overrides


def apply_overrides(rules: list[dict[str, Any]], overrides: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for rule in rules:
        merged = dict(rule)
        override = overrides.get(str(rule.get("id") or ""))
        if override:
            merged.update(override)
        result.append(merged)
    return result


def learned_rules() -> list[dict[str, Any]]:
    if ptl_learning is None:
        return []
    rules: list[dict[str, Any]] = []
    for item in ptl_learning.accepted_rules():
        if not isinstance(item, dict):
            continue
        decision = str(item.get("decision") or "warn")
        if decision not in DECISION_RANK:
            decision = "warn"
        rule_id = f"learned.{item.get('id') or stable_hash(item.get('stableKey'))}"
        rules.append(
            {
                "id": rule_id,
                "scope": str(item.get("scope") or "user-global"),
                "status": "accepted",
                "severity": decision,
                "source": {
                    "type": "learned-registry",
                    "path": str(ptl_learning.registry_path()),
                    "stableKey": str(item.get("stableKey") or ""),
                },
                "description": str(item.get("ruleText") or item.get("title") or "Accepted PTL learned rule."),
                "trigger": {"modes": ["continue", "progress", "execute", "release"], "paths": ["*"]},
                "check": {
                    "type": "accepted_learning_rule",
                    "stableKey": str(item.get("stableKey") or ""),
                    "keywords": [str(keyword) for keyword in item.get("keywords", []) if str(keyword).strip()],
                },
            }
        )
    return rules


def base_rules(repo: Path, domains: list[str]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = [
        {
            "id": "project-assistant.control-surface.required-files",
            "scope": "project-local",
            "status": "accepted",
            "severity": "block",
            "source": {"type": "control-surface", "path": ".codex/control-surface.json"},
            "description": "Required control-surface files must exist before project-assistant can produce reliable PTL decisions.",
            "trigger": {"modes": ["continue", "progress", "execute", "release"], "paths": ["*"]},
            "check": {"type": "required_files_exist", "paths": configured_required_files(repo)},
        },
        {
            "id": "project-assistant.escalation.require-human-review",
            "scope": "project-local",
            "status": "accepted",
            "severity": "require-review",
            "source": {"type": "control-surface", "path": ".codex/status.md"},
            "description": "If the current escalation gate requires user decision, PTL preflight must stop automatic continuation.",
            "trigger": {"modes": ["continue", "execute", "release"], "paths": ["*"]},
            "check": {"type": "current_escalation_gate"},
        },
    ]
    modules = official_modules(repo)
    if modules:
        rules.append(
            {
                "id": "project-assistant.module-boundary.changed-paths",
                "scope": "project-local",
                "status": "warn",
                "severity": "warn",
                "source": {"type": "control-surface", "path": ".codex/control-surface.json"},
                "description": "Module-aware repos should surface PTL review when a change touches module-owned paths.",
                "trigger": {"modes": ["continue", "execute", "progress"], "paths": [f"{module}/**" for module in modules]},
                "check": {"type": "changed_path_match"},
            }
        )
    if "image-generation" in domains:
        rules.append(
            {
                "id": "domain.image-generation.reusable-mainline-contract",
                "scope": "domain-pack",
                "status": "warn",
                "severity": "warn",
                "source": {"type": "seeded-domain-pack", "domain": "image-generation"},
                "description": "Image-generation mainline work should distinguish reusable pipeline evidence from one-off prompt, mask, seed, or fallback tuning.",
                "trigger": {
                    "modes": ["continue", "execute", "progress"],
                    "paths": [
                        "apps/product-restyle-lab/**",
                        "**/product-restyle-lab/**",
                        "**/*prompt*",
                        "**/*mask*",
                        "docs/reference/**/*vision*",
                        "docs/reference/**/*sdxl*",
                    ],
                },
                "check": {"type": "changed_path_match"},
            }
        )
    if "plugin-runtime" in domains:
        rules.append(
            {
                "id": "domain.plugin-runtime.release-and-runtime-smoke",
                "scope": "domain-pack",
                "status": "warn",
                "severity": "warn",
                "source": {"type": "seeded-domain-pack", "domain": "plugin-runtime"},
                "description": "Plugin/runtime changes should keep install metadata, gateway/runtime smoke, and public docs aligned.",
                "trigger": {
                    "modes": ["continue", "execute", "progress", "release"],
                    "paths": ["openclaw.plugin.json", "package.json", "src/plugin/**", "plugins/**", "**/SKILL.md"],
                },
                "check": {"type": "changed_path_match"},
            }
        )
    if "order-runtime" in domains:
        rules.append(
            {
                "id": "domain.order-runtime.adapter-boundary",
                "scope": "domain-pack",
                "status": "warn",
                "severity": "warn",
                "source": {"type": "seeded-domain-pack", "domain": "order-runtime"},
                "description": "Order adapters should call the runtime API instead of duplicating business logic or starting external writes before dry-run contracts.",
                "trigger": {
                    "modes": ["continue", "execute", "progress"],
                    "paths": ["order/**", "plugins/openclaw-order/**", "order-host-plugin/**"],
                },
                "check": {"type": "changed_path_match"},
            }
        )
    if "health-intake" in domains:
        rules.append(
            {
                "id": "domain.health-intake.authoritative-source",
                "scope": "domain-pack",
                "status": "warn",
                "severity": "warn",
                "source": {"type": "seeded-domain-pack", "domain": "health-intake"},
                "description": "Health intake changes should preserve unified intake, deterministic writes, and the distinction between hints and authoritative facts.",
                "trigger": {"modes": ["continue", "execute", "progress"], "paths": ["health/**", "src/plugin/**"]},
                "check": {"type": "changed_path_match"},
            }
        )
    return rules


def sync_policy(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    corpus = corpus_text(repo)
    domains = detect_domain_packs(repo, corpus)
    overrides = existing_rule_overrides(repo)
    accepted_learned_rules = learned_rules()
    rules = apply_overrides([*base_rules(repo, domains), *accepted_learned_rules], overrides)
    body = {
        "schema": POLICY_SCHEMA,
        "generatedBy": "project-assistant",
        "project": repo.name,
        "tier": parse_control_surface(repo).get("tier", "unknown"),
        "officialModules": official_modules(repo),
        "domainPacks": domains,
        "sourceDocuments": [rel(path, repo) for path in source_documents(repo)],
        "learnedRegistryPath": str(ptl_learning.registry_path()) if ptl_learning is not None else "",
        "learnedRuleCount": len(accepted_learned_rules),
        "rules": rules,
    }
    body["policyHash"] = stable_hash(body)
    body["generatedAt"] = iso_now()
    write_json(repo / POLICY_FILE, body)
    return body


def git_changed_paths(repo: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except Exception:
        return []
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        payload = line[3:] if len(line) > 3 else line.strip()
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1]
        paths.append(payload.strip().strip('"'))
    return list(dict.fromkeys(paths))


def path_matches(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        if pattern == "*":
            return True
        if fnmatch.fnmatch(normalized, pattern):
            return True
        if pattern.endswith("/**") and normalized.startswith(pattern[:-3]):
            return True
    return False


def labeled_value(text: str, label: str) -> str:
    prefix = f"- {label}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(prefix.lower()):
            return stripped[len(prefix) :].strip().strip("`")
    return ""


def current_signal(repo: Path) -> dict[str, str]:
    text = read_text(repo / ".codex/status.md")
    signal = labeled_value(text, "Signal") or "unknown"
    gate = labeled_value(text, "Escalation Gate") or labeled_value(text, "Current Gate") or "unknown"
    trigger = labeled_value(text, "Automatic Review Trigger") or "unknown"
    return {"signal": signal, "gate": gate, "automaticReviewTrigger": trigger}


def current_task_text(repo: Path) -> str:
    payload = read_json(repo / ".codex/task-pipeline.json", {})
    if not isinstance(payload, dict):
        return ""
    tasks = payload.get("tasks")
    if not isinstance(tasks, list):
        return ""
    active_id = str(payload.get("activeTaskId") or "")
    selected: dict[str, Any] | None = None
    for task in tasks:
        if isinstance(task, dict) and str(task.get("id") or "") == active_id:
            selected = task
            break
    if selected is None:
        for task in reversed(tasks):
            if isinstance(task, dict):
                selected = task
                break
    if selected is None:
        return ""
    metadata = selected.get("metadata") if isinstance(selected.get("metadata"), dict) else {}
    values = [
        selected.get("title"),
        selected.get("description"),
        metadata.get("rawMessage"),
        metadata.get("intent"),
        metadata.get("source"),
    ]
    return "\n".join(str(value) for value in values if value)


def effective_decision(rule: dict[str, Any]) -> str:
    status = str(rule.get("status") or "observe")
    if status in {"observe", "candidate", "rejected", "decayed"}:
        return "observe"
    if status in {"warn", "require-review", "block"}:
        return status
    if status == "accepted":
        severity = str(rule.get("severity") or "warn")
        return severity if severity in DECISION_RANK else "warn"
    return "observe"


def max_decision(decisions: list[str]) -> str:
    if not decisions:
        return "allow"
    return max(decisions, key=lambda item: DECISION_RANK.get(item, 0))


def run_preflight(repo: Path, *, mode: str, changed_paths: list[str] | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    learning_review: dict[str, Any] = {}
    if ptl_learning is not None:
        try:
            learning_review = ptl_learning.scan(repo)
        except Exception as exc:
            learning_review = {"error": str(exc)}
    policy = sync_policy(repo)
    changes = list(dict.fromkeys([*(changed_paths or []), *git_changed_paths(repo)]))
    signal = current_signal(repo)
    task_text = current_task_text(repo).casefold()
    hits: list[dict[str, Any]] = []

    for rule in policy.get("rules", []):
        if not isinstance(rule, dict):
            continue
        trigger = rule.get("trigger") if isinstance(rule.get("trigger"), dict) else {}
        modes = trigger.get("modes") if isinstance(trigger.get("modes"), list) else []
        if modes and mode not in modes:
            continue
        check = rule.get("check") if isinstance(rule.get("check"), dict) else {}
        check_type = str(check.get("type") or "")
        decision = effective_decision(rule)
        if check_type == "required_files_exist":
            missing = [path for path in check.get("paths", []) if isinstance(path, str) and not (repo / path).exists()]
            if missing:
                hits.append(
                    {
                        "ruleId": rule.get("id"),
                        "decision": "block",
                        "reason": "required control-surface files are missing",
                        "evidence": missing,
                    }
                )
        elif check_type == "current_escalation_gate":
            gate = signal.get("gate", "").lower()
            arch_signal = signal.get("signal", "").lower()
            if "require user" in gate or "require-review" in gate or arch_signal == "red":
                hits.append(
                    {
                        "ruleId": rule.get("id"),
                        "decision": "require-review",
                        "reason": "current project signal requires human review",
                        "evidence": [f"signal={signal.get('signal')}", f"gate={signal.get('gate')}"],
                    }
                )
        elif check_type == "changed_path_match":
            patterns = trigger.get("paths") if isinstance(trigger.get("paths"), list) else []
            matched = [path for path in changes if path_matches(path, [str(pattern) for pattern in patterns])]
            if matched and decision != "observe":
                hits.append(
                    {
                        "ruleId": rule.get("id"),
                        "decision": decision,
                        "reason": str(rule.get("description") or "changed paths matched this PTL policy"),
                        "evidence": matched[:12],
                    }
                )
        elif check_type == "accepted_learning_rule":
            keywords = [str(keyword).casefold() for keyword in check.get("keywords", []) if str(keyword).strip()]
            matched = [keyword for keyword in keywords if task_text and keyword in task_text]
            if matched and decision != "observe":
                hits.append(
                    {
                        "ruleId": rule.get("id"),
                        "decision": decision,
                        "reason": str(rule.get("description") or "current task matched an accepted PTL learned rule"),
                        "evidence": matched[:8],
                    }
                )

    decision = max_decision([str(hit.get("decision") or "allow") for hit in hits])
    learning_summary = learning_review.get("summary") if isinstance(learning_review.get("summary"), dict) else {}
    payload = {
        "schema": PREFLIGHT_SCHEMA,
        "generatedAt": iso_now(),
        "mode": mode,
        "project": repo.name,
        "decision": decision,
        "signal": "red" if decision == "block" else "yellow" if decision in {"warn", "require-review"} else "green",
        "policyPath": POLICY_FILE.as_posix(),
        "policyHash": policy.get("policyHash"),
        "domainPacks": policy.get("domainPacks", []),
        "officialModules": policy.get("officialModules", []),
        "learnedRuleCount": policy.get("learnedRuleCount", 0),
        "learningReview": {
            "path": (POLICY_DIR / "learning-review.json").as_posix(),
            "pending": learning_summary.get("pending", 0),
            "acceptedRegistry": learning_summary.get("acceptedRegistry", policy.get("learnedRuleCount", 0)),
            "error": learning_review.get("error", ""),
        },
        "changedPaths": changes,
        "currentSignal": signal,
        "hits": hits,
    }
    write_json(repo / PREFLIGHT_FILE, payload)
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    hits = payload.get("hits") if isinstance(payload.get("hits"), list) else []
    packs = ", ".join(f"`{item}`" for item in payload.get("domainPacks", []) or []) or "`(none)`"
    learning = payload.get("learningReview") if isinstance(payload.get("learningReview"), dict) else {}
    lines = [
        "## PTL Preflight",
        "",
        "| 项目 | 当前值 |",
        "| --- | --- |",
        f"| Decision | `{payload.get('decision')}` |",
        f"| Signal | `{payload.get('signal')}` |",
        f"| Policy | `{payload.get('policyPath')}` |",
        f"| Policy Hash | `{payload.get('policyHash')}` |",
        f"| Domain Packs | {packs} |",
        f"| Pending Learning Review | `{learning.get('pending', 0)}` |",
        f"| Accepted Learned Rules | `{payload.get('learnedRuleCount', 0)}` |",
        f"| Current Gate | `{(payload.get('currentSignal') or {}).get('gate', 'unknown')}` |",
    ]
    if not hits:
        lines.extend(["", "本轮没有命中需要提示或阻塞的 PTL 规则。"])
        return "\n".join(lines)
    lines.extend(
        [
            "",
            "| Rule | Decision | Evidence |",
            "| --- | --- | --- |",
        ]
    )
    for hit in hits:
        evidence = "; ".join(str(item) for item in hit.get("evidence", [])[:4])
        lines.append(f"| `{hit.get('ruleId')}` | `{hit.get('decision')}` | {evidence or hit.get('reason', '')} |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate and run a lightweight PTL policy preflight for a repository.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Generate or refresh the project PTL policy pack.")
    sync_parser.add_argument("repo", type=Path)

    preflight_parser = subparsers.add_parser("preflight", help="Run PTL preflight and print a compact panel.")
    preflight_parser.add_argument("repo", type=Path)
    preflight_parser.add_argument("--mode", default="continue", choices=["continue", "progress", "execute", "release"])
    preflight_parser.add_argument("--changed-path", action="append", default=[], help="Additional changed path for tests or host-provided context.")
    preflight_parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")

    args = parser.parse_args(argv)
    if args.command == "sync":
        policy = sync_policy(args.repo)
        print(json.dumps({"ok": True, "policyPath": POLICY_FILE.as_posix(), "policyHash": policy.get("policyHash")}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "preflight":
        payload = run_preflight(args.repo, mode=args.mode, changed_paths=args.changed_path)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(render_markdown(payload))
        return 0 if payload.get("decision") != "block" else 2
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
