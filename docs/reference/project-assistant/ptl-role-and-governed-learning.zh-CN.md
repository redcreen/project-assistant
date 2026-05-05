# PTL 角色与受治理自我学习职责

[English](ptl-role-and-governed-learning.md) | [中文](ptl-role-and-governed-learning.zh-CN.md)

## 目的

这份文档把当前关于 PTL 的讨论收敛成一个可执行的角色定义。

它回答 5 个问题：

1. PTL 到底是干什么的
2. PTL 如何稳定生效，而不是只停留在聊天提醒里
3. PTL 的规则包是否应该自动生成
4. 人类在这套机制里到底需要做什么
5. `style engine` 和 `openclaw-skills` 这两类项目应该怎样应用同一套 PTL 机制

## 一句话定义

PTL 是项目里的技术负责人控制层。

它不是另一个聊天人格，也不是后台自动写代码的执行器，而是负责在 AI worker 行动前后做技术方向、边界、规则、复用性和升级判断的项目治理层。

更具体地说：

`PTL 负责约束 AI 不要乱干活，并把反复出现的问题沉淀成可审查、可生效、可迁移的项目规则。`

## 为什么需要 PTL

Codex 或任何 AI worker 在真实项目中常见的问题不是“不会写代码”，而是：

- 看到局部问题就直接修局部，忽略根因
- 跳过最小可行性探针，在没有证明路线能走通前就投入大量实现
- 为了让当前结果看起来更好，走不可复用 workaround
- 把一次实验成功误写成项目结论
- 忘记项目原有文档、边界和发布规则
- worker 停下、失败、超时后，项目状态丢失
- 人类反复纠正同一类问题，但纠正只留在聊天里

PTL 的价值就是把这些风险变成可观察、可治理、可执行的控制层。

## PTL 不是什么

PTL 不应该承担下面这些角色：

| 不是 | 原因 |
| --- | --- |
| 不是产品 owner | 业务方向、成本、外部承诺仍然必须由人类裁决 |
| 不是组织级 CTO | 它只对当前项目或当前 workspace 生效 |
| 不是后台自动写业务代码的 worker | 首版 PTL 应保护前台主写入线，不抢业务代码写入权 |
| 不是静默自我修改器 | 学习结果必须先生成候选，再经 review 后生效 |
| 不是全仓实时扫描器 | 稳定性和性能要求它按事件和 checkpoint 工作 |
| 不是硬编码项目特判集合 | 项目差异应来自 policy pack，而不是写死在 engine 里 |

## 核心职责

### 1. 定方向

PTL 要判断当前工作是否还在项目主线上。

它要回答：

- 当前应该继续哪个 active slice
- 当前工作是主线、实验、支撑 backlog，还是临时 fallback
- 当前计划是否已经和 roadmap、development plan、status 漂移
- 是否需要重排主线或插入治理专项

### 2. 定边界

PTL 要决定哪些事可以自动继续，哪些事必须提醒或升级。

典型边界包括：

- 业务方向变化
- 兼容性承诺变化
- 外部系统写入
- 成本或时间边界变化
- 发布、安装、用户可见行为变化
- 数据权威来源变化

### 3. 先验证可行性

PTL 必须在允许长实现线之前，先证明选定路线至少可能走通。

当任务依赖不确定的外部表面、宿主能力、API、binary、插件机制、协议或未文档化行为时，PTL 应要求最小有用可行性探针。

它必须回答：

- 哪个关键假设必须为真
- 哪条命令、fixture、源码检查或 smoke 能证明它
- 什么结果代表路线不可行或成本过高
- 写生产代码或大面积文档前是否有更便宜路线
- 是否应停止、缩小范围或切换层级后再实现

### 4. 防 workaround

PTL 要识别“当前能跑”和“长期可维护”之间的差异。

它要防止：

- 单图调参被写成通用方法
- prompt / mask / seed / 临时路径变成隐性依赖
- adapter 里重新实现业务逻辑
- smoke test 打到了错误入口，却被当成真实验证
- 文档写了规则，但执行路径没有 gate

### 5. 管规则和 gate

PTL 要把项目文档、模块边界、测试和人类纠正编译成机器可执行的 policy。

规则不应该靠 worker 每次临时想起，而应该进入：

- project policy
- module policy
- domain policy pack
- learned registry
- preflight gate
- checkpoint review

### 6. 管接续

PTL 要让项目在 worker 停下后还能继续。

它需要维护：

- 当前 active slice
- execution line
- task board
- architecture signal
- escalation gate
- next checkpoint
- handoff / resume truth

