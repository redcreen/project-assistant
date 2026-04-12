# 测试计划

[English](test-plan.md) | [中文](test-plan.zh-CN.md)

## 范围与风险

本计划用于验证 `project-assistant` 作为一个可收敛的项目治理 skill 仍然可用。

主要风险：

- 控制面漂移
- 整改停在中间态
- 进展输出不够清楚
- 公开文档结构或双语对照失效

## 验收用例

| 用例 | 前置条件 | 操作 | 预期结果 |
| --- | --- | --- | --- |
| 控制面整改 | 目标仓库缺 `.codex/*` | 运行整改流程 | 必需控制文件存在且通过校验 |
| 大项目进展 | 目标仓库有模块层 | 运行进展流程 | 输出包含全局视角、模块视角和 Mermaid |
| 长任务执行线 | 目标、约束和 active slice 已明确 | 运行执行或恢复流程 | 助手会推进一段有检查点的长任务，而不是反复等待“继续” |
| 上下文交接 | 长会话仓库有 active slice | 运行交接流程 | 生成可复制恢复包 |
| 文档整改 | 仓库已有公开文档 | 运行文档整改 | README 与 docs 系统被规范化且通过校验 |
| 控制面质量 | 仓库已有 `.codex/*` | 运行控制面质量校验 | brief / plan / status / modules 不再停留在模板态 |
| 公开文档双语 | 仓库要求双语公开文档 | 运行双语校验脚本 | 中英文文档对和切换链接齐全 |
| 公开文档质量 | 仓库已有公开文档 | 运行质量校验脚本 | 公开文档不再包含模板占位、空图示或坏链接 |
| 开发日志 | 仓库在实现过程中产生了值得保留的推理链路 | 写入或校验开发日志 | 开发日志索引存在，条目含问题、思考、解决方案和验证 |

## 自动化覆盖

- `scripts/validate_control_surface.py`
- `scripts/validate_docs_system.py`
- `scripts/validate_public_docs_i18n.py`
- `scripts/validate_gate_set.py`
- `scripts/validate_doc_quality.py`
- `scripts/validate_control_surface_quality.py`
- `scripts/validate_development_log.py`

## 手工检查

- 确认 README 对首次读者足够清楚
- 确认中英文公开文档可以互相切换
- 确认图示是在帮助理解，而不是重复文本
- 确认执行与恢复语义是“有检查点的长任务”，而不是微小步进循环
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
- skill 仓库自身通过分层门禁校验
- skill 仓库自身通过文档质量校验
- skill 仓库自身通过控制面质量校验
- skill 仓库自身通过开发日志校验
