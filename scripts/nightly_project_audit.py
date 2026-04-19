#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from control_surface_lib import control_surface_version_state, is_project_assistant_managed_repo, parse_tier


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = Path.home() / ".codex" / "project-assistant" / "nightly-audit" / "config.json"
DEFAULT_REPORT_ROOT = Path.home() / ".codex" / "project-assistant" / "nightly-audit" / "reports"
GATE_SCRIPT = ROOT / "scripts" / "validate_gate_set.py"
MARKDOWN_SCRIPT = ROOT / "scripts" / "validate_repo_markdown_integrity.py"


def expand_path(value: str) -> Path:
    return Path(os.path.expanduser(value)).resolve()


def default_config() -> dict[str, Any]:
    return {
        "discoveryRoots": [
            "/Users/redcreen/Project",
        ],
        "includeRepos": [
            str(ROOT),
        ],
        "excludeRepos": [],
        "excludeNamePrefixes": [
            ".",
        ],
        "excludeNameContains": [
            "--废弃",
        ],
        "defaultProfile": "auto",
        "expectProjectAssistantManagedByDefault": True,
        "notifyOnFailure": True,
        "reportDir": str(DEFAULT_REPORT_ROOT),
        "email": {
            "enabled": False,
            "recipients": [],
            "subjectPrefix": "项目助手夜间巡检",
            "language": "zh-CN",
            "alwaysSend": True,
            "attachMarkdownReport": True,
        },
        "repoPolicies": {
            str(ROOT): {
                "profile": "release",
            },
            "/Users/redcreen/Project/redcreen.github.io": {
                "allowUnmanaged": True,
                "profile": "fast",
            },
        },
    }


