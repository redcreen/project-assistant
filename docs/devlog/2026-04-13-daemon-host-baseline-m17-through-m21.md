# 落成 M17-M21 daemon-host baseline 并收口控制真相

- 日期：2026-04-13
- 状态：resolved

## 问题

用户已经把 project-assistant 的同步编排时延定义成留存级问题：空白项目初始化接近分钟级，整改和恢复也会频繁打断主编码线。已有设计文档把方向切到 daemon-first + VS Code host，但仓库里仍停留在规划态，缺 working runtime、宿主壳、恢复桥和对应回归验证。

## 思考

如果继续只优化单点脚本或停在规划文档，用户体感不会真正改善。要把时延问题打掉，必须一次性把 M17-M21 落到 working baseline：前门仍保持唯一入口，低风险支撑任务移到本地 daemon 和 queue，宿主提供 live status 与 continue bridge，再用本地和 legacy fixture 把新基线压实。实现后还要把 status/plan/roadmap/development plan/README/architecture/test-plan/entry-routing 一起改到同一套真相，否则 durable surfaces 会重新分叉。

## 解决方案

新增 daemon runtime 与 daemon control surface（scripts/daemon_runtime.py、scripts/daemon_entry.py），把 daemon/queue 收进统一前门（scripts/project_assistant_entry.py），新增 VS Code 宿主壳（integrations/vscode-host/），补 daemon/runtime/host/legacy rollout 四条验证脚本，并把 deep gate 纳入这些校验。随后把 .codex/status.md、.codex/plan.md、roadmap、development plan、README、architecture、test plan、usage、COMMANDS、entry-routing 与监督面统一切到 post-M21 daemon-host baseline 叙事。顺手补了 daemon 并发 ensure 的 startup lock，避免双启动 race。

## 验证

已通过 validate_daemon_runtime.py、validate_vscode_host_extension.py、validate_daemon_host_mvp.py、validate_daemon_legacy_rollout.py，以及 validate_gate_set.py --profile deep；控制面、roadmap、development plan、README、architecture、test-plan、usage、entry-routing 和 supervision surfaces 已同步到 daemon-host baseline。

## 后续

- 继续做 daemon-host baseline 的 dogfooding 和 release 包装，不提前扩大到更重宿主表面或 M15。

## 相关文件

- .codex/status.md
- .codex/plan.md
- .codex/program-board.md
- scripts/daemon_runtime.py
- scripts/daemon_entry.py
- scripts/project_assistant_entry.py
- integrations/vscode-host/extension.js
- docs/roadmap.zh-CN.md
- docs/reference/project-assistant/development-plan.zh-CN.md
