# 纠错驱动的自我学习

[English](correction-driven-self-learning.md) | [中文](correction-driven-self-learning.zh-CN.md)

## 目的

这份文档定义 `project-assistant` 后续自我学习能力的第一条正式主线：

`先解决用户在 Codex 里反复纠正同一类问题。`

它不试图一开始就做“全能学习系统”，而是先把下面这件事做成 durable 能力：

`把用户反复纠正 assistant 的内容，变成 reviewable 候选规则；由用户接受后再进入稳定规则库。`

## 先解决什么

第一阶段只解决这类问题：

- 用户在同一 workspace 或长期使用中，反复说同一种纠正
- 这些纠正已经不只是一次性偏好，而是可以沉淀成后续默认行为
- 用户希望这类改进不要继续停留在聊天里，而是能被插件明确提示、review、接受并持久生效

典型例子：

- “不要每次都先讲一大段空话”
- “先看代码再下判断”
- “优先给我结果，不要先给计划”
- “做规划时要把文档写进 repo，而不是只在对话里说”
- “默认先收口到 PTL / control-surface，而不是把它当成一次性 prompt”

## 当前代码基础已经具备什么

这件事不是从零开始。

当前仓库已经有 4 个关键基础：

| 基础 | 现在在哪里 | 说明 |
| --- | --- | --- |
| 宿主状态面 | [../../../integrations/vscode-host/extension.js](../../../integrations/vscode-host/extension.js) | 已有 Tree View、Status Bar、通知、workspaceState、最近事件、最近文件 |
| daemon 事件与状态 | [../../../scripts/daemon_runtime.py](../../../scripts/daemon_runtime.py) | 已有 runtime store、queue、events、status snapshot、repo 级 runtime id |
| Codex workspace 会话定位 | [../../../integrations/vscode-host/extension.js](../../../integrations/vscode-host/extension.js) | 宿主已能从本地 `~/.codex/sessions/**/*.jsonl` 找到当前 workspace 的最近会话 |
| durable 工作方法 | [project-origin-and-working-method.zh-CN.md](project-origin-and-working-method.zh-CN.md)、[ptl-daemon-mvp.zh-CN.md](ptl-daemon-mvp.zh-CN.md) | 这个 skill 已明确强调 durable truth、review、checkpoint、host/daemon 分层 |

也就是说，难点已经不是“能不能显示一个提示”，而是：

1. 候选规则怎么抽取
2. review 和接受契约怎么定义
3. 接受后的规则放在哪里才不会被重装覆盖

## 一句话边界

推荐边界是：

`自动发现候选；人工 review 接受；接受后进入规则库；下一轮再自动生效。`

不推荐的边界是：

`assistant 直接从原始聊天里偷偷改自己。`

## Phase 1 用户体验

第一阶段的目标体验应该非常具体：

| 场景 | 目标体验 |
| --- | --- |
| 用户多次纠正同一类问题 | 系统自动聚合成一个候选规则 |
| 候选规则出现 | VS Code 宿主侧边栏出现 `Learning Review` 区块 |
| 候选规则待审 | Status Bar 出现单独的明确提示，例如 `PA Learn: 2 pending` |
| 点击状态栏提示 | 打开 review 面板，而不是跳进模糊的日志输出 |
| 用户接受 | 规则进入稳定规则库，并在后续 resume / new thread 中生效 |
| 用户拒绝或暂缓 | 候选被标记为 rejected / snoozed，不再反复骚扰 |

## 推荐的数据流

### 1. 采集

第一阶段优先使用当前 workspace 的本地 Codex 会话记录作为输入源。

输入优先级：

1. 当前 workspace 的本地 session log
2. 宿主生成的 continue / handoff / progress artifact
3. 未来再扩到 repo docs、devlog、外部 source

### 2. 纠正信号识别

第一阶段不要做过度“智能”的通用学习。

优先只识别显式纠正信号，例如：

