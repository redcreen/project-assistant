# 自我学习治理总览

[English](self-learning-governance-overview.md) | [中文](self-learning-governance-overview.zh-CN.md)

## 目的

这份文档把当前关于 `project-assistant` 自我学习能力的讨论收敛成一份可整体 review 的总览。

它回答 6 个问题：

1. 我们真正要解决的问题到底是什么
2. 这件事和 `growware` 之前的合约到底是不是同一件事
3. 当前项目里的“规则”已经分离到什么程度
4. 后续应该怎样继续分层、分离和治理
5. 学习结果到底应该沉淀成什么资产
6. 哪些资产可以带进新项目，去更好地引导 AI 做事

## 一句话结论

我们真正要做的，不是“让 assistant 偷偷变聪明”，而是：

`让 project-assistant 作为上游治理层，能从人类行为和自身错误中持续生成可审查的改进提案，并把被接受的提案沉淀成规则、judge、gate、template 和回归资产，在后续项目中继续约束和引导 AI 的动作。`

## 真正的问题定义

最开始暴露出来的表面问题是：

`别再让我重复纠正你。`

但这只是症状，不是最终目标。

这轮讨论后，真正的问题定义已经升级为：

`让 assistant 具备受治理的自我改进闭环，并且这条闭环不只服务当前项目，还要能把稳定经验晋升成新项目可复用的上游治理资产。`

## 非目标

下面这些都不是我们现在要做的东西：

- 让模型绕过 review 自动改自己
- 让原始聊天直接变成长期规则
- 把所有记忆问题一口气做成“大而全记忆系统”
- 把项目规则、个人偏好、运行时状态混在一起
- 让安装目录成为学习结果的主存储

## 和 Growware 合约的关系

这轮讨论不是凭空开始的。

`growware` 里已经有一套更成熟的 contract 体系，和这次问题直接相关的有这些文档：

- `shared-policy-contract`
- `policy-loading`
- `learning-writeback`
- `regression-assets`

## 和 Growware 一致的部分

当前讨论已经与 `growware` 达成一致的地方有：

| 主题 | `growware` 合约结论 | 当前 `project-assistant` 讨论结论 |
| --- | --- | --- |
| 规则归属 | 规则属于项目，不属于执行器 | 同意 |
| 文档与机器层 | 人类改文档，执行器读机器层 | 同意 |
| 运行时发明规则 | 规则不清楚时，执行器不能从聊天记忆临时发明规则 | 同意 |
| 学习写回 | 已解决工作应形成 `proposal`，不能 silent 激活 | 同意 |
| 可复用资产 | 问题关闭后要沉淀成 `rule / judge / regression asset / deferred-gap` 等资产 | 同意 |

## 和 Growware 不完全一样的地方

两者也有明确差异。

| 维度 | `growware` 更强调 | 当前 `project-assistant` 讨论更强调 |
| --- | --- | --- |
| 主体 | 项目 policy 如何成为机器 policy 并被执行 | 经验如何先从人类纠正和 AI 错误里被学习出来 |
| 作用域 | 项目级规则、项目级机器 policy、执行闭环 | 用户级 / workspace 级 / 项目级 / 跨项目级经验晋升 |
| 第一优先级 | 先把项目 policy source、machine layer、approval contract 做实 | 先把 learning proposal、review、promotion、rule library 分清楚 |
| 核心风险 | 执行器不能越权立法 | assistant 不能偷偷学会并改自己 |

一句话说：

