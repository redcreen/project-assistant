#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any


REVIEW_SCHEMA = "project-assistant.ptl-learning-review.v1"
REGISTRY_SCHEMA = "project-assistant.learned-registry.v1"
REVIEW_FILE = Path(".codex/ptl-policy/learning-review.json")
DEFAULT_REGISTRY_FILE = Path.home() / ".codex/project-assistant/learned-registry.json"
PIPELINE_SCHEMA = "project-assistant.task-pipeline.v1"
PIPELINE_FILE = Path(".codex/task-pipeline.json")
HUMAN_REVIEW_TASK_ID = "PTL-LEARNING-REVIEW"

VALID_DECISIONS = {"observe", "warn", "require-review", "block"}
VALID_SCOPES = {"project-local", "module-local", "domain-pack", "user-global", "global-promoted"}
ACCEPT_WORDS = {"接受", "同意", "批准", "accept", "approve"}
REJECT_WORDS = {"拒绝", "不同意", "不要", "reject"}
SNOOZE_WORDS = {"稍后", "延后", "暂缓", "snooze", "later"}

PATTERNS: list[dict[str, Any]] = [
    {
        "stableKey": "correction.feasibility-first",
        "title": "Feasibility probe before broad implementation",
        "ruleText": (
            "When a task depends on uncertain host, API, plugin, protocol, binary, or undocumented behavior, "
            "run the smallest feasibility probe before broad implementation."
        ),
        "rationale": "Repeated corrections show that speculative implementation without an early probe creates wasted work.",
        "suggestedScope": "user-global",
        "suggestedDecision": "warn",
        "keywords": ["可行性", "先验证", "最小", "probe", "根本不可行", "不做最基础", "host/api/plugin/protocol/binary"],
        "tokens": ["可行性", "先验证", "probe", "根本不可行", "不做最基础", "最基础的可行性", "feasibility"],
    },
    {
        "stableKey": "correction.pipeline-continuity",
        "title": "Continue inside the task loop until the completion gate",
        "ruleText": (
            "For non-trivial execution work, stay inside the task loop and continue automatically until completion, "
            "blocker, human-decision gate, or explicit stop instruction."
        ),
        "rationale": "Repeated corrections show that stopping after one step breaks long-running project execution.",
        "suggestedScope": "user-global",
        "suggestedDecision": "warn",
        "keywords": ["一口气", "持续推进", "继续，直到", "做一步停一步", "loop", "pipeline", "completion gate"],
        "tokens": ["一口气", "一直做", "继续，直到", "做一步停一步", "loop", "pipeline", "自动继续"],
    },
    {
        "stableKey": "correction.anti-workaround-reuse",
        "title": "Avoid one-off workaround behavior when a reusable path is required",
        "ruleText": (
            "Do not replace reusable project behavior with one-off workaround, hardcoded, prompt-only, mask-only, "
            "or short-term fallback changes unless the user explicitly accepts that tradeoff."
        ),
        "rationale": "Repeated corrections show that short-term fixes often violate the intended reusable project direction.",
        "suggestedScope": "domain-pack",
        "suggestedDecision": "warn",
        "keywords": ["workaround", "硬编码", "不可复用", "短期", "fallback", "prompt", "mask"],
        "tokens": ["workaround", "硬编码", "不可复用", "短期", "fallback", "不可复用行为", "短期不可复用"],
    },
    {
        "stableKey": "correction.host-ingress-proof",
        "title": "Prove host/message ingress behavior before assuming transport control",
        "ruleText": (
            "When changing Codex App, VS Code, hook, wrapper, or message-ingress behavior, verify the actual host "
            "transport path with a direct smoke before claiming all messages enter the loop."
        ),
        "rationale": "Repeated corrections show that host integration claims need direct transport evidence.",
        "suggestedScope": "user-global",
        "suggestedDecision": "warn",
        "keywords": ["codex app", "hook", "热加载", "wrapper", "message ingress", "传输层"],
        "tokens": ["codex app", "hook", "热加载", "wrapper", "传输层", "message ingress", "是否生效"],
    },
    {
        "stableKey": "correction.precise-technical-discussion",
        "title": "Separate verified facts from untested implementation paths",
        "ruleText": (
            "Do not present an unverified path as implemented fact; label assumptions, testability, and evidence "
            "before asking the human to accept a technical direction."
        ),
        "rationale": "Repeated corrections show that ambiguous discussion can hide feasibility gaps.",
        "suggestedScope": "user-global",
        "suggestedDecision": "observe",
        "keywords": ["验证", "证据", "事实", "假设", "文字游戏", "深入验证"],
        "tokens": ["文字游戏", "深入的验证", "靠我给你解题思路", "不能确定", "是否能够达到", "证据"],
    },
]