def load_config(path: Path) -> dict[str, Any]:
    defaults = default_config()
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(defaults, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return defaults
    loaded = json.loads(path.read_text(encoding="utf-8"))
    merged = dict(defaults)
    merged.update(loaded)
    merged_email = dict(defaults.get("email", {}))
    merged_email.update(loaded.get("email", {}))
    merged["email"] = merged_email
    if merged != loaded:
        path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return merged


def is_repo_root(path: Path) -> bool:
    return (path / ".git").exists() or (path / ".codex").exists()


def repo_policy(config: dict[str, Any], repo: Path) -> dict[str, Any]:
    policies = config.get("repoPolicies") or {}
    return dict(policies.get(str(repo), {}))


def should_exclude_repo(config: dict[str, Any], repo: Path) -> bool:
    exact = {str(expand_path(item)) for item in config.get("excludeRepos", [])}
    if str(repo) in exact:
        return True
    name = repo.name
    for prefix in config.get("excludeNamePrefixes", []):
        if prefix and name.startswith(str(prefix)):
            return True
    for fragment in config.get("excludeNameContains", []):
        if fragment and str(fragment) in name:
            return True
    return False


def discover_repos(config: dict[str, Any]) -> list[Path]:
    discovered: set[Path] = set()
    for raw_path in config.get("includeRepos", []):
        repo = expand_path(str(raw_path))
        if repo.exists():
            discovered.add(repo)
    for raw_root in config.get("discoveryRoots", []):
        root = expand_path(str(raw_root))
        if not root.exists():
            continue
        if is_repo_root(root):
            discovered.add(root)
        for child in sorted(root.iterdir()):
            if not child.is_dir():
                continue
            if is_repo_root(child):
                discovered.add(child.resolve())
    return sorted((repo for repo in discovered if not should_exclude_repo(config, repo)), key=lambda path: path.as_posix())


def run_command(args: list[str], cwd: Path | None = None) -> tuple[int, str]:
    result = subprocess.run(args, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
    output = result.stdout.strip()
    if result.stderr.strip():
        output = (output + "\n" + result.stderr.strip()).strip()
    return result.returncode, output


def git_dirty_summary(repo: Path) -> dict[str, Any]:
    if not (repo / ".git").exists():
        return {"tracked": False, "dirty": False, "count": 0}
    code, output = run_command(["git", "status", "--short"], cwd=repo)
    if code != 0:
        return {"tracked": True, "dirty": False, "count": 0, "error": output}
    lines = [line for line in output.splitlines() if line.strip()]
    return {
        "tracked": True,
        "dirty": bool(lines),
        "count": len(lines),
    }


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def notify_failure(summary: str) -> None:
    message = summary.replace('"', "'")
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification "{message}" with title "Project Assistant Nightly Audit"',
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception:
        pass


def apple_script_quote(value: str) -> str:
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"')


def should_send_email(config: dict[str, Any], payload: dict[str, Any], force: bool) -> bool:
    email_config = config.get("email") or {}
    if not email_config.get("enabled"):
        return False
    recipients = [item for item in email_config.get("recipients", []) if str(item).strip()]
    if not recipients:
        return False
    if force:
        return True
    if email_config.get("alwaysSend", True):
        return True
    summary = payload.get("summary") or {}
    return bool(summary.get("failingRepos") or summary.get("unmanagedRepos"))


def render_email_subject(config: dict[str, Any], payload: dict[str, Any]) -> str:
    email_config = config.get("email") or {}
    language = str(email_config.get("language") or "zh-CN").strip().lower()
    prefix = str(email_config.get("subjectPrefix") or ("项目助手夜间巡检" if language.startswith("zh") else "Project Assistant Nightly Audit")).strip()
    summary = payload.get("summary") or {}
    stamp = str(payload.get("generatedAt") or "")
    if language.startswith("zh"):
        return (
            f"{prefix} | 通过 {summary.get('passingRepos', 0)} | "
            f"失败 {summary.get('failingRepos', 0)} | 未托管 {summary.get('unmanagedRepos', 0)} | {stamp}"
        )
    return (
        f"{prefix} | pass {summary.get('passingRepos', 0)} | "
        f"fail {summary.get('failingRepos', 0)} | unmanaged {summary.get('unmanagedRepos', 0)} | {stamp}"
    )


def render_email_body(payload: dict[str, Any], markdown_path: Path) -> str:
    return render_email_body_zh(payload, markdown_path)


def render_email_body_zh(payload: dict[str, Any], markdown_path: Path) -> str:
    summary = payload.get("summary") or {}
    repos = payload.get("repos", [])
    passing = [item for item in repos if item.get("status") == "pass"]
    failing = [item for item in repos if item.get("status") == "fail"]
    unmanaged = [item for item in repos if item.get("status") == "unmanaged"]

    lines = [
        "项目助手夜间巡检摘要",
        "",
        f"生成时间：{payload.get('generatedAt', '')}",
        f"主机：{payload.get('host', '')}",
        f"扫描仓库数：{summary.get('totalRepos', 0)}",
        f"通过：{summary.get('passingRepos', 0)}",
        f"失败：{summary.get('failingRepos', 0)}",
        f"未托管：{summary.get('unmanagedRepos', 0)}",
        "",
        "总报告：",
        str(markdown_path),
        "",
    ]

    if passing:
        lines.append("已通过：")
        for item in passing:
            lines.append(
                f"- {item['name']}：门禁={item.get('gateResult', {}).get('ok', 'n/a')}，"
                f"Markdown={item.get('markdownResult', {}).get('ok', 'n/a')}，"
                f"工作区变更={item.get('git', {}).get('count', 0)}"
            )
        lines.append("")

    if failing:
        lines.append("失败项目：")
        for item in failing:
            reasons = "；".join(item.get("findings", [])[:3]) or "需要查看详细报告"
            lines.append(
                f"- {item['name']}：门禁={item.get('gateResult', {}).get('ok', 'n/a')}，"
                f"Markdown={item.get('markdownResult', {}).get('ok', 'n/a')}，"
                f"工作区变更={item.get('git', {}).get('count', 0)}"
            )
            lines.append(f"  原因：{reasons}")
            if item.get("gateOutputPath"):
                lines.append(f"  门禁明细：{item['gateOutputPath']}")
            if item.get("markdownOutputPath"):
                lines.append(f"  Markdown 明细：{item['markdownOutputPath']}")
        lines.append("")

    if unmanaged:
        lines.append("未托管项目：")
        for item in unmanaged:
            reasons = "；".join(item.get("findings", [])[:2]) or "当前未纳入项目助手治理"
            lines.append(f"- {item['name']}：{reasons}")
            if item.get("markdownOutputPath"):
                lines.append(f"  Markdown 明细：{item['markdownOutputPath']}")
        lines.append("")

    lines.extend(
        [
            "说明：",
            "- 这封邮件只发中文摘要，完整表格和明细见总报告与各仓库输出文件。",
            "- `工作区变更` 只表示当前有未提交改动，不单独算门禁失败。",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def render_email_body_en(payload: dict[str, Any], markdown_path: Path) -> str:
    summary = payload.get("summary") or {}
    lines = [
        "Nightly Project Assistant Audit",
        "",
        f"Generated: {payload.get('generatedAt', '')}",
        f"Host: {payload.get('host', '')}",
        f"Repositories Scanned: {summary.get('totalRepos', 0)}",
        f"Passing: {summary.get('passingRepos', 0)}",
        f"Failing: {summary.get('failingRepos', 0)}",
        f"Unmanaged: {summary.get('unmanagedRepos', 0)}",
        f"Latest Markdown Report: {markdown_path}",
        "",
        "Top-Level Status:",
    ]
    for item in payload.get("repos", []):
        lines.append(
            f"- {item['name']}: {item['status']} | gates={item.get('gateResult', {}).get('ok', 'n/a')} | "
            f"markdown={item.get('markdownResult', {}).get('ok', 'n/a')} | dirty={item.get('git', {}).get('count', 0)}"
        )
    lines.extend(
        [
            "",
            "Markdown Summary:",
            "",
            markdown_path.read_text(encoding="utf-8"),
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def send_email_via_mail_app(recipients: list[str], subject: str, body: str, attachment_path: Path | None) -> tuple[bool, str]:
    if not shutil.which("osascript"):
        return False, "osascript is unavailable"
    recipient_lines = "\n".join(
        f'make new to recipient at end of to recipients with properties {{address:"{apple_script_quote(item)}"}}'
        for item in recipients
    )
    attachment_block = ""
    if attachment_path:
        attachment_block = (
            f'make new attachment with properties {{file name:POSIX file "{apple_script_quote(str(attachment_path))}"}} '
            "at after the last paragraph\n"
        )
    script = "\n".join(
        [
            'tell application "Mail"',
            f'  set auditMessage to make new outgoing message with properties {{subject:"{apple_script_quote(subject)}", content:"{apple_script_quote(body)}", visible:false}}',
            "  tell auditMessage",
            f"    {recipient_lines}",
            f"    {attachment_block}".rstrip(),
            "    send",
            "  end tell",
            "end tell",
        ]
    )
    result = subprocess.run(["osascript", "-e", script], text=True, capture_output=True)
    if result.returncode == 0:
        return True, ""
    return False, (result.stderr or result.stdout or "Mail.app send failed").strip()


def send_email(config: dict[str, Any], payload: dict[str, Any], markdown_path: Path, force: bool = False) -> tuple[bool, str]:
    if not should_send_email(config, payload, force):
        return True, "email disabled"
    email_config = config.get("email") or {}
    recipients = [str(item).strip() for item in email_config.get("recipients", []) if str(item).strip()]
    subject = render_email_subject(config, payload)
    body = render_email_body(payload, markdown_path)
    attachment = markdown_path if email_config.get("attachMarkdownReport", True) else None
    return send_email_via_mail_app(recipients, subject, body, attachment)


def status_rank(status: str) -> int:
    return {
        "fail": 0,
        "unmanaged": 1,
        "pass": 2,
        "skipped": 3,
    }.get(status, 9)


def render_markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Nightly Project Assistant Audit",
        "",
        f"- Generated: `{payload['generatedAt']}`",
        f"- Host: `{payload['host']}`",
        f"- Config: `{payload['configPath']}`",
        f"- Repositories Scanned: `{payload['summary']['totalRepos']}`",
        f"- Passing: `{payload['summary']['passingRepos']}`",
        f"- Failing: `{payload['summary']['failingRepos']}`",
        f"- Unmanaged: `{payload['summary']['unmanagedRepos']}`",
        "",
        "| Repo | Managed | Tier | Profile | Gates | Markdown | Dirty | Status |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in payload["repos"]:
        managed = "yes" if item["managed"] else "no"
        gates = item.get("gateResult", {}).get("ok")
        markdown = item.get("markdownResult", {}).get("ok")
        dirty = item.get("git", {}).get("count", 0)
        lines.append(
            f"| `{item['name']}` | {managed} | `{item['tier']}` | `{item['profile']}` | "
            f"`{gates if gates is not None else 'n/a'}` | `{markdown if markdown is not None else 'n/a'}` | "
            f"`{dirty}` | `{item['status']}` |"
        )
    failures = [item for item in payload["repos"] if item["status"] in {"fail", "unmanaged"}]
    if failures:
        lines.extend(["", "## Findings", ""])
        for item in failures:
            lines.append(f"### {item['name']}")
            for finding in item.get("findings", []):
                lines.append(f"- {finding}")
            if item.get("gateOutputPath"):
                lines.append(f"- Gate Output: `{item['gateOutputPath']}`")
            if item.get("markdownOutputPath"):
                lines.append(f"- Markdown Audit Output: `{item['markdownOutputPath']}`")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def audit_repo(repo: Path, config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    policy = repo_policy(config, repo)
    tier = parse_tier(repo)
    managed = is_project_assistant_managed_repo(repo, tier=tier)
    version_state = control_surface_version_state(repo, tier=tier)
    dirty = git_dirty_summary(repo)
    expect_managed = policy.get("allowUnmanaged") is not True and bool(config.get("expectProjectAssistantManagedByDefault", True))
    profile = str(policy.get("profile") or config.get("defaultProfile") or "auto")

    result: dict[str, Any] = {
        "name": repo.name,
        "path": str(repo),
        "managed": managed,
        "tier": tier,
        "profile": profile,
        "status": "pass",
        "findings": [],
        "git": dirty,
        "versionState": version_state,
    }

    if expect_managed and not managed:
        result["status"] = "unmanaged"
        result["findings"].append("Repository is not yet managed by project-assistant control surfaces.")
    elif managed:
        code, output = run_command([sys.executable, str(GATE_SCRIPT), str(repo), "--profile", profile], cwd=ROOT)
        gate_output_path = output_dir / f"{repo.name}.gate.txt"
        write_text(gate_output_path, output + ("\n" if output else ""))
        result["gateResult"] = {"ok": code == 0}
        result["gateOutputPath"] = str(gate_output_path)
        if code != 0:
            result["status"] = "fail"
            result["findings"].append(f"Validation gates failed with profile `{profile}`.")
    else:
        result["gateResult"] = {"ok": None}
        result["findings"].append("Repository is intentionally outside project-assistant control-surface governance.")

    code, output = run_command([sys.executable, str(MARKDOWN_SCRIPT), str(repo), "--format", "text"], cwd=ROOT)
    markdown_output_path = output_dir / f"{repo.name}.markdown.txt"
    write_text(markdown_output_path, output + ("\n" if output else ""))
    result["markdownResult"] = {"ok": code == 0}
    result["markdownOutputPath"] = str(markdown_output_path)
    if code != 0:
        if result["status"] == "pass":
            result["status"] = "fail"
        result["findings"].append("Repo-wide markdown integrity audit found broken links, missing anchors, or absolute local paths.")

    if dirty.get("dirty"):
        result["findings"].append(f"Git worktree is dirty with {dirty['count']} changed paths.")

    return result


def build_payload(config_path: Path, repos: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "totalRepos": len(repos),
        "passingRepos": sum(1 for item in repos if item["status"] == "pass"),
        "failingRepos": sum(1 for item in repos if item["status"] == "fail"),
        "unmanagedRepos": sum(1 for item in repos if item["status"] == "unmanaged"),
    }
    return {
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "host": f"{socket.gethostname()} ({platform.platform()})",
        "configPath": str(config_path),
        "summary": summary,
        "repos": sorted(repos, key=lambda item: (status_rank(item["status"]), item["name"].lower())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a nightly multi-repo project-assistant compliance audit.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--write-default-config", action="store_true")
    parser.add_argument("--report-dir", type=Path, default=None)
    parser.add_argument("--notify", action="store_true", help="Force macOS failure notification for this run.")
    parser.add_argument("--force-email", action="store_true", help="Send the audit email even if policy would normally skip it.")
    args = parser.parse_args()

    config_path = args.config.expanduser().resolve()
    if args.write_default_config:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        write_text(config_path, json.dumps(default_config(), ensure_ascii=False, indent=2) + "\n")
        print(config_path)
        return 0

    config = load_config(config_path)
    report_root = (args.report_dir.expanduser().resolve() if args.report_dir else expand_path(str(config.get("reportDir") or DEFAULT_REPORT_ROOT)))
    run_stamp = datetime.now().astimezone().strftime("%Y-%m-%d/%H%M%S")
    output_dir = report_root / run_stamp
    output_dir.mkdir(parents=True, exist_ok=True)

    repos = discover_repos(config)
    repo_results = [audit_repo(repo, config, output_dir) for repo in repos]
    payload = build_payload(config_path, repo_results)

    json_path = output_dir / "summary.json"
    md_path = output_dir / "summary.md"
    safe_payload = json_safe(payload)
    write_text(json_path, json.dumps(safe_payload, ensure_ascii=False, indent=2) + "\n")
    write_text(md_path, render_markdown_report(payload))
    write_text(report_root / "latest.json", json.dumps(safe_payload, ensure_ascii=False, indent=2) + "\n")
    write_text(report_root / "latest.md", render_markdown_report(payload))

    email_ok, email_message = send_email(config, payload, md_path, force=args.force_email)
    if not email_ok:
        print(f"email-error: {email_message}", file=sys.stderr)

    print(md_path)
    if (args.notify or bool(config.get("notifyOnFailure"))) and (payload["summary"]["failingRepos"] or payload["summary"]["unmanagedRepos"]):
        notify_failure(
            f"{payload['summary']['failingRepos']} failing, {payload['summary']['unmanagedRepos']} unmanaged. See {md_path}"
        )

    if not email_ok:
        return 1
    return 0 if not (payload["summary"]["failingRepos"] or payload["summary"]["unmanagedRepos"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
