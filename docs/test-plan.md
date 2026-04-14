# Test Plan

[English](test-plan.md) | [中文](test-plan.zh-CN.md)

## Scope and Risk

This plan verifies that `project-assistant` remains usable as a convergent project-governance skill.

Primary risks:

- control-surface drift
- partial retrofit behavior
- unclear progress output
- public docs falling out of structure or bilingual parity
- daemon runtime / host-state drift
- continue bridge or legacy rollout regressions on the new baseline

## Acceptance Cases

| Case | Setup | Action | Expected Result |
| --- | --- | --- | --- |
| Unified bootstrap front door | blank repo with a git root | run `project_assistant_entry.py bootstrap` | control surface, docs, and fast gate complete through one tool call |
| Control surface retrofit | target repo missing `.codex/*` | run retrofit flow | required control files exist and validate |
| Unified retrofit front door | repo has legacy docs / markdown clutter | run `project_assistant_entry.py retrofit` | control surface, docs, markdown governance, and fast gate complete through one tool call |
| Entry routing truth | repo expects the unified front door layer | run `validate_entry_routing.py` after bootstrap/retrofit or resume upgrade | `.codex/entry-routing.md` states the same daemon-host default fast path that maintainers, docs, and validators use |
| Large-project progress | target repo has module layer | run progress flow | output contains global view, module view, and Mermaid |
| Autonomous execution line | goal and active slice are clear | run execute or resume flow | assistant continues a meaningful checkpoint-sized run instead of stopping for repeated continue prompts |
| Context handoff | long-running repo with active slice | run handoff flow | compact resume pack with copy-paste commands |
| Daemon runtime | target repo already has control truth | run `project_assistant_entry.py daemon start/status/queue` | the local runtime starts, exposes queue/event state, and keeps a protected foreground-write lease |
| VS Code host shell | open the workspace that contains `integrations/vscode-host` | run extension validation and local smoke | the host shows live status, recent files, and task-log entry points |
| Continue bridge | runtime is `resume-ready` | trigger `manual continue` or `one-click continue` through the host | the resume action still reuses the unified front door instead of chat-box injection |
| Daemon-host local validation | use a representative local fixture repo | run `validate_daemon_host_mvp.py` | the daemon-host baseline covers bootstrap, retrofit, docs-retrofit, progress, continue, handoff, and the fast gate |
| Daemon-host legacy rollout | use a downgraded legacy fixture repo | run `validate_daemon_legacy_rollout.py` | the legacy repo upgrades first and then emits structured continue / progress / handoff output |
| Docs retrofit | repo has public docs | run docs retrofit flow | README and docs system are normalized and validate |
| Public-doc i18n | repo requires bilingual public docs | run i18n validator | English/Chinese doc pairs and switch links exist |
| Public-doc quality | repo has public docs | run doc-quality validator | public docs contain no placeholder prose, empty diagrams, or broken local links |
| Control-surface quality | repo has `.codex/*` | run control-surface quality validator | brief, plan, status, and module docs are not left in TODO/template state |
| Development log | repo produced durable implementation reasoning | write or validate a devlog entry | devlog index exists and each entry contains problem, thinking, solution, and validation |

## Automation Coverage

- `scripts/validate_control_surface.py`
- `scripts/validate_docs_system.py`
- `scripts/validate_public_docs_i18n.py`
- `scripts/validate_entry_routing.py`
- `scripts/validate_dogfooding_evidence.py`
- `scripts/validate_gate_set.py`
- `scripts/validate_doc_quality.py`
- `scripts/validate_control_surface_quality.py`
- `scripts/validate_development_log.py`
- `scripts/benchmark_latency.py`
- `scripts/validate_daemon_runtime.py`
- `scripts/validate_vscode_host_extension.py`
- `scripts/validate_daemon_host_mvp.py`
- `scripts/validate_daemon_legacy_rollout.py`

## Manual Checks

- verify the README reads well for first-time users
- verify Chinese and English public docs point to each other correctly
- verify diagrams clarify structure instead of repeating text
- verify execute and resume semantics imply a meaningful autonomous run, not a micro-step loop
- verify bootstrap and retrofit can be triggered from one canonical CLI front door instead of a hand-stitched shell sequence
- verify README, usage, architecture, test-plan, and `.codex/entry-routing.md` all describe the same daemon-host default fast path
- verify the daemon / queue control surface exposes readable state without interrupting the foreground coding lane
- verify the VS Code host makes it obvious that the page is moving, code is changing, and the task is still advancing
- verify development-log entries preserve the reasoning path without drifting into status prose

## Test Data and Fixtures

- this skill repo itself
- a medium repo with `.codex` only
- a large repo with module layer and durable docs

## Release Gate

Before calling the skill update complete:

- control-surface validation passes on the skill repo
- docs-system validation passes on the skill repo
- public-doc i18n validation passes on the skill repo
- entry-routing validation passes on the skill repo
- dogfooding-evidence validation passes on the skill repo
- layered gate-set validation passes on the skill repo
- doc-quality validation passes on the skill repo
- control-surface quality validation passes on the skill repo
- development-log validation passes on the skill repo
- daemon runtime, VS Code host shell, daemon-host baseline, and legacy rollout validation all pass on the skill repo