### 7. 管学习

PTL 要从人类行为、AI 错误和项目结果里发现可复用经验。

但学习闭环必须受治理：

`signal -> candidate -> review -> accepted rule -> policy injection -> observation -> promotion or decay`

PTL 可以自动发现和归纳，但不能静默立法。

## 工作层级

为了稳定生效且不影响性能，PTL 应分成 4 层工作。

| 层级 | 职责 | 性能策略 | 是否阻塞 |
| --- | --- | --- | --- |
| L0 intent router | 判断任务类型、模块、风险域和要加载的 policy pack | 只读小型索引和路径规则 | 可同步，目标 0-3 秒 |
| L1 preflight gate | 根据 policy 判断 `allow / warn / require-review / block` | 确定性规则优先，不默认调用大模型 | 只在硬风险上阻塞 |
| L2 checkpoint PTL | worker 停下、验证失败、出图完成、发布前做复核 | daemon 后台运行，写回状态和事件 | 默认不阻塞 |
| L3 learning reviewer | 分析重复纠正、失败模式和可推广经验 | 异步生成 proposal | 不阻塞 |

这套分层的关键是：

- 轻判断同步跑
- 重分析后台跑
- 高风险才硬拦
- 学习只生成候选，接受后才生效

## 任务生命周期

### 任务进入

PTL 先生成一张短的 `PTL Card`：

| 字段 | 含义 |
| --- | --- |
| `intent` | 当前任务类型，例如 image generation、plugin release、order adapter |
| `module` | 受影响模块，例如 `style engine`、`health`、`order` |
| `risk` | `low / medium / high` |
| `feasibility_probe` | 对不确定宿主、API、协议、插件、binary 或未文档化行为的最小证明 |
| `policy_packs` | 本轮要加载的规则包 |
| `required_artifacts` | 本轮必须出现的产物 |
| `decision` | `allow / warn / require-review / block` |

### 执行前

PTL 做 preflight：

- 读取当前 `.codex/*` 控制面
- 读取 project / module policy
- 判断改动路径和任务意图
- 识别不确定假设，并先运行最小可行性探针
- 检查必需产物是否存在
- 如果基础探针失败，停止或重排执行线
- 给 worker 一个短 brief

### worker 执行中

PTL 不应持续打断 worker。

它只监听：

- 文件路径触发
- 测试结果变化
- gate 失败
- worker 停下
- 用户纠正
- 关键 artifact 生成

### checkpoint 后

PTL 统一复核：

- 结果是否满足本轮目标
- 大面积实现前，可行性假设是否已经被证明
- 是否用了正确层级
- 是否引入 workaround
- 是否需要更新 plan / status / devlog
- 是否出现学习候选
- 是否要继续、重排、提醒或升级

## 规则包如何生成

规则包应该主要由 PTL 自动生成候选，人类负责裁决和校准。

### 规则来源

| 来源 | PTL 自动能力 | 人类参与 |
| --- | --- | --- |
| 项目文档明确规则 | 自动抽取为 seeded project policy | 第一次启用前建议确认 |
| 代码里的测试和 smoke | 自动识别为 gate evidence | 通常不需要逐条确认 |
| 人类反复纠正 | 自动聚合成 learning proposal | 需要确认 |
| AI 反复失败或 workaround | 自动归纳失败模式 | 需要确认是否升级 |
| 业务方向、外部写入、成本边界 | 只能提出建议 | 必须确认 |

### 规则状态

| 状态 | 含义 |
| --- | --- |
| `candidate` | PTL 自动发现，还没有进入执行 |
| `observe` | 只记录命中，不提醒或阻塞 |
| `warn` | 提醒风险，但允许继续 |
| `require-review` | 需要人类看过再继续 |
| `block` | 阻止进入主线、发布或外部写入 |
| `accepted` | 人类已接受，进入稳定规则库 |
| `rejected` | 人类拒绝，后续不应反复提示 |
| `decayed` | 长期不再命中或已被新规则替代 |

### 规则作用域

| 作用域 | 适用场景 |
| --- | --- |
| `project-local` | 只在当前项目成立 |
| `module-local` | 只在当前模块成立，例如 `order` 或 `health` |
| `domain-pack` | 同类项目可复用，例如 image generation、plugin runtime、order system |
| `user-global` | 用户长期协作偏好 |
| `global-promoted` | 跨项目高置信度通用规则 |

## 人类需要做什么

人类不应该负责手写大批规则。

人类主要做 4 类决策：

