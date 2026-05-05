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
- PTL 职责停留在文档里，没有在其它项目入口默认生效
- PTL gate 过重，影响 `continue / progress` 的响应速度或产生不可解释的误报
- PTL 在不确定宿主、API、协议、插件、binary 或未文档化行为缺少基础可行性探针时，仍允许大面积实现
- assistant 把“已知必要下一步”写进最终答复后停下，导致用户反复催 `继续`
- 非平凡执行请求没有先入队到程序化 pipeline，导致流程控制继续依赖 LLM 自觉
- host/user message 绕过 message ingress，导致普通聊天没有被分类、记录或入队成 pipeline work
- 终端启动的 Codex prompt 绕过 message ingress wrapper，直接进入真实 Codex binary
- release / install 文档声称稳定 tag 已具备只有 mainline 才有的 daemon-host 或 PTL-loop 行为

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
| PTL policy sync | 任意带 `.codex/control-surface.json` 的项目 | 运行 `ptl_gate.py preflight <repo> --mode continue` | 生成 `.codex/ptl-policy/project-policy.json` 与 `.codex/ptl-policy/preflight.json`，默认 decision 为 `allow` 或可解释的更高等级 |
| PTL 缺控制面阻塞 | fixture repo 缺失必需 `.codex/*` 文件 | 运行 `validate_ptl_gate.py` | preflight 返回 `block`，并命中 `project-assistant.control-surface.required-files` |
| PTL 出图域识别 | style-engine-like fixture 包含出图、mask、prompt、fallback 相关 durable docs | 运行 `validate_ptl_gate.py` | 自动加载 `image-generation` domain pack，变更命中时返回 `warn` |
| PTL OpenClaw 域识别 | openclaw-skills-like fixture 包含插件 runtime 与 order adapter 线索 | 运行 `validate_ptl_gate.py` | 自动加载 `plugin-runtime` / `order-runtime` domain pack，变更命中时返回 `warn` |
| PTL 入口默认生效 | 目标仓库已有项目助手控制面 | 运行 `continue_entry.py` 或 `progress_entry.py` | 输出面板包含 `PTL Preflight`，且不需要用户手工串联额外脚本 |
| PTL 可行性优先职责 | 任务依赖不确定宿主、API、插件或协议表面 | 检查 PTL 角色文档和执行契约 | 文档要求大面积实现前先做探针，并在失败时停止、缩小范围或切换层级 |
| PTL 语义归纳候选 | 重复纠错消息没有完全命中固定 pattern，但共享“人类确认 + 明确回复格式”等语义概念 | 运行 `validate_ptl_learning.py` | 生成 `semantic.*` learning candidate，显示在 governed review panel，且不会绕过 human review 自动生效 |
| Completion gate 完成语义 | fixture repo 的 execution tasks 全部完成 | 运行 `completion_gate.py final-check <repo> --stop-reason complete` | 返回 `allow`，并写入 `.codex/completion-gate.json` |
| Completion gate 拦截 open task | fixture repo 仍有必做 checkbox 未完成 | 运行 `validate_completion_gate.py` | 返回 `require-continue`，不能把本轮声明为完成 |
| Completion gate 拦截最终答复 next-step | final text 包含“下一步仍需 / still need”等必做后续 | 运行 `validate_completion_gate.py` | 返回 `require-continue`，要求继续执行而不是停下 |
| Completion gate 允许合法停止 | stop reason 为 `blocked`、`requires-human-decision` 或 `explicitly-deferred` | 运行 `validate_completion_gate.py` | 不误判为完成，也不强迫继续 |
| Task pipeline 自动继续 | fixture repo 包含两个 command tasks，第二个依赖第一个输出 | 运行 `validate_pipeline_runner.py` | runner 自动执行下一 task，最终 pipeline 状态为 `complete` |
| Task pipeline 自动修复 | command task 首次失败且带 `repairCommand` | 运行 `validate_pipeline_runner.py` | runner 创建 repair task，repair 完成后回到原 task 并最终完成 |
| Task pipeline LLM 边界 | fixture repo 包含 `llm` task | 运行 `validate_pipeline_runner.py` | runner 停在 `awaiting-llm`，输出明确 task brief，而不是让 LLM 控制循环 |
| Task pipeline final-text 后续入队 | LLM task resolve 时 final text 提到必做下一步 | 运行 `validate_pipeline_runner.py` | runner 自动创建 completion-gate follow-up task，不再丢掉已知必要后续 |
| Task pipeline 历史 backlog 维护 | 第一条已完成 live message 前存在历史 message-ingress pending | 运行 `pipeline_runner.py maintain <repo> --archive-stale-message-backlog` | 旧导入 pending 变成 `explicitly-deferred`，不再阻塞新工作 |
| Task pipeline 显式 human gate | PTL 或 completion review 需要人类确认 | 运行 `validate_pipeline_runner.py` | runner 创建真实 `human-decision` task，包含明确接受/暂停回复格式，接受后可继续执行 |
| Task pipeline 入队入口 | 新执行请求通过 `pipeline_runner.py run <repo> --task ...` 进入 | 运行 `validate_pipeline_runner.py` | 用户任务先成为 `.codex/task-pipeline.json` 中的 pending task，再进入 loop |
| Task pipeline 统一前门 | 新执行请求通过 `project_assistant_entry.py execute <repo> --task ...` 进入 | 运行 `validate_pipeline_runner.py` | 统一前门会路由到 pipeline runner，并先入队再执行 |
| Task pipeline 入口面板 | 目标仓库已有 pipeline state | 运行 `continue_entry.py` 或 `progress_entry.py` | 输出面板包含 `Task Pipeline` |
| Message ingress 执行消息 | 新实现请求通过 `message_ingress.py ingest <repo> --message ...` 进入 | 运行 `validate_message_ingress.py` | message 被分类为 `execute`，写入 `.codex/message-ingress.json`，并入队到 `.codex/task-pipeline.json` |
| Message ingress 讨论消息 | 新讨论或 review 问题通过 `message_ingress.py ingest <repo> --message ...` 进入 | 运行 `validate_message_ingress.py` | message 被分类为 `analysis`，并仍然进入 task pipeline 成为显式可 review task |
| Message ingress classify-only | 宿主只需要分类，不需要入队 | 运行 `message_ingress.py ingest <repo> --message ... --classify-only` | message 被记录，但不会创建 `.codex/task-pipeline.json` |
| Message ingress 统一前门 | 宿主通过 `project_assistant_entry.py message <repo> --message ...` 路由用户消息 | 运行 `validate_message_ingress.py` | 统一前门会调用 message ingress，并返回同一套 record/task 结果 |
| Message ingress 入口面板 | 目标仓库已有 message ingress state | 运行 `continue_entry.py` 或 `progress_entry.py` | 输出面板包含 `Message Ingress` |
| Codex CLI wrapper 初始 prompt | 终端安装轻量 wrapper 后启动 `codex "<prompt>"` | 运行 `validate_codex_message_wrapper.py` | prompt 会先通过 message ingress 记录并入队 task pipeline，然后原样转发给真实 Codex binary |
| Codex CLI wrapper exec prompt | 终端安装轻量 wrapper 后启动 `codex exec "<prompt>"` | 运行 `validate_codex_message_wrapper.py` | exec prompt 会在真实 Codex binary 收到同一组参数前被记录 |
| Codex CLI wrapper app-server 跳过 | Codex 启动内部 `app-server` 进程 | 运行 `validate_codex_message_wrapper.py` | wrapper 会转发命令，但不会把它当作用户消息 |
| 安装脚本 release refs | 分别从 tag 和 branch/mainline ref 安装 | 运行 `validate_install_scripts.py` | `install.sh` 能 checkout tag 和 branch refs，`install-vscode-tools.sh` 能安装指定 branch package |
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
- `scripts/ptl_gate.py`
- `scripts/validate_ptl_gate.py`
- `scripts/ptl_learning.py`
- `scripts/validate_ptl_learning.py`
- `scripts/completion_gate.py`
- `scripts/validate_completion_gate.py`
- `scripts/pipeline_runner.py`
- `scripts/validate_pipeline_runner.py`
- `scripts/message_ingress.py`
- `scripts/validate_message_ingress.py`
- `scripts/codex_message_wrapper.py`
- `scripts/install_codex_message_wrapper.py`
- `scripts/validate_codex_message_wrapper.py`
- `scripts/validate_install_scripts.py`

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
- 确认 PTL preflight 输出的 rule、decision、evidence 足够让人类判断是否需要接受、拒绝或继续观察
- 确认不确定宿主、API、插件、协议、binary 或未文档化路线在大面积实现前有记录过的可行性探针
- 确认最终答复不会把必做项写成“下一步”后停下；如果确实停下，必须属于 blocker、人类决策或显式延期
- 确认非平凡执行请求不会绕过 `.codex/task-pipeline.json`，LLM 只在具体 task 内执行，循环控制由 runner 决定
- 确认 host/user message 不会绕过 `.codex/message-ingress.json`；ingress 层在 LLM 工作前负责分类、记录和入队
- 确认 Codex CLI wrapper 在 `PATH` 中排在真实 Codex binary 前面，并且会跳过 `app-server` 进程
- 确认稳定 tag 安装说明没有暗示 mainline-only 的 daemon-host 或 PTL-loop 行为

