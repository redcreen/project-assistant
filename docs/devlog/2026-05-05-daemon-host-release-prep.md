# 明确 daemon-host release prep 与安装入口

- 日期：2026-05-05
- 状态：resolved

## 问题

README 把 v0.1.9 稳定 tag 和当前 mainline daemon-host / PTL-loop 能力混在一起；实际 v0.1.9 tag 的 install.sh 默认还是旧 Workspace Doc Browser，不能声称它默认安装当前 Project Assistant Host / PTL loop。

## 思考

发布入口必须先区分不可变 tag 和 mainline release candidate；如果文档要求用户走 mainline，安装脚本也必须能 checkout branch/mainline ref，并且这个行为要进入 fast gate，而不是只靠说明文字。

## 解决方案

更新 README / README.zh-CN，把 v0.1.9 标为 previous stable，把当前 daemon-host / PTL-loop 入口改为 mainline release-candidate；修正 install.sh 支持 tag 与 branch/mainline ref；新增 validate_install_scripts.py 并接入 validate_gate_set.py --profile fast；新增 daemon-host-release-prep 双语文档记录 release 边界。

## 验证

已通过 validate_install_scripts.py、validate_docs_system.py、validate_public_docs_i18n.py，并通过 validate_gate_set.py --profile fast；release gate 仍需要在当前 release-candidate changes 提交后再运行并打 tag。

## 后续

- 提交当前 release-candidate changes 后运行 python3 scripts/validate_gate_set.py . --profile release，再执行 release_skill.py patch

## 相关文件

- README.md
- README.zh-CN.md
- install.sh
- scripts/validate_install_scripts.py
- docs/reference/project-assistant/daemon-host-release-prep.md
- docs/reference/project-assistant/daemon-host-release-prep.zh-CN.md