`growware` 更像项目 policy 执行层合同；当前这轮讨论更像 project-assistant 的上游学习与晋升层设计。两者不是冲突，而是上下游关系。`

## 当前规则分离现状

现在这个仓库里的“规则”，其实已经被分成几层了，但还没有全部分离干净。

### 已经分离出来的层

| 层 | 当前落点 | 状态 |
| --- | --- | --- |
| 工具默认规则 | `SKILL.md`、[../../../agents/openai.yaml](../../../agents/openai.yaml) | 已存在 |
| repo durable 规则 | `.codex/*`、`docs/*`、`.codex/doc-governance.json` | 已存在 |
| 运行时状态 | `~/.codex/daemon/<repo-id>/`、VS Code `workspaceState` | 已存在 |

### 还没真正落地的层

| 层 | 当前状态 |
| --- | --- |
| 学习出来的规则库 | 设计已定，尚未正式实现 |
| 跨项目晋升后的全局 / domain 规则库 | 还停留在规划阶段 |
| project-local / user-global / domain-pack / global-promoted 的优先级体系 | 还未编码为正式契约 |

## 推荐的规则分层模型

为了避免以后继续混淆，后续建议固定为 5 层：

### 1. shipped-base

来源：

- `SKILL.md`
- `agents/openai.yaml`
- skill repo 里随版本发布的固定契约

特点：

- 跟版本走
- 可被升级覆盖
- 不应被学习系统直接改写

### 2. project-policy

来源：

- repo 内的 policy source、架构、roadmap、test-plan、`.codex/doc-governance.json` 等 durable 真相

特点：

- 归项目所有
- 应进入 Git
- 应可 review 和版本化

### 3. machine policy layer

来源：

- 从项目文档或 policy source 编译出来的机器可读层

特点：

- 执行器真正读取这一层
- 不应在运行时由 assistant 临时发明

### 4. learned registry

来源：

- 人类纠正
- 人类行为
- assistant 错误
- 失败 close-out
- 重复返工与审批

特点：

- 先是 candidate / proposal
- 经过 review 接受后才变成 stable
- 可以有 `project-local`、`workspace-local`、`user-global`、`domain-pack`、`global-promoted` 多个层次

### 5. runtime state

来源：

- daemon runtime
- VS Code host `workspaceState`
- 最近事件、最近文件、当前自动继续状态

特点：

- 不是规则真相
- 可以丢失、可以重建
- 不应承担长期规则存储

## 学习资产类型

为了防止“学到什么都叫规则”，建议只允许学习系统产出以下 6 类资产：

| 资产类型 | 主要含义 | 典型例子 |
| --- | --- | --- |
| `communication rule` | 回答和协作方式偏好 | 先给结果，再解释；先看代码再判断 |
| `workflow rule` | 做事顺序和推进流程 | 先目标 / 方案 / 架构 / roadmap / test-plan，再开发 |
| `judge` | 判断标准与判定逻辑 | 什么情况下算方向漂移；什么情况下必须升级给人 |
| `gate/checklist` | 执行前或收口前必须检查的门槛 | 改行为必须补验证；改 schema 必须补 migration |
| `template/playbook` | 可复用的项目起步或阶段模板 | 新项目默认生成哪些文档和默认流程 |
| `regression asset` | 用于未来防止重复犯错的资产 | test、fixture、replay、failure pattern |

## 学习信号来源

推荐把可学习信号限制在这 4 类：

1. `人类显式纠正`
2. `人类隐式行为`
3. `assistant 自身失败`
4. `长期结果`

### 1. 人类显式纠正

例如：

- “不要这样答”
- “先看代码再判断”
- “默认先给结果”

### 2. 人类隐式行为

例如：

- 总是跳过某类输出
- 总是补某一类遗漏信息
- 总是把某类回答打回重做

### 3. assistant 自身失败

例如：

- 测试失败
- validator 失败
- 方案反复回滚
- 同类问题多次出现

### 4. 长期结果

例如：

- 哪类流程总能更快收口
- 哪类做法总导致 drift、返工、误判

## 建议的学习闭环

推荐闭环如下：

`signal -> candidate/proposal -> human review -> accepted stable asset -> local/domain/global promotion -> periodic decay or supersede`

这个闭环有两个关键前提：

- proposal 不是 active rule
- promotion 一定要留下 provenance 和 decision trail

## project-assistant 第一阶段应该做什么

在所有可能的自我学习方向里，`project-assistant` 第一阶段不应试图全包。

最合理的是先做：

`reviewable correction learning`

也就是：

- 从当前 workspace 的本地 Codex session 抓显式纠正
- 形成 candidate rule
- 宿主和状态栏明确提示 review
- 用户接受后进入 stable rule library
- 下一轮 resume / new thread 读取这些 accepted rules

这只是入口，不是终局。

## 更大的目标：跨项目学习

真正高价值的能力，是下一层：

`让 project-assistant 能从多个项目里沉淀经验，再把成熟经验带入新项目，去约束 AI 动作。`

所以第一阶段之后，必须继续支持：

- `project-local` 学习
- `domain-pack` 晋升
- `global-promoted` 晋升

## 哪些经验只留在当前项目

这些内容通常不应轻易晋升：

- 明显依赖当前业务语义的规则
- 明显依赖当前 repo 结构的规则
- 某个项目的特定审批流程
- 某个项目独有 workaround
- 纯个人表达偏好

一句话判断：

`离开当前项目就不一定成立的，留在 project-local。`

## 哪些经验可以带进新项目

这些内容才值得晋升：

- 在多个项目里反复成立
- 不依赖具体业务
- 能稳定减少返工、误判、重复纠正
- 能写成清晰的 rule、judge、gate 或 playbook

最适合跨项目晋升的通常是：

- `workflow rule`
- `judge`
- `gate/checklist`
- `template/playbook`

## 推荐的晋升路径

### project-local

当前项目内被反复证明成立的规则。

### domain-pack

在同类项目里反复成立的规则包。

例如：

- SaaS 后台
- CLI 工具
- 前端交互应用
- AI agent 系统
- VS Code 扩展

### global-promoted

跨项目、跨 domain 仍然成立的高置信度规则。

## 建议的晋升门槛

### candidate -> accepted local

至少满足：

- 有明确证据
- 能写成稳定规则、judge 或 checklist
- 人类接受
- 不和当前项目 policy 冲突

### accepted local -> domain-pack

至少满足：

- 在 2 个以上同类项目中成立
- 被显式接受或保留多次
- 有清楚的收益证据
- 有明确适用边界

### domain-pack -> global-promoted

至少满足：

- 跨 domain 仍然成立
- 冲突率低
- 不依赖具体业务语义
- 经更严格人工 review

## 推荐的优先级栈

为了避免不同层相互打架，建议固定优先级：

`project policy > project-local accepted rules > domain-pack > user-global accepted rules > global-promoted > shipped-base > runtime hints`

其中：

- `project policy` 永远优先于学习规则
- `runtime hints` 永远不应覆盖 durable rule

## 重装和持久化问题

这轮讨论中已经明确：

`安装代码 != 学习数据`

### 不应放的地方

- skill 安装目录
- 扩展安装目录
- daemon runtime store

### 推荐放置

后续 learned registry 建议放在类似：

- `~/.codex/registry/project-assistant/workspaces/<workspace-id>/candidates.jsonl`
- `~/.codex/registry/project-assistant/workspaces/<workspace-id>/stable-rules.json`
- `~/.codex/registry/project-assistant/global/stable-rules.json`

### 导出到项目

只有在显式批准的情况下，才导出到 repo 里的机器 policy 层，例如：

- `.codex/policy-input/learning-rules.json`
- `.codex/policy-input/learning-rules.md`

## 这轮讨论后的收敛结果

到目前为止，可以把讨论结果收成下面这几句：

1. `project-assistant` 的自我学习目标，不是减少一次重复纠正，而是建立受治理的自我改进闭环。
2. 这条闭环的更大意义，不在 `project-assistant` 自己，而在于它能把经验带入新项目，去引导 AI 的动作。
3. `growware` 合约已经给出了项目 policy 的执行层合同；当前 `project-assistant` 需要补的是上游学习、proposal、promotion、rule library 和跨项目晋升层。
4. 规则必须明确分层，不能再把安装规则、项目规则、学习规则和运行时状态混在一起。
5. 第一阶段最值得先做的是 `reviewable correction learning`，但最终目标必须扩展到 `rule / judge / gate / template / regression asset` 的多资产学习体系。

## 推荐的下一步

如果要继续推进，而不是继续泛讨论，下一步最值得固定成正式规范的是：

1. 学习资产 schema
2. promotion / decay 规则
3. 各层规则优先级与冲突处理
4. project-local、domain-pack、global-promoted 的晋升门槛

## 相关文档

- [correction-driven-self-learning.zh-CN.md](correction-driven-self-learning.zh-CN.md)
- [project-origin-and-working-method.zh-CN.md](project-origin-and-working-method.zh-CN.md)
- [ptl-daemon-mvp.zh-CN.md](ptl-daemon-mvp.zh-CN.md)
- [host-resume-bridge.zh-CN.md](host-resume-bridge.zh-CN.md)
- [ai-coding-modes-comparison.zh-CN.md](ai-coding-modes-comparison.zh-CN.md)
- `growware` repo: `shared-policy-contract`
- `growware` repo: `policy-loading`
- `growware` repo: `learning-writeback`
- `growware` repo: `regression-assets`
