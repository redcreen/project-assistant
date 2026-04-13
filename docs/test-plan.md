# Test Plan

[English](test-plan.md) | [中文](test-plan.zh-CN.md)

## Scope and Risk

This plan verifies that `project-assistant` remains usable as a convergent project-governance skill.

Primary risks:

- control-surface drift
- partial retrofit behavior
- unclear progress output
- public docs falling out of structure or bilingual parity

## Acceptance Cases

| Case | Setup | Action | Expected Result |
| --- | --- | --- | --- |
| Unified bootstrap front door | blank repo with a git root | run `project_assistant_entry.py bootstrap` | control surface, docs, and fast gate complete through one tool call |
| Control surface retrofit | target repo missing `.codex/*` | run retrofit flow | required control files exist and validate |
| Unified retrofit front door | repo has legacy docs / markdown clutter | run `project_assistant_entry.py retrofit` | control surface, docs, markdown governance, and fast gate complete through one tool call |
| Large-project progress | target repo has module layer | run progress flow | output contains global view, module view, and Mermaid |
| Autonomous execution line | goal and active slice are clear | run execute or resume flow | assistant continues a meaningful checkpoint-sized run instead of stopping for repeated continue prompts |
| Context handoff | long-running repo with active slice | run handoff flow | compact resume pack with copy-paste commands |
| Docs retrofit | repo has public docs | run docs retrofit flow | README and docs system are normalized and validate |
| Public-doc i18n | repo requires bilingual public docs | run i18n validator | English/Chinese doc pairs and switch links exist |
| Public-doc quality | repo has public docs | run doc-quality validator | public docs contain no placeholder prose, empty diagrams, or broken local links |
| Control-surface quality | repo has `.codex/*` | run control-surface quality validator | brief, plan, status, and module docs are not left in TODO/template state |
| Development log | repo produced durable implementation reasoning | write or validate a devlog entry | devlog index exists and each entry contains problem, thinking, solution, and validation |

## Automation Coverage

- `scripts/validate_control_surface.py`
- `scripts/validate_docs_system.py`
- `scripts/validate_public_docs_i18n.py`
- `scripts/validate_gate_set.py`
- `scripts/validate_doc_quality.py`
- `scripts/validate_control_surface_quality.py`
- `scripts/validate_development_log.py`
- `scripts/benchmark_latency.py`

## Manual Checks

- verify the README reads well for first-time users
- verify Chinese and English public docs point to each other correctly
- verify diagrams clarify structure instead of repeating text
- verify execute and resume semantics imply a meaningful autonomous run, not a micro-step loop
- verify bootstrap and retrofit can be triggered from one canonical CLI front door instead of a hand-stitched shell sequence
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
- layered gate-set validation passes on the skill repo
- doc-quality validation passes on the skill repo
- control-surface quality validation passes on the skill repo
- development-log validation passes on the skill repo