| 人类职责 | 具体内容 |
| --- | --- |
| 确认方向 | 项目目标、业务边界、成本和外部承诺 |
| 批准规则 | PTL 提出的规则是否成立，作用域在哪里 |
| 升级 block | 哪些 warning 应该变成硬阻塞 |
| 处理冲突 | 项目规则、个人偏好、domain pack 之间冲突时怎么取舍 |

人类不应该被要求：

- 从零整理规则包
- 每次提醒 PTL 读文档
- 手工判断所有低风险路径
- 重复纠正同一类 AI 行为

## 稳定生效机制

PTL 要稳定生效，必须同时落到 4 个位置。

| 位置 | 要求 |
| --- | --- |
| 入口 | `continue / execute / release / script / host action` 前触发 L0/L1 |
| 规则 | 项目规则编译成机器可读 policy，不靠聊天记忆 |
| 状态 | 状态栏、Tree View、`.codex/status.md` 显示当前 signal 和 pending review |
| 验证 | gate 命中、阻塞、放行和学习候选都要有 evidence |

如果只有文档，没有入口，PTL 不会生效。

如果只有入口，没有规则，PTL 会变成空壳。

如果只有规则，没有状态，用户无法信任。

如果只有状态，没有验证，PTL 无法稳定改进。

## 性能原则

PTL 不能影响主编码性能。

首版应遵守：

| 原则 | 说明 |
| --- | --- |
| 小输入 | 只读 intent、changed paths、policy hash、必要 artifact 列表 |
| 小输出 | 只输出 decision、reason、required action |
| 事件驱动 | 只在任务入口、checkpoint、验证变化、用户纠正时运行 |
| 缓存优先 | policy pack 编译结果有 hash，未变更不重复分析 |
| 后台分析 | 深度 review、学习、跨项目晋升都进 daemon 后台 |
| 硬阻塞稀缺 | 只有高风险和已确认 block 规则才阻塞 |

## 案例一：Style Engine

`style engine` 的 PTL 重点不是插件发布，而是防止出图路线退回不可复用 workaround。

### 应加载的规则包

- `project-local: style-engine`
- `domain-pack: image-generation`
- `module-local: product-restyle-lab`
- `learned-registry: image-generation corrections`

### 典型 gate

| 场景 | PTL 行为 |
| --- | --- |
| 主线出图验证缺 `product_surface_spec` | block |
| 缺 `method_contract_audit` 或 `mask_refinement_audit` | block 或 require-review |
| 使用历史 mask / seed / denoise 作为选择策略 | block，前提是规则已被接受 |
| 手工 prompt、临时参数、fallback 出图 | warn，标记为 `not reusable` |
| 单图效果变好但不能迁移到新白模 | warn，生成学习候选 |
| 文档已禁止硬编码但代码继续绕过 | require-review，并建议升级规则 |

### 关键判断

Style Engine 的 PTL 不能问“这张图是否好看”作为唯一标准。

它必须问：

- 这次结果是实验，还是主线验证
- 控制条件能否追溯到结构化 contract
- 结果是否能迁移到下一张白模
- 是否把历史成功参数伪装成通用能力
- 是否需要把反复纠正升级成 project policy

## 案例二：OpenClaw Skills

`openclaw-skills` 的 PTL 重点是多 skill、plugin、runtime、adapter 和 release 边界。

### 应加载的规则包

- `project-local: openclaw-skills`
- `module-local: health`
- `module-local: order`
- `domain-pack: plugin-runtime`
- `domain-pack: local-first-data`
- `release-pack: public-skill-release`

### Health 模块 gate

| 场景 | PTL 行为 |
| --- | --- |
| OCR / sidecar extraction 被当成权威事实 | block |
| 健康输入绕过统一 intake | block |
| 用错误 smoke 路径代替 gateway `before_dispatch` 验证 | block 或 require-review |
| 真实 live turn 与 smoke 结果矛盾 | reopen module |

### Order 模块 gate

| 场景 | PTL 行为 |
| --- | --- |
| adapter 重新实现订单业务逻辑 | block |
| 绕过 `order_runtime_api.py` 直接调用底层脚本 | block |
| ERP / 仓库真实写入早于 dry-run contract | block |
| 把订单业务真相搬到 OpenClaw / MCP / Hermes / JuShuiTan | require-review 或 block |

### Workspace gate

| 场景 | PTL 行为 |
| --- | --- |
| root docs 重新承载某个子项目业务计划 | warn 或 require-review |
| `health` 和 `order` 模块边界混写 | require-review |
| release 前双语、安装、smoke、devlog 缺口 | block release |

