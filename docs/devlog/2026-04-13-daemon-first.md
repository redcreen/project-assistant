# 把异步执行专项切到 daemon-first 快升级版

- 日期：2026-04-13
- 状态：resolved

## 问题

用户明确表示：如果 skill 继续这么慢，使用意愿会直接降到想卸载。此前的方案仍偏保守，主要停留在 async-by-default 的执行模型讨论，但这不足以满足“尽快升级一版、先把写代码速度提起来”的目标。

## 思考

问题的严重性已经从“某些流程慢”升级成产品留存风险。继续只讨论后台优先规则，虽然方向没错，但无法给出足够明确的近期交付目标。因此需要把目标架构直接切到 daemon-first，同时用一个 write-safe 的快升级版约束首版范围：先把 validator、snapshot、docs sync、control-surface refresh 等支撑任务移出主写入线，先恢复编码速度，再在 daemon 基线上逐项回归旧功能。

## 解决方案

将专项方向正式改为 `daemon-first PTL scheduler`，并新增 `PTL daemon MVP` 设计文档。控制面、roadmap、development plan 统一改成“先发快升级版，再逐项验证旧功能”的节奏；首版明确不做后台自动写业务代码，也不做多主写入调度。

## 验证

新增 `docs/reference/project-assistant/ptl-daemon-mvp.md` 与中文配对文件；更新 `async-execution-and-latency-governance`、`.codex/status.md`、`.codex/plan.md`、roadmap、development plan，使它们一致表达 daemon-first 与 fast-upgrade 策略。

## 后续

- 下一步先收口 daemon fast upgrade 的精确范围、runtime store、首批后台任务名单和旧功能回归顺序，然后进入实现。

## 相关文件

- 无