CORRECTION_TRIGGERS = [
    "需要",
    "应该",
    "必须",
    "不要",
    "不能",
    "别再",
    "不对",
    "问题是",
    "记住",
    "每次",
    "always",
    "must",
    "should",
]

SEMANTIC_CONCEPTS: dict[str, dict[str, Any]] = {
    "clear-response": {
        "label": "clear response format",
        "tokens": ["明确", "清楚", "简单", "回复", "提示", "列清楚", "pending items", "response format"],
    },
    "human-decision": {
        "label": "human decision gate",
        "tokens": ["人类", "确认", "介入", "接受", "拒绝", "暂停", "human", "decision", "accept", "reject"],
    },
    "loop-continuity": {
        "label": "task loop continuity",
        "tokens": ["loop", "pipeline", "自动继续", "直到完成", "一直", "completion gate", "run-next"],
    },
    "evidence-first": {
        "label": "evidence-first execution",
        "tokens": ["验证", "证据", "测试", "可行性", "smoke", "probe", "verify"],
    },
    "reuse-mainline": {
        "label": "reusable mainline",
        "tokens": ["可复用", "主线", "workaround", "硬编码", "短期", "fallback", "reuse"],
    },
}

SEMANTIC_RULE_TEMPLATES: dict[tuple[str, str], dict[str, str]] = {
    ("clear-response", "human-decision"): {
        "title": "Make human-decision prompts explicit and easy to answer",
        "ruleText": (
            "When human input is required, show the current pending items and the exact one-line reply format; "
            "do not rely on prior context or vague wording."
        ),
        "rationale": "Repeated corrections connect human confirmation with clearer, simpler response instructions.",
        "suggestedScope": "user-global",
        "suggestedDecision": "warn",
    },
    ("human-decision", "loop-continuity"): {
        "title": "Keep human confirmation inside the task loop",
        "ruleText": (
            "Represent human confirmation as a loop task; after the human decision is processed, resume the original "
            "pipeline automatically unless the user explicitly pauses or stops."
        ),
        "rationale": "Repeated corrections connect human decisions with preserving the enclosing task loop.",
        "suggestedScope": "user-global",
        "suggestedDecision": "warn",
    },
    ("evidence-first", "reuse-mainline"): {
        "title": "Validate reusable paths instead of landing speculative workarounds",
        "ruleText": (
            "When reusable mainline behavior is at stake, verify the smallest representative path before landing a "
            "workaround, fallback, or hardcoded change."
        ),
        "rationale": "Repeated corrections connect evidence requirements with avoiding one-off replacement behavior.",
        "suggestedScope": "domain-pack",
        "suggestedDecision": "warn",
    },
}


def iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def iso_from_epoch(value: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(value))


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
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def compact_text(value: str, limit: int = 220) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def registry_path(raw: str | Path | None = None) -> Path:
    if raw:
        return Path(raw).expanduser()
    configured = os.environ.get("PROJECT_ASSISTANT_LEARNED_REGISTRY")
    if configured:
        return Path(configured).expanduser()
    return DEFAULT_REGISTRY_FILE


def review_path(repo: Path) -> Path:
    return repo.resolve() / REVIEW_FILE


def load_registry(path: Path | None = None) -> dict[str, Any]:
    target = registry_path(path)
    payload = read_json(target, {})
    if not isinstance(payload, dict) or payload.get("schema") != REGISTRY_SCHEMA:
        return {"schema": REGISTRY_SCHEMA, "rules": [], "updatedAt": iso_now()}
    rules = payload.get("rules")
    if not isinstance(rules, list):
        payload["rules"] = []
    return payload


def accepted_rules(path: Path | None = None) -> list[dict[str, Any]]:
    payload = load_registry(path)
    return [
        item
        for item in payload.get("rules", [])
        if isinstance(item, dict) and item.get("status") == "accepted" and item.get("stableKey")
    ]


def accepted_stable_keys(path: Path | None = None) -> set[str]:
    return {str(item.get("stableKey")) for item in accepted_rules(path)}


def message_records(repo: Path) -> list[dict[str, Any]]:
    payload = read_json(repo.resolve() / ".codex/message-ingress.json", {})
    messages = payload.get("messages") if isinstance(payload, dict) else None
    if not isinstance(messages, list):
        return []
    return [item for item in messages if isinstance(item, dict) and str(item.get("message") or "").strip()]