## 通用机制和项目规则的关系

PTL 的 engine 必须通用。

项目差异必须放在 policy pack 里。

正确形态：

```text
PTL gate engine
+ project policy
+ module policy
+ domain pack
+ learned registry
+ runtime state
```

错误形态：

```text
if repo == "style engine" then ...
if repo == "openclaw-skills" then ...
```

前者可迁移、可 review、可学习。

后者只是硬编码，会把 PTL 变成越来越重的项目特判集合。

## 接受标准

一套 PTL 能力只有满足下面条件，才算真正生效：

1. 新项目能自动生成初始 project policy candidate
2. 低风险规则能自动进入 observe / warn
3. 高风险 block 规则必须有人类接受记录
4. 状态栏或宿主面板能显示当前 PTL signal
5. 点击 signal 能看到具体命中规则和证据
6. worker 执行前能收到短 PTL Card
7. 不确定的宿主、API、协议、插件、binary 或未文档化路线在实现前有记录过的可行性探针
8. worker checkpoint 后能触发复核
9. 同类纠正重复出现后能生成学习候选
10. 重装 skill 不会覆盖已接受规则
11. 新项目能复用 domain-pack 和 global-promoted 经验

## 最小落地顺序

第一阶段不应直接追求全自动学习。

推荐顺序是：

1. 实现通用 PTL gate engine 的 policy 输入格式
2. 从现有项目文档生成 seeded project policy candidate
3. 在宿主里显示 PTL signal 和 pending review
4. 让低风险规则先以 observe / warn 模式运行
5. 对高风险规则提供 accept / reject / snooze
6. 接受后写入 learned registry 或 project policy
7. 下一轮 resume / new thread 注入 accepted rules
8. 后台 daemon 再做重复纠正、失败模式和跨项目晋升

## 当前实现状态

这份职责文档对应的最小闭环已经落地：

| 能力 | 状态 | 落点 |
| --- | --- | --- |
| 通用 PTL gate policy 输入格式 | 已完成 | `scripts/ptl_gate.py`、`.codex/ptl-policy/project-policy.json` |
| seeded project policy candidate | 已完成 | 根据控制面、项目文档和 domain pack 自动生成 |
| 宿主显示 PTL signal | 已完成 | VS Code host Status Bar / Tree View + `preflight.json` |
| pending learning review | 已完成 | `.codex/ptl-policy/learning-review.json` + `scripts/ptl_learning.py panel` |
| 人类确认 task 进入 loop | 已完成 | pending review 会同步 `PTL-LEARNING-REVIEW` / `human-decision` task；支持 `全部接受` 或 `接受 1/2，3 稍后` 这类局部确认，未确认完继续等待，确认结束后自动关闭并继续 runner |
| 人类提示格式 | 已完成 | 需要确认时输出 `# 需要你确认`，只给最短回复格式和编号列表，避免长解释淹没动作 |
| observe / warn 低风险运行 | 已完成 | PTL policy 的 `severity / decision` |
| accept / reject / snooze | 已完成 | `scripts/ptl_learning.py accept/reject/snooze` + host 命令 |
| accepted rules 持久化 | 已完成 | `~/.codex/project-assistant/learned-registry.json`，不在 skill 安装目录内，重装不覆盖 |
| 下一轮注入 accepted rules | 已完成 | `ptl_gate.py preflight` 会把 learned registry 合成 `learned.*` 规则 |
| 反复纠正触发候选 | 已完成 | Codex App hook / preflight 事件驱动 scan message ingress |
| 语义归纳候选 | 已完成 | `ptl_learning.py` 会把重复纠错消息按语义概念对聚合成 candidate，例如“人类确认 + 明确回复格式”“人类确认 + loop 连续性”；候选仍需 human review 后才会生效 |
| 可行性优先职责 | 已完成 | core contract + PTL learning pattern + accepted rule 注入 |

当前实现是受治理 baseline：先用明确 pattern 和轻量语义概念对把反复纠正聚合成候选，再让人类 review 后生效。跨项目自动晋升和规则衰减可以继续增强，但不再阻塞这个受治理学习闭环的可用性。

## 最终目标

PTL 的最终形态不是“更会说的 AI 角色”，而是：

`一个会自己发现风险、自己整理规则候选、自己试运行观察、自己提出升级建议，并在关键边界上请人类确认的项目技术负责人。`

人类负责方向和裁决。

PTL 负责发现、可行性验证、归纳、执行和接续。

worker 负责具体实现。

这三者分开，项目才能在 AI 长期参与下稳定推进。
