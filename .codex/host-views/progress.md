# 项目进展

## 一眼总览
| 问题 | 当前答案 |
| --- | --- |
| 项目 | `Project Assistant` |
| 当前判断 | 核心能力已完成；当前在做维护者体验与自动触发增强。 |
| 当前阶段 | post-M21 daemon-host baseline active |
| 当前工作域 | 运行时边界增强 |
| 当前切片 | stabilize-daemon-host-baseline-for-dogfooding |
| 当前执行进度 | `2 / 3` |
| 架构信号 | `绿色` |
| 直接价值 | 让下一次回来看项目时更容易接手。 |
| 当前主要风险 | 当前无主要风险。 |

## 当前定位
| 维度 | 当前状态 | 说明 | 入口 |
| --- | --- | --- | --- |
| 主线状态 | 核心能力已完成；当前在做维护者体验与自动触发增强。 | 当前主要在补增强与边界收口 | [路线图](/Users/redcreen/.codex/skills/project-assistant/docs/roadmap.zh-CN.md) |
| 当前阶段 | post-M21 daemon-host baseline active | 当前主要在补增强与边界收口 | [路线图 / 当前阶段](/Users/redcreen/.codex/skills/project-assistant/docs/roadmap.zh-CN.md:13) |
| 当前工作域 | 运行时边界增强 | 当前这轮主要面向维护者 / 值班者的使用体验与验证链路 | 暂无 |
| 当前切片 | stabilize-daemon-host-baseline-for-dogfooding | 原始切片名：`stabilize-daemon-host-baseline-for-dogfooding` | [当前切片对应位置](/Users/redcreen/.codex/skills/project-assistant/docs/roadmap.zh-CN.md:17) |
| 当前执行线 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins | 当前这轮正在推进，下面的任务板就是本轮收口内容 | [状态](/Users/redcreen/.codex/skills/project-assistant/.codex/status.md) |

## 当前这轮到底在做什么
| 当前工作 | 类型 | 对维护者的直接价值 | 当前状态 | 对应任务 |
| --- | --- | --- | --- | --- |
| harden daemon runtime edges exposed by concurrent startup, shutdown, or status polling in real workspaces | 主线 | 让当前切片更容易被维护者看懂并继续推进。 | 已完成 | `EL-1` |
| keep README / architecture / usage / test plan / entry routing aligned with daemon-host as the new default fast path | 主线 | 让方向偏掉时更早暴露，而不是修一个冒一个。 | 已完成 | `EL-2` |
| collect broader dogfooding evidence before opening the next host surface or any M15 discussion | 主线 | 让当前切片更容易被维护者看懂并继续推进。 | 待完成 | `EL-3` |

## 架构监督
| 项目 | 当前值 |
| --- | --- |
| 信号 | `绿色` |
| 根因假设 | the main latency pain was orchestration shape, not raw script runtime; the new baseline removes most support work from the foreground write lane by moving queueable work behind a local daemon and host shell. |
| 正确落层 | keep the runtime contract, host shell, queue visibility, and regression coverage aligned; do not reopen chat-box injection or multi-executor scope prematurely. |
| 信号依据 | 当前没有 blocker 或升级信号迫使做更高层裁决 |
| 自动触发 | 当前没有自动触发 |
| 升级 Gate | `自动继续` |
| 升级原因 | 当前执行可以沿既有方向继续，不需要用户层面的额外取舍。 |

## 战略视角
| 维度 | 当前值 |
| --- | --- |
| 当前战略方向 | stabilize-daemon-host-baseline-for-dogfooding |
| 当前状态 | `活跃` |
| 为什么现在做 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins |
| 系统可自动提出 | roadmap 重排建议；治理 / 架构专项插入建议；... |
| 必须人类审批 | 业务方向变化；兼容性承诺；... |
| 下一战略检查 | 在 daemon-host baseline 的 dogfooding 过程中继续要求战略判断引用 durable repo 证据，而不是只凭聊天感受。；当 adoption 里仍出现 runtime / host / operator docs 摩擦时，先区分是 repo 层问题、宿主桥接问题还是 baseline 包装问题。；... |

