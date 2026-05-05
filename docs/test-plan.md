# Test Plan

[English](test-plan.md) | [中文](test-plan.zh-CN.md)

## Scope and Risk

This plan verifies that `project-assistant` remains usable as a convergent project-governance skill.

Primary risks:

- control-surface drift
- partial retrofit behavior
- unclear progress output
- public docs falling out of structure or bilingual parity
- daemon runtime / host-state drift
- continue bridge or legacy rollout regressions on the new baseline
- PTL responsibilities remaining doc-only instead of activating by default in other project entries
- PTL gate becoming too heavy for `continue / progress` or producing unexplained false positives
- PTL allows broad implementation before a basic feasibility probe proves uncertain host, API, protocol, plugin, binary, or undocumented behavior
- the assistant leaves a known required next step in the final answer and stops, forcing the user to ask for `continue`
- non-trivial execution requests bypass the programmatic pipeline and leave control flow to LLM willingness
- host/user messages bypass message ingress, so ordinary chat never becomes classified, recorded, or enqueued pipeline work
- terminal-launched Codex prompts bypass the message ingress wrapper and go straight to the real Codex binary
- release/install documentation claims a stable tag has mainline-only daemon-host or PTL-loop behavior

## Acceptance Cases

| Case | Setup | Action | Expected Result |
| --- | --- | --- | --- |
| Unified bootstrap front door | blank repo with a git root | run `project_assistant_entry.py bootstrap` | control surface, docs, and fast gate complete through one tool call |
| Control surface retrofit | target repo missing `.codex/*` | run retrofit flow | required control files exist and validate |
| Unified retrofit front door | repo has legacy docs / markdown clutter | run `project_assistant_entry.py retrofit` | control surface, docs, markdown governance, and fast gate complete through one tool call |
| Entry routing truth | repo expects the unified front door layer | run `validate_entry_routing.py` after bootstrap/retrofit or resume upgrade | `.codex/entry-routing.md` states the same daemon-host default fast path that maintainers, docs, and validators use |
| Large-project progress | target repo has module layer | run progress flow | output contains global view, module view, and Mermaid |
| Autonomous execution line | goal and active slice are clear | run execute or resume flow | assistant continues a meaningful checkpoint-sized run instead of stopping for repeated continue prompts |
| Context handoff | long-running repo with active slice | run handoff flow | compact resume pack with copy-paste commands |
| Daemon runtime | target repo already has control truth | run `project_assistant_entry.py daemon start/status/queue` | the local runtime starts, exposes queue/event state, and keeps a protected foreground-write lease |
| VS Code host shell | open the workspace that contains `integrations/vscode-host` | run extension validation and local smoke | the host shows live status, recent files, and task-log entry points |
| Continue bridge | runtime is `resume-ready` | trigger `manual continue` or `one-click continue` through the host | the resume action still reuses the unified front door instead of chat-box injection |
| Daemon-host local validation | use a representative local fixture repo | run `validate_daemon_host_mvp.py` | the daemon-host baseline covers bootstrap, retrofit, docs-retrofit, progress, continue, handoff, and the fast gate |
| Daemon-host legacy rollout | use a downgraded legacy fixture repo | run `validate_daemon_legacy_rollout.py` | the legacy repo upgrades first and then emits structured continue / progress / handoff output |
| PTL policy sync | any project with `.codex/control-surface.json` | run `ptl_gate.py preflight <repo> --mode continue` | `.codex/ptl-policy/project-policy.json` and `.codex/ptl-policy/preflight.json` are generated, with decision `allow` or an explainable higher severity |
| PTL missing-control block | fixture repo is missing required `.codex/*` files | run `validate_ptl_gate.py` | preflight returns `block` and hits `project-assistant.control-surface.required-files` |
| PTL image-generation detection | style-engine-like fixture has durable docs for image generation, masks, prompts, and fallback behavior | run `validate_ptl_gate.py` | `image-generation` domain pack loads automatically and changed-path matches return `warn` |
| PTL OpenClaw detection | openclaw-skills-like fixture has plugin-runtime and order-adapter evidence | run `validate_ptl_gate.py` | `plugin-runtime` / `order-runtime` domain packs load automatically and changed-path matches return `warn` |
| PTL entry activation | target repo already has the project-assistant control surface | run `continue_entry.py` or `progress_entry.py` | output includes `PTL Preflight` without manually chaining extra scripts |
| PTL feasibility-first duty | task depends on uncertain host/API/plugin/protocol surface | inspect PTL role docs and execution contract | required probe and stop, shrink, or switch-layer semantics are documented before broad implementation |
| PTL semantic induction candidates | repeated correction messages do not exactly match fixed patterns but share concepts such as human decision plus clear reply format | run `validate_ptl_learning.py` | generates `semantic.*` learning candidates, renders them in the governed review panel, and does not let them take effect without human review |
| Completion gate complete semantics | fixture repo has all execution tasks complete | run `completion_gate.py final-check <repo> --stop-reason complete` | returns `allow` and writes `.codex/completion-gate.json` |
| Completion gate open-task interception | fixture repo still has a required unchecked task | run `validate_completion_gate.py` | returns `require-continue` and does not allow declaring the run complete |
| Completion gate final-answer next-step interception | final text contains required follow-up language such as "next step still needs" | run `validate_completion_gate.py` | returns `require-continue` and requires continuing instead of stopping |
| Completion gate legal stop reasons | stop reason is `blocked`, `requires-human-decision`, or `explicitly-deferred` | run `validate_completion_gate.py` | does not mislabel the run as complete and does not force continuation |
| Task pipeline automatic continuation | fixture repo has two command tasks, with the second depending on the first output | run `validate_pipeline_runner.py` | runner automatically executes the next task and ends with pipeline status `complete` |
| Task pipeline automatic repair | command task fails once and has `repairCommand` | run `validate_pipeline_runner.py` | runner creates a repair task, completes repair, returns to the original task, and finishes |
| Task pipeline LLM boundary | fixture repo contains an `llm` task | run `validate_pipeline_runner.py` | runner stops at `awaiting-llm` with a concrete task brief instead of letting the LLM own the loop |
| Task pipeline final-text follow-up | an LLM task is resolved with final text that names a required next step | run `validate_pipeline_runner.py` | runner enqueues a completion-gate follow-up task instead of dropping the known next step |
| Task pipeline stale backlog maintenance | historical message-ingress tasks exist before the first resolved live message | run `pipeline_runner.py maintain <repo> --archive-stale-message-backlog` | old imported pending tasks become `explicitly-deferred` and no longer block new work |
| Task pipeline explicit human gate | PTL or completion review requires human confirmation | run `validate_pipeline_runner.py` | runner creates a real `human-decision` task with exact accept/pause reply formats and can continue after acceptance |
| Task pipeline enqueue entry | new execution request enters through `pipeline_runner.py run <repo> --task ...` | run `validate_pipeline_runner.py` | user work becomes a pending task in `.codex/task-pipeline.json` before the loop runs |
| Task pipeline unified front door | new execution request enters through `project_assistant_entry.py execute <repo> --task ...` | run `validate_pipeline_runner.py` | the unified front door routes to the pipeline runner and enqueues before execution |
| Task pipeline entry panel | target repo already has pipeline state | run `continue_entry.py` or `progress_entry.py` | output includes `Task Pipeline` |
| Message ingress execution message | new implementation request enters through `message_ingress.py ingest <repo> --message ...` | run `validate_message_ingress.py` | message is classified as `execute`, recorded in `.codex/message-ingress.json`, and enqueued into `.codex/task-pipeline.json` |
| Message ingress discussion message | new discussion or review question enters through `message_ingress.py ingest <repo> --message ...` | run `validate_message_ingress.py` | message is classified as `analysis` and still enters the task pipeline as an explicit reviewable task |
| Message ingress classify-only | host wants classification without enqueue | run `message_ingress.py ingest <repo> --message ... --classify-only` | message is recorded without creating `.codex/task-pipeline.json` |
| Message ingress unified front door | host routes a user message through `project_assistant_entry.py message <repo> --message ...` | run `validate_message_ingress.py` | the unified front door calls message ingress and returns the same record/task result |
| Message ingress entry panel | target repo already has message ingress state | run `continue_entry.py` or `progress_entry.py` | output includes `Message Ingress` |
| Codex CLI wrapper initial prompt | `codex "<prompt>"` is launched from a terminal with the lightweight wrapper installed | run `validate_codex_message_wrapper.py` | the prompt is recorded through message ingress, enqueued into the task pipeline, and then forwarded to the real Codex binary |
| Codex CLI wrapper exec prompt | `codex exec "<prompt>"` is launched from a terminal with the lightweight wrapper installed | run `validate_codex_message_wrapper.py` | the exec prompt is recorded before the real Codex binary receives the same arguments |
| Codex CLI wrapper app-server skip | Codex starts an internal `app-server` process | run `validate_codex_message_wrapper.py` | the wrapper forwards the command without treating it as a user message |
| Install script release refs | install from a tag and from a branch/mainline ref | run `validate_install_scripts.py` | `install.sh` can checkout tag and branch refs, and `install-vscode-tools.sh` installs the requested branch package |
| Docs retrofit | repo has public docs | run docs retrofit flow | README and docs system are normalized and validate |
| Public-doc i18n | repo requires bilingual public docs | run i18n validator | English/Chinese doc pairs and switch links exist |
| Public-doc quality | repo has public docs | run doc-quality validator | public docs contain no placeholder prose, empty diagrams, or broken local links |
| Control-surface quality | repo has `.codex/*` | run control-surface quality validator | brief, plan, status, and module docs are not left in TODO/template state |
| Development log | repo produced durable implementation reasoning | write or validate a devlog entry | devlog index exists and each entry contains problem, thinking, solution, and validation |

