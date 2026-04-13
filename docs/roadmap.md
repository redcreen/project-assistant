# Roadmap

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## Scope

This roadmap describes the evolution of the `project-assistant` skill itself. It does not replace current execution truth from `.codex/status.md`.

Detailed execution queue:

- [project-assistant/development-plan.md](reference/project-assistant/development-plan.md)

## Now / Next / Later

| Horizon | Focus | Exit Signal |
| --- | --- | --- |
| Now | lock the default fast-upgrade build order: `daemon core -> VS Code host shell -> resume bridge -> local workspace validation`, so implementation can start slice by slice from roadmap / plan | the first host, build order, resume level, and local validation boundary are explicit enough for direct implementation |
| Next | build the daemon core, VS Code host frontend, and continue-resume bridge in order, then validate that MVP on representative local workspaces | users can see live status in VS Code, resume work through the host, and confirm that active coding feels materially lighter |
| Later | re-validate older feature families on the daemon-host baseline, resume post-M16 rollout verification, and only then consider chat-surface integration, web/remote hosts, or more aggressive auto-resume | do not mix daemon core, host bridge, old-feature re-validation, and farther chat integration into one release |

## Milestones

| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |
| [M1](reference/project-assistant/development-plan.md#m1) | done | establish `.codex` control surface and tiering | core skill routing | current state is recoverable |
| [M2](reference/project-assistant/development-plan.md#m2) | done | establish convergent retrofit | control-surface scripts | retrofit no longer stops midway |
| [M3](reference/project-assistant/development-plan.md#m3) | done | establish progress and handoff workflows | module layer + snapshot scripts | progress and handoff are stable |
| [M4](reference/project-assistant/development-plan.md#m4) | done | establish durable-doc standards and doc validation | document standards + docs scripts | durable docs pass structural gates |
| [M5](reference/project-assistant/development-plan.md#m5) | done | establish bilingual public-doc switching and validation | i18n rules + i18n validator | public docs switch cleanly between English and Chinese |
| [M6](reference/project-assistant/development-plan.md#m6) | done | shift to an embedded architect-assistant operating model | previous milestones | planning, execution, architecture supervision, and devlog capture are default-on behaviors |
| [M7](reference/project-assistant/development-plan.md#m7) | done | improve narrative quality and automated architecture triggers | [M6](reference/project-assistant/development-plan.md#m6) | less manual cleanup after retrofit and fewer direction-correction prompts |
| [M8](reference/project-assistant/development-plan.md#m8) | deferred | locale-aware internal control-surface output | handoff + command templates + validation policy | becomes a bounded supporting backlog topic under M10 instead of the mainline |
| [M9](reference/project-assistant/development-plan.md#m9) | deferred | automatic context compression plus slimmer continue/resume/handoff snapshots without losing recoverability | continue snapshot + handoff + validation policy | becomes a bounded supporting backlog topic under M10 instead of the mainline |

## Strategic Layer Milestones

| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |
| [M10](reference/project-assistant/development-plan.md#m10) | done | add a strategic-evaluation layer above execution and retrofit | [M7](reference/project-assistant/development-plan.md#m7) + approved strategic direction | the system can produce durable strategy judgments, track when governance/architecture tracks should be inserted, and keep business-direction changes gated to humans |
| [M11](reference/project-assistant/development-plan.md#m11) | done | add a program-orchestration layer across multiple slices or workers | [M10](reference/project-assistant/development-plan.md#m10) + durable program board | the system can coordinate multiple related slices without constant human continuation prompts |
| [M12](reference/project-assistant/development-plan.md#m12) | done | add supervised long-run delivery | [M11](reference/project-assistant/development-plan.md#m11) + stable escalation policy | long-running delivery can continue until a real business decision point instead of stopping for routine steering |
| [M13](reference/project-assistant/development-plan.md#m13) | done | add a PTL supervision loop so the project keeps a standing technical lead even after a worker stops | [M12](reference/project-assistant/development-plan.md#m12) + durable delivery supervision | the PTL can inspect, continue, re-sequence, or escalate through periodic and event-driven checks without relying on repeated human continuation prompts |
| [M14](reference/project-assistant/development-plan.md#m14) | done | add worker handoff and re-entry so unfinished work can be resumed, reassigned, or re-queued instead of dying with the worker | [M13](reference/project-assistant/development-plan.md#m13) + durable handoff / supervision truth | after a checkpoint, timeout, failure, or handoff, the remaining work still has a durable path forward |
| [M15](reference/project-assistant/development-plan.md#m15) | later | add selective multi-executor scheduling only for safe parallel work | [M14](reference/project-assistant/development-plan.md#m14) + disjoint write scopes + conflict control | true parallel execution is only allowed when write boundaries, merge paths, and conflict gates are explicit |
| [M16](reference/project-assistant/development-plan.md#m16) | done | add a tool-first front door and hard-entry bridge so `continue / progress / handoff` must pass through one router, version preflight, and structured first-screen contract | [M14](reference/project-assistant/development-plan.md#m14) + versioned control surface + entry scripts | legacy repos auto-upgrade before resume, and the first screen no longer falls back to free-form prose |

## Milestone Flow

```mermaid
flowchart LR
    M1["M1 Control Surface"] --> M2["M2 Convergent Retrofit"]
    M2 --> M3["M3 Progress + Handoff"]
    M3 --> M4["M4 Document Standards"]
    M4 --> M5["M5 Public Doc I18n"]
    M5 --> M6["M6 Embedded Architect Assistant"]
    M6 --> M7["M7 Better Narrative + Triggers"]
    M7 --> M10["M10 Strategic Evaluation"]
    M10 --> M11["M11 Program Orchestration"]
    M11 --> M12["M12 Supervised Long-Run Delivery"]
    M12 --> M13["M13 PTL Supervision Loop"]
    M13 --> M14["M14 Worker Handoff And Re-entry"]
    M14 --> M16["M16 Tool-First Front Door"]
    M16 --> M15["M15 Selective Multi-Executor Scheduling"]
```

## Risks and Dependencies

- document sync can scaffold structure faster than it can rewrite polished prose
- default-on architecture supervision must stay high-level first; too much local detail would weaken its value
- long execution lines must stop at real checkpoints, not drift into opaque background work
- public-doc bilingual quality still depends on good content generation, not only file-pair checks
- exact context-usage thresholds still require runtime support
- locale-aware internal output and automatic context compression still matter, but now as bounded supporting backlog under M10 rather than as the mainline
- strategy surfaces must stay evidence-backed and must not auto-change business direction
- program orchestration should not arrive before the strategy layer has a stable review contract
- M13 is not just another abstract layer name; it must make the PTL behave like a standing supervision loop that keeps the project moving
- M14 is not only about restoring chat context; it must let the PTL catch, re-queue, reassign, or resume unfinished work after a worker stops
- M15 only applies to safe parallel work; if two tasks touch the same files, control truth, or abstraction boundary, they should stay out of the multi-executor layer
- M16 is not “just another CLI”; it exists to stop entry correctness from depending on whether the model remembers to call the right script first
- M16 must keep the boundary explicit: the repo now owns a canonical front door and script backend, but it should not falsely claim that the desktop host is already hard-bound
- the first host-resume bridge is now intentionally scoped to a VS Code extension frontend; “type continue into the built-in chat box” is not the mainline architecture

## Behavior Backlog

| Topic | Why It Matters | Current Position |
| --- | --- | --- |
| daemon-first async execution, host resume bridge, and latency governance | users are explicitly saying the skill is close to uninstall territory because it is too slow and too synchronous. The product now needs not only a daemon-backed PTL runtime, but also a host-side resume bridge and live status surfaces. The first implementation target is now a VS Code extension host frontend. | active / current mainline |
| issue-driven closure loop | This request pattern will keep recurring: write the current problem, reasoning, and solution into a devlog, sync the key conclusions into architecture plus roadmap / development plan, and then carry the change through one long implementation run. The skill should eventually do this by default instead of relying on repeated user reminders. | supporting backlog / todo |
| control-truth sync determinism | When a user runs `project assistant continue`, `.codex/status.md`, `.codex/plan.md`, the strategy / program-board / delivery / PTL / handoff surfaces, and the `continue / progress / handoff` outputs should no longer feel partially refreshed, locally stale, or out of sync with one another. | supporting backlog / todo |
| VS Code chat surfaces as an enhancement entry | the VS Code extension can later add `@project-assistant`, slash commands, or language-model tools, but those should not block the first host frontend and resume bridge | later / supporting backlog |

## Strategic Direction

| Topic | Why It Matters | Current Position |
| --- | --- | --- |
| daemon-first async execution, host resume bridge, and latency governance | the current user feedback is now at product-retention severity: what matters is not only background-first policy, but a daemon runtime plus a host-side resume bridge and live UI that remove process drag from active coding. | active in roadmap and development plan |
| business planning, orchestration, and hard-entry routing | `project-assistant` has now closed the PTL-centered `M10 / M11 / M12 / M13 / M14` layers and added `M16` to make `continue / progress / handoff` pass through one canonical front door; `M15` stays evidence-gated later, and M8/M9 remain bounded supporting backlog topics | active in roadmap and development plan |
| issue-driven closure loop | When a durable problem is identified, the skill should eventually auto-run the loop `devlog -> architecture -> roadmap / development plan -> long-task implementation` instead of waiting for the user to restate the sequence | supporting backlog / todo |

Direction document:

- [Strategic Planning And Program Orchestration Direction](reference/project-assistant/strategic-planning-and-program-orchestration.md)
- [Host Resume Bridge And VS Code Extension Feasibility](reference/project-assistant/host-resume-bridge.md)