- `不要 / 别 / 以后不要`
- `应该 / 要 / 需要`
- `先 ... 再 ...`
- `默认`
- `不要每次`
- `还是按 ...`

目标不是一次命中所有表达，而是先把高 precision 的“明确纠正”抓出来。

### 3. 候选规则归一化

抽取后不要直接把原句当规则。

需要先生成一条 reviewable 候选：

- 原始证据
- 归一化规则文本
- 作用范围
- 建议落点
- 是否已重复出现

### 4. review

宿主应把候选规则作为单独面板显示，而不是塞进普通 Recent Events。

每个候选至少要支持：

- `Accept as workspace rule`
- `Accept as user-global rule`
- `Reject`
- `Snooze`
- `Open evidence`

### 5. promotion

只有用户点击接受，候选才 promotion 成 stable rule。

promotion 后：

- 写入稳定规则库
- 记录 decision trail
- daemon / host 在下一轮 resume 时加载
- 必要时生成 policy-input artifact 给 Codex / PTL 消费

## 候选规则建议的数据结构

第一阶段建议至少包含这些字段：

| 字段 | 作用 |
| --- | --- |
| `id` | 候选规则唯一标识 |
| `workspace_id` | 绑定当前 workspace |
| `scope` | `workspace` 或 `user-global` |
| `source_session_id` | 来源会话 |
| `source_turn_ids` | 证据 turn |
| `evidence_snippet` | 用户纠正的短摘录 |
| `normalized_rule` | 归一化后的规则文本 |
| `rule_kind` | `communication / workflow / validation / architecture / docs / escalation` |
| `proposed_target` | 准备作用到哪里，例如 prompt supplement / checklist / review policy |
| `occurrence_count` | 出现次数 |
| `status` | `pending-review / accepted / rejected / snoozed / decayed` |
| `created_at` | 首次发现时间 |
| `last_seen_at` | 最近一次再次出现时间 |
| `decision` | 接受 / 拒绝 / 暂缓的决策记录 |

## 规则真正应该作用到哪里

接受后的规则，不应直接改这些东西：

- `SKILL.md`
- [../../../agents/openai.yaml](../../../agents/openai.yaml)
- 安装目录下的 prompt / code 文件

Phase 1 推荐的作用方式是：

`把 stable rules 当作额外 policy-input artifact，在下一轮 resume / new thread / host-generated prompt 时注入。`

这样做有 3 个好处：

1. 不需要在安装目录里打补丁
2. 不会因为重装 skill 把规则冲掉
3. review / export / decay 都更容易治理

## 插件与状态栏怎么改

当前宿主已经有一个总状态栏项和 Tree View。

第一阶段建议新增这些 UI：

### Tree View

新增 `Learning Review` 分组，至少包含：

- pending candidates 数量
- 每条候选的摘要
- 点击后打开 review 面板
- accept / reject / snooze 动作

### Status Bar

新增一个独立状态栏项，而不是把学习提示混进现有 `PA: running` 总状态里。

推荐文案：

- `PA Learn: 2 pending`
- `PA Learn: review needed`
- `PA Learn: clean`

点击动作：

- 打开 learning review 视图
- 如果只有 1 条候选，可直接定位到这条候选

### Notifications

只在这些时机提示：

- 第一次出现新的 pending candidate
- 待 review 数量从 `0 -> N`
- 某条候选被成功 promotion

不要在每次 polling 都重复弹通知。

## daemon 需要补什么

第一阶段不需要 daemon 直接做复杂学习推理，但需要补最小事件契约：

| 事件 | 说明 |
| --- | --- |
| `learning_candidate_detected` | 发现新的候选规则 |
| `learning_review_needed` | 当前有待 review 的候选 |
| `learning_rule_promoted` | 候选被接受并进入规则库 |
| `learning_rule_rejected` | 候选被拒绝 |

同时扩展 status snapshot：