## Automation Coverage

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

## Manual Checks

- verify the README reads well for first-time users
- verify Chinese and English public docs point to each other correctly
- verify diagrams clarify structure instead of repeating text
- verify execute and resume semantics imply a meaningful autonomous run, not a micro-step loop
- verify bootstrap and retrofit can be triggered from one canonical CLI front door instead of a hand-stitched shell sequence
- verify README, usage, architecture, test-plan, and `.codex/entry-routing.md` all describe the same daemon-host default fast path
- verify the daemon / queue control surface exposes readable state without interrupting the foreground coding lane
- verify the VS Code host makes it obvious that the page is moving, code is changing, and the task is still advancing
- verify development-log entries preserve the reasoning path without drifting into status prose
- verify PTL preflight rule, decision, and evidence output is clear enough for a human to accept, reject, or keep observing the proposal
- verify uncertain host, API, plugin, protocol, binary, or undocumented routes have a recorded feasibility probe before broad implementation
- verify final answers do not stop after naming required follow-up work; any stop must be a blocker, human decision, or explicit deferral
- verify non-trivial execution requests do not bypass `.codex/task-pipeline.json`; the LLM acts inside a task while the runner owns control flow
- verify host/user messages do not bypass `.codex/message-ingress.json`; the ingress layer owns classification, recording, and task enqueue before LLM work starts
- verify the Codex CLI wrapper is installed ahead of the real Codex binary in `PATH` and that it skips `app-server` processes
- verify stable tag install instructions do not imply mainline-only daemon-host or PTL-loop behavior

