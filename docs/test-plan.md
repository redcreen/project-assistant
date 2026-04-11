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
| Control surface retrofit | target repo missing `.codex/*` | run retrofit flow | required control files exist and validate |
| Large-project progress | target repo has module layer | run progress flow | output contains global view, module view, and Mermaid |
| Context handoff | long-running repo with active slice | run handoff flow | compact resume pack with copy-paste commands |
| Docs retrofit | repo has public docs | run docs retrofit flow | README and docs system are normalized and validate |
| Public-doc i18n | repo requires bilingual public docs | run i18n validator | English/Chinese doc pairs and switch links exist |

## Automation Coverage

- `scripts/validate_control_surface.py`
- `scripts/validate_docs_system.py`
- `scripts/validate_public_docs_i18n.py`

## Manual Checks

- verify the README reads well for first-time users
- verify Chinese and English public docs point to each other correctly
- verify diagrams clarify structure instead of repeating text

## Test Data and Fixtures

- this skill repo itself
- a medium repo with `.codex` only
- a large repo with module layer and durable docs

## Release Gate

Before calling the skill update complete:

- control-surface validation passes on the skill repo
- docs-system validation passes on the skill repo
- public-doc i18n validation passes on the skill repo
