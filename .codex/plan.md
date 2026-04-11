# Plan

## Current Phase

`self-retrofit and documentation-standard hardening`

## Slices

- Slice: establish self control surface
  - Objective: 给 `project-assistant` 自己补齐 `.codex/brief.md`、`.codex/plan.md`、`.codex/status.md`
  - Dependencies: 现有 skill 规则与脚本
  - Risks: 控制面内容与脚本能力描述不一致
  - Validation: `validate_control_surface.py` returns `ok: True`
  - Exit Condition: control surface exists and is usable

- Slice: normalize self docs
  - Objective: 把 `README.md`、`docs/README.md`、`docs/test-plan.md` 收到统一文档结构
  - Dependencies: `document-standards.md`, `sync_docs_system.py`, `validate_docs_system.py`
  - Risks: README 只满足门禁但不够易读
  - Validation: `validate_docs_system.py` returns `ok: True`
  - Exit Condition: durable docs are readable and pass the standard checks

- Slice: preserve convergent retrofit workflow
  - Objective: 确保 `整改` 默认同时覆盖控制面和文档系统，并具备脚本验收
  - Dependencies: `retrofit.md`, `usage.md`, `SKILL.md`
  - Risks: 规则写了但 README/usage 没同步
  - Validation: docs and rule references align; no missing command alias
  - Exit Condition: user can invoke `项目助手 整改` or `项目助手 文档整改` with predictable behavior