## Test Data and Fixtures

- this skill repo itself
- a medium repo with `.codex` only
- a large repo with module layer and durable docs
- temporary generic, missing-control, style-engine-like, and openclaw-skills-like fixtures generated by `validate_ptl_gate.py`
- temporary complete, open-task, final-text-next-step, explicit-deferred, and human-decision fixtures generated by `validate_completion_gate.py`
- temporary command-loop, repair-loop, llm-pause, run-argument-enqueue, human-decision, final-text follow-up, backlog maintenance, generic human response, and entry-panel fixtures generated by `validate_pipeline_runner.py`
- temporary execution-message, discussion-message, classify-only, front-door, and entry-panel fixtures generated by `validate_message_ingress.py`
- temporary fake-codex fixtures generated by `validate_codex_message_wrapper.py`
- temporary tag and branch install fixtures generated by `validate_install_scripts.py`

## Release Gate

Before calling the skill update complete:

- control-surface validation passes on the skill repo
- docs-system validation passes on the skill repo
- public-doc i18n validation passes on the skill repo
- entry-routing validation passes on the skill repo
- dogfooding-evidence validation passes on the skill repo
- layered gate-set validation passes on the skill repo
- doc-quality validation passes on the skill repo
- control-surface quality validation passes on the skill repo
- development-log validation passes on the skill repo
- daemon runtime, VS Code host shell, daemon-host baseline, and legacy rollout validation all pass on the skill repo
- PTL gate fixture validation passes on the skill repo, and `continue / progress` entries append the PTL preflight panel by default
- PTL role docs and execution contract require feasibility-first probes for uncertain host, API, protocol, plugin, binary, or undocumented routes
- PTL learning fixture validation passes on the skill repo, including governed semantic induction candidates
- Completion gate fixture validation passes on the skill repo, and the fast gate catches "known required next step remains but declared complete" behavior
- Task pipeline fixture validation passes on the skill repo, and the fast gate verifies enqueue-first execution, automatic repair, return-to-mainline, and explicit LLM task pause behavior
- Message ingress fixture validation passes on the skill repo, and the fast gate verifies message classification, persistence, enqueue, front-door routing, and panel visibility
- Codex CLI wrapper fixture validation passes on the skill repo, and the fast gate verifies prompt capture, `exec` capture, `app-server` skip, and disable switch behavior
- install script validation passes on the skill repo, and the fast gate verifies tag plus branch/mainline ref installation
