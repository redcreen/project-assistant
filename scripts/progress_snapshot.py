#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from control_surface_lib import (
    classify_architecture_signal,
    completion_band,
    completion_percent,
    display_execution_task,
    execution_task_kind,
    execution_task_lines,
    execution_task_progress,
    first_line,
    labeled_bullet_value,
    normalized_execution_task_body,
    parse_delivery_supervision,
    parse_ptl_supervision,
    parse_program_board,
    parse_strategy_surface,
    parse_worker_handoff,
    parse_official_modules,
    parse_tier,
    primary_human_windows,
    read_text,
    repo_capabilities,
    section,
    slugify,
)
from sync_resume_readiness import ResumeReadinessResult, ensure_resume_ready


TRIVIAL_TOKENS = {
    "active",
    "advance",
    "adapter",
    "and",
    "current",
    "execution",
    "for",
    "line",
    "memory",
    "module",
    "next",
    "phase",
    "quality",
    "recall",
    "slice",
    "stage",
    "system",
    "the",
}

MODULE_NAME_MAP = {
    "source-system": "来源系统",
    "reflection-system": "反思系统",
    "memory-registry": "记忆注册表",
    "projection-system": "投影系统",
    "governance-system": "治理系统",
    "openclaw-adapter": "OpenClaw 适配层",
    "codex-adapter": "Codex 适配层",
}

SUBPROJECT_NAME_MAP = {
    "core-product": "核心产品",
    "host-neutral-memory": "宿主中立记忆",
    "memory-governance": "记忆治理",
    "plugin-runtime": "插件运行时",
}

MEDIUM_SLICE_EXPLANATIONS = {
    "operator ux snapshot depth": "给 continuity / triage 增加更短的值班快照",
    "planning anomaly acceptance expansion": "补规划异常场景的正式验收覆盖",
    "channel acceptance sample expansion": "补更真实的渠道样本验收覆盖",
    "operator recovery acceptance expansion": "补运维恢复路径的正式验收覆盖",
    "planning evidence archival convergence": "把 planning 证据收口到归档链路",
    "runtime source-of-truth convergence": "把 runtime 双源收口到唯一 canonical source",
    "lifecycle coordinator boundary": "把 lifecycle 责任收口到单一协调边界",
    "post-hardening feature follow-on": "在架构加固完成后推进下一条功能增强",
    "tighten-maintainer-facing-narrative-and-architecture-triggers": "把 progress / continue / handoff 改得更像给维护者看，并把架构升级触发变成自动信号",
    "evaluate-locale-aware-internal-output": "评估哪些内部控制面输出应该按语言优化，减少中文工作流里的冗余英文",
    "close-m13-and-m14-and-queue-m15-evidence": "收口 PTL 监督环与 worker 接续层，并开始判断是否真的需要 M15 多执行器层",
}

MEDIUM_SLICE_VALUE = {
    "operator ux snapshot depth": "值班时更快看出哪些任务卡住、哪些需要恢复。",
    "planning anomaly acceptance expansion": "让异常场景不是只靠人工猜，而是进入正式验收。",
    "channel acceptance sample expansion": "让渠道行为不只停留在静态矩阵，而是有可运行样本。",
    "operator recovery acceptance expansion": "让恢复路径成为 release-facing 契约，而不是零散 helper。",
    "planning evidence archival convergence": "让历史 planning 证据可追溯，回来看项目时不丢上下文。",
    "runtime source-of-truth convergence": "避免维护者继续在双 runtime 树之间来回猜 canonical source。",
    "lifecycle coordinator boundary": "把生命周期责任收口，减少后续同类修补。",
    "post-hardening feature follow-on": "让项目从补结构切回有价值的功能增强。",
    "tighten-maintainer-facing-narrative-and-architecture-triggers": "让维护者回来接手时更少需要翻译，并让架构纠偏更早自动暴露。",
    "evaluate-locale-aware-internal-output": "让中文优先工作流更短、更顺手，同时不牺牲公开文档双语和 AI 恢复精度。",
    "close-m13-and-m14-and-queue-m15-evidence": "让 PTL 监督环和 worker 接续都变成 durable 真相，并把是否需要 M15 交给后续证据来决定。",
}

TERM_CATALOG = {
    "dashboard": {
        "label": "dashboard",
        "meaning": "运维总览视图",
        "when": "想先看整体状态时",
        "current": "这是运维视图的总入口。",
    },
    "triage": {
        "label": "triage",
        "meaning": "异常分诊视图",
        "when": "想优先看问题和处理顺序时",
        "current": "这轮给它补了更短的快照视图。",
    },
    "continuity": {
        "label": "continuity",
        "meaning": "连续性 / 恢复视图",
        "when": "想看哪些任务断了、卡住了、需要续跑时",
        "current": "这轮给它补了 `--compact` 和 `--only-issues`。",
    },
    "watchdog": {
        "label": "watchdog",
        "meaning": "看门狗恢复机制",
        "when": "想确认是否有阻塞、卡死、自动恢复提示时",
        "current": "当前 acceptance 已覆盖它的 operator-facing 表现。",
    },
    "[wd]": {
        "label": "[wd]",
        "meaning": "runtime 接管回执",
        "when": "想确认请求是否已进入 task-system 控制时",
        "current": "这是主线已完成能力的一部分。",
    },
}

STEADY_STATE_TOKENS = (
    "steady state",
    "steady-state maintenance",
    "stable after closing milestone",
    "后基线已稳定",
    "回到稳定维护状态",
    "等待新的命名 roadmap 候选",
)

EXACT_TEXT_MAP = {
    "stage closeout / stage 5 complete": "收口阶段 / Stage 5 已完成",
    "hold-post-stage5-roadmap-state-aligned": "保持 post-Stage-5 路线图状态对齐",
    "none at the implementation layer": "实现层当前无 blocker",
    "align project/workstream roadmap summaries with the current stage 5 closeout baseline": "把 project/workstream roadmap 摘要对齐到当前 Stage 5 收口基线",
    "refresh smoke and memory-search governance snapshots in the visible project state": "刷新可见项目状态里的 smoke 与 memory-search governance 快照",
    "keep `registry inspect`, release-preflight, and public docs aligned with the operator baseline": "保持 `registry inspect`、release-preflight 与公开文档和当前 operator baseline 一致",
    "keep later enhancement planning gated behind stable runtime api prerequisites instead of reopening the next phase early": "在 runtime API 前提稳定之前，继续把后续 enhancement planning 挂起，不提前重开下一阶段",
    "source system": "来源系统",
    "reflection system": "反思系统",
    "memory registry": "记忆注册表",
    "projection system": "投影系统",
    "governance system": "治理系统",
    "openclaw adapter": "OpenClaw 适配层",
    "codex adapter": "Codex 适配层",
    "strategic evaluation layer": "战略评估层",
    "program orchestration layer": "程序编排层",
    "program orchestration layer closed; m12 queued": "程序编排层已收口；M12 启动已排队",
    "supervised long-run delivery": "长期受监督交付层",
    "supervised long-run delivery layer closed; rollout queued": "长期受监督交付层已收口；rollout 已排队",
    "ptl supervision loop": "PTL 监督环",
    "worker handoff and re-entry": "worker 接续与回流",
    "ptl supervision and worker handoff layers closed; m15 evidence collection queued": "PTL 监督环与 worker 接续层已收口；M15 证据采集已排队",
    "strategic evaluation layer foundation": "战略评估层基线",
    "strategic evaluation layer closed; m11 kickoff queued": "战略评估层已收口；M11 启动已排队",
    "establish-strategy-surface-and-review-contract": "建立战略面与 review contract",
    "close-m10-and-queue-m11": "关闭 M10 并排队 M11",
    "close-m11-and-queue-m12": "关闭 M11 并排队 M12",
    "close-m12-and-open-rollout": "关闭 M12 并打开 rollout",
    "close-m13-and-m14-and-queue-m15-evidence": "关闭 M13 / M14 并排队 M15 证据采集",
    "activate-program-board-and-orchestration-boundary": "激活 program-board 与程序编排边界",
    "define-strategy-evidence-and-review-contract": "定义战略证据与 review contract",
    "activate-m10-strategic-evaluation-layer": "激活 M10 战略评估层",
    "governed execution / module-view active": "治理执行中 / 模块视角已启用",
    "stage 3: self-learning lifecycle baseline": "阶段 3：self-learning 生命周期基线",
    "narrative quality and automated architecture triggers": "维护者视角叙事收口与自动架构触发",
    "locale-aware internal control-surface output": "按语言优化内部控制面输出",
    "stage 3：self-learning lifecycle 基线": "阶段 3：self-learning 生命周期基线",
    "advance-openclaw-adapter-recall-quality": "推进 OpenClaw 适配层召回质量扩面",
    "tighten-maintainer-facing-narrative-and-architecture-triggers": "收紧维护者视角叙事与自动架构触发",
    "evaluate-locale-aware-internal-output": "评估哪些内部控制面输出应该按语言优化",
    "milestone: post-hardening closeout": "加固后收口里程碑",
    "post-hardening closeout is complete, and the repo is back in steady-state maintenance until a new named roadmap candidate exists.": "加固后收口已经完成；在出现新的命名 roadmap 候选之前，仓库回到稳定维护状态。",
    "steady state: post-hardening stable": "稳定维护：加固后基线已稳定",
    "keep the shipped runtime, docs, and release-facing evidence stable after closing milestone 1": "在 Milestone 1 收口后，继续保持已发布 runtime、文档与 release-facing 证据稳定。",
    "registration and slash-override coverage expansion": "注册与 slash-override 覆盖扩面",
    "status command path coverage expansion": "status 命令路径覆盖扩面",
    "none currently.": "当前无主要风险。",
    "none currently": "当前无主要风险。",
    "post-doc baseline hardening is now closed through runtime-path and registration coverage; the repo is ready to choose its next maintenance or feature slice.": "文档整改后的基线加固已通过 runtime 路径与注册路径覆盖收口；仓库已准备进入下一条维护或功能切片。",
    "post-hardening feature work is underway; the broader release gate is still green and the latest extension slice deepened operator snapshot ux.": "后续增强正在推进；更宽的 release gate 仍保持绿色，本轮切片把 operator 短快照视图补得更深了。",
    "the docs retrofit slice is complete, and the repo is now rolled forward to one explicit next milestone: a post-hardening closeout run that should execute as one long-task line instead of many small cleanup slices.": "文档整改切片已完成；仓库已推进到一条明确的下一里程碑：用一条加固后收口长任务替代多条零散清理切片。",
    "close the remaining post-hardening boundary work in one uninterrupted run across compound/future-first convergence, evidence depth, operator/release-facing closeout, and final docs/archive convergence": "把剩余的加固后边界工作收成一条不停顿的长任务，覆盖 compound / future-first 收口、证据加深、operator/release-facing closeout，以及最终 docs/archive 收敛。",
    "ownership or boundary drift is visible in the current slice": "当前切片里已经出现 ownership / boundary drift 信号",
    "the current direction can continue, but architecture review should stay visible because an automatic trigger fired": "当前方向可以继续，但因为自动触发已经生效，架构复盘应继续保持可见。",
    "post-hardening work had remained too diffuse across extension bullets and small slices, which made “later closeout” easy to defer without one milestone owner or execution line": "post-hardening 工作之前分散在很多 extension bullets 和小切片里，没有一个明确 owner 或执行线，导致“以后再收口”这件事一直容易被推迟。",
    "close the milestone explicitly and return to watch-mode maintenance until a new named roadmap candidate exists": "明确关闭当前里程碑，并回到观察型稳定维护，直到出现新的命名 roadmap 候选。",
    "promote the remaining work into one named milestone with a durable plan and control-surface ownership": "把剩余工作提升成一条命名里程碑，并明确 durable plan 与 control-surface owner。",
    "deepen day-to-day operator ux by adding compact and issue-focused continuity / triage snapshots, then prove them through acceptance, docs, and broader gates": "给日常值班用的 operator 视图补更短、更聚焦问题的 continuity / triage 快照，并通过 acceptance、文档与更宽门禁把它收口。",
    "lock down plugin registration behavior so enabled/disabled, slashoverride, and command registration paths stay stable without relying on upstream host changes": "锁定插件注册行为，让启用/禁用、slashOverride 与命令注册路径保持稳定，且不依赖上游宿主改动。",
    "current execution can proceed inside the existing direction without a user-level tradeoff": "当前执行可以沿既有方向继续，不需要用户层面的额外取舍。",
    "current plugin registration boundary, config defaults, current status handler coverage": "当前插件注册边界、配置默认值与 status handler 覆盖面。",
    "low; tests may accidentally bind to incidental logger text instead of runtime behavior": "风险较低；测试可能误绑定到日志文案，而不是 runtime 行为。",
    "add snapshot summaries and cli flags for `continuity` and `triage` without splitting runbook truth": "给 `continuity` 与 `triage` 增加 snapshot 摘要和 CLI 参数，但不分叉 runbook 真相源。",
    "extend operator tests and acceptance so the shorter snapshot contract becomes release-facing": "扩 operator tests 与 acceptance，让较短快照 contract 进入 release-facing 验证。",
    "refresh operator docs, devlog, and `.codex/*` so the new snapshot entrypoints are recoverable": "刷新 operator docs、devlog 与 `.codex/*`，让新的 snapshot 入口可恢复。",
    "re-sync repo / installed runtime surfaces and rerun the broader release gate": "重新同步 repo / installed runtime 面，并重跑更宽的 release gate。",
    "choose the next post-hardening slice from real feishu / telegram evidence capture or broader release-gate depth instead of reopening already-covered helpers.": "从真实 Feishu / Telegram 证据采集或更深的 release-gate 覆盖里选择下一条 post-hardening 切片，而不是回头重做已覆盖的 helper。",
    "keep the new continuity / triage snapshot views aligned with stable acceptance if operator recovery wording changes again.": "如果 operator recovery 文案再变化，继续保持新的 continuity / triage 快照视图与 stable acceptance 对齐。",
    "rerun `bash scripts/run_tests.sh` and `python3 scripts/runtime/stable_acceptance.py --json` before batching more feature-facing changes on top of this operator ux slice.": "在叠加更多面向功能的改动前，先重跑 `bash scripts/run_tests.sh` 和 `python3 scripts/runtime/stable_acceptance.py --json`。",
    "define the next milestone in roadmap and durable project-level development plan docs": "在 roadmap 和 durable development plan 里定义下一条里程碑。",
    "close compound follow-up, future-first, and output-separation boundary drift from active docs and runtime-facing evidence": "从 active docs 与 runtime-facing 证据中，收口 compound follow-up、future-first 与 output-separation 的边界漂移。",
    "deepen planning/channel/operator evidence while keeping `bash scripts/run_tests.sh` and `release_gate.py --json` green": "在保持 `bash scripts/run_tests.sh` 与 `release_gate.py --json` 绿色的前提下，加深 planning / channel / operator 证据覆盖。",
    "do one final closeout pass across roadmap, test-plan, archive guidance, and control surfaces, then either close the milestone or split a new named roadmap candidate": "对 roadmap、test-plan、archive guidance 与控制面做最后一轮收口，然后决定关闭当前里程碑，还是拆出新的命名 roadmap 候选。",
    "keep `bash scripts/run_tests.sh` and `python3 scripts/runtime/release_gate.py --json` green on every runtime or plugin change.": "每次改动 runtime 或 plugin 时，都保持 `bash scripts/run_tests.sh` 和 `python3 scripts/runtime/release_gate.py --json` 为绿色。",
    "rerun planning evidence capture when a future change touches planning/runtime contracts or release-facing acceptance coverage materially.": "当后续改动实质影响 planning/runtime 契约或 release-facing acceptance 覆盖时，重新采集 planning 证据。",
    "name a new roadmap candidate before starting broader planning, steering, or operator extension work.": "在启动更宽的 planning、steering 或 operator 扩展工作前，先命名新的 roadmap 候选。",
    "release-facing validation fails, evidence requirements materially change, or new capability work needs a named roadmap candidate": "只有 release-facing 验证退红、证据要求发生实质变化，或确实出现新的命名 roadmap 候选时，才重开主线。",
    "choose the next slice: user-visible feature growth vs. install/runtime hardening.": "选择下一条切片：先做用户可见功能增强，还是先做安装 / 运行时加固。",
    "if feature-first wins, define the first concrete enhancement around quota display or command ergonomics.": "如果先做功能，先明确 quota 展示或命令体验的第一条具体增强。",
    "if hardening-first wins, evaluate whether cli injection runtime patch coverage should be the next checkpoint.": "如果先做加固，评估 CLI 注入 runtime patch 覆盖是否应成为下一检查点。",
    "n/a": "暂无",
    "no major blocker recorded.": "当前无主要风险。",
    "no major blocker recorded": "当前无主要风险。",
    "confirm whether the next enhancement phase introduces any new source requirements beyond the current local-first baseline.": "确认下一增强阶段是否会引入超出当前本地优先基线的新来源需求。",
    "name the next self-learning phase explicitly and decide whether it starts with promotion/decay rules or policy-input artifacts.": "明确命名下一阶段 self-learning，并决定先从 promotion/decay 规则还是 policy-input artifacts 开始。",
    "lock the host-neutral registry root and migration behavior before opening a deeper self-learning phase.": "在开启更深一层 self-learning phase 前，先锁定宿主中立的 registry root 与迁移行为。",
    "decide the policy-input artifact shape before starting consumer-specific adaptation work.": "在启动 consumer-specific 适配前，先决定 policy-input artifact 的形态。",
    "maintain stable governance outputs while the next plugin-runtime and learning changes are introduced.": "在引入下一批 plugin-runtime 与 learning 变更时，保持治理输出稳定。",
    "keep live openclaw behavior stable while the now-single-card family-overview path rolls into the next stable fact / stable rule batch.": "在当前 single-card family-overview 路径滚入下一批稳定事实 / 稳定规则时，保持线上 OpenClaw 行为稳定。",
    "prove that codex can read the same workspace memory from the shared canonical root.": "证明 Codex 能从共享 canonical root 读取同一份 workspace memory。",
    "continue expanding stable facts / stable rules while keeping recalled context clean": "继续扩稳定事实 / 稳定规则，同时保持召回上下文干净",
    "advance-openclaw-adapter-recall-quality: continue expanding stable facts / stable rules while keeping recalled context clean": "推进 OpenClaw 适配层 recall 质量扩面：继续扩稳定事实 / 稳定规则，同时保持召回上下文干净",
    "继续扩稳定事实 / 稳定规则，同时保持 recalled context 干净": "继续扩稳定事实 / 稳定规则，同时保持召回上下文干净",
}

