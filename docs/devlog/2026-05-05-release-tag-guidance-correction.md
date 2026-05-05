# 修正发布 tag 指南并重跑 release

- 日期：2026-05-05
- 状态：resolved

## 问题

v0.1.10 已经生成后，README 和 daemon-host release prep 文档仍保留 v0.1.9 previous stable / mainline release candidate 的旧表述，导致安装命令和说明不一致。

## 思考

发布门禁能验证引用版本一致，但旧文案没有被 release_ref_lib 自动改写；这类问题会误导用户安装错误能力集，必须在 release flow 内自动修复并重新打 patch tag，而不是把错误留给后续人工发现。

## 解决方案

将安装说明改成 current release / 当前 release，不再把 PTL-loop baseline 描述成 mainline-only；保留 v0.1.9 作为 docs-browser-era 历史说明；同步 .codex/status.md 与 .codex/plan.md 的 release 状态。

## 验证

已运行 validate_release_readiness.py、validate_public_docs_i18n.py、validate_docs_system.py；release_skill.py patch 首次被 development-log pending gate 拦截，当前 devlog 记录用于解除该 gate 后重新执行完整 release flow。

## 后续

- 后续 release tag 仍通过 clean-tree release_skill.py patch 创建

## 相关文件

- README.md
- README.zh-CN.md
- docs/reference/project-assistant/daemon-host-release-prep.md
- docs/reference/project-assistant/daemon-host-release-prep.zh-CN.md