| 字段 | 说明 |
| --- | --- |
| `learningSummary.pendingReview` | 待 review 数量 |
| `learningSummary.acceptedRules` | 已接受规则数量 |
| `learningSummary.lastCandidateAt` | 最近发现候选时间 |
| `learningSummary.lastPromotedAt` | 最近 promotion 时间 |

## 规则库存放在哪里

这是这条能力成败的关键。

### 不应该放的地方

- 不应放在 `~/.codex/skills/project-assistant/`
- 不应放在扩展安装目录
- 不应只放在 daemon runtime store

原因：

- skill 重装可能覆盖安装目录
- 扩展更新也可能覆盖扩展代码目录
- daemon runtime store 是运行时状态，不是 durable truth

### 推荐放置

第一阶段推荐使用独立的宿主中立 registry root：

- `~/.codex/registry/project-assistant/workspaces/<workspace-id>/candidates.jsonl`
- `~/.codex/registry/project-assistant/workspaces/<workspace-id>/stable-rules.json`
- `~/.codex/registry/project-assistant/global/stable-rules.json`

这样定义后：

- 重装 `project-assistant` skill 不会覆盖规则
- 更新 VS Code 扩展也不会覆盖规则
- daemon 可以继续把 `~/.codex/daemon/<repo-id>/` 只当 runtime store
- 后续如果需要让别的 consumer 读取，也有共享 canonical root

### repo 内是否需要落文件

默认不自动把 local learned rules 写进 repo。

只在用户显式选择“导出为 repo 规则”时，才建议写入类似：

- `.codex/policy-input/learning-rules.json`
- `.codex/policy-input/learning-rules.md`

这一步是“导出”，不是默认存储。

## 这就回答了重装覆盖问题

结论很明确：

`如果 learned rules 存在安装目录，重装很可能覆盖；如果 learned rules 存在独立 registry root，重装不应覆盖。`

因此这条能力必须把“安装代码”和“学习数据”分离。

## PTL 在这里的角色

把这条能力放到 PTL 角色里是合理的，但边界要收紧。

PTL 应该负责：

- 发现值得学习的候选
- 把候选写成 reviewable artifact
- 在后续执行中消费 stable rules

PTL 不应该负责：

- 绕过用户 review 直接改规则
- 直接改自身安装 prompt
- 把一次情绪化纠正当成长期规则

## 推荐分阶段落地

### Phase 1

`reviewable correction learning`

目标：

- 从本地 Codex session 中抓显式纠正
- 形成 pending candidates
- 在宿主侧边栏和状态栏明确提示
- 支持 accept / reject / snooze
- 把 accepted rules 写入独立规则库

### Phase 2

`stable rule consumption`

目标：

- 在 continue / handoff / auto-resume / new thread 中加载 stable rules
- 先影响 prompt supplement、review checklist、plan preflight
- 不直接 patch skill 代码

### Phase 3

`governance and decay`

目标：

- conflict / superseded / decay 规则
- workspace rule 与 global rule 的冲突处理
- 显式导出到 repo policy-input artifacts

## 当前建议

如果只选一条最小但高价值的路，应该是：

`先做 reviewable correction learning，而不是一上来做大而全的 memory system。`

原因：

- 用户价值最直接
- 证据来源最清楚
- 宿主和状态栏已经有承载面
- 规则持久化边界也最容易先定义清楚

## 相关文档

- [project-origin-and-working-method.zh-CN.md](project-origin-and-working-method.zh-CN.md)
- [ptl-daemon-mvp.zh-CN.md](ptl-daemon-mvp.zh-CN.md)
- [host-resume-bridge.zh-CN.md](host-resume-bridge.zh-CN.md)
- [orchestration-model.zh-CN.md](orchestration-model.zh-CN.md)
- [ai-coding-modes-comparison.zh-CN.md](ai-coding-modes-comparison.zh-CN.md)
