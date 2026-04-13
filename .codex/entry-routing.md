# Entry Routing

## Current Entry Direction
- Direction: `tool-first front door plus bootstrap-retrofit fast path`
- Status: `active`
- Why Now: 在 `continue / progress / handoff` 之外，空白项目初始化和整改也已经被用户明确反馈为主要时延来源；repo 现在用同一条工具前门把 `启动 / 整改 / 文档整改` 收成一次事务，减少宿主反复串脚本的等待。

## Entry Routing Contract
- `启动 / 整改 / 文档整改 / 继续 / 进展 / 交接` 的第一步都必须先走统一前门，而不是由 skill 或宿主手工拼多段脚本。
- `继续 / 进展 / 交接` 必须先触发版本 preflight；旧控制面必须先补到当前代际，再允许继续读取真实状态。
- `启动 / 整改 / 文档整改` 必须走 transaction-style fast path，把 control-surface、docs、markdown governance 和默认门禁合并成一条脚本链路。
- 统一前门只负责命令路由、版本 preflight / fast path 和结构化面板输出；真正的业务逻辑仍留在后端脚本。
- 自然语言 skill 负责把用户意图路由到统一前门，但不能再绕过统一前门自发生成第一屏。
- 宿主或插件级硬接入如果存在，应继续调用同一条统一前门，而不是复制一套平行逻辑。

## Front Door Layers
| Layer | Current Implementation | Responsibility |
| --- | --- | --- |
| natural-language routing | `SKILL.md` + prompt routing | 把用户说的 `项目助手 启动 / 整改 / 文档整改 / 继续 / 进展 / 交接` 路由到同一条前门 |
| canonical tool front door | `scripts/project_assistant_entry.py` + `bin/project-assistant` | 统一解析模式、仓库路径和子命令别名 |
| mode backends | `bootstrap_entry.py` / `retrofit_entry.py` / `continue_entry.py` / `progress_entry.py` / `handoff_entry.py` | 生成对应的事务化快路径或结构化第一屏 |
| durable repo state | `.codex/*` + durable docs | 提供启动、整改、继续、进展和交接真正读取与写回的真相层 |

## Preflight Contract
| Mode | Preflight Rule | Why |
| --- | --- | --- |
| `bootstrap` | 直接进入 `sync_control_surface.py -> sync_docs_system.py -> validate_gate_set(fast)` | 把空白项目初始化收成一次事务，不再让宿主串多轮脚本 |
| `retrofit` | 直接进入 `sync_control_surface.py -> sync_docs_system.py -> sync_markdown_governance.py -> validate_gate_set(fast)` | 把结构整改收成一次事务，并把深门禁留给收口轮次 |
| `docs-retrofit` | 与 `retrofit` 共用同一条 transaction fast path | 文档整改默认也包含 Markdown governance，不再维护平行链路 |
| `continue` | 先跑 `sync_resume_readiness.py`；旧代际必须先升级 | 不让旧 `.codex` 真相直接误导继续输出 |
| `progress` | 先跑 `sync_resume_readiness.py`；再生成完整看板 | 不让维护者读到过时代际的全局进展 |
| `handoff` | 先跑 `sync_resume_readiness.py`；再生成恢复包 | 不让交接包继续引用旧控制面结构 |

## Structured Output Contract
| Mode | First Output Must Be | Not Allowed First |
| --- | --- | --- |
| `bootstrap` | 结构化启动结果面板 | 先在 commentary 里拆着讲要跑哪些脚本 |
| `retrofit` | 结构化整改结果面板 | 让宿主先串多轮 sync 再回来说结果 |
| `docs-retrofit` | 结构化文档整改结果面板 | 单独维护另一条 docs-only 手工脚本链 |
| `continue` | 表格化 continue 面板 | 自由 prose 摘要 |
| `progress` | 表格化 maintainer dashboard | 只有自然语言长段落 |
| `handoff` | 可复制的结构化交接面板 | 先解释再慢慢拼交接信息 |

## Host / Tool Bridge Boundary
| Boundary | Repo Owns Today | Future Bridge |
| --- | --- | --- |
| tool-shaped entry | `project_assistant_entry.py` + CLI wrapper | 宿主或插件可以直接调用这条统一前门，减少重复 orchestration 回合 |
| business logic | 后端脚本继续留在 skill repo | 宿主不应复制 bootstrap/retrofit/continue/progress/handoff 逻辑 |
| hard host routing | 仅通过文档和统一前门定义边界 | 真正桌面级强绑定需由宿主 / 插件集成承接 |

## Next Entry Checks
1. 在代表性旧代际仓库上继续验证：`continue / progress / handoff` 会先升级再输出结构化面板。
2. 在空白仓库和真实整改仓库上持续 benchmark：默认 front door 应继续把宿主调用次数压到一次，而不是重新回退成多轮串脚本。
3. 继续检查 task / 新 session 场景是否仍会绕过统一前门；如果会，记录为宿主桥接证据，而不是继续改后端脚本。
4. 如果未来引入插件或宿主硬接入，必须继续复用统一前门，而不是复制另一套命令逻辑。