def token_matches(text: str, tokens: list[str]) -> bool:
    folded = text.casefold()
    return any(str(token).casefold() in folded for token in tokens if str(token).strip())


def is_correction_text(text: str) -> bool:
    folded = text.casefold()
    return any(str(token).casefold() in folded for token in CORRECTION_TRIGGERS if str(token).strip())


def semantic_concepts(text: str) -> list[str]:
    folded = text.casefold()
    found: list[str] = []
    for concept, spec in SEMANTIC_CONCEPTS.items():
        tokens = [str(item) for item in spec.get("tokens", [])]
        if token_matches(folded, tokens):
            found.append(concept)
    return sorted(found)


def evidence_from_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "messageId": str(record.get("id") or ""),
        "taskId": str(record.get("taskId") or ""),
        "source": str(record.get("source") or ""),
        "receivedAt": str(record.get("receivedAt") or ""),
        "excerpt": compact_text(str(record.get("message") or "")),
    }


def generate_candidates(repo: Path, *, min_occurrences: int = 2) -> list[dict[str, Any]]:
    records = message_records(repo)
    candidates: list[dict[str, Any]] = []
    now = iso_now()
    for pattern in PATTERNS:
        matched = [
            record
            for record in records
            if token_matches(str(record.get("message") or ""), [str(item) for item in pattern.get("tokens", [])])
        ]
        if len(matched) < min_occurrences:
            continue
        first_seen = str(matched[0].get("receivedAt") or now)
        last_seen = str(matched[-1].get("receivedAt") or now)
        stable_key = str(pattern["stableKey"])
        candidates.append(
            {
                "id": f"learn-{stable_hash(stable_key)}",
                "stableKey": stable_key,
                "status": "candidate",
                "title": pattern["title"],
                "ruleText": pattern["ruleText"],
                "rationale": pattern["rationale"],
                "suggestedScope": pattern["suggestedScope"],
                "suggestedDecision": pattern["suggestedDecision"],
                "keywords": list(pattern["keywords"]),
                "occurrenceCount": len(matched),
                "confidence": min(0.95, 0.55 + len(matched) * 0.1),
                "firstSeen": first_seen,
                "lastSeen": last_seen,
                "updatedAt": now,
                "evidence": [evidence_from_record(record) for record in matched[-8:]],
            }
        )
    candidates.extend(generate_semantic_candidates(records, min_occurrences=min_occurrences, now=now))
    return candidates


def generate_semantic_candidates(records: list[dict[str, Any]], *, min_occurrences: int, now: str) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for record in records:
        text = str(record.get("message") or "")
        if not is_correction_text(text):
            continue
        concepts = semantic_concepts(text)
        for left_index, left in enumerate(concepts):
            for right in concepts[left_index + 1 :]:
                pair = tuple(sorted((left, right)))
                if pair in SEMANTIC_RULE_TEMPLATES:
                    grouped.setdefault(pair, []).append(record)

    candidates: list[dict[str, Any]] = []
    for pair, matched in sorted(grouped.items()):
        if len(matched) < min_occurrences:
            continue
        template = SEMANTIC_RULE_TEMPLATES[pair]
        stable_key = f"semantic.{pair[0]}.{pair[1]}"
        keywords = sorted(
            {
                token
                for concept in pair
                for token in [str(item) for item in SEMANTIC_CONCEPTS.get(concept, {}).get("tokens", [])[:4]]
            }
        )
        candidates.append(
            {
                "id": f"learn-{stable_hash(stable_key)}",
                "stableKey": stable_key,
                "status": "candidate",
                "origin": "semantic-induction",
                "semanticConcepts": list(pair),
                "title": template["title"],
                "ruleText": template["ruleText"],
                "rationale": template["rationale"],
                "suggestedScope": template["suggestedScope"],
                "suggestedDecision": template["suggestedDecision"],
                "keywords": keywords,
                "occurrenceCount": len(matched),
                "confidence": min(0.9, 0.5 + len(matched) * 0.1),
                "firstSeen": str(matched[0].get("receivedAt") or now),
                "lastSeen": str(matched[-1].get("receivedAt") or now),
                "updatedAt": now,
                "evidence": [evidence_from_record(record) for record in matched[-8:]],
            }
        )
    return candidates