PHRASE_REPLACEMENTS = [
    ("roadmap reshaping", "roadmap 重排建议"),
    ("governance / architecture side-tracks", "治理 / 架构专项插入建议"),
    ("milestone reorder suggestions", "里程碑重排建议"),
    ("strategic carryover decisions for supporting backlog topics", "supporting backlog 议题的战略回收建议"),
    ("confirm the closeout objective for", "确认收口目标："),
    ("add a reusable strategic surface sync path and a strategy validator", "增加可复用的战略面 sync 路径和 strategy validator"),
    ("wire strategic snapshots into", "把战略快照接入"),
    ("close m10 across readme, roadmap, development plan, strategy docs, and control truth", "把 M10 在 README、roadmap、development plan、strategy docs 和 control truth 上全部收口"),
    ("capture a devlog entry because m10 is now complete and m11 is officially queued", "记录一条开发日志，因为 M10 已完成且 M11 已正式排队"),
    ("add a reusable program-board sync path and a program-board validator", "增加可复用的 program-board sync 路径和 program-board validator"),
    ("wire program-board summaries into `progress / continue / handoff`", "把 program-board 摘要接入 `progress / continue / handoff`"),
    ("close m11 across readme, roadmap, development plan, program-board docs, and control truth", "把 M11 在 README、roadmap、development plan、program-board docs 和 control truth 上全部收口"),
    ("capture a devlog entry because m11 is now complete and m12 is officially queued", "记录一条开发日志，因为 M11 已完成且 M12 已正式排队"),
    ("add a reusable delivery-supervision sync path and a delivery-supervision validator", "增加可复用的 delivery-supervision sync 路径和 validator"),
    ("wire delivery-supervision summaries into `progress / continue / handoff`", "把 delivery-supervision 摘要接入 `progress / continue / handoff`"),
    ("close m12 across readme, roadmap, development plan, delivery-supervision docs, and control truth", "把 M12 在 README、roadmap、development plan、delivery-supervision docs 和 control truth 上全部收口"),
    ("capture a devlog entry because m12 is now complete and rollout is officially queued", "记录一条开发日志，因为 M12 已完成且 rollout 已正式排队"),
    ("business direction changes", "业务方向变化"),
    ("compatibility promises", "兼容性承诺"),
    ("external positioning changes", "对外定位变化"),
    ("significant cost or timeline tradeoffs", "显著成本或时间取舍"),
    ("no automatic trigger is currently active", "当前没有自动触发"),
    ("no blocker or escalation trigger is currently forcing a higher-level decision", "当前没有 blocker 或升级信号迫使做更高层裁决"),
    ("continue automatically", "自动继续"),
    ("raise but continue", "提醒后继续"),
    ("require user decision", "需要用户裁决"),
    ("Post-doc baseline hardening", "文档整改后基线加固"),
    ("is now closed", "已收口"),
    ("the repo is ready to choose its next maintenance or feature slice", "仓库已准备进入下一条维护或功能切片"),
    ("runtime-path", "runtime 路径"),
    ("registration coverage", "注册路径覆盖"),
    ("lock down", "锁定"),
    ("plugin registration behavior", "插件注册行为"),
    ("enabled/disabled", "启用/禁用"),
    ("slashoverride", "slashOverride"),
    ("command registration paths", "命令注册路径"),
    ("stay stable", "保持稳定"),
    ("without relying on upstream host changes", "且不依赖上游宿主改动"),
    ("插件注册行为 so 启用/禁用, slashOverride, and 命令注册路径 保持稳定", "插件注册行为，让启用/禁用、slashOverride 与命令注册路径保持稳定"),
    ("current plugin registration boundary", "当前插件注册边界"),
    ("config defaults", "配置默认值"),
    ("current status handler coverage", "当前 status handler 覆盖面"),
    ("tests may accidentally bind to incidental logger text instead of runtime behavior", "测试可能误绑定到偶发日志文本，而不是 runtime 行为"),
    ("low; ", "风险较低；"),
    ("current plugin registration boundary, config defaults, current status handler coverage", "当前插件注册边界、配置默认值与 status handler 覆盖面"),
    ("declared sources", "声明式来源"),
    ("candidate artifacts", "候选 artifacts"),
    ("candidate promotion", "候选升级"),
    ("export/audit surfaces", "export / audit 面"),
    ("decision trails", "决策轨迹"),
    ("repeated signal", "重复信号"),
    ("clean assembly", "clean assembly"),
    ("self-learning foundations implemented", "self-learning foundations 已落地"),
    ("next lifecycle-phase planning", "下一生命周期阶段待规划"),
    ("promotion helper", "promotion helper"),
    ("synthetic-query", "synthetic-query"),
    ("confirm the checkpoint and objective for", "确认当前检查点与目标："),
    ("verify dependencies and affected boundaries", "确认依赖与受影响边界"),
    ("confirm architecture signal, root-cause hypothesis, and correct layer still hold", "确认架构信号、根因假设和正确落层仍然成立"),
    ("implement the highest-value change for", "实现当前切片里价值最高的一项改动："),
    ("address the main execution risk", "处理当前执行风险"),
    ("update docs, control-surface notes, or contracts touched by this slice", "同步本切片涉及的文档、控制面说明或契约"),
    ("run validation", "运行验证"),
    ("refresh progress, capabilities, next checkpoint, and next 3 actions", "刷新进展、能力快照、下一检查点和 Next 3"),
    ("capture a devlog entry if the root cause, tradeoff, or rejected shortcut changed", "如果根因、取舍或拒绝捷径发生变化，记录一条开发日志"),
    ("the repo can drift back to local fixes if the current slice loses a visible architectural checkpoint", "如果当前切片失去可见的架构检查点，仓库很容易退回局部修补"),
    ("control surface, validators, and reporting", "控制面、校验器和进展汇报层"),
    ("the current direction can continue, but the supervision state should stay visible", "当前方向可以继续，但监督状态需要保持可见"),
    ("open blockers or architectural risks are still recorded", "当前仍记录着 blocker 或架构风险"),
    ("architecture supervision is guarding against local-only fixes", "架构监督正在防止问题退回局部修补"),
    ("source contracts and manifest baseline", "来源契约与清单基线"),
    ("local-first source registration and normalization", "本地优先来源注册与标准化"),
    ("registry persistence baseline", "registry 持久化基线"),
    ("source/candidate/stable artifact separation", "source/candidate/stable artifact 分层"),
    ("reflection contract baseline", "reflection 契约基线"),
    ("candidate extraction and reflection outputs", "候选提取与 reflection 输出"),
    ("daily reflection runner and structured report shape", "daily reflection 执行器与结构化报告形态"),
    ("repeated-signal scoring and explicit-remember detection baseline", "重复信号评分与显式 remember 检测基线"),
    ("promotion-review baseline through reflection outputs", "通过 reflection 输出形成 promotion-review 基线"),
    ("projection export contract baseline", "projection 导出契约基线"),
    ("visibility filtering", "可见性过滤"),
    ("OpenClaw / Codex / generic projection path", "OpenClaw / Codex / 通用 projection 路径"),
    ("promoted stable artifacts can already leave the registry through explicit exports", "promoted stable artifacts 已可通过显式导出离开 registry"),
    ("projection-system tests", "projection-system 测试"),
    ("formal audit, duplicate audit, and conflict audit", "正式审计、重复审计与冲突审计"),
    ("governance cycle and repair/replay primitives", "governance cycle 与 repair/replay 基元"),
    ("memory-search governance metrics", "memory-search 治理指标"),
    ("namespace audit around exported stable artifacts", "围绕 exported stable artifacts 的 namespace 审计"),
    ("smoke-promotion helper as a conservative suggestion path", "smoke-promotion helper 作为保守建议路径"),
    ("registry-root consistency surfaced through governance cycle output", "通过 governance cycle 输出暴露 registry-root consistency"),
    ("OpenClaw adapter runtime integration", "OpenClaw 适配层 runtime 集成"),
    ("memory-search phases A-E baseline", "memory-search A-E 阶段基线"),
    ("retrieval / rerank / assembly / scoring baseline", "retrieval / rerank / assembly / scoring 基线"),
    ("smoke coverage and current quality metrics", "smoke 覆盖与当前质量指标"),
    ("dedicated family-overview stable card path for", "为"),
    ("with same-path dual-card fallback kept only as a compatibility backstop", "并仅把同路径双卡兜底保留为兼容回退"),
    ("Codex adapter runtime integration baseline", "Codex 适配层 runtime 集成基线"),
    ("compatibility coverage across OpenClaw / Codex / governance surfaces", "OpenClaw / Codex / governance 面的兼容性覆盖"),
    ("first-class adapter position in product docs and architecture", "在产品文档和架构中的一等适配层位置"),
    ("registry persistence baseline", "registry 持久化基线"),
    ("source/candidate/stable artifact separation", "source/candidate/stable artifact 分层"),
    ("local-first lifecycle loop", "本地优先生命周期闭环"),
    ("candidate -> stable promotion baseline with decision trail", "带 decision trail 的 candidate -> stable 升级基线"),
    ("registry test coverage for lifecycle primitives", "生命周期基元的 registry 测试覆盖"),
    ("source contracts and manifest baseline", "来源契约与清单基线"),
    ("local-first source registration and normalization", "本地优先来源注册与标准化"),
    ("fingerprinting and source-to-candidate pipeline", "指纹提取与 source-to-candidate 管线"),
    ("source-system tests and replay-oriented structure", "source-system 测试与面向 replay 的结构"),
    ("baseline complete", "基线完成"),
    ("next-phase candidate", "下一阶段候选"),
    ("maintain mode", "维护模式"),
    ("policy adaptation", "策略适配"),
    ("remaining steps", "剩余步骤"),
    ("next checkpoint", "下一检查点"),
    ("revisit only if the next enhancement phase needs new source types or stronger replay/change inspection", "仅在下一增强阶段需要新来源类型或更强 replay/change 检查时再回看"),
    ("harden additional adapters when independent-product operation requires them", "仅在独立产品化运行需要时再加固更多适配层"),
    ("keep source contracts aligned with future learning-policy inputs", "保持来源契约与未来 learning-policy 输入对齐"),
    ("define the next self-learning phase beyond the current baseline", "定义当前基线之后的下一阶段 self-learning"),
    ("the docs retrofit slice is complete", "文档整改切片已完成"),
    ("the repo is now rolled forward to one explicit next milestone", "仓库已推进到一条明确的下一里程碑"),
    ("a post-hardening closeout run", "一条加固后收口执行线"),
    ("that should execute as one long-task line instead of many small cleanup slices", "并且应用一条长任务执行线收口，而不是继续切成很多零散清理小切片"),
    ("define the next milestone in roadmap and durable project-level development plan docs", "在 roadmap 和 durable development plan 里定义下一条里程碑"),
    ("close compound follow-up", "收口 compound 后续项"),
    ("future-first", "future-first"),
    ("output-separation boundary drift", "output-separation 边界漂移"),
    ("runtime-facing evidence", "runtime-facing 证据"),
    ("deepen planning/channel/operator evidence while keeping", "在保持"),
    ("do one final closeout pass across roadmap, test-plan, archive guidance, and control surfaces", "对 roadmap、test-plan、archive guidance 与控制面做最后一轮收口"),
    ("then either close the milestone or split a new named roadmap candidate", "然后决定关闭当前里程碑，还是拆出一条新的命名 roadmap 候选"),
    ("add explicit promotion, decay, and conflict behavior for learned artifacts", "为 learned artifacts 增加显式 promotion、decay 与 conflict 行为"),
    ("add learning-specific reports, replay paths, and policy-facing outputs", "补 learning-specific reports、replay 路径与面向策略的输出"),
    ("define the host-neutral registry root contract and compatibility fallback", "定义宿主中立的 registry root 契约与兼容回退"),
    ("add richer update rules for promoted learning artifacts", "为 promoted learning artifacts 增加更丰富的更新规则"),
    ("refine conflict, decay, and superseded-record handling for future learning phases", "为未来 learning phases 收紧 conflict、decay 与 superseded-record 处理"),
    ("keep export compatibility aligned with future projection changes", "保持导出兼容性与未来 projection 变化对齐"),
    ("define the policy-input artifact contract", "定义 policy-input artifact 契约"),
    ("project promoted learning outputs into policy-facing artifacts", "把 promoted learning outputs 投影成面向策略的 artifacts"),
    ("validate consumer-specific export compatibility during the next enhancement phase", "在下一增强阶段验证面向 consumer 的导出兼容性"),
    ("keep governance signals readable and stable during ongoing work", "在持续推进中保持治理信号可读且稳定"),
    ("add learning-specific governance reports, decay/conflict review paths, and time-window comparisons", "补 learning-specific governance 报告、decay/conflict review 路径与时间窗口对比"),
    ("optionally split high-frequency reports into clearer durable/generated groups", "视需要把高频报告拆成更清晰的 durable/generated 分组"),
    ("align OpenClaw runtime reads and writes with the future host-neutral canonical registry root", "让 OpenClaw runtime 的读写与未来宿主中立 canonical registry root 对齐"),
    ("expand the next batch of stable facts and stable rules", "扩下一批稳定事实与稳定规则"),
    ("keep supporting context clean while expanding recall coverage", "在扩 recall 覆盖时保持 supporting context 干净"),
    ("keep smoke natural-query coverage and governance coverage aligned as new cases appear", "随着新 case 出现，保持 smoke 自然 query 覆盖与 governance 覆盖对齐"),
    ("use `eval:smoke-promotion` and governance checks before promoting anything new into smoke", "在把任何新内容推进 smoke 前先跑 `eval:smoke-promotion` 和治理检查"),
    ("converge Codex on the same canonical registry root used by OpenClaw", "让 Codex 收敛到和 OpenClaw 相同的 canonical registry root"),
    ("define when Codex-specific policy adaptation should begin", "定义 Codex-specific 策略适配应从何时开始"),
    ("validate future consumer-specific exports once policy-input artifacts exist", "在 policy-input artifacts 落地后验证未来 consumer-specific 导出"),
    ("revisit task-side consumption only when the next product phase requires it", "仅在下一产品阶段需要时再回看 task-side consumption"),
    ("baseline complete; self-learning foundations implemented; next lifecycle-phase planning", "基线完成；self-learning foundations 已落地；下一生命周期阶段待规划"),
    ("migration/reporting hardening implemented; move to cutover decision and live adoption tracking", "migration/reporting 加固已完成；转入 cutover 决策与 live adoption tracking"),
    ("governance signals + promotion helper now stable", "governance signals + promotion helper 已稳定"),
    ("stable-fact expansion with clean assembly", "以 clean assembly 方式扩稳定事实"),
    ("continue expanding stable facts / stable rules while keeping recalled context clean", "继续扩稳定事实 / 稳定规则，同时保持召回上下文干净"),
    ("recalled context", "召回上下文"),
    ("smoke surfaces", "smoke 面"),
    ("same-path dual-card fallback", "同路径双卡兜底"),
    ("same-path two-card", "同路径双卡"),
    ("single-card", "单卡"),
    ("status handler", "status handler"),
    ("current plugin registration boundary, config defaults, current status handler coverage", "当前插件注册边界、配置默认值与当前 status handler 覆盖面"),
    ("current plugin registration boundary, config defaults, and current status handler coverage", "当前插件注册边界、配置默认值与当前 status handler 覆盖面"),
    ("promotion helper", "promotion helper"),
    ("candidate -> stable", "candidate -> stable"),
    ("policy-input artifacts", "policy-input artifacts"),
    ("policy-input artifact", "policy-input artifact"),
    ("consumer-specific adaptation", "consumer-specific 适配"),
    ("consumer-specific exports", "consumer-specific 导出"),
    ("workspace memory", "workspace memory"),
    ("canonical registry root", "canonical registry root"),
    ("plugin-runtime", "插件运行时"),
    ("learning changes", "learning 变更"),
    ("stable rules", "稳定规则"),
    ("stable facts", "稳定事实"),
    ("current plugin registration boundary, 配置默认值, 当前 status handler 覆盖面", "当前插件注册边界、配置默认值与当前 status handler 覆盖面"),
    ("锁定 插件注册行为", "锁定插件注册行为"),
    (" so ", "，让 "),
]