## 程序编排视角
| 维度 | 当前值 |
| --- | --- |
| 当前程序方向 | stabilize-daemon-host-baseline-for-dogfooding |
| 当前状态 | `活跃` |
| 为什么现在做 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins |
| 活跃工作流 | daemon-host baseline stabilization；control truth and gates；... |
| 当前编排序列 | keep the new runtime / host / continue baseline stable while dogfooding begins；keep supervision surfaces, strategy, program board, plan, status, and handoff aligned；... |
| 当前执行器输入 | supervisor；delivery worker；... |
| Supporting Backlog | M8 locale-aware internal output；M9 slimmer continue snapshot；... |
| 下一程序检查 | 在更多本地 workspace 上继续 dogfood daemon-host baseline，并记录 runtime / host 摩擦。；继续确认 README / architecture / usage / queue / daemon 输出和控制面真相保持同一套当前叙事。；... |

## 程序编排工作流
| 工作流 | 范围 | 状态 | 优先级 | 当前焦点 | 下一检查点 |
| --- | --- | --- | --- | --- | --- |
| daemon-host baseline stabilization | 把 daemon runtime、queue、VS Code host、continue bridge、legacy rollout、文档与门禁继续收成同一条默认快路径 | 活跃 | `P0` | 稳住 runtime contract、前门说明和 host 行为 | 更广泛 dogfooding 前保持 baseline 一致 |
| control truth and gates | 保持 `.codex` 真相、门禁和 release 保护一致 | 活跃 | `P1` | 保持 strategy / program board / delivery supervision / plan / status / handoff 一致 | 继续只允许一套 control truth |
| operator-facing docs and host UX | 让 README / architecture / usage / queue / daemon 输出对维护者和使用者都足够清楚 | 活跃 | `P1` | 让 daemon-host baseline 的第一屏和说明继续保持结构化、表格优先、可操作 | release 叙事与 operator docs 对齐 |
| supporting backlog routing | 管理 M8 / M9、future host surfaces 和 M15 evidence，不让它们无计划回流主线 | 活跃 | `P2` | 只有 dogfooding 证据充分时才提升优先级 | 在没有证据前继续保持 backlog |

## 长期交付视角
| 维度 | 当前值 |
| --- | --- |
| 当前长期交付方向 | post-M21 daemon-host baseline active |
| 当前状态 | `活跃` |
| 为什么现在做 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins |
| Checkpoint 节奏 | 对齐方向与输入；推进执行线；... |
| 自动继续边界 | 已批准方向内的实现与验证；黄色信号但可在既有方向内收口；... |
| 升级时机 | 开始新一轮长任务前；每轮验证之后；... |
| 执行器监督循环 | supervisor；delivery worker；... |
| Backlog 回流规则 | M8 locale-aware internal output；M9 slimmer continue snapshot；... |
| 下一长期交付检查 | 在更多本地 workspace 上继续 dogfood daemon-host baseline，并记录 runtime / host / operator docs 摩擦。；根据真实 adoption 证据决定 `M8 / M9` 是否继续保持在 supporting backlog。；... |

## 长期交付检查点
| 顺序 | 检查点 | 发生什么 | Owner | 什么时候 |
| --- | --- | --- | --- | --- |
| 1 | 对齐方向与输入 | 读取 strategy / program board / plan / status，确认当前工作流和 checkpoint 目标 | supervisor | 每轮开始前 |
| 2 | 推进执行线 | 执行当前切片，保持任务板、统一前门、验证入口和控制面一致 | delivery worker | 每轮主体 |
| 3 | 运行验证并刷新真相 | 运行 gate / tests，并刷新 status / progress / continue / handoff / entry-routing | delivery worker | 每轮验证后 |
| 4 | 决定继续 / 升级 / 暂停 | 根据信号、blocker 和升级边界决定下一轮动作 | supervisor | 每轮收口时 |
| 5 | 记录 dogfooding 摩擦 | 把 runtime / host / docs / adoption 的真实摩擦、supporting backlog 回流建议和下一里程碑候选沉淀到 `.codex/dogfooding-evidence.md` | supervisor + docs-and-release | 每个 adoption checkpoint |

