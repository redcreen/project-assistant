#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from control_surface_lib import (
    classify_architecture_signal,
    completion_band,
    completion_percent,
    display_execution_task,
    execution_task_lines,
    execution_task_progress,
    first_line,
    labeled_bullet_value,
    parse_official_modules,
    parse_tier,
    primary_human_windows,
    read_text,
    repo_capabilities,
    section,
    slugify,
)


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

EXACT_TEXT_MAP = {
    "governed execution / module-view active": "治理执行中 / 模块视角已启用",
    "stage 3: self-learning lifecycle baseline": "阶段 3：self-learning 生命周期基线",
    "stage 3：self-learning lifecycle 基线": "阶段 3：self-learning 生命周期基线",
    "advance-openclaw-adapter-recall-quality": "推进 OpenClaw 适配层召回质量扩面",
    "registration and slash-override coverage expansion": "注册与 slash-override 覆盖扩面",
    "status command path coverage expansion": "status 命令路径覆盖扩面",
    "none currently.": "当前无主要风险。",
    "none currently": "当前无主要风险。",
    "post-doc baseline hardening is now closed through runtime-path and registration coverage; the repo is ready to choose its next maintenance or feature slice.": "文档整改后的基线加固已通过 runtime 路径与注册路径覆盖收口；仓库已准备进入下一条维护或功能切片。",
    "lock down plugin registration behavior so enabled/disabled, slashoverride, and command registration paths stay stable without relying on upstream host changes": "锁定插件注册行为，让启用/禁用、slashOverride 与命令注册路径保持稳定，且不依赖上游宿主改动。",
    "current execution can proceed inside the existing direction without a user-level tradeoff": "当前执行可以沿既有方向继续，不需要用户层面的额外取舍。",
    "current plugin registration boundary, config defaults, current status handler coverage": "当前插件注册边界、配置默认值与 status handler 覆盖面。",
    "low; tests may accidentally bind to incidental logger text instead of runtime behavior": "风险较低；测试可能误绑定到日志文案，而不是 runtime 行为。",
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
    (" and ", " 与 "),
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
    target = str(path)
    if line:
        target = f"{target}:{line}"
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
        or section(text, "Core Capabilities")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a quick markdown progress snapshot from the control surface.")
    parser.add_argument("repo", type=Path, help="Repository root")
    args = parser.parse_args()

    repo = args.repo.resolve()
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

    print("# 项目进展\n")
    print("## 一眼总览")
    print(f"- 项目: `{project_name}`")
    print(f"- 层级: `{zh_tier(tier)}`")
    print(f"- 当前阶段: `{phase_display}`")
    print(f"- 当前切片: `{active_slice_display}`")
    print(f"- 当前执行线: `{execution_line_display}`")
    print(f"- 执行进度: `{done_tasks} / {total_tasks}`")
    print(f"- 架构信号: `{zh_signal(architecture_signal or 'n/a')}`")
    print(f"- 升级门: `{zh_gate(escalation_gate or 'n/a')}`")
    print(f"- 当前主要风险: {pretty_text_zh(main_risk)}")

    print("\n## 当前位置")
    print("| 项目位置 | 当前值 | 链接 |")
    print("| --- | --- | --- |")
    print(f"| 当前阶段 | `{phase_display}` | {pretty_text_zh(phase_link) if phase_link == 'n/a' else phase_link} |")
    print(f"| 当前切片 | `{active_slice_display}` | {pretty_text_zh(slice_link) if slice_link == 'n/a' else slice_link} |")
    print(f"| 当前执行线 | `{execution_line_display}` | 暂无 |")
    if active_module:
        print(f"| 当前模块 | `{module_display_name_zh(active_module)}` | 暂无 |")
    if roadmap_path:
        print(f"| 总路线图 | `docs/roadmap` | {markdown_file_link(roadmap_path, 'docs/roadmap')} |")
    if project_roadmap_path:
        print(f"| 工作流路线图 | `project roadmap` | {markdown_file_link(project_roadmap_path, 'project roadmap')} |")

    print("\n## 全局视角")
    print("| 区域 | 当前状态 | 当前焦点 | 退出条件 |")
    print("| --- | --- | --- | --- |")
    print(f"| 项目整体 | {phase_display or '暂无'} | {active_slice_display or '暂无'} | 在不丢失模块视角和治理清晰度的前提下推进当前切片 |")

    if current_execution_line:
        print("\n## 当前执行线")
        print(f"- 目标: {execution_line_display}")
        print(f"- 关联切片: `{active_slice_display or '暂无'}`")
        if execution_tasks:
            print(f"- 进度: {done_tasks} / {total_tasks}")
            print("- 任务板:")
            for item in execution_tasks:
                print(f"  - {display_execution_task_zh(item)}")

    if architecture_signal or escalation_gate or root_cause_hypothesis or correct_layer:
        print("\n## 架构监督")
        if architecture_signal:
            print(f"- 信号: {zh_signal(architecture_signal)}")
        if root_cause_hypothesis:
            print(f"- 根因假设: {pretty_text_zh(root_cause_hypothesis)}")
        if correct_layer:
            print(f"- 正确落层: {pretty_text_zh(correct_layer)}")
        if signal_basis:
            print(f"- 信号依据: {pretty_text_zh(signal_basis)}")
        if escalation_gate:
            print(f"- 升级门: {zh_gate(escalation_gate)}")
        if escalation_reason:
            print(f"- 升级原因: {pretty_text_zh(escalation_reason)}")

    if readme_capabilities or phase_capabilities:
        print("\n## 当前系统能做什么")
        readme_source = "n/a"
        phase_source = "n/a"
        roadmap_source = "n/a"
        if readme_path:
            core_line = line_number_for_heading(readme_path, "核心能力") or line_number_for_heading(readme_path, "Core Capabilities")
            readme_source = markdown_file_link(readme_path, "README / 核心能力", core_line) if core_line else markdown_file_link(
                readme_path, "README"
            )
            phase_line = line_number_for_heading(readme_path, "为什么 Self-Learning 现在就重要") or line_number_for_heading(
                readme_path, "Why Self-Learning Already Matters"
            )
            if phase_line:
                phase_source = markdown_file_link(readme_path, "README / 当前阶段基线", phase_line)
        if roadmap_path:
            now_line = (
                line_number_for_heading(roadmap_path, "Now / Next / Later")
                or line_number_for_heading(roadmap_path, "现在 / 下一步 / 后续")
                or line_number_for_heading(roadmap_path, "当前 / 下一步 / 更后面")
            )
            if now_line:
                roadmap_source = markdown_file_link(roadmap_path, "Roadmap / Now-Next-Later", now_line)
        print("| 能力 / 结论 | 当前状态 | 来源 |")
        print("| --- | --- | --- |")
        for item in readme_capabilities[:6]:
            print(f"| {pretty_text_zh(item)} | 已可直接使用 | {readme_source} |")
        for item in phase_capabilities[:4]:
            print(f"| {pretty_text_zh(item)} | 当前阶段已落地 | {phase_source if phase_source != 'n/a' else roadmap_source} |")

    if capabilities:
        print("\n## 项目控制能力")
        print("| 能力 | 状态 |")
        print("| --- | --- |")
        for _, label in capabilities:
            print(f"| {label} | 已就绪 |")

    print("\n## 人工窗口")
    for item in human_windows:
        print(f"- `{item}`")

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

        average_completion = round(
            sum(int(summary["completion_percent"]) for summary in module_summaries) / len(module_summaries)
        )

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

    subproject_rows = load_subproject_rows(repo)
    if subproject_rows:
        print("\n## 横切工作流")
        print("| 工作流 | 当前切片 | 下一检查点 |")
        print("| --- | --- | --- |")
        for name, current_slice, next_checkpoint in subproject_rows:
            print(f"| {name} | {current_slice or 'n/a'} | {next_checkpoint or 'n/a'} |")

    print("\n## 接下来要做的事")
    if next_actions_display:
        for idx, item in enumerate(next_actions_display, start=1):
            print(f"{idx}. {item}")
    else:
        print("当前未记录下一步。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