def load_review(repo: Path) -> dict[str, Any]:
    payload = read_json(review_path(repo), {})
    if not isinstance(payload, dict) or payload.get("schema") != REVIEW_SCHEMA:
        return {"schema": REVIEW_SCHEMA, "project": repo.resolve().name, "candidates": [], "updatedAt": iso_now()}
    if not isinstance(payload.get("candidates"), list):
        payload["candidates"] = []
    return payload


def snooze_is_active(candidate: dict[str, Any], *, now_epoch: float | None = None) -> bool:
    until = str(candidate.get("snoozedUntil") or "")
    if not until:
        return False
    try:
        until_epoch = time.mktime(time.strptime(until, "%Y-%m-%dT%H:%M:%SZ"))
    except Exception:
        return False
    return until_epoch > (time.time() if now_epoch is None else now_epoch)


def merge_candidates(
    existing_payload: dict[str, Any],
    generated: list[dict[str, Any]],
    *,
    registry: Path | None = None,
) -> dict[str, Any]:
    now = iso_now()
    accepted_keys = accepted_stable_keys(registry)
    existing_by_key = {
        str(item.get("stableKey")): item
        for item in existing_payload.get("candidates", [])
        if isinstance(item, dict) and item.get("stableKey")
    }
    merged_by_key: dict[str, dict[str, Any]] = {}
    for item in existing_by_key.values():
        copied = dict(item)
        if copied.get("stableKey") in accepted_keys:
            copied["status"] = "accepted"
        elif copied.get("status") == "snoozed" and not snooze_is_active(copied):
            copied["status"] = "candidate"
            copied.pop("snoozedUntil", None)
        merged_by_key[str(copied.get("stableKey"))] = copied

    for candidate in generated:
        stable_key = str(candidate.get("stableKey"))
        old = merged_by_key.get(stable_key)
        if old and old.get("status") in {"rejected"}:
            continue
        if stable_key in accepted_keys:
            candidate = {**candidate, "status": "accepted"}
        elif old and old.get("status") == "snoozed" and snooze_is_active(old):
            candidate = {**candidate, "status": "snoozed", "snoozedUntil": old.get("snoozedUntil"), "snoozeReason": old.get("snoozeReason", "")}
        elif old and old.get("status") == "accepted":
            candidate = {**candidate, "status": "accepted"}
        merged_by_key[stable_key] = {**old, **candidate} if old else candidate

    candidates = sorted(
        merged_by_key.values(),
        key=lambda item: (
            {"candidate": 0, "snoozed": 1, "accepted": 2, "rejected": 3}.get(str(item.get("status")), 9),
            str(item.get("id") or ""),
        ),
    )
    return {
        "schema": REVIEW_SCHEMA,
        "project": str(existing_payload.get("project") or ""),
        "updatedAt": now,
        "registryPath": str(registry_path(registry)),
        "candidates": candidates,
        "summary": summarize_candidates(candidates, registry=registry),
    }


def summarize_candidates(candidates: list[dict[str, Any]], *, registry: Path | None = None) -> dict[str, Any]:
    pending = [item for item in candidates if item.get("status") == "candidate"]
    return {
        "pending": len(pending),
        "acceptedLocal": len([item for item in candidates if item.get("status") == "accepted"]),
        "rejected": len([item for item in candidates if item.get("status") == "rejected"]),
        "snoozed": len([item for item in candidates if item.get("status") == "snoozed"]),
        "acceptedRegistry": len(accepted_rules(registry)),
    }


