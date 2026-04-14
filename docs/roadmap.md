# Roadmap

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## Scope

This roadmap describes the evolution of the `project-assistant` skill itself. It does not replace the live execution truth in `.codex/status.md`.

For the detailed execution queue, see:

- [project-assistant/development-plan.md](reference/project-assistant/development-plan.md)

## Current / Next / Later

| Horizon | Focus | Exit Signal |
| --- | --- | --- |
| Current | stabilize the newly shipped daemon-host baseline so it becomes a real default fast path: runtime, queue, VS Code host, continue bridge, legacy rollout, docs, and gates stay aligned | broader dogfooding no longer exposes frequent runtime/host regressions and the daemon-host baseline can be adopted by default |
| Next | decide the release narrative, install entry, and broader dogfooding scope for the daemon-host baseline while continuing to collect host-resume evidence | operator docs, release-facing docs, and install path align, and broader workspaces still pass consistently |
| Later | only expand host surfaces, assess web/remote hosts, or reopen `M15 selective multi-executor scheduling` when evidence is strong enough | do not mix baseline hardening, host expansion, and multi-executor discussion into one release |

## Milestones

| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |
| [M1](reference/project-assistant/development-plan.md#m1) | done | establish `.codex` control surfaces and project tiering | core skill routing | current state is recoverable |
| [M2](reference/project-assistant/development-plan.md#m2) | done | establish convergent retrofit | control-surface scripts | retrofit no longer stops halfway |
| [M3](reference/project-assistant/development-plan.md#m3) | done | establish progress and handoff workflows | module layer + snapshot scripts | progress and handoff are stable |
| [M4](reference/project-assistant/development-plan.md#m4) | done | establish durable doc standards and doc validation | document standards + docs scripts | durable docs pass structure gates |
| [M5](reference/project-assistant/development-plan.md#m5) | done | establish public-doc bilingual switching and acceptance | i18n rules + i18n validator | public docs switch cleanly between English and Chinese |
| [M6](reference/project-assistant/development-plan.md#m6) | done | converge on the embedded architect-assistant operating model | previous milestones | planning, execution, architecture supervision, and devlogs are default capabilities |
| [M7](reference/project-assistant/development-plan.md#m7) | done | improve narrative quality and automatic architecture triggers | [M6](reference/project-assistant/development-plan.md#m6) | less manual cleanup and fewer direction corrections after retrofit |
| [M8](reference/project-assistant/development-plan.md#m8) | deferred | optimize internal control-surface output by language | handoff + command templates + validation policy | continues as bounded supporting backlog |
| [M9](reference/project-assistant/development-plan.md#m9) | deferred | compress continue / resume / handoff snapshots without losing recoverability | continue snapshot + handoff + validation policy | continues as bounded supporting backlog |
| [M10](reference/project-assistant/development-plan.md#m10) | done | add a strategic-evaluation layer above execution | [M7](reference/project-assistant/development-plan.md#m7) + approved strategic direction | the system emits durable strategic judgment and still leaves direction changes to human approval |
| [M11](reference/project-assistant/development-plan.md#m11) | done | add program orchestration across slices/executors | [M10](reference/project-assistant/development-plan.md#m10) + durable program board | the system coordinates related slices instead of depending on repeated human “continue” prompts |
| [M12](reference/project-assistant/development-plan.md#m12) | done | add supervised long-run delivery | [M11](reference/project-assistant/development-plan.md#m11) + stable escalation policy | long-running delivery can continue to real business decision points |
| [M13](reference/project-assistant/development-plan.md#m13) | done | add the PTL-driven supervision loop | [M12](reference/project-assistant/development-plan.md#m12) + durable delivery supervision | PTL can inspect, continue, re-sequence, or escalate periodically or by event |
| [M14](reference/project-assistant/development-plan.md#m14) | done | add worker handoff and re-entry | [M13](reference/project-assistant/development-plan.md#m13) + durable handoff / supervision truth | `when a worker stops, the project does not stop` becomes durable capability |
| [M15](reference/project-assistant/development-plan.md#m15) | later | add selective multi-executor scheduling only for safe parallel work | [M14](reference/project-assistant/development-plan.md#m14) + disjoint write scopes + conflict control | real multi-executor work is only allowed when write scopes and return paths are explicit |
| [M16](reference/project-assistant/development-plan.md#m16) | done | add the unified hard entry and tool front door | [M14](reference/project-assistant/development-plan.md#m14) + versioned control surface + entry scripts | old repos auto-upgrade first and `continue / progress / handoff` no longer fall back to free prose first |
| [M17](reference/project-assistant/development-plan.md#m17) | done | build the PTL daemon runtime core and write-safe fast-path baseline | [M16](reference/project-assistant/development-plan.md#m16) + daemon-first architecture + runtime contract | the daemon runtime, queue/event contract, runtime store, and minimum CLI control surface are usable |
| [M18](reference/project-assistant/development-plan.md#m18) | done | build the VS Code host shell and live-status surfaces | [M17](reference/project-assistant/development-plan.md#m17) + daemon event contract | users can see queue state, status, the active slice, and recent events in VS Code |
| [M19](reference/project-assistant/development-plan.md#m19) | done | build the host continue-resume bridge so `resume-ready` becomes a host action | [M18](reference/project-assistant/development-plan.md#m18) + Codex runner / command contract | `manual continue` and conservative `one-click continue` work without chat-box injection |
| [M20](reference/project-assistant/development-plan.md#m20) | done | validate the daemon-host baseline on local workspaces and re-validate older feature families on top of it | [M19](reference/project-assistant/development-plan.md#m19) + representative local workspaces | the daemon-host baseline is stable and older capabilities keep passing on the new baseline |
| [M21](reference/project-assistant/development-plan.md#m21) | done | resume post-M16 rollout verification on top of the daemon-host baseline | [M20](reference/project-assistant/development-plan.md#m20) | representative legacy repos still upgrade first, render structured panels, and are no longer dominated by avoidable synchronous work |

## Milestone Flow

```mermaid
flowchart LR
    M1["M1 control surface"] --> M2["M2 convergent retrofit"]
    M2 --> M3["M3 progress + handoff"]
    M3 --> M4["M4 doc standards"]
    M4 --> M5["M5 public-doc bilingual switching"]
    M5 --> M6["M6 embedded architect assistant"]
    M6 --> M7["M7 stronger narrative + triggers"]
    M7 --> M10["M10 strategic evaluation"]
    M10 --> M11["M11 program orchestration"]
    M11 --> M12["M12 supervised long-run delivery"]
    M12 --> M13["M13 PTL supervision loop"]
    M13 --> M14["M14 worker handoff and re-entry"]
    M14 --> M16["M16 unified hard entry"]
    M16 --> M17["M17 daemon runtime core"]
    M17 --> M18["M18 VS Code host shell"]
    M18 --> M19["M19 host resume bridge"]
    M19 --> M20["M20 daemon-host validation + legacy regression"]
    M20 --> M21["M21 resume post-M16 rollout"]
    M21 --> M15["M15 selective multi-executor scheduling"]
```

## Risks and Dependencies

- the daemon-host baseline is now implemented, but release packaging, version entry, and broader dogfooding still need to catch up
- the first host bridge is intentionally the VS Code extension frontend; “type continue into an existing chat box” should not become the main architecture
- `M15` still applies only to safe parallel work; if tasks touch the same files, control surfaces, or abstraction boundaries, they should stay on one primary write line
- `M8 / M9` remain important, but they stay bounded as supporting backlog instead of reclaiming the mainline
- any future web / remote host support needs new runtime, transport, and trust-boundary design instead of reusing desktop-local assumptions blindly

## Behavior Backlog

| Topic | Why It Matters | Current Position |
| --- | --- | --- |
| daemon-host baseline hardening and dogfooding | `M17-M21` are complete, but retention will depend on whether the baseline stays fast and stable in real use | active / current mainline |
| issue-driven closure loop | when a durable problem is identified, the skill should eventually auto-run the chain `devlog -> architecture -> roadmap/development plan -> long implementation run` | supporting backlog / todo |
| control-truth synchronization determinism | when users run `project assistant continue`, `.codex/status.md`, `.codex/plan.md`, `strategy / program-board / delivery / PTL / handoff`, and `continue / progress / handoff` should stop feeling out of sync | supporting backlog / todo |
| stronger host surfaces | Webview dashboards, chat participants, and web/remote hosts should be built only after the daemon-host baseline is trusted | later / supporting backlog |

## Strategic Direction

| Topic | Why It Matters | Current Position |
| --- | --- | --- |
| daemon-first async execution, host resume bridge, and latency governance | the original latency complaint is now embodied in a working baseline: daemon runtime, host live status, and continue bridge ship together; the next job is to make that path stable and adoptable | active in roadmap and development plan |
| business planning and program orchestration | `project-assistant` has completed the PTL-centered `M10 / M11 / M12 / M13 / M14 / M16` layers; `M15` remains an evidence-gated later layer | active in roadmap and development plan |
| issue-driven closure loop | when a durable problem is identified, the skill should eventually auto-trigger `devlog -> architecture -> roadmap/development plan -> long implementation run` rather than depending on repeated human prompts | supporting backlog / todo |

Direction docs:

- [Strategic Planning And Program Orchestration](reference/project-assistant/strategic-planning-and-program-orchestration.md)
- [Host Resume Bridge And VS Code Feasibility](reference/project-assistant/host-resume-bridge.md)