## 测试数据与夹具

- 当前 skill 仓库自身
- 仅有 `.codex` 的 medium 仓库
- 带模块层和 durable docs 的 large 仓库
- `validate_ptl_gate.py` 生成的 generic、missing-control、style-engine-like、openclaw-skills-like 临时 fixture
- `validate_completion_gate.py` 生成的 complete、open-task、final-text-next-step、explicit-deferred、human-decision 临时 fixture
- `validate_pipeline_runner.py` 生成的 command-loop、repair-loop、llm-pause、run-argument-enqueue、human-decision、final-text follow-up、backlog maintenance、generic human response、entry-panel 临时 fixture
- `validate_message_ingress.py` 生成的 execution-message、discussion-message、classify-only、front-door、entry-panel 临时 fixture
- `validate_codex_message_wrapper.py` 生成的 fake-codex 临时 fixture
- `validate_install_scripts.py` 生成的 tag 和 branch install 临时 fixture

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
- skill 仓库自身通过 PTL gate fixture 校验，且 `continue / progress` 入口默认追加 PTL preflight 面板
- PTL 角色文档和执行契约要求不确定宿主、API、协议、插件、binary 或未文档化路线先做可行性探针
- skill 仓库自身通过 Completion gate fixture 校验，且 fast gate 会拦截“已知必要下一步仍存在却声明完成”的行为
- skill 仓库自身通过 Task pipeline fixture 校验，且 fast gate 会验证执行请求先入队、失败自动 repair、repair 后回到主线、LLM task 明确暂停
- skill 仓库自身通过 Message ingress fixture 校验，且 fast gate 会验证消息分类、持久化、入队、统一前门路由和面板可见性
- skill 仓库自身通过 Codex CLI wrapper fixture 校验，且 fast gate 会验证 prompt capture、`exec` capture、`app-server` skip 和禁用开关
- skill 仓库自身通过安装脚本校验，且 fast gate 会验证 tag 与 branch/mainline ref 安装路径
