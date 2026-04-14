# 测试计划

[English](test-plan.md) | [中文](test-plan.zh-CN.md)

## 范围与风险

本计划用于验证 `project-assistant` 作为一个可收敛的项目治理 skill 仍然可用。

主要风险：

- 控制面漂移
- 整改停在中间态
- 进展输出不够清楚
- 公开文档结构或双语对照失效
- daemon runtime / host state 漂移
- continue 恢复桥或 legacy rollout 在新基线上退化

## 验收用例

| 用例 | 前置条件 | 操作 | 预期结果 |
| --- | --- | --- | --- |
| 统一启动前门 | 空白仓库且有 git 根目录 | 运行 `project_assistant_entry.py bootstrap` | 通过一次工具调用完成 control surface、docs 和 fast gate |
| 控制面整改 | 目标仓库缺 `.codex/*` | 运行整改流程 | 必需控制文件存在且通过校验 |
| 统一整改前门 | 仓库带 legacy docs 或 Markdown 杂乱结构 | 运行 `project_assistant_entry.py retrofit` | 通过一次工具调用完成 control surface、docs、Markdown governance 和 fast gate |
| 入口路由真相 | 仓库当前需要统一前门层 | 在 bootstrap / retrofit 或恢复升级后运行 `validate_entry_routing.py` | `.codex/entry-routing.md` 描述的 daemon-host 默认快路径与维护者文档、入口和门禁保持一致 |
| 大项目进展 | 目标仓库有模块层 | 运行进展流程 | 输出包含全局视角、模块视角和 Mermaid |
| 长任务执行线 | 目标、约束和 active slice 已明确 | 运行执行或恢复流程 | 助手会推进一段有检查点的长任务，而不是反复等待“继续” |
| 上下文交接 | 长会话仓库有 active slice | 运行交接流程 | 生成可复制恢复包 |
| daemon runtime | 目标仓库已有控制面 | 运行 `project_assistant_entry.py daemon start/status/queue` | 本地 runtime 可启动、暴露队列 / 事件状态，并保持前台主写入线 lease |
| VS Code 宿主壳 | 打开 `integrations/vscode-host` 对应 workspace | 运行扩展校验与本地 smoke | 宿主能显示 live status、最近文件和任务日志入口 |
| continue 恢复桥 | runtime 处于 `resume-ready` | 通过宿主命令触发 `manual continue` 或 `one-click continue` | 恢复动作继续复用统一前门，不依赖聊天框注入 |
| daemon-host 本地验证 | 使用代表性本地 fixture repo | 运行 `validate_daemon_host_mvp.py` | daemon-host baseline 覆盖 bootstrap、retrofit、docs-retrofit、progress、continue、handoff 和 fast gate |
| daemon-host legacy rollout | 使用降代 legacy fixture repo | 运行 `validate_daemon_legacy_rollout.py` | legacy repo 会先升级，再输出结构化 continue / progress / handoff |
| 文档整改 | 仓库已有公开文档 | 运行文档整改 | README 与 docs 系统被规范化且通过校验 |
| 控制面质量 | 仓库已有 `.codex/*` | 运行控制面质量校验 | brief / plan / status / modules 不再停留在模板态 |
| 公开文档双语 | 仓库要求双语公开文档 | 运行双语校验脚本 | 中英文文档对和切换链接齐全 |
| 公开文档质量 | 仓库已有公开文档 | 运行质量校验脚本 | 公开文档不再包含模板占位、空图示或坏链接 |
| 开发日志 | 仓库在实现过程中产生了值得保留的推理链路 | 写入或校验开发日志 | 开发日志索引存在，条目含问题、思考、解决方案和验证 |

## 自动化覆盖

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

## 手工检查

- 确认 README 对首次读者足够清楚
- 确认中英文公开文档可以互相切换
- 确认图示是在帮助理解，而不是重复文本
- 确认执行与恢复语义是“有检查点的长任务”，而不是微小步进循环
- 确认启动与整改可以从同一条 CLI 前门触发，而不是依赖手工串脚本
- 确认 README、usage、architecture、test-plan 与 `.codex/entry-routing.md` 描述的是同一条 daemon-host 默认快路径
- 确认 daemon / queue 控制面能在不打断主编码线的前提下提供可读状态
- 确认 VS Code 宿主能让用户感知“页面在动、代码在改、任务在推进”
- 确认开发日志保留了关键推理链路，而不是重复 status

## 测试数据与夹具

- 当前 skill 仓库自身
- 仅有 `.codex` 的 medium 仓库
- 带模块层和 durable docs 的 large 仓库

## 发布门禁

在认定 skill 更新完成前：

- skill 仓库自身通过控制面校验
- skill 仓库自身通过文档系统校验
- skill 仓库自身通过公开文档双语校验
- skill 仓库自身通过 entry-routing 校验
- skill 仓库自身通过 dogfooding-evidence 校验
- skill 仓库自身通过分层门禁校验
- skill 仓库自身通过文档质量校验
- skill 仓库自身通过控制面质量校验
- skill 仓库自身通过开发日志校验
- skill 仓库自身通过 daemon runtime、VS Code 宿主壳、daemon-host baseline 和 legacy rollout 校验