def scan(repo: Path, *, min_occurrences: int = 2, registry: Path | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    generated = generate_candidates(repo, min_occurrences=min_occurrences)
    existing = load_review(repo)
    existing["project"] = repo.name
    merged = merge_candidates(existing, generated, registry=registry)
    merged["project"] = repo.name
    write_json(review_path(repo), merged)
    sync_human_review_task(repo, merged)
    return merged


def find_candidate(review: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    for item in review.get("candidates", []):
        if isinstance(item, dict) and str(item.get("id") or "") == candidate_id:
            return item
    raise SystemExit(f"unknown PTL learning candidate id: {candidate_id}")


def save_review(repo: Path, review: dict[str, Any]) -> dict[str, Any]:
    candidates = [item for item in review.get("candidates", []) if isinstance(item, dict)]
    review["summary"] = summarize_candidates(candidates, registry=Path(str(review.get("registryPath") or registry_path())))
    review["updatedAt"] = iso_now()
    write_json(review_path(repo), review)
    sync_human_review_task(repo, review)
    return review


def sync_human_review_task(repo: Path, review: dict[str, Any]) -> None:
    pipeline_path = repo.resolve() / PIPELINE_FILE
    state = read_json(pipeline_path, {})
    if not isinstance(state, dict) or state.get("schema") != PIPELINE_SCHEMA:
        return
    tasks = state.get("tasks")
    if not isinstance(tasks, list):
        return
    candidates = [item for item in review.get("candidates", []) if isinstance(item, dict)]
    pending = [item for item in candidates if item.get("status") == "candidate"]
    existing = next((task for task in tasks if isinstance(task, dict) and task.get("id") == HUMAN_REVIEW_TASK_ID), None)
    now = iso_now()
    if pending:
        candidate_ids = [str(item.get("id")) for item in pending if item.get("id")]
        required_action = render_human_prompt(pending)
        task = existing if isinstance(existing, dict) else {
            "id": HUMAN_REVIEW_TASK_ID,
            "createdAt": now,
            "attempts": 0,
            "maxAttempts": 1,
            "origin": "ptl-learning-review",
        }
        current_status = str(task.get("status") or "pending")
        task.update(
            {
                "title": f"human decision: review {len(pending)} PTL learning candidate(s)",
                "kind": "human-decision",
                "status": current_status if current_status in {"pending", "requires-human-decision"} else "pending",
                "updatedAt": now,
                "metadata": {
                    "requiredAction": required_action,
                    "candidateIds": candidate_ids,
                    "reviewPath": REVIEW_FILE.as_posix(),
                    "registryPath": str(registry_path()),
                },
            }
        )
        task.pop("resolution", None)
        if existing is None:
            tasks.append(task)
            state.setdefault("history", []).append(
                {
                    "at": now,
                    "event": "task-enqueued",
                    "taskId": HUMAN_REVIEW_TASK_ID,
                    "kind": "human-decision",
                    "title": task["title"],
                }
            )
        if state.get("status") == "complete":
            state["status"] = "active"
    elif existing and existing.get("status") not in {"done", "skipped", "explicitly-deferred"}:
        existing["status"] = "done"
        existing["updatedAt"] = now
        existing["resolution"] = {"outcome": "done", "summary": "All PTL learning candidates have been reviewed.", "resolvedAt": now}
        if state.get("activeTaskId") == HUMAN_REVIEW_TASK_ID:
            state["activeTaskId"] = None
        if state.get("status") == "requires-human-decision":
            state["status"] = "active"
        state.setdefault("history", []).append(
            {
                "at": now,
                "event": "task-resolved",
                "taskId": HUMAN_REVIEW_TASK_ID,
                "outcome": "done",
                "summary": "All PTL learning candidates have been reviewed.",
            }
        )
    history = state.get("history")
    if isinstance(history, list):
        del history[:-200]
    write_json(pipeline_path, state)


def accept_candidate(
    repo: Path,
    *,
    candidate_id: str,
    scope: str | None = None,
    decision: str | None = None,
    registry: Path | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    review = scan(repo, registry=registry)
    candidate = find_candidate(review, candidate_id)
    accepted_scope = scope or str(candidate.get("suggestedScope") or "user-global")
    accepted_decision = decision or str(candidate.get("suggestedDecision") or "warn")
    if accepted_scope not in VALID_SCOPES:
        raise SystemExit(f"invalid scope: {accepted_scope}")
    if accepted_decision not in VALID_DECISIONS:
        raise SystemExit(f"invalid decision: {accepted_decision}")

    target = registry_path(registry)
    registry_payload = load_registry(target)
    rules = [item for item in registry_payload.get("rules", []) if isinstance(item, dict)]
    rule = {
        "id": str(candidate.get("id")),
        "stableKey": str(candidate.get("stableKey")),
        "status": "accepted",
        "title": str(candidate.get("title")),
        "ruleText": str(candidate.get("ruleText")),
        "rationale": str(candidate.get("rationale")),
        "scope": accepted_scope,
        "decision": accepted_decision,
        "keywords": candidate.get("keywords", []),
        "sourceProject": repo.name,
        "sourceReviewPath": REVIEW_FILE.as_posix(),
        "acceptedAt": iso_now(),
        "acceptedBy": "human-review",
        "evidence": candidate.get("evidence", [])[:8],
    }
    replaced = False
    for index, item in enumerate(rules):
        if item.get("stableKey") == rule["stableKey"]:
            rules[index] = {**item, **rule}
            replaced = True
            break
    if not replaced:
        rules.append(rule)
    registry_payload = {"schema": REGISTRY_SCHEMA, "updatedAt": iso_now(), "rules": rules}
    write_json(target, registry_payload)

    candidate["status"] = "accepted"
    candidate["acceptedAt"] = rule["acceptedAt"]
    candidate["acceptedScope"] = accepted_scope
    candidate["acceptedDecision"] = accepted_decision
    review["registryPath"] = str(target)
    save_review(repo, review)
    return {"ok": True, "action": "accepted", "candidate": candidate, "registryPath": str(target), "rule": rule}


def accept_all_candidates(repo: Path, *, registry: Path | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    review = scan(repo, registry=registry)
    pending = [item for item in review.get("candidates", []) if isinstance(item, dict) and item.get("status") == "candidate"]
    accepted: list[dict[str, Any]] = []
    for candidate in pending:
        result = accept_candidate(
            repo,
            candidate_id=str(candidate.get("id")),
            scope=str(candidate.get("suggestedScope") or "user-global"),
            decision=str(candidate.get("suggestedDecision") or "warn"),
            registry=registry,
        )
        accepted.append(result.get("candidate", {}))
    final_review = scan(repo, registry=registry)
    return {
        "ok": True,
        "action": "accepted-all",
        "accepted": len(accepted),
        "candidates": accepted,
        "summary": final_review.get("summary", {}),
        "registryPath": str(registry_path(registry)),
    }


def normalized_decision_text(text: str) -> str:
    return "".join(ch for ch in text.strip().casefold() if ch.isalnum() or "\u4e00" <= ch <= "\u9fff")


def word_action(text: str) -> str:
    lowered = text.casefold()
    if any(word in lowered for word in ACCEPT_WORDS):
        return "accept"
    if any(word in lowered for word in REJECT_WORDS):
        return "reject"
    if any(word in lowered for word in SNOOZE_WORDS):
        return "snooze"
    return ""


def extract_numbers(text: str, max_index: int) -> list[int]:
    numbers: list[int] = []
    for raw in re.findall(r"\d+", text):
        value = int(raw)
        if 1 <= value <= max_index and value not in numbers:
            numbers.append(value)
    return numbers


def parse_review_decisions(text: str, pending: list[dict[str, Any]]) -> dict[str, str]:
    normalized = normalized_decision_text(text)
    actions: dict[str, str] = {}
    if not pending:
        return actions
    if normalized in {"全部接受", "全都接受", "都接受", "acceptall", "approveall"}:
        return {str(item.get("id")): "accept" for item in pending if item.get("id")}
    if normalized in {"全部拒绝", "全都拒绝", "都拒绝", "rejectall"}:
        return {str(item.get("id")): "reject" for item in pending if item.get("id")}
    if normalized in {"全部稍后", "全部暂缓", "全都稍后", "snoozeall", "laterall"}:
        return {str(item.get("id")): "snooze" for item in pending if item.get("id")}

    chunks = [chunk.strip() for chunk in re.split(r"[，,；;\n]+", text) if chunk.strip()]
    for chunk in chunks:
        action = word_action(chunk)
        if not action:
            continue
        for number in extract_numbers(chunk, len(pending)):
            candidate_id = str(pending[number - 1].get("id") or "")
            if candidate_id:
                actions[candidate_id] = action
    return actions


def apply_human_review_response(repo: Path, *, response: str, registry: Path | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    review = scan(repo, registry=registry)
    pending = [item for item in review.get("candidates", []) if isinstance(item, dict) and item.get("status") == "candidate"]
    actions = parse_review_decisions(response, pending)
    if not actions:
        return {
            "ok": True,
            "processed": False,
            "reason": "no supported PTL review decision found",
            "remaining": concise_pending(pending),
        }

    applied: list[dict[str, str]] = []
    by_id = {str(item.get("id")): item for item in pending if item.get("id")}
    for candidate_id, action in actions.items():
        if candidate_id not in by_id:
            continue
        if action == "accept":
            candidate = by_id[candidate_id]
            accept_candidate(
                repo,
                candidate_id=candidate_id,
                scope=str(candidate.get("suggestedScope") or "user-global"),
                decision=str(candidate.get("suggestedDecision") or "warn"),
                registry=registry,
            )
        elif action == "reject":
            reject_candidate(repo, candidate_id=candidate_id, reason="human review response", registry=registry)
        elif action == "snooze":
            snooze_candidate(repo, candidate_id=candidate_id, days=7, reason="human review response", registry=registry)
        applied.append({"id": candidate_id, "action": action})

    final_review = scan(repo, registry=registry)
    final_pending = [item for item in final_review.get("candidates", []) if isinstance(item, dict) and item.get("status") == "candidate"]
    return {
        "ok": True,
        "processed": bool(applied),
        "applied": applied,
        "remaining": concise_pending(final_pending),
        "summary": final_review.get("summary", {}),
        "registryPath": str(registry_path(registry)),
    }


def concise_pending(pending: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "index": str(index),
            "id": str(item.get("id") or ""),
            "title": str(item.get("title") or ""),
            "suggestedAction": str(item.get("suggestedDecision") or ""),
        }
        for index, item in enumerate(pending, start=1)
    ]


def human_prompt_label(item: dict[str, Any]) -> str:
    title = str(item.get("title") or item.get("id") or "")
    if "human-decision prompts" in title.lower():
        return "人类确认提示必须列清待办项和一行回复格式"
    if "human confirmation inside the task loop" in title.lower():
        return "人类确认必须作为 loop task，确认后自动继续"
    if "workaround" in title.lower():
        return "禁止短期 workaround 代替可复用主线"
    if "host/message ingress" in title.lower() or "transport" in title.lower():
        return "宿主 / hook / wrapper 改动必须先 smoke 验证"
    if "verified facts" in title.lower() or "untested" in title.lower():
        return "未验证路径不能当事实说"
    if "task loop" in title.lower() or "completion gate" in title.lower():
        return "开发任务持续在 loop 中推进到完成或阻塞"
    return title


def render_human_prompt(pending: list[dict[str, Any]], *, title: str = "需要你确认") -> str:
    lines = [
        f"# {title}",
        "",
        "## 需要人类做什么",
        "",
        "1. 看下面的待确认规则。",
        "2. 只回复一行决策。",
        "3. 如果不想一次全处理，就按编号分别写清楚。",
        "",
        "## 你可以直接回复",
        "",
        "### 全部同意就回复：",
        "",
        "`全部接受`",
        "",
        "### 只处理部分就回复：",
        "",
        "`接受 1/2，3 稍后，4 拒绝`",
        "",
        "## 待确认规则",
    ]
    for index, item in enumerate(pending, start=1):
        lines.append(f"{index}. {human_prompt_label(item)}")
    return "\n".join(lines)


def reject_candidate(repo: Path, *, candidate_id: str, reason: str = "", registry: Path | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    review = scan(repo, registry=registry)
    candidate = find_candidate(review, candidate_id)
    candidate["status"] = "rejected"
    candidate["rejectedAt"] = iso_now()
    candidate["rejectReason"] = reason
    save_review(repo, review)
    return {"ok": True, "action": "rejected", "candidate": candidate}


def snooze_candidate(repo: Path, *, candidate_id: str, days: int = 7, reason: str = "", registry: Path | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    review = scan(repo, registry=registry)
    candidate = find_candidate(review, candidate_id)
    candidate["status"] = "snoozed"
    candidate["snoozedAt"] = iso_now()
    candidate["snoozedUntil"] = iso_from_epoch(time.time() + max(days, 1) * 86400)
    candidate["snoozeReason"] = reason
    save_review(repo, review)
    return {"ok": True, "action": "snoozed", "candidate": candidate}


def render_panel(review: dict[str, Any], *, registry: Path | None = None) -> str:
    candidates = [item for item in review.get("candidates", []) if isinstance(item, dict)]
    pending = [item for item in candidates if item.get("status") == "candidate"]
    accepted = accepted_rules(registry)
    summary = review.get("summary") if isinstance(review.get("summary"), dict) else summarize_candidates(candidates, registry=registry)
    lines = [
        "## PTL Learning Review",
        "",
        "| 项目 | 当前值 |",
        "| --- | --- |",
        f"| Pending | `{summary.get('pending', 0)}` |",
        f"| Accepted Registry Rules | `{summary.get('acceptedRegistry', 0)}` |",
        f"| Registry | `{registry_path(registry)}` |",
        f"| Review File | `{REVIEW_FILE.as_posix()}` |",
    ]
    if not pending:
        lines.extend(["", "当前没有待 review 的 PTL learning candidate。"])
    else:
        lines.extend(["", render_human_prompt(pending), "", "## 详情（可选）"])
        for item in pending:
            evidence_lines = []
            for ev in item.get("evidence", [])[:3]:
                if isinstance(ev, dict):
                    evidence_lines.append(f"- `{ev.get('messageId')}` / `{ev.get('taskId')}`: {ev.get('excerpt')}")
            display_index = pending.index(item) + 1
            lines.extend(
                [
                    "",
                    f"## {display_index}. {human_prompt_label(item)}",
                    "",
                    f"- 建议：`{item.get('suggestedDecision')}`",
                    f"- 范围：`{item.get('suggestedScope')}`",
                    f"- ID：`{item.get('id')}`",
                    f"- 规则：{item.get('ruleText')}",
                    "",
                    "证据：",
                    *(evidence_lines or ["- `(none)`"]),
                ]
            )
    if accepted:
        lines.extend(["", "### Accepted Learned Rules"])
        for rule in accepted[:20]:
            lines.append(f"- `{rule.get('id')}` `{rule.get('decision')}` {rule.get('title')}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage governed PTL learning review and persistent learned rules.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("repo", type=Path)
        subparser.add_argument("--registry", type=Path, default=None, help="Override learned registry path for tests or custom hosts.")
        subparser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown/text.")

    scan_parser = subparsers.add_parser("scan", help="Scan message ingress and update pending learning candidates.")
    add_common(scan_parser)
    scan_parser.add_argument("--min-occurrences", type=int, default=2)

    status_parser = subparsers.add_parser("status", help="Scan and print compact learning status.")
    add_common(status_parser)

    panel_parser = subparsers.add_parser("panel", help="Render a human review panel.")
    add_common(panel_parser)

    accept_parser = subparsers.add_parser("accept", help="Accept a candidate into the persistent learned registry.")
    add_common(accept_parser)
    accept_parser.add_argument("--id", required=True, dest="candidate_id")
    accept_parser.add_argument("--scope", choices=sorted(VALID_SCOPES), default=None)
    accept_parser.add_argument("--decision", choices=sorted(VALID_DECISIONS), default=None)

    accept_all_parser = subparsers.add_parser("accept-all", help="Accept every pending candidate into the persistent learned registry.")
    add_common(accept_all_parser)

    apply_response_parser = subparsers.add_parser("apply-response", help="Apply a concise human review response such as '接受 1/2/4，3 稍后'.")
    add_common(apply_response_parser)
    apply_response_parser.add_argument("--response", required=True)

    reject_parser = subparsers.add_parser("reject", help="Reject a candidate.")
    add_common(reject_parser)
    reject_parser.add_argument("--id", required=True, dest="candidate_id")
    reject_parser.add_argument("--reason", default="")

    snooze_parser = subparsers.add_parser("snooze", help="Snooze a candidate for a fixed number of days.")
    add_common(snooze_parser)
    snooze_parser.add_argument("--id", required=True, dest="candidate_id")
    snooze_parser.add_argument("--days", type=int, default=7)
    snooze_parser.add_argument("--reason", default="")

    args = parser.parse_args(argv)
    if args.command == "scan":
        payload = scan(args.repo, min_occurrences=max(args.min_occurrences, 1), registry=args.registry)
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render_panel(payload, registry=args.registry))
        return 0
    if args.command == "status":
        payload = scan(args.repo, registry=args.registry)
        result = {"ok": True, "reviewPath": str(review_path(args.repo)), "summary": payload.get("summary", {})}
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else f"pending: {result['summary'].get('pending', 0)}")
        return 0
    if args.command == "panel":
        payload = scan(args.repo, registry=args.registry)
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) if args.json else render_panel(payload, registry=args.registry))
        return 0
    if args.command == "accept":
        result = accept_candidate(args.repo, candidate_id=args.candidate_id, scope=args.scope, decision=args.decision, registry=args.registry)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else f"accepted: {args.candidate_id}")
        return 0
    if args.command == "accept-all":
        result = accept_all_candidates(args.repo, registry=args.registry)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else f"accepted: {result.get('accepted', 0)}")
        return 0
    if args.command == "apply-response":
        result = apply_human_review_response(args.repo, response=args.response, registry=args.registry)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else f"processed: {result.get('processed')}")
        return 0
    if args.command == "reject":
        result = reject_candidate(args.repo, candidate_id=args.candidate_id, reason=args.reason, registry=args.registry)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else f"rejected: {args.candidate_id}")
        return 0
    if args.command == "snooze":
        result = snooze_candidate(args.repo, candidate_id=args.candidate_id, days=args.days, reason=args.reason, registry=args.registry)
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) if args.json else f"snoozed: {args.candidate_id}")
        return 0
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