## PTL 监督视角
| 维度 | 当前值 |
| --- | --- |
| 当前 PTL 方向 | post-M21 daemon-host baseline active |
| 当前状态 | `活跃` |
| 为什么现在做 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins |
| 监督触发 | 周期巡检；worker 停下；... |
| 常驻职责 | PTL；delivery worker；... |
| 继续 / 重排 / 升级矩阵 | 当前方向内、验证通过、无新 blocker；黄色信号但仍在既定方向内；... |
| 当前监督检查 | 监督输入完整；继续边界清楚；... |
| 下一 PTL 检查 | 在更多本地 workspace 上继续验证 PTL 监督判断会沿着 daemon-host baseline 推进，而不是退回同步串脚本路径。；继续观察 runtime / host / operator docs 是否还暴露需要回写到监督契约的摩擦。；... |

## Worker 接续视角
| 维度 | 当前值 |
| --- | --- |
| 当前 handoff 方向 | post-M21 daemon-host baseline active |
| 当前状态 | `活跃` |
| 为什么现在做 | keep the newly shipped daemon-host baseline stable and easy to adopt by aligning runtime control truth, host-facing docs, and validation surfaces while broader dogfooding begins |
| handoff 触发 | checkpoint 完成；超时 / 长时间无输出；... |
| 恢复源 | `.codex/status.md`；`.codex/plan.md`；... |
| 接续动作 | 继续同一 worker；换 worker 接手；... |
| 回流规则 | 仍是主线且边界没变；当前不该继续但仍有价值；... |
| 升级边界 | 方向未变，技术边界清楚；只是需要换 worker 或等下一 checkpoint；... |
| 下一 handoff 检查 | 在更多本地 workspace 上验证 worker 停下后的接续、回流和升级都能靠 daemon-host baseline 的 durable 真相完成。；继续观察 runtime / host / adoption 里哪些 handoff 场景会反复出现，再决定是否真的需要更强宿主表面或 `M15`。；... |

## 当前系统能做什么
| 面向谁 | 已能做什么 | 当前状态 | 来源 |
| --- | --- | --- | --- |
| 普通用户 | 创建并维护 `.codex` 控制面 | 已可直接使用 | [README](/Users/redcreen/.codex/skills/project-assistant/README.zh-CN.md) |
| 普通用户 | 维护 `.codex/doc-governance.json` 作为 Markdown 治理契约 | 已可直接使用 | [README](/Users/redcreen/.codex/skills/project-assistant/README.zh-CN.md) |
| 普通用户 | 把工作拆成可验证的切片 | 已可直接使用 | [README](/Users/redcreen/.codex/skills/project-assistant/README.zh-CN.md) |
| 普通用户 | 把当前工作收敛成一条有检查点的长任务执行线，而不是频繁等待“继续” | 已可直接使用 | [README](/Users/redcreen/.codex/skills/project-assistant/README.zh-CN.md) |
| 普通用户 | 把执行线显示成一个可见的子任务板，并用 `Plan Link` 映射回当前切片 | 已可直接使用 | [README](/Users/redcreen/.codex/skills/project-assistant/README.zh-CN.md) |
| 普通用户 | 把架构监督状态和升级 gate 并排展示在执行线旁边 | 已可直接使用 | [README](/Users/redcreen/.codex/skills/project-assistant/README.zh-CN.md) |
| 普通用户 | 把 `progress / continue / handoff` 做成更像给维护者看的第一屏，而不是只剩 raw status dump | 已可直接使用 | [README](/Users/redcreen/.codex/skills/project-assistant/README.zh-CN.md) |
| 普通用户 | 让 `继续` 自动判断旧项目是否需要最小控制面升级，而不是把这个判断甩给用户 | 已可直接使用 | [README](/Users/redcreen/.codex/skills/project-assistant/README.zh-CN.md) |

