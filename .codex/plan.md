# Plan

## Current Phase

`embedded architect-assistant redesign`

## Current Execution Line

- Objective: 把“长任务执行线 + 可见子任务板 + plan 映射”真正落到 `project-assistant` 的脚手架、门禁和恢复输出里
- Plan Link: redefine the operating model
- Runway: 完成执行线脚手架、任务板门禁、progress/handoff 输出修正，以及对应文档语义收口
- Progress: 8 / 8 tasks complete
- Stop Conditions:
  - 脚手架默认产出执行线和任务板
  - 门禁要求执行线、任务板、Plan Link 和任务 id
  - `progress` / `handoff` 能直接显示 done/total 与任务列表
- Validation:
  - `validate_gate_set.py --profile deep` returns `ok: True`
  - `progress_snapshot.py` 与 `context_handoff.py` 能输出当前执行线和可见子任务板

## Execution Tasks

- [x] EL-1 把默认自动工作模型写入 `SKILL.md`
- [x] EL-2 把长任务执行线语义写入 `governance.md`、`usage.md` 和 README
- [x] EL-3 给开发日志写入本轮关于内嵌式架构师助手的结论
- [x] EL-4 让脚手架默认生成 `Current Execution Line` 与 `Execution Tasks`
- [x] EL-5 让控制面门禁强制要求执行线、子任务列表、检查点和停止条件
- [x] EL-6 让 `progress` 与 `handoff` 默认展示当前执行线和子任务列表
- [x] EL-7 修正执行线输出，避免重复前缀并显示干净的任务板项
- [x] EL-8 把“任务板映射 active slice / plan”写进模板和规则文档

## Slices

- Slice: redefine the operating model
  - Objective: 把 `project-assistant` 从“命令驱动 skill”重新定位成“默认内嵌的 AI 工程系统”
  - Dependencies: 当前 `SKILL.md`、`usage.md`、`governance.md`
  - Risks: 新定位只停留在文案层，没有进入默认执行语义
  - Validation: 规则文档明确区分业务裁决、人类干预窗口、默认自动职责
  - Exit Condition: skill 自己能清楚表达“用户给方向，系统默认推进”的工作模型

- Slice: embed architecture supervision by default
  - Objective: 把架构监督从手工命令升级为 `plan / execute / retrofit / closeout` 的默认内嵌能力
  - Dependencies: 架构模式定义、控制面更新策略、命令窗口保留策略
  - Risks: 监督逻辑过重，影响节奏；或者过轻，仍然放任局部修补
  - Validation: 明确同步轻审查、异步重审查、升级给用户的裁决点
  - Exit Condition: 架构监督默认自动运行，`项目助手 架构 xxx` 退化为人工覆盖入口

- Slice: embed development-log capture by default
  - Objective: 把开发日志从“可选记录动作”变成“出现持久推理链路时自动沉淀”
  - Dependencies: `write_development_log.py`、`validate_development_log.py`、devlog 触发规则
  - Risks: 写成流水账，或者触发条件太松导致噪声过多
  - Validation: 规则文档明确自动触发条件、跳过条件和人工补记入口
  - Exit Condition: `devlog` 成为默认自动能力，手工命令只保留为补记和强制记录窗口

- Slice: simplify the human surface
  - Objective: 让命令从主工作流降级成“观察/干预窗口”，只保留少量高价值入口
  - Dependencies: help menu、usage、README、handoff 规则
  - Risks: 命令太多依然让用户记不住；命令太少又无法人工覆盖
  - Validation: 能清楚给出默认自动行为 + 手工干预窗口的边界
  - Exit Condition: 常态下用户只需要提需求与业务方向，命令主要用于查看、纠偏和覆盖

- Slice: define the escalation and gate model
  - Objective: 明确哪些情况自动推进，哪些情况必须升级给用户裁决
  - Dependencies: control-surface rules、validation gates、release rules
  - Risks: 自动化越界，或者仍然频繁把技术判断抛回给用户
  - Validation: 形成明确的“自动推进 / 强制提醒 / 必须人工裁决”分层
  - Exit Condition: 项目助手的自主性边界可解释、可验证、可持续维护
