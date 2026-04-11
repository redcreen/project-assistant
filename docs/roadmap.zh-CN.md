# 路线图

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## 范围

这个路线图只描述 `project-assistant` skill 自身的演进，不替代 `.codex/status.md` 中的当前执行状态。

## 当前 / 下一步 / 更后面

| 时间层级 | 重点 | 退出信号 |
| --- | --- | --- |
| 当前 | 收敛式整改、进展、交接、文档系统门禁 | 控制面、文档系统、公开文档双语都通过校验 |
| 下一步 | 提升自动文档重组质量与模板能力 | 真实项目里更少需要手工重排 README 和 docs |
| 更后面 | 更丰富的验收规则、更好的恢复自动化、更多可视化 | 新仓库更少需要额外提示 |

## 里程碑

| 里程碑 | 状态 | 目标 | 依赖 | 退出条件 |
| --- | --- | --- | --- | --- |
| M1 | done | 建立 `.codex` 控制面与项目分级 | core skill routing | 当前状态可恢复 |
| M2 | done | 建立收敛式 retrofit | control-surface scripts | 整改不再停在中间态 |
| M3 | done | 建立进展与交接工作流 | module layer + snapshot scripts | 进展和交接稳定可用 |
| M4 | done | 建立 durable 文档标准与文档校验 | document standards + docs scripts | durable 文档通过结构门禁 |
| M5 | active | 建立公开文档双语切换与验收 | i18n rules + i18n validator | 公开文档可在中英文之间稳定切换 |
| M6 | next | 提升自动文档重组的叙事质量 | previous milestones | 整改后的手工清理更少 |

## 里程碑流转

```mermaid
flowchart LR
    M1["M1 控制面"] --> M2["M2 收敛式整改"]
    M2 --> M3["M3 进展 + 交接"]
    M3 --> M4["M4 文档标准"]
    M4 --> M5["M5 公开文档双语"]
    M5 --> M6["M6 更深文档重构"]
```

## 风险与依赖

- 文档同步脚本更擅长快速补齐结构，不一定能一次重写出最好的叙事质量
- 公开文档双语质量仍然依赖内容生成，不仅是文件对和切换链接
- 如果未来要支持精确 context 门禁，仍然需要运行时暴露对应指标