## 工作域视角
| 工作域 | 这是干什么的 | 当前状态 | 优先级 | 当前在做什么 | 下一步 |
| --- | --- | --- | --- | --- | --- |
| 控制面与收敛 | 保证 `.codex` truth、任务板和门禁一致 | 活跃 | P1 | 维持当前控制面真相 | 继续保持 plan / status / progress / handoff 一致 |
| 进展与恢复输出 | 给维护者和未来接手者看的恢复面板 | 活跃 | P0 | 维持当前恢复面板 | 继续压掉需要人工翻译的表达 |
| 架构监督与门禁 | 让方向偏掉时更早自动暴露 | 活跃 | P0 | 维持自动架构监督 | 继续收紧自动 review trigger |
| 文档与发布 | 保证 README / roadmap / development-plan / gates 对齐 | 稳定 | P2 | 保持文档与门禁同步 | 只在里程碑切换时更新 |

## 当前长任务
| 项目 | 当前值 |
| --- | --- |
| 长任务名称 | `stabilize-daemon-host-baseline-for-dogfooding` |
| 长任务目标 | stabilize-daemon-host-baseline-for-dogfooding |
| 执行进度 | `2 / 3` |
| 当前结论 | 这条长任务正在推进 |
| 是否存在 blocker | 当前无主要风险。 |
| 下一步性质 | 继续当前战略或编排层切片并收口任务板 |

## 当前任务板
| 任务 ID | 类型 | 状态 | 任务内容 |
| --- | --- | --- | --- |
| EL-1 | 主线 | 已完成 | harden daemon runtime edges exposed by concurrent startup, shutdown, or status polling in real workspaces |
| EL-2 | 主线 | 已完成 | keep README / architecture / usage / test plan / entry routing aligned with daemon-host as the new default fast path |
| EL-3 | 主线 | 待完成 | collect broader dogfooding evidence before opening the next host surface or any M15 discussion |

## 项目控制能力
| 能力 | 状态 |
| --- | --- |
| 恢复当前状态与下一步 | 已就绪 |
| 长任务执行线与可见任务板 | 已就绪 |
| 默认架构监督与升级 gate | 已就绪 |
| 文档整改与 Markdown 治理 | 已就绪 |
| 开发日志索引与自动沉淀 | 已就绪 |
| 公开文档中英文切换 | 已就绪 |

## 人工窗口
| 命令 | 用途 |
| --- | --- |
| `项目助手 菜单` | 查看主入口和当前可用窗口 |
| `项目助手 进展` | 查看完整项目进展面板 |
| `项目助手 架构` | 单独拉出架构监督 / 根因 / 复盘入口 |
| `项目助手 开发日志` | 查看或补记关键开发结论 |

## 接下来要做什么
| 下一步 | 为什么做 | 对应入口 |
| --- | --- | --- |
| `stabilize-daemon-host-baseline-for-dogfooding` | 避免继续在已完成的 helper 上打转 | [状态](/Users/redcreen/.codex/skills/project-assistant/.codex/status.md) |
| `EL-3` collect broader dogfooding evidence before opening the next host surface or any M15 discussion | 防止短视图和正式发布验证漂移 | [测试计划](/Users/redcreen/.codex/skills/project-assistant/docs/test-plan.zh-CN.md) |
| keep release packaging and broader host expansion evidence-gated until the new baseline proves stable in more workspaces | 避免带着回归风险前进 | 暂无 |
| 如果要看完整全局视图 | 使用更完整的项目进展输出 | `项目助手 进展` |