def first_heading(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return ""


def bullet_lines(text: str) -> list[str]:
    items: list[str] = []
    in_code_block = False
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if line.startswith("- "):
            items.append(line[2:].strip())
        elif re.match(r"^\d+\.\s+", line):
            items.append(re.sub(r"^\d+\.\s+", "", line))
    return items


def compact_list(items: list[str], limit: int = 2) -> str:
    if not items:
        return "n/a"
    shown = items[:limit]
    text = "; ".join(shown)
    if len(items) > limit:
        text += "; ..."
    return text


def zh_tier(tier: str) -> str:
    return {"small": "小型", "medium": "中型", "large": "大型"}.get(tier, tier)


def zh_signal(signal: str) -> str:
    return {"green": "绿色", "yellow": "黄色", "red": "红色"}.get(signal.lower(), signal)


def zh_gate(gate: str) -> str:
    lowered = gate.lower()
    mapping = {
        "continue automatically": "自动继续",
        "raise but continue": "提醒后继续",
        "require user decision": "需要用户裁决",
    }
    return mapping.get(lowered, gate)


def zh_band(band: str) -> str:
    return {
        "maintain": "维护",
        "stable": "稳定",
        "active": "活跃",
        "forming": "形成中",
        "planned": "计划中",
    }.get(band.lower(), band)


def zh_status(status: str) -> str:
    mapping = {
        "baseline-complete": "基线完成",
        "baseline-complete / next-phase candidate": "基线完成 / 下一阶段候选",
        "baseline-complete / maintain": "基线完成 / 维护",
        "active": "活跃推进",
        "governing": "持续治理",
        "maintain": "维护",
        "planned": "计划中",
        "missing": "缺失",
    }
    return mapping.get(status.lower(), status)


def module_display_name(slug: str) -> str:
    return slug.replace("-", " ").title()


def module_display_name_zh(slug: str) -> str:
    return MODULE_NAME_MAP.get(slug, module_display_name(slug))


def translate_inline_code(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        inner = match.group(1).strip()
        translated = EXACT_TEXT_MAP.get(inner) or EXACT_TEXT_MAP.get(inner.lower())
        if not translated:
            translated = pretty_text_zh(inner) if inner != text else inner
        return f"`{translated}`"

    return re.sub(r"`([^`]+)`", replace, text)


def pretty_text_zh(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return "暂无"
    exact = EXACT_TEXT_MAP.get(stripped)
    if exact:
        return exact
    lowered = stripped.lower()
    if lowered in EXACT_TEXT_MAP:
        return EXACT_TEXT_MAP[lowered]
    result = stripped
    code_placeholders: list[str] = []

    def stash_code(match: re.Match[str]) -> str:
        code_placeholders.append(match.group(0))
        return f"__CODE_PLACEHOLDER_{len(code_placeholders) - 1}__"

    result = re.sub(r"`[^`]+`", stash_code, result)
    for source, target in PHRASE_REPLACEMENTS:
        result = re.sub(re.escape(source), target, result, flags=re.IGNORECASE)
    for idx, original in enumerate(code_placeholders):
        result = result.replace(f"__CODE_PLACEHOLDER_{idx}__", original)
    result = translate_inline_code(result)
    result = result.replace(" ;", ";").replace(" ,", ",")
    result = result.replace(" n/a ", " 暂无 ")
    result = re.sub(r"\s{2,}", " ", result).strip()
    return result


def compact_value_zh(text: str) -> str:
    if not text or text == "n/a":
        return "暂无"
    parts = [part.strip() for part in text.split(";")]
    translated: list[str] = []
    for part in parts:
        if not part:
            continue
        if part == "...":
            translated.append("...")
        else:
            translated.append(pretty_text_zh(part))
    return "; ".join(translated) if translated else "暂无"


def display_execution_task_zh(line: str) -> str:
    return pretty_text_zh(display_execution_task(line))


def print_upgrade_notice(result: ResumeReadinessResult) -> None:
    if not result.upgrade_needed:
        return
    upgraded = ", ".join(result.layers_synced) if result.layers_synced else "control-surface"
    syncs = ", ".join(result.syncs_run) if result.syncs_run else "none"
    detected = (
        "检测到旧控制面代际，已先自动补齐。"
        if result.generation_upgraded
        else "检测到控制面缺层或局部版本落后，已先自动补齐。"
    )
    print("## 自动补齐")
    print("| 项目 | 当前值 |")
    print("| --- | --- |")
    print(f"| 检测结果 | {detected} |")
    print(f"| 控制面版本 | `{result.detected_version} -> {result.current_version}` |")
    print(f"| 补齐层 | `{upgraded}` |")
    print(f"| 已执行 | `{syncs}` |")
    print()


def numbered_actions_zh(text: str) -> list[str]:
    actions = bullet_lines(text)
    return [pretty_text_zh(item) for item in actions]


def mermaid_status_label(status: str) -> str:
    lowered = status.lower()
    if "active" in lowered:
        return "Active"
    if "governing" in lowered:
        return "Governing"
    if "planned" in lowered:
        return "Planned"
    if "complete" in lowered:
        return "Baseline Complete"
    if "maintain" in lowered:
        return "Maintain"
    return status


def first_risk(status_text: str) -> str:
    risks = bullet_lines(section(status_text, "Blockers / Open Decisions"))
    return risks[0] if risks else "No major blocker recorded."


def markdown_file_link(path: Path, label: str, line: int | None = None) -> str:
    resolved = path.resolve()
    repo_root = next(
        (
            candidate
            for candidate in [resolved.parent, *resolved.parents]
            if (candidate / ".codex").exists()
        ),
        resolved.parent,
    )
    source_dir = repo_root / ".codex" / "host-views"
    if source_dir.exists():
        target = os.path.relpath(resolved, start=source_dir).replace(os.sep, "/")
    else:
        target = os.path.relpath(resolved, start=repo_root).replace(os.sep, "/")
    if " " in target:
        target = f"<{target}>"
    return f"[{label}]({target})"


def normalized_tokens(text: str) -> list[str]:
    return [token for token in slugify(text).split("-") if token and token not in TRIVIAL_TOKENS]


def line_number_for_heading(path: Path, heading: str) -> int | None:
    if not path.exists():
        return None
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.strip() == f"## {heading}" or line.strip() == f"# {heading}":
            return index
    return None


def line_number_for_active_milestone(path: Path) -> tuple[int | None, str]:
    if not path.exists():
        return None, ""
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if "| active |" in line.lower():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells:
                return index, cells[0]
    return None, ""


def line_number_for_query(path: Path, queries: list[str]) -> int | None:
    if not path.exists():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    normalized_queries = [query.lower() for query in queries if query.strip()]
    token_sets = [normalized_tokens(query) for query in queries if query.strip()]
    for index, line in enumerate(lines, start=1):
        lowered = line.lower()
        if any(query in lowered for query in normalized_queries):
            return index
        for tokens in token_sets:
            if len(tokens) >= 2 and sum(token in lowered for token in tokens) >= min(2, len(tokens)):
                return index
    return None


def preferred_existing_path(repo: Path, candidates: list[str]) -> Path | None:
    for rel in candidates:
        path = repo / rel
        if path.exists():
            return path
    return None


def roadmap_horizon_focus(repo: Path) -> dict[str, str]:
    roadmap_path = preferred_existing_path(repo, ["docs/roadmap.zh-CN.md", "docs/roadmap.md"])
    if not roadmap_path:
        return {}
    rows: dict[str, str] = {}
    for line in roadmap_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) < 2:
            continue
        horizon = cells[0].lower()
        if horizon in {"now", "next", "later", "现在", "当前", "下一步", "后续", "更后面"}:
            rows[horizon] = cells[1]
    return rows


def roadmap_links(
    repo: Path,
    current_phase: str,
    active_slice: str,
    active_module: str,
    current_execution_line: str,
) -> tuple[str, str]:
    stable_roadmap = preferred_existing_path(repo, ["docs/roadmap.zh-CN.md", "docs/roadmap.md"])
    project_roadmap = preferred_existing_path(
        repo,
        ["docs/workstreams/project/roadmap.zh-CN.md", "docs/workstreams/project/roadmap.md"],
    )

    phase_link = "n/a"
    if stable_roadmap:
        line, milestone = line_number_for_active_milestone(stable_roadmap)
        if line:
            label = f"路线图当前阶段：{pretty_text_zh(milestone)}"
            phase_link = markdown_file_link(stable_roadmap, label, line)
        else:
            line = line_number_for_query(stable_roadmap, [current_phase])
            if line:
                phase_link = markdown_file_link(stable_roadmap, "路线图当前阶段", line)
            else:
                line = line_number_for_heading(stable_roadmap, "Milestones") or line_number_for_heading(stable_roadmap, "里程碑")
                phase_link = markdown_file_link(stable_roadmap, "路线图里程碑", line) if line else markdown_file_link(
                    stable_roadmap, "路线图"
                )

    slice_link = "n/a"
    slice_queries = [active_slice]
    if current_execution_line:
        slice_queries.append(current_execution_line)
    for candidate in [project_roadmap, stable_roadmap]:
        if not candidate:
            continue
        line = line_number_for_query(candidate, slice_queries)
        if line:
            slice_link = markdown_file_link(candidate, "当前切片对应位置", line)
            break
    if slice_link == "n/a" and project_roadmap:
        line = line_number_for_heading(project_roadmap, "Current Focus") or line_number_for_heading(project_roadmap, "当前焦点")
        slice_link = markdown_file_link(project_roadmap, "当前焦点", line) if line else markdown_file_link(
            project_roadmap, "项目工作流路线图"
        )
    if slice_link == "n/a":
        fallback_queries = []
        if active_module:
            fallback_queries.extend([active_module, module_display_name(active_module)])
        for candidate in [project_roadmap, stable_roadmap]:
            if not candidate:
                continue
            line = line_number_for_query(candidate, fallback_queries)
            if line:
                slice_link = markdown_file_link(candidate, "当前切片相关位置", line)
                break

    return phase_link, slice_link


def readme_capability_sections(repo: Path) -> tuple[Path | None, list[str], list[str]]:
    readme_path = preferred_existing_path(repo, ["README.zh-CN.md", "README.md"])
    if not readme_path:
        return None, [], []
    text = readme_path.read_text(encoding="utf-8")
    core = bullet_lines(
        section(text, "当前系统能做什么")
        or section(text, "核心能力")
        or section(text, "已交付能力地图")
        or section(text, "Core Capabilities")
        or section(text, "Shipped Capability Map")
        or section(text, "What It Can Do")
    )
    phase_section = section(text, "为什么 Self-Learning 现在就重要") or section(text, "Why Self-Learning Already Matters")
    already: list[str] = []
    if phase_section:
        capture = False
        for line in phase_section.splitlines():
            stripped = line.strip()
            lowered = stripped.lower()
            if "现在仓库里已经有这些基线" in stripped or "today the repo already includes" in lowered:
                capture = True
                continue
            if "还没有做完的部分" in stripped or "what is not finished yet" in lowered:
                break
            if capture and stripped.startswith("- "):
                already.append(stripped[2:].strip())
    return readme_path, core, already


def active_module_slug(repo: Path, active_slice: str) -> str:
    dashboard_text = read_text(repo / ".codex/module-dashboard.md")
    summary = section(dashboard_text, "Summary")
    active_module = labeled_bullet_value(summary, "Active Module")
    if active_module:
        return slugify(active_module)
    official_modules = parse_official_modules(repo)
    active_text = active_slice.lower()
    for module in official_modules:
        tokens = normalized_tokens(module)
        if tokens and sum(token in active_text for token in tokens) >= min(2, len(tokens)):
            return module
    return ""


def module_priority(module: str, summary: dict[str, str], active_module: str, horizon_focus: dict[str, str]) -> str:
    status = summary["status"].lower()
    if module == active_module:
        return "P0"

    tokens = normalized_tokens(module)

    def matches(text: str) -> bool:
        lowered = text.lower()
        if not tokens:
            return False
        return sum(token in lowered for token in tokens) >= min(2, len(tokens))

    if matches(horizon_focus.get("now", "")) or matches(horizon_focus.get("现在", "")):
        return "P1"
    if matches(horizon_focus.get("next", "")) or matches(horizon_focus.get("下一步", "")):
        return "P1"
    if "next-phase candidate" in status or "active" in status:
        return "P1"
    if "governing" in status:
        return "P2"
    if "maintain" in status:
        return "P4"
    return "P3"


def load_module_summary(module_path: Path) -> dict[str, str]:
    text = module_path.read_text(encoding="utf-8")
    status = first_line(section(text, "Current Status")) or "missing"
    return {
        "status": status,
        "completion_percent": str(completion_percent(status)),
        "completion_band": completion_band(status),
        "implemented": compact_value_zh(compact_list(bullet_lines(section(text, "Already Implemented")), limit=2)),
        "remaining": compact_value_zh(compact_list(bullet_lines(section(text, "Remaining Steps")), limit=2)),
        "completion": pretty_text_zh(first_line(section(text, "Completion Signal")) or "n/a"),
        "next_checkpoint": pretty_text_zh(first_line(section(text, "Next Checkpoint")) or "n/a"),
    }


def load_subproject_rows(repo: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    subproject_dir = repo / ".codex/subprojects"
    if not subproject_dir.exists():
        return rows
    for path in sorted(subproject_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        rows.append(
            (
                SUBPROJECT_NAME_MAP.get(path.stem, path.stem),
                pretty_text_zh(first_line(section(text, "Current Slice")) or "n/a"),
                pretty_text_zh(first_line(section(text, "Next 3 Actions")) or compact_list(bullet_lines(section(text, "Next 3 Actions")), limit=1)),
            )
        )
    return rows


def module_health_breakdown(module_summaries: list[dict[str, str]]) -> str:
    if not module_summaries:
        return "n/a"
    buckets = {"maintain": 0, "stable": 0, "active": 0, "forming": 0, "planned": 0}
    for summary in module_summaries:
        buckets[summary["completion_band"]] = buckets.get(summary["completion_band"], 0) + 1
    parts = [f"{zh_band(label)}:{count}" for label, count in buckets.items() if count]
    return ", ".join(parts) if parts else "n/a"


def project_display_name(repo: Path) -> str:
    brief_heading = first_heading(read_text(repo / ".codex/brief.md"))
    if brief_heading and brief_heading.lower() not in {"project brief", "brief"}:
        return brief_heading
    readme_heading = first_heading(read_text(repo / "README.md"))
    if readme_heading:
        return readme_heading
    return repo.name


def is_skill_repo(repo: Path) -> bool:
    return (repo / "SKILL.md").exists()


def is_medium_steady_state(current_phase: str, active_slice: str, execution_line: str) -> bool:
    lowered = " ".join([current_phase, active_slice, execution_line]).lower()
    return any(token in lowered for token in STEADY_STATE_TOKENS)


def medium_mainline_status_zh(
    repo: Path,
    current_phase: str = "",
    active_slice: str = "",
    execution_line: str = "",
) -> str:
    if is_medium_steady_state(current_phase, active_slice, execution_line):
        return "当前主线里程碑已收口；现在处于稳定维护，只在出现新的命名 roadmap 候选或实质性验证变化时才重开新主线。"
    readme = read_text(repo / "README.zh-CN.md") or read_text(repo / "README.md")
    roadmap = read_text(repo / "docs/roadmap.zh-CN.md") or read_text(repo / "docs/roadmap.md")
    if is_skill_repo(repo):
        status_text = read_text(repo / ".codex/status.md")
        active_slice = first_line(section(status_text, "Active Slice")).strip("`").lower()
        current_phase = first_line(section(status_text, "Current Phase")).strip("`").lower()
        if "supervised long-run delivery" in current_phase or "delivery-supervision" in active_slice or "close-m12" in active_slice:
            if "closed" in current_phase or "rollout" in current_phase:
                return "核心能力、战略层、程序编排层与长期受监督交付层都已完成；当前进入 rollout 与摩擦采集阶段。"
            return "核心能力、战略层与程序编排层已完成；当前在做长期受监督交付层，把 checkpoint 节奏、自动继续边界和升级时机沉淀成 durable 真相。"
        if "program orchestration" in current_phase or "orchestration" in active_slice or "program-board" in active_slice:
            if "closed" in current_phase or "m12" in current_phase or "queue" in active_slice:
                return "核心能力、战略层与程序编排层已完成；当前正在为长期受监督交付层排队。"
            return "核心能力与战略层已完成；当前在做程序编排层，把多个切片或执行器的推进沉淀成 durable program board。"
        if "strategic evaluation" in current_phase or "strategic" in active_slice:
            return "核心能力已完成；当前在做更高层的战略评估层，把“项目下一步怎么走”沉淀成可 review 的 repo 真相。"
        if "locale-aware" in current_phase or "locale-aware" in active_slice:
            return "核心能力已完成；当前在做内部控制面按语言收口的评估。"
        return "核心能力已完成；当前在做维护者体验与自动触发增强。"
    if "后续剩余工作属于扩展方向，不是主线欠账" in readme or "remaining work is extension work, not unfinished mainline debt" in readme.lower():
        return "主线 Phase 0-6 已完成；当前在做主线全部完成后的扩展与增强。"
    if "mainline roadmap is complete" in readme.lower() or "正式主线 roadmap 已完成" in readme:
        return "主线已完成；当前在做后续扩展与增强。"
    if "后续收口" in roadmap or "current extension areas" in roadmap.lower():
        return "主线已完成；当前在做后续增强与边界收口。"
    return "当前处于持续推进中。"


def medium_work_area_zh(active_slice: str, execution_line: str) -> str:
    if is_medium_steady_state("", active_slice, execution_line):
        return "稳定维护 / 新候选观察"
    lowered = f"{active_slice} {execution_line}".lower()
    if any(token in lowered for token in ["supervised long-run delivery", "delivery-supervision", "checkpoint rhythm", "长期受监督交付", "close-m12", "rollout"]):
        return "长期受监督交付层"
    if any(token in lowered for token in ["program orchestration", "program-board", "sequencing", "executor", "orchestration", "程序编排"]):
        return "程序编排层"
    if any(token in lowered for token in ["strategic", "strategy", "program-board", "roadmap reshaping", "milestone reorder", "战略", "程序编排"]):
        return "战略评估层"
    if any(token in lowered for token in ["locale-aware", "用户语言", "中文工作流", "冗余英文"]):
        return "内部输出与恢复面收口"
    if any(token in lowered for token in ["progress", "continue", "handoff", "narrative", "architecture trigger", "maintainer"]):
        return "维护者恢复与架构监督增强"
    if any(token in lowered for token in ["operator", "dashboard", "triage", "continuity", "main_ops", "watchdog"]):
        return "运维视图增强"
    if any(token in lowered for token in ["planning", "acceptance", "stable_acceptance", "channel", "release gate"]):
        return "规划与验收增强"
    if any(token in lowered for token in ["install", "runtime_mirror", "drift", "canonical", "source-of-truth", "mirror"]):
        return "安装与同步增强"
    if any(token in lowered for token in ["lifecycle", "runtime", "queue", "task truth", "session"]):
        return "运行时边界增强"
    return "后续增强"


def medium_slice_explanation_zh(active_slice: str, execution_line: str) -> str:
    if is_medium_steady_state("", active_slice, execution_line):
        return "保持加固后基线稳定；在出现新的命名 roadmap 候选之前，不提前重开下一条主线。"
    lowered = active_slice.lower().strip()
    if "delivery-supervision" in lowered or "supervised long-run" in lowered or "close-m12-and-open-rollout" in lowered:
        return "把 checkpoint 节奏、自动继续边界、升级时机和执行器监督循环收口成 durable delivery-supervision，并把项目切到 rollout / 摩擦采集阶段"
    if "program-board" in lowered or "orchestration" in lowered or "close-m11-and-queue-m12" in lowered:
        return "把 durable program-board、编排状态和维护者恢复面全部收口，并把 M12 排成下一条主线"
    if "strategy-surface" in lowered or "strategic" in lowered:
        return "建立可复用的战略判断面，并明确哪些问题必须继续升级给人类 review"
    if lowered in MEDIUM_SLICE_EXPLANATIONS:
        return MEDIUM_SLICE_EXPLANATIONS[lowered]
    if "continuity" in execution_line.lower() or "triage" in execution_line.lower():
        return "给 continuity / triage 增加更短的值班快照"
    if "planning" in lowered:
        return "补 planning 相关的正式验收或恢复覆盖"
    if "channel" in lowered:
        return "补渠道行为的真实样本和正式验收覆盖"
    if "runtime" in lowered or "source-of-truth" in lowered:
        return "收口 runtime 边界，减少后续维护时的猜测成本"
    return pretty_text_zh(active_slice)


def medium_direct_value_zh(active_slice: str, execution_line: str) -> str:
    if is_medium_steady_state("", active_slice, execution_line):
        return "让维护者先确认已发布基线持续为绿，不把观察型维护误读成还有一条正在开发的大任务。"
    lowered = active_slice.lower().strip()
    if "delivery-supervision" in lowered or "supervised long-run" in lowered or "close-m12-and-open-rollout" in lowered:
        return "让系统明确知道什么时候可以自动继续、什么时候该提醒、什么时候必须停下来等人类裁决，并把这套节奏沉淀成 durable 交付真相。"
    if "program-board" in lowered or "orchestration" in lowered or "close-m11-and-queue-m12" in lowered:
        return "让多个相关切片和执行器的推进顺序、边界和升级点不再散落在聊天里，而是留在 durable program board 里。"
    if "strategy-surface" in lowered or "strategic" in lowered:
        return "让项目后续怎么走、何时插专项、何时改 roadmap 不再散落在聊天里，而是留在 repo 真相中。"
    if lowered in MEDIUM_SLICE_VALUE:
        return MEDIUM_SLICE_VALUE[lowered]
    if "continuity" in execution_line.lower() or "triage" in execution_line.lower():
        return "值班时更快看出哪些任务卡住、哪些需要恢复。"
    if "planning" in lowered:
        return "让 planning 边界不只靠口头约定，而是进入正式验证。"
    if "channel" in lowered:
        return "让渠道行为对维护者来说更可验证、更少凭感觉。"
    if "runtime" in lowered:
        return "减少维护者在 runtime 边界和 source-of-truth 上反复猜测。"
    return "让下一次回来看项目时更容易接手。"


def task_direct_value_zh(task_text: str, active_slice: str) -> str:
    lowered = f"{task_text} {active_slice}".lower()
    if any(token in lowered for token in ["docs", "progress", "handoff", "capabilities", ".codex", "devlog"]):
        return "让维护者下次回来时，不需要重新猜当前状态和入口。"
    if any(token in lowered for token in ["validate", "validation", "acceptance", "gate", "tests", "release"]):
        return "让这轮变化进入正式验证，不再只靠口头记忆。"
    if any(token in lowered for token in ["architecture", "root-cause", "correct layer", "trigger", "signal"]):
        return "让方向偏掉时更早暴露，而不是修一个冒一个。"
    if any(token in lowered for token in ["implement", "sync", "refresh", "expand", "compact", "issues"]):
        return "把当前切片的核心增量真正落地成可接手的结果。"
    return "让当前切片更容易被维护者看懂并继续推进。"


def maintenance_task_type_zh(text: str) -> str:
    lowered = text.lower()
    if "name a new roadmap candidate" in lowered or "命名新的 roadmap 候选" in text:
        return "开新主线前置"
    if "rerun" in lowered or "重新采集" in text or "when" in lowered or "当后续改动" in text:
        return "条件触发"
    return "观察任务"


def maintenance_task_status_zh(text: str) -> str:
    lowered = text.lower()
    if "name a new roadmap candidate" in lowered or "命名新的 roadmap 候选" in text:
        return "待触发"
    if "rerun" in lowered or "重新采集" in text or "when" in lowered or "当后续改动" in text:
        return "按需触发"
    return "持续执行"


def maintenance_task_value_zh(text: str) -> str:
    lowered = text.lower()
    if "name a new roadmap candidate" in lowered or "命名新的 roadmap 候选" in text:
        return "避免在没有命名下一条主线之前，仓库又回到边做边想的状态。"
    if "rerun" in lowered or "重新采集" in text or "planning evidence" in lowered:
        return "让 release-facing 证据在真正变化时再刷新，不把稳态维护做成无意义重复劳动。"
    return "保持已发布 runtime、文档和 release-facing 基线持续为绿。"


def maintenance_task_rows(actions: list[str]) -> list[tuple[str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str]] = []
    for idx, action in enumerate(actions[:3], start=1):
        rows.append(
            (
                f"MAINT-{idx}",
                maintenance_task_type_zh(action),
                maintenance_task_status_zh(action),
                pretty_text_zh(action),
                maintenance_task_value_zh(action),
            )
        )
    return rows


def usage_links(repo: Path) -> dict[str, str]:
    usage = preferred_existing_path(repo, ["docs/usage_guide.zh-CN.md", "docs/usage_guide.md"])
    links: dict[str, str] = {}
    if not usage:
        return links
    for term in ["dashboard", "triage", "continuity", "watchdog"]:
        line = line_number_for_query(usage, [term])
        if line:
            links[term] = markdown_file_link(usage, "使用指南", line)
    return links


def relevant_terms(repo: Path, active_slice: str, execution_line: str, readme_capabilities: list[str]) -> list[dict[str, str]]:
    corpus = " ".join([active_slice, execution_line] + readme_capabilities).lower()
    links = usage_links(repo)
    rows: list[dict[str, str]] = []
    for key in ["dashboard", "triage", "continuity", "watchdog", "[wd]"]:
        if key.lower() in corpus:
            meta = TERM_CATALOG[key]
            rows.append(
                {
                    "term": meta["label"],
                    "meaning": meta["meaning"],
                    "when": meta["when"],
                    "current": meta["current"],
                    "source": links.get(key, "暂无"),
                }
            )
    return rows


def split_medium_capabilities(repo: Path, readme_capabilities: list[str]) -> list[tuple[str, str, str, str]]:
    readme_path = preferred_existing_path(repo, ["README.zh-CN.md", "README.md"])
    source = markdown_file_link(readme_path, "README") if readme_path else "暂无"
    rows: list[tuple[str, str, str, str]] = []
    for item in readme_capabilities:
        lowered = item.lower()
        audience = "维护者" if any(
            token in lowered
            for token in ["dashboard", "triage", "continuity", "planning", "producer contract", "channel acceptance", "ops", "watchdog"]
        ) else "普通用户"
        rows.append((audience, pretty_text_zh(item), "已可直接使用", source))
    return rows


def medium_workstream_rows(repo: Path, active_slice: str, execution_line: str) -> list[tuple[str, str, str, str, str, str]]:
    if is_medium_steady_state("", active_slice, execution_line):
        return [
            ("主线运行时", "核心 task-system 能力本体", "已完成", "P2", "维持已发布基线", "只做回归"),
            ("稳定维护", "保持 runtime、文档和 release-facing 证据持续为绿", "活跃", "P0", "执行 watch-mode 维护任务", "只有命名新 roadmap 候选时才重开主线"),
            ("规划与验收", "planning / acceptance / release-facing 验证", "活跃", "P1", "按需刷新证据，不做空转验证", "当契约实质变化时再补采样本"),
            ("下一候选评估", "判断何时值得打开下一条命名切片", "活跃", "P1", "观察是否出现真实 roadmap candidate", "有明确信号后再升级为主线"),
        ]
    lowered = active_slice.lower()
    if is_skill_repo(repo):
        current_narrative = "收口第一屏叙事，让维护者更容易恢复" if any(token in lowered for token in ["narrative", "progress", "handoff", "continue"]) else "维持当前恢复面板"
        current_architecture = "把自动 review trigger 接到 supervision signal" if any(token in lowered for token in ["architecture", "trigger"]) else "维持自动架构监督"
        return [
            ("控制面与收敛", "保证 `.codex` truth、任务板和门禁一致", "活跃", "P1", "维持当前控制面真相", "继续保持 plan / status / progress / handoff 一致"),
            ("进展与恢复输出", "给维护者和未来接手者看的恢复面板", "活跃", "P0", current_narrative, "继续压掉需要人工翻译的表达"),
            ("架构监督与门禁", "让方向偏掉时更早自动暴露", "活跃", "P0", current_architecture, "继续收紧自动 review trigger"),
            ("文档与发布", "保证 README / roadmap / development-plan / gates 对齐", "稳定", "P2", "保持文档与门禁同步", "只在里程碑切换时更新"),
        ]
    current_operator = "补 continuity / triage 短快照" if "operator" in lowered or "triage" in lowered or "continuity" in lowered else "维持稳定"
    next_operator = "转向真实渠道证据或更深 release gate" if "operator" in lowered or "triage" in lowered or "continuity" in lowered else "按下一条切片推进"
    return [
        ("主线运行时", "核心 task-system 能力本体", "已完成", "P2", "维持稳定", "只做回归"),
        ("运维视图", "给维护者 / 值班者看的观察与恢复视图", "活跃", "P0" if "operator" in lowered or "triage" in lowered or "continuity" in lowered else "P1", current_operator, next_operator),
        ("规划与验收", "planning / acceptance / release-facing 验证", "活跃", "P1", "保持 acceptance 与当前视图同步", "扩更多真实或半真实样本"),
        ("安装与同步", "repo runtime 与安装态 runtime 的一致性", "稳定", "P2", "维持 canonical source 规则", "只做回归"),
    ]


def task_kind_zh(kind: str) -> str:
    return {"mainline": "主线", "parallel": "并行"}.get(kind, "主线")


def medium_current_work_rows(
    active_slice: str,
    execution_tasks: list[str],
    next_actions_display: list[str],
    current_phase: str,
    execution_line: str,
) -> list[tuple[str, str, str, str, str]]:
    if is_medium_steady_state(current_phase, active_slice, execution_line) and next_actions_display:
        return [
            (content, value, status, task_id, task_type)
            for task_id, task_type, status, content, value in maintenance_task_rows(next_actions_display)
        ]
    rows: list[tuple[str, str, str, str, str]] = []
    for task_id, task_type, state, content in execution_task_rows(execution_tasks)[:5]:
        rows.append((content, task_direct_value_zh(content, active_slice), state, task_id, task_type))
    if rows:
        return rows
    explanation = medium_slice_explanation_zh(active_slice, active_slice)
    return [
        (
            explanation,
            task_direct_value_zh(explanation, active_slice),
            "已记录",
            "切片",
            "主线",
        )
    ]


def render_medium_supervision_summary(
    automatic_review_trigger: str,
    escalation_gate: str,
    escalation_reason: str,
    stop_conditions: str,
) -> None:
    print("\n## 监督与接续")
    print("| 维度 | 当前值 |")
    print("| --- | --- |")
    print("| 当前监督模式 | 稳态维护 / watch-mode |")
    print("| PTL 当前职责 | 保持已发布基线为绿、判断是否出现新的 roadmap 候选、并在 worker 停下时从 durable 真相继续接手。 |")
    print("| 自动继续条件 | 当前仍在既定方向内，验证保持绿色，且没有出现新的命名主线候选。 |")
    print(f"| 当前提醒原因 | {pretty_text_zh(automatic_review_trigger)} |")
    print(f"| 当前 Gate | `{zh_gate(escalation_gate or 'n/a')}` |")
    print(f"| 当前 Gate 解释 | {pretty_text_zh(escalation_reason)} |")
    print(f"| 什么时候重开主线 | {pretty_text_zh(stop_conditions) if stop_conditions else '当出现新的命名 roadmap 候选或实质性验证变化时。'} |")


def execution_task_rows(task_lines: list[str]) -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for line in task_lines:
        stripped = line.strip()
        match = re.match(r"-\s*\[(?P<mark>[ xX])\]\s*(?P<id>EL-\d+)\s*(?P<body>.*)", stripped)
        task_type = task_kind_zh(execution_task_kind(line))
        if match:
            status = "已完成" if match.group("mark").lower() == "x" else "待完成"
            rows.append((match.group("id"), task_type, status, pretty_text_zh(normalized_execution_task_body(line))))
            continue
        rows.append(("任务", task_type, "已记录", pretty_text_zh(normalized_execution_task_body(line))))
    return rows


def human_window_rows_zh() -> list[tuple[str, str]]:
    return [
        ("`项目助手 菜单`", "查看主入口和当前可用窗口"),
        ("`项目助手 进展`", "查看完整项目进展面板"),
        ("`项目助手 架构`", "单独拉出架构监督 / 根因 / 复盘入口"),
        ("`项目助手 开发日志`", "查看或补记关键开发结论"),
    ]


def strategy_status_zh(status: str) -> str:
    return {
        "active": "活跃",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
        "supporting backlog": "supporting backlog",
    }.get(status.lower(), pretty_text_zh(status))


def program_status_zh(status: str) -> str:
    return {
        "active": "活跃",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
        "supporting backlog": "supporting backlog",
    }.get(status.lower(), pretty_text_zh(status))


def workstream_state_zh(status: str) -> str:
    return {
        "active": "活跃",
        "stable": "稳定",
        "done": "已完成",
        "supporting backlog": "supporting backlog",
    }.get(status.lower(), pretty_text_zh(status))


def delivery_status_zh(status: str) -> str:
    return {
        "active": "活跃",
        "stable": "稳定",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
    }.get(status.lower(), pretty_text_zh(status))


def ptl_status_zh(status: str) -> str:
    return {
        "active": "活跃",
        "stable": "稳定",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
    }.get(status.lower(), pretty_text_zh(status))


def handoff_status_zh(status: str) -> str:
    return {
        "active": "活跃",
        "stable": "稳定",
        "done": "已完成",
        "next": "下一阶段",
        "later": "更后面",
    }.get(status.lower(), pretty_text_zh(status))


def compact_strategy_items(items: list[str], limit: int = 2) -> str:
    if not items:
        return "暂无"
    shown = [pretty_text_zh(item) for item in items[:limit]]
    if len(items) > limit:
        shown.append("...")
    return "；".join(shown)


def render_strategy_view(repo: Path) -> None:
    strategy = parse_strategy_surface(repo)
    if not strategy["exists"]:
        return
    print("\n## 战略视角")
    print("| 维度 | 当前值 |")
    print("| --- | --- |")
    print(f"| 当前战略方向 | {pretty_text_zh(strategy['direction'])} |")
    print(f"| 当前状态 | `{strategy_status_zh(strategy['status'])}` |")
    print(f"| 为什么现在做 | {pretty_text_zh(strategy['why_now'])} |")
    print(f"| 系统可自动提出 | {compact_strategy_items(strategy['system_may_propose'])} |")
    print(f"| 必须人类审批 | {compact_strategy_items(strategy['human_approves'])} |")
    print(f"| 下一战略检查 | {compact_strategy_items(strategy['next_checks'])} |")


def compact_program_rows(rows: list[dict[str, str]], key: str, limit: int = 2) -> str:
    if not rows:
        return "暂无"
    values = [pretty_text_zh(item.get(key, "")) for item in rows[:limit] if item.get(key, "").strip()]
    values = [value for value in values if value]
    if not values:
        return "暂无"
    if len(rows) > limit:
        values.append("...")
    return "；".join(values)


def render_program_view(repo: Path) -> None:
    program = parse_program_board(repo)
    if not program["exists"]:
        return
    print("\n## 程序编排视角")
    print("| 维度 | 当前值 |")
    print("| --- | --- |")
    print(f"| 当前程序方向 | {pretty_text_zh(program['direction'])} |")
    print(f"| 当前状态 | `{program_status_zh(program['status'])}` |")
    print(f"| 为什么现在做 | {pretty_text_zh(program['why_now'])} |")
    print(f"| 活跃工作流 | {compact_program_rows(program['workstreams'], 'Workstream')} |")
    print(f"| 当前编排序列 | {compact_program_rows(program['queue'], 'Slice / Input')} |")
    print(f"| 当前执行器输入 | {compact_program_rows(program['executors'], 'Executor')} |")
    print(f"| Supporting Backlog | {compact_program_rows(program['backlog'], 'Topic')} |")
    print(f"| 下一程序检查 | {compact_strategy_items(program['next_checks'])} |")

    if program["workstreams"]:
        print("\n## 程序编排工作流")
        print("| 工作流 | 范围 | 状态 | 优先级 | 当前焦点 | 下一检查点 |")
        print("| --- | --- | --- | --- | --- | --- |")
        for row in program["workstreams"]:
            print(
                f"| {pretty_text_zh(row.get('Workstream', 'n/a'))} | {pretty_text_zh(row.get('Scope', 'n/a'))} | "
                f"{workstream_state_zh(row.get('State', 'n/a'))} | `{row.get('Priority', 'n/a')}` | "
                f"{pretty_text_zh(row.get('Current Focus', 'n/a'))} | {pretty_text_zh(row.get('Next Checkpoint', 'n/a'))} |"
            )


def render_delivery_view(repo: Path) -> None:
    delivery = parse_delivery_supervision(repo)
    if not delivery["exists"]:
        return
    print("\n## 长期交付视角")
    print("| 维度 | 当前值 |")
    print("| --- | --- |")
    print(f"| 当前长期交付方向 | {pretty_text_zh(delivery['direction'])} |")
    print(f"| 当前状态 | `{delivery_status_zh(delivery['status'])}` |")
    print(f"| 为什么现在做 | {pretty_text_zh(delivery['why_now'])} |")
    print(f"| Checkpoint 节奏 | {compact_program_rows(delivery['checkpoint_rows'], 'Checkpoint')} |")
    print(f"| 自动继续边界 | {compact_program_rows(delivery['continue_rows'], 'Situation')} |")
    print(f"| 升级时机 | {compact_program_rows(delivery['escalation_rows'], 'When')} |")
    print(f"| 执行器监督循环 | {compact_program_rows(delivery['executor_rows'], 'Executor')} |")
    print(f"| Backlog 回流规则 | {compact_program_rows(delivery['backlog_rows'], 'Topic')} |")
    print(f"| 下一长期交付检查 | {compact_strategy_items(delivery['next_checks'])} |")

    if delivery["checkpoint_rows"]:
        print("\n## 长期交付检查点")
        print("| 顺序 | 检查点 | 发生什么 | Owner | 什么时候 |")
        print("| --- | --- | --- | --- | --- |")
        for row in delivery["checkpoint_rows"]:
            print(
                f"| {row.get('Order', 'n/a')} | {pretty_text_zh(row.get('Checkpoint', 'n/a'))} | "
                f"{pretty_text_zh(row.get('What Happens', 'n/a'))} | {pretty_text_zh(row.get('Owner', 'n/a'))} | "
                f"{pretty_text_zh(row.get('When', 'n/a'))} |"
            )


def render_ptl_view(repo: Path) -> None:
    ptl = parse_ptl_supervision(repo)
    if not ptl["exists"]:
        return
    print("\n## PTL 监督视角")
    print("| 维度 | 当前值 |")
    print("| --- | --- |")
    print(f"| 当前 PTL 方向 | {pretty_text_zh(ptl['direction'])} |")
    print(f"| 当前状态 | `{ptl_status_zh(ptl['status'])}` |")
    print(f"| 为什么现在做 | {pretty_text_zh(ptl['why_now'])} |")
    print(f"| 监督触发 | {compact_program_rows(ptl['trigger_rows'], 'Trigger')} |")
    print(f"| 常驻职责 | {compact_program_rows(ptl['responsibility_rows'], '角色')} |")
    print(f"| 继续 / 重排 / 升级矩阵 | {compact_program_rows(ptl['matrix_rows'], '情况')} |")
    print(f"| 当前监督检查 | {compact_program_rows(ptl['check_rows'], '检查项')} |")
    print(f"| 下一 PTL 检查 | {compact_strategy_items(ptl['next_checks'])} |")


def render_handoff_view(repo: Path) -> None:
    handoff = parse_worker_handoff(repo)
    if not handoff["exists"]:
        return
    print("\n## Worker 接续视角")
    print("| 维度 | 当前值 |")
    print("| --- | --- |")
    print(f"| 当前 handoff 方向 | {pretty_text_zh(handoff['direction'])} |")
    print(f"| 当前状态 | `{handoff_status_zh(handoff['status'])}` |")
    print(f"| 为什么现在做 | {pretty_text_zh(handoff['why_now'])} |")
    print(f"| handoff 触发 | {compact_program_rows(handoff['trigger_rows'], 'Trigger')} |")
    print(f"| 恢复源 | {compact_program_rows(handoff['source_rows'], '恢复源')} |")
    print(f"| 接续动作 | {compact_program_rows(handoff['action_rows'], 'PTL 动作')} |")
    print(f"| 回流规则 | {compact_program_rows(handoff['queue_rows'], '情况')} |")
    print(f"| 升级边界 | {compact_program_rows(handoff['escalation_rows'], '情况')} |")
    print(f"| 下一 handoff 检查 | {compact_strategy_items(handoff['next_checks'])} |")


def large_project_judgement_zh(phase_display: str, active_module: str, active_slice_display: str) -> str:
    slice_phrase = active_slice_display
    if slice_phrase.startswith("推进"):
        slice_phrase = slice_phrase.removeprefix("推进").strip()
    if "治理执行" in phase_display:
        if active_module:
            return f"项目已进入治理执行阶段；当前主战场是 {module_display_name_zh(active_module)}，正在推进 {slice_phrase}。"
        return f"项目已进入治理执行阶段；当前正在推进 {slice_phrase}。"
    if "阶段 3" in phase_display:
        if active_module:
            return f"{phase_display} 已进入执行；当前主战场是 {module_display_name_zh(active_module)}，正在推进 {slice_phrase}。"
        return f"{phase_display} 已进入执行；当前正在推进 {slice_phrase}。"
    if active_module:
        return f"{phase_display} 已进入执行；当前主战场是 {module_display_name_zh(active_module)}，正在推进 {slice_phrase}。"
    return f"{phase_display} 已进入执行；当前正在推进 {slice_phrase}。"


def large_direct_value_zh(active_module: str, current_execution_line: str, active_slice_display: str) -> str:
    mapping = {
        "source-system": "让输入来源更稳定进入系统，而不是散落在各处。",
        "reflection-system": "让学习输入更稳定地转成候选与后续可晋升内容。",
        "memory-registry": "把记忆真相源收口，减少后续迁移和冲突。",
        "projection-system": "让导出给消费者的结果更稳定、更容易被策略消费。",
        "governance-system": "让问题更早通过治理信号暴露，而不是靠人工临时发现。",
        "openclaw-adapter": "把 OpenClaw 侧的召回结果做得更稳定、更可控、更容易解释。",
        "codex-adapter": "让 Codex 侧也能稳定消费同一套共享记忆根。",
    }
    if active_module in mapping:
        return mapping[active_module]
    if current_execution_line:
        return pretty_text_zh(current_execution_line)
    return f"让维护者更容易理解并继续推进 {active_slice_display}。"


def render_medium_progress(
    repo: Path,
    readiness: ResumeReadinessResult,
    project_name: str,
    current_phase: str,
    active_slice: str,
    current_execution_line: str,
    done_tasks: int,
    total_tasks: int,
    architecture_signal: str,
    signal_basis: str,
    root_cause_hypothesis: str,
    correct_layer: str,
    automatic_review_trigger: str,
    escalation_gate: str,
    escalation_reason: str,
    main_risk: str,
    phase_link: str,
    slice_link: str,
    readme_capabilities: list[str],
    next_actions_display: list[str],
    execution_tasks: list[str],
) -> None:
    current_phase_display = pretty_text_zh(current_phase)
    execution_line_display = pretty_text_zh(current_execution_line or "n/a")
    steady_state = is_medium_steady_state(current_phase, active_slice, current_execution_line)
    work_area = medium_work_area_zh(active_slice, current_execution_line)
    slice_explanation = medium_slice_explanation_zh(active_slice, current_execution_line)
    direct_value = medium_direct_value_zh(active_slice, current_execution_line)
    line_complete = total_tasks > 0 and done_tasks == total_tasks
    execution_line_note = "当前这轮已经完成，下一步转向下一条增强切片" if line_complete else "当前这轮正在推进，下面的任务板就是本轮收口内容"
    taskboard_conclusion = "这条长任务已经完成" if line_complete else "这条长任务正在推进"
    next_step_nature = "进入下一条 post-hardening feature slice" if line_complete else "继续当前增强切片并收口任务板"
    position_note = "当前主要在补增强与边界收口"
    work_area_note = "当前这轮主要面向维护者 / 值班者的使用体验与验证链路"
    stop_conditions_display = ""
    if is_skill_repo(repo):
        lowered_phase = current_phase.lower()
        if "ptl supervision" in lowered_phase or "worker handoff" in lowered_phase or "m15" in lowered_phase:
            execution_line_note = "当前这轮已经完成，下一步转向 post-M14 证据采集，并判断是否真的需要 M15 多执行器层" if line_complete else "当前这轮正在推进，下面的任务板就是本轮收口内容"
            next_step_nature = "进入 post-M14 证据采集；M15 继续保持证据驱动 later 层" if line_complete else "继续当前 PTL 监督或 worker 接续切片并收口任务板"
        elif "supervised long-run delivery" in lowered_phase or "rollout" in lowered_phase:
            execution_line_note = "当前这轮已经完成，下一步转向 rollout / 试跑与摩擦采集" if line_complete else "当前这轮正在推进，下面的任务板就是本轮收口内容"
            next_step_nature = "进入 rollout / 试跑与摩擦采集" if line_complete else "继续当前长期受监督交付切片并收口任务板"
        elif "program orchestration" in lowered_phase or "m12" in lowered_phase:
            execution_line_note = "当前这轮已经完成，下一步转向 M12 长期受监督交付层" if line_complete else "当前这轮正在推进，下面的任务板就是本轮收口内容"
            next_step_nature = "进入下一条主线：M12 长期受监督交付层" if line_complete else "继续当前程序编排层切片并收口任务板"
        else:
            execution_line_note = "当前这轮已经完成，下一步转向 M11 程序编排层" if line_complete else "当前这轮正在推进，下面的任务板就是本轮收口内容"
            next_step_nature = "进入下一条主线：M11 程序编排层" if line_complete else "继续当前战略或编排层切片并收口任务板"
    roadmap_path = preferred_existing_path(repo, ["docs/roadmap.zh-CN.md", "docs/roadmap.md"])
    plan_path = repo / ".codex/plan.md"
    status_path = repo / ".codex/status.md"
    status_text = read_text(status_path)
    usage_path = preferred_existing_path(repo, ["docs/usage_guide.zh-CN.md", "docs/usage_guide.md"])
    test_plan_path = preferred_existing_path(repo, ["docs/test-plan.zh-CN.md", "docs/test-plan.md"])
    stop_conditions_display = labeled_bullet_value(section(status_text, "Current Execution Line"), "Stop Conditions")

    if steady_state:
        execution_line_note = "当前没有新的主写入长任务；先把已发布 runtime、文档与 release-facing 基线保持稳定。"
        taskboard_conclusion = "上一轮里程碑已完成；当前处于观察型稳定维护"
        next_step_nature = "继续稳态维护；只有出现新的命名 roadmap 候选或实质性验证变化时才重开主线"
        position_note = "当前不在补旧债，也不在开新里程碑；先维持已发布基线并观察何时值得命名下一条主线。"
        work_area_note = "当前主要做 watch-mode 维护、验证保绿和新候选观察。"

    current_phase_link = phase_link
    if roadmap_path:
        current_phase_line = (
            line_number_for_heading(roadmap_path, "当前 / 下一步 / 更后面")
            or line_number_for_heading(roadmap_path, "Current / Next / Later")
            or line_number_for_heading(roadmap_path, "Status")
        )
        if current_phase_line:
            current_phase_link = markdown_file_link(roadmap_path, "路线图 / 当前阶段", current_phase_line)

    print("# 项目进展\n")
    print_upgrade_notice(readiness)
    print("## 一眼总览")
    print("| 问题 | 当前答案 |")
    print("| --- | --- |")
    print(f"| 项目 | `{project_name}` |")
    print(f"| 当前判断 | {medium_mainline_status_zh(repo, current_phase, active_slice, current_execution_line)} |")
    print(f"| 当前阶段 | {current_phase_display} |")
    print(f"| 当前工作域 | {work_area} |")
    print(f"| 当前切片 | {slice_explanation} |")
    print(f"| 当前执行进度 | `{done_tasks} / {total_tasks}` |")
    print(f"| 架构信号 | `{zh_signal(architecture_signal or 'n/a')}` |")
    print(f"| 直接价值 | {direct_value} |")
    print(f"| 当前主要风险 | {pretty_text_zh(main_risk)} |")

    print("\n## 当前定位")
    print("| 维度 | 当前状态 | 说明 | 入口 |")
    print("| --- | --- | --- | --- |")
    print(f"| 主线状态 | {medium_mainline_status_zh(repo, current_phase, active_slice, current_execution_line)} | {position_note} | {markdown_file_link(roadmap_path, '路线图') if roadmap_path else '暂无'} |")
    print(f"| 当前阶段 | {current_phase_display} | {position_note} | {current_phase_link if current_phase_link != 'n/a' else '暂无'} |")
    print(f"| 当前工作域 | {work_area} | {work_area_note} | {markdown_file_link(usage_path, '使用指南') if usage_path else '暂无'} |")
    print(f"| 当前切片 | {slice_explanation} | 原始切片名：`{active_slice}` | {slice_link if slice_link != 'n/a' else markdown_file_link(plan_path, '计划') if plan_path.exists() else '暂无'} |")
    print(f"| 当前执行线 | {execution_line_display} | {execution_line_note} | {markdown_file_link(status_path, '状态') if status_path.exists() else '暂无'} |")

    print("\n## 当前这轮到底在做什么")
    print("| 当前工作 | 类型 | 对维护者的直接价值 | 当前状态 | 对应任务 |")
    print("| --- | --- | --- | --- | --- |")
    for current, value, state, task_id, task_type in medium_current_work_rows(
        active_slice,
        execution_tasks,
        next_actions_display,
        current_phase,
        current_execution_line,
    ):
        print(f"| {current} | {task_type} | {value} | {state} | `{task_id}` |")

    print("\n## 架构监督")
    print("| 项目 | 当前值 |")
    print("| --- | --- |")
    print(f"| 信号 | `{zh_signal(architecture_signal or 'n/a')}` |")
    print(f"| 根因假设 | {pretty_text_zh(root_cause_hypothesis)} |")
    print(f"| 正确落层 | {pretty_text_zh(correct_layer)} |")
    print(f"| 信号依据 | {pretty_text_zh(signal_basis)} |")
    print(f"| 自动触发 | {pretty_text_zh(automatic_review_trigger)} |")
    print(f"| 升级 Gate | `{zh_gate(escalation_gate or 'n/a')}` |")
    print(f"| 升级原因 | {pretty_text_zh(escalation_reason)} |")

    if steady_state:
        render_medium_supervision_summary(
            automatic_review_trigger,
            escalation_gate,
            escalation_reason,
            stop_conditions_display,
        )
    else:
        render_strategy_view(repo)
        render_program_view(repo)
        render_delivery_view(repo)
        render_ptl_view(repo)
        render_handoff_view(repo)

    glossary_rows = relevant_terms(repo, active_slice, current_execution_line, readme_capabilities)
    if glossary_rows:
        print("\n## 关键术语解释")
        print("| 术语 | 中文解释 | 什么时候看它 | 当前与它的关系 |")
        print("| --- | --- | --- | --- |")
        for row in glossary_rows:
            print(f"| `{row['term']}` | {row['meaning']} | {row['when']} | {row['current']} |")

    capability_rows = split_medium_capabilities(repo, readme_capabilities)
    if capability_rows:
        print("\n## 当前系统能做什么")
        print("| 面向谁 | 已能做什么 | 当前状态 | 来源 |")
        print("| --- | --- | --- | --- |")
        for audience, capability, state, source in capability_rows[:8]:
            print(f"| {audience} | {capability} | {state} | {source} |")

    print("\n## 工作域视角")
    print("| 工作域 | 这是干什么的 | 当前状态 | 优先级 | 当前在做什么 | 下一步 |")
    print("| --- | --- | --- | --- | --- | --- |")
    for domain, purpose, state, priority, current, next_step in medium_workstream_rows(repo, active_slice, current_execution_line):
        print(f"| {domain} | {purpose} | {state} | {priority} | {current} | {next_step} |")

    print("\n## 当前长任务")
    print("| 项目 | 当前值 |")
    print("| --- | --- |")
    print(f"| 长任务名称 | `{active_slice}` |" if not steady_state else "| 长任务名称 | `当前没有新的主写入长任务` |")
    print(f"| 长任务目标 | {slice_explanation} |" if not steady_state else "| 长任务目标 | 保持已发布 runtime、文档与 release-facing 基线稳定；在真正出现新的命名 roadmap 候选前，不提前打开下一条主线。 |")
    print(f"| 执行进度 | `{done_tasks} / {total_tasks}` |" if not steady_state else f"| 执行进度 | `上一轮 {done_tasks} / {total_tasks} 已完成` |")
    print(f"| 当前结论 | {taskboard_conclusion} |")
    print(f"| 是否存在 blocker | {pretty_text_zh(main_risk)} |")
    print(f"| 下一步性质 | {next_step_nature} |")

    task_rows = execution_task_rows(execution_tasks)
    if steady_state and next_actions_display:
        task_rows = [(task_id, task_type, state, content) for task_id, task_type, state, content, _ in maintenance_task_rows(next_actions_display)]
    if task_rows:
        print("\n## 当前任务板")
        print("| 任务 ID | 类型 | 状态 | 任务内容 |")
        print("| --- | --- | --- | --- |")
        for task_id, task_type, state, content in task_rows:
            print(f"| {task_id} | {task_type} | {state} | {content} |")

    print("\n## 项目控制能力")
    print("| 能力 | 状态 |")
    print("| --- | --- |")
    print("| 恢复当前状态与下一步 | 已就绪 |")
    print("| 长任务执行线与可见任务板 | 已就绪 |")
    print("| 默认架构监督与升级 gate | 已就绪 |")
    print("| 文档整改与 Markdown 治理 | 已就绪 |")
    print("| 开发日志索引与自动沉淀 | 已就绪 |")
    print("| 公开文档中英文切换 | 已就绪 |")

    print("\n## 人工窗口")
    print("| 命令 | 用途 |")
    print("| --- | --- |")
    for command, purpose in human_window_rows_zh():
        print(f"| {command} | {purpose} |")

    print("\n## 接下来要做什么")
    print("| 下一步 | 为什么做 | 对应入口 |")
    print("| --- | --- | --- |")
    next_rows: list[tuple[str, str, str]] = []
    if next_actions_display:
        action_sources = [
            markdown_file_link(status_path, "状态") if status_path.exists() else "暂无",
            markdown_file_link(test_plan_path, "测试计划") if test_plan_path else "暂无",
            markdown_file_link(usage_path, "使用指南") if usage_path else "暂无",
        ]
        reason_defaults = [
            "避免继续在已完成的 helper 上打转",
            "防止短视图和正式发布验证漂移",
            "避免带着回归风险前进",
        ]
        for idx, action in enumerate(next_actions_display[:3]):
            next_rows.append((action, reason_defaults[min(idx, len(reason_defaults) - 1)], action_sources[min(idx, len(action_sources) - 1)]))
    for action, reason, source in next_rows:
        print(f"| {action} | {reason} | {source} |")
    print("| 如果要看完整全局视图 | 使用更完整的项目进展输出 | `项目助手 进展` |")


def render_large_progress(
    repo: Path,
    readiness: ResumeReadinessResult,
    project_name: str,
    tier: str,
    current_phase: str,
    active_slice: str,
    current_execution_line: str,
    architecture_signal: str,
    signal_basis: str,
    root_cause_hypothesis: str,
    correct_layer: str,
    automatic_review_trigger: str,
    escalation_gate: str,
    escalation_reason: str,
    execution_tasks: list[str],
    done_tasks: int,
    total_tasks: int,
    capabilities: list[tuple[str, str]],
    next_actions_display: list[str],
    main_risk: str,
    active_module: str,
    phase_link: str,
    slice_link: str,
    roadmap_path: Path | None,
    project_roadmap_path: Path | None,
    readme_capabilities: list[str],
    phase_capabilities: list[str],
    official_modules: list[str],
    module_summaries: list[dict[str, str]],
    subproject_rows: list[tuple[str, str, str]],
) -> None:
    phase_display = pretty_text_zh(current_phase)
    active_slice_display = pretty_text_zh(active_slice)
    execution_line_display = pretty_text_zh(current_execution_line or "n/a")
    judgment = large_project_judgement_zh(phase_display, active_module, active_slice_display)
    direct_value = large_direct_value_zh(active_module, current_execution_line, active_slice_display)

    print("# 项目进展\n")
    print_upgrade_notice(readiness)
    print("## 一眼总览")
    print("| 问题 | 当前答案 |")
    print("| --- | --- |")
    print(f"| 项目 | `{project_name}` |")
    print(f"| 层级 | `{zh_tier(tier)}` |")
    print(f"| 当前判断 | {judgment} |")
    print(f"| 当前阶段 | {phase_display} |")
    if active_module:
        print(f"| 当前主战场 | `{module_display_name_zh(active_module)}` |")
    print(f"| 当前切片 | {active_slice_display} |")
    print(f"| 当前执行线 | {execution_line_display} |")
    print(f"| 执行进度 | `{done_tasks} / {total_tasks}` |")
    print(f"| 架构信号 | `{zh_signal(architecture_signal or 'n/a')}` |")
    print(f"| 直接价值 | {direct_value} |")
    print(f"| 当前主要风险 | {pretty_text_zh(main_risk)} |")

    print("\n## 当前定位")
    print("| 项目位置 | 当前值 | 说明 | 链接 |")
    print("| --- | --- | --- | --- |")
    print(f"| 当前阶段 | {phase_display} | 当前所处的大阶段 | {phase_link if phase_link != 'n/a' else '暂无'} |")
    print(f"| 当前切片 | {active_slice_display} | 当前真正推进的工作单元 | {slice_link if slice_link != 'n/a' else '暂无'} |")
    print(f"| 当前执行线 | {execution_line_display} | 这一轮长任务的人话说明 | 暂无 |")
    if active_module:
        print(f"| 当前模块 | `{module_display_name_zh(active_module)}` | 当前主战场 | 暂无 |")
    if roadmap_path:
        print(f"| 总路线图 | `docs/roadmap` | 项目总阶段和 now/next/later | {markdown_file_link(roadmap_path, 'docs/roadmap')} |")
    if project_roadmap_path:
        print(f"| 工作流路线图 | `project roadmap` | 当前工作流与焦点位置 | {markdown_file_link(project_roadmap_path, 'project roadmap')} |")

    print("\n## 全局视角")
    print("| 区域 | 当前状态 | 当前焦点 | 退出条件 |")
    print("| --- | --- | --- | --- |")
    print(f"| 项目整体 | {phase_display or '暂无'} | {active_slice_display or '暂无'} | 在不丢失模块视角和治理清晰度的前提下推进当前切片 |")

    print("\n## 当前长任务")
    print("| 项目 | 当前值 |")
    print("| --- | --- |")
    print(f"| 长任务名称 | {active_slice_display} |")
    print(f"| 长任务目标 | {execution_line_display} |")
    print(f"| 执行进度 | `{done_tasks} / {total_tasks}` |")
    print(f"| 当前结论 | 当前切片已经推进到当前检查点 |")
    print(f"| 是否存在 blocker | {pretty_text_zh(main_risk)} |")
    print(f"| 下一步性质 | {pretty_text_zh(next_actions_display[0]) if next_actions_display else '继续推进当前阶段'} |")

    if execution_tasks:
        print("\n## 当前任务板")
        print("| 任务 ID | 类型 | 状态 | 任务内容 |")
        print("| --- | --- | --- | --- |")
        for task_id, task_type, state, content in execution_task_rows(execution_tasks):
            print(f"| {task_id} | {task_type} | {state} | {content} |")

    print("\n## 架构监督")
    print("| 项目 | 当前值 |")
    print("| --- | --- |")
    print(f"| 信号 | `{zh_signal(architecture_signal)}` |")
    print(f"| 根因假设 | {pretty_text_zh(root_cause_hypothesis)} |")
    print(f"| 正确落层 | {pretty_text_zh(correct_layer)} |")
    print(f"| 信号依据 | {pretty_text_zh(signal_basis)} |")
    print(f"| 自动触发 | {pretty_text_zh(automatic_review_trigger)} |")
    print(f"| 升级门 | `{zh_gate(escalation_gate)}` |")
    print(f"| 升级原因 | {pretty_text_zh(escalation_reason)} |")

    render_strategy_view(repo)
    render_program_view(repo)
    render_delivery_view(repo)
    render_ptl_view(repo)
    render_handoff_view(repo)

    if readme_capabilities or phase_capabilities:
        readme_path = preferred_existing_path(repo, ["README.zh-CN.md", "README.md"])
        readme_source = markdown_file_link(readme_path, "README") if readme_path else "暂无"
        phase_source = readme_source
        if readme_path:
            phase_line = line_number_for_heading(readme_path, "为什么 Self-Learning 现在就重要") or line_number_for_heading(
                readme_path, "Why Self-Learning Already Matters"
            )
            if phase_line:
                phase_source = markdown_file_link(readme_path, "README / 当前阶段基线", phase_line)
        print("\n## 当前系统能做什么")
        print("| 能力 / 结论 | 当前状态 | 来源 |")
        print("| --- | --- | --- |")
        for item in readme_capabilities[:6]:
            print(f"| {pretty_text_zh(item)} | 已可直接使用 | {readme_source} |")
        for item in phase_capabilities[:4]:
            print(f"| {pretty_text_zh(item)} | 当前阶段已落地 | {phase_source} |")

    if capabilities:
        print("\n## 项目控制能力")
        print("| 能力 | 状态 |")
        print("| --- | --- |")
        for _, label in capabilities:
            print(f"| {label} | 已就绪 |")

    print("\n## 人工窗口")
    print("| 命令 | 用途 |")
    print("| --- | --- |")
    for command, purpose in human_window_rows_zh():
        print(f"| {command} | {purpose} |")

    average_completion = round(
        sum(int(summary["completion_percent"]) for summary in module_summaries) / len(module_summaries)
    ) if module_summaries else 0
    print("\n## 模块总览")
    print("| 指标 | 当前值 |")
    print("| --- | --- |")
    print(f"| 官方模块数 | `{len(official_modules)}` |")
    print(f"| 平均完成度 | `{average_completion}%` |")
    print(f"| 当前投入分布 | {module_health_breakdown(module_summaries)} |")
    print("| 优先级说明 | `P0` 当前主战场，`P1` 下一批高优先级，`P2` 持续治理，`P3` 稳定维护，`P4` 观察/维护 |")

    print("\n## 模块视角")
    print("| 模块 | 优先级 | 当前状态 | 完成度 | 已有能力 | 剩余步骤 | 下一检查点 |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for module, summary in zip(official_modules, module_summaries):
        print(
            f"| {module_display_name_zh(module)} | {summary['priority']} | {zh_status(summary['status'])} | {summary['completion_percent']}% ({zh_band(summary['completion_band'])}) | {summary['implemented']} | {summary['remaining']} | {summary['next_checkpoint']} |"
        )

    print("\n## 模块位置图")
    print("```mermaid")
    print("flowchart TB")
    print(f'    P["{project_name}"]')
    for module, summary in zip(official_modules, module_summaries):
        label = module_display_name_zh(module)
        priority = summary["priority"]
        status_label = f"{priority} / {summary['completion_percent']}%"
        node_id = re.sub(r"[^A-Za-z0-9]+", "", module.title()) or "Module"
        print(f'    P --> {node_id}["{label}\\n{status_label}"]')
    print("```")

    if subproject_rows:
        print("\n## 横切工作流")
        print("| 工作流 | 当前切片 | 下一检查点 |")
        print("| --- | --- | --- |")
        for name, current_slice, next_checkpoint in subproject_rows:
            print(f"| {name} | {current_slice or '暂无'} | {next_checkpoint or '暂无'} |")

    print("\n## 接下来要做什么")
    print("| 下一步 | 为什么做 | 对应入口 |")
    print("| --- | --- | --- |")
    status_path = repo / ".codex/status.md"
    for idx, item in enumerate(next_actions_display[:3]):
        reason = "保持当前阶段继续收敛" if idx == 0 else "避免方向漂移并保持验证同步" if idx == 1 else "在继续扩展前先确认门禁与治理决策"
        print(f"| {item} | {reason} | {markdown_file_link(status_path, '状态')} |")
    print("| 如果要看完整全局视图 | 当前已经是完整项目进展面板 | `项目助手 进展` |")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a quick markdown progress snapshot from the control surface.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
    readiness = ensure_resume_ready(repo, check_only=False)
    repo = readiness.repo
    tier = parse_tier(repo)
    status_text = (repo / ".codex/status.md").read_text(encoding="utf-8")
    project_name = project_display_name(repo)

    current_phase = first_line(section(status_text, "Current Phase"))
    active_slice = first_line(section(status_text, "Active Slice"))
    current_execution_line = labeled_bullet_value(section(status_text, "Current Execution Line"), "Objective")
    architecture_state = classify_architecture_signal(repo)
    architecture_signal = architecture_state["signal"]
    signal_basis = architecture_state["signal_basis"]
    root_cause_hypothesis = architecture_state["root_cause_hypothesis"]
    correct_layer = architecture_state["correct_layer"]
    escalation_gate = architecture_state["gate"]
    escalation_reason = architecture_state["reason"]
    execution_tasks = execution_task_lines(status_text)
    done_tasks, total_tasks = execution_task_progress(execution_tasks)
    capabilities = repo_capabilities(repo)
    human_windows = primary_human_windows("zh")
    next_actions = section(status_text, "Next 3 Actions")
    main_risk = first_risk(status_text)
    active_module = active_module_slug(repo, active_slice)
    phase_link, slice_link = roadmap_links(repo, current_phase, active_slice, active_module, current_execution_line)
    roadmap_path = preferred_existing_path(repo, ["docs/roadmap.zh-CN.md", "docs/roadmap.md"])
    project_roadmap_path = preferred_existing_path(
        repo,
        ["docs/workstreams/project/roadmap.zh-CN.md", "docs/workstreams/project/roadmap.md"],
    )
    readme_path, readme_capabilities, phase_capabilities = readme_capability_sections(repo)
    horizon_focus = roadmap_horizon_focus(repo)
    phase_line, phase_milestone_label = line_number_for_active_milestone(roadmap_path) if roadmap_path else (None, "")
    phase_display = pretty_text_zh(phase_milestone_label or current_phase)
    active_slice_display = pretty_text_zh(active_slice)
    execution_line_display = pretty_text_zh(current_execution_line or "n/a")
    next_actions_display = numbered_actions_zh(next_actions)

    if tier == "medium":
        render_medium_progress(
            repo=repo,
            readiness=readiness,
            project_name=project_name,
            current_phase=current_phase,
            active_slice=active_slice,
            current_execution_line=current_execution_line,
            done_tasks=done_tasks,
            total_tasks=total_tasks,
            architecture_signal=architecture_signal,
            signal_basis=signal_basis,
            root_cause_hypothesis=root_cause_hypothesis,
            correct_layer=correct_layer,
            automatic_review_trigger=architecture_state["automatic_review_trigger"],
            escalation_gate=escalation_gate,
            escalation_reason=escalation_reason,
            main_risk=main_risk,
            phase_link=phase_link,
            slice_link=slice_link,
            readme_capabilities=readme_capabilities,
            next_actions_display=next_actions_display,
            execution_tasks=execution_tasks,
        )
        return 0

    module_dir = repo / ".codex/modules"
    official_modules = parse_official_modules(repo)
    module_summaries: list[dict[str, str]] = []
    if tier == "large" and module_dir.exists() and official_modules:
        for module in official_modules:
            path = module_dir / f"{module}.md"
            if path.exists():
                summary = load_module_summary(path)
            else:
                summary = {
                    "status": "missing",
                    "completion_percent": "0",
                    "completion_band": "planned",
                    "implemented": "missing",
                    "remaining": "missing",
                    "completion": "missing",
                    "next_checkpoint": "missing",
                }
            summary["priority"] = module_priority(module, summary, active_module, horizon_focus)
            module_summaries.append(summary)

    subproject_rows = load_subproject_rows(repo)
    if tier == "large":
        render_large_progress(
            repo=repo,
            readiness=readiness,
            project_name=project_name,
            tier=tier,
            current_phase=current_phase,
            active_slice=active_slice,
            current_execution_line=current_execution_line,
            architecture_signal=architecture_signal,
            signal_basis=signal_basis,
            root_cause_hypothesis=root_cause_hypothesis,
            correct_layer=correct_layer,
            automatic_review_trigger=architecture_state["automatic_review_trigger"],
            escalation_gate=escalation_gate,
            escalation_reason=escalation_reason,
            execution_tasks=execution_tasks,
            done_tasks=done_tasks,
            total_tasks=total_tasks,
            capabilities=capabilities,
            next_actions_display=next_actions_display,
            main_risk=main_risk,
            active_module=active_module,
            phase_link=phase_link,
            slice_link=slice_link,
            roadmap_path=roadmap_path,
            project_roadmap_path=project_roadmap_path,
            readme_capabilities=readme_capabilities,
            phase_capabilities=phase_capabilities,
            official_modules=official_modules,
            module_summaries=module_summaries,
            subproject_rows=subproject_rows,
        )
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
