# Strategic Planning And Program Orchestration Direction

[English](strategic-planning-and-program-orchestration.md) | [中文](strategic-planning-and-program-orchestration.zh-CN.md)

## Status

This document records the approved next major direction above the current `project-assistant` operating model:

- strategic evaluation
- program orchestration
- supervised long-run delivery

This direction is now part of the official roadmap. M10 strategic evaluation, M11 program orchestration, and M12 supervised long-run delivery are complete. M8 and M9 are no longer the mainline; they remain bounded supporting backlog topics inside this strategic layer, while rollout / friction collection becomes the current durable follow-through so any post-M12 milestone is driven by real adoption evidence.

The standing role across these three layers is named:

- Project Technical Lead (PTL)

## Why This Layer Is Needed

`project-assistant` already does a lot of the execution-side work well:

- control surfaces
- long execution lines
- architecture supervision
- progress / continue / handoff
- docs retrofit and markdown governance
- development logs
- validation and release gates

What it does not yet fully handle is the higher-level question:

`how should a project evolve next, and who keeps long-running multi-slice work aligned when the human is not constantly steering?`

That gap shows up in several recurring situations:

| Situation | Why Current Layers Are Not Enough |
| --- | --- |
| A project keeps surfacing root-cause drift and side work | execution can continue, but there is no explicit strategic layer deciding whether to insert a governance or architecture track |
| Earlier milestones no longer fit reality | current layers can show drift, but they do not yet own roadmap reshaping proposals |
| A project grows beyond one slice or one worker | execution boards help locally, but there is no formal orchestration layer across multiple streams |
| Humans mainly want to set direction, not babysit delivery | current flows reduce babysitting, but they do not yet define a higher-level supervising role that keeps delivery moving until a true business decision is needed |

## Role Model

| Layer | Primary Owner | Responsibility |
| --- | --- | --- |
| Business Direction | human | define needs, priorities, product direction, and major tradeoffs |
| Strategic Planning | Project Technical Lead (PTL) | decide what should happen next, whether special governance / architecture tracks should be inserted, whether roadmap structure should change, and whether project positioning should be elevated |
| Program Orchestration | Project Technical Lead (PTL) | manage multiple workstreams, slices, dependencies, and execution agents over time |
| Delivery Execution | AI delivery workers | implement code, tests, docs, validation, and control-surface updates |
| Governance And Recovery | existing `project-assistant` layers | keep truth, gates, progress, devlogs, docs, and handoff aligned |

## Key Principle

The human should remain responsible for:

- business direction
- product positioning
- major compatibility choices
- significant cost / timeline tradeoffs
- requirement changes

The AI system should increasingly handle:

- strategic evaluation proposals
- long-run orchestration inside an approved direction
- continued execution across slices
- surfacing when a human decision is genuinely required

PTL here is not a product owner and not an organization-wide CTO. It is a project-scoped technical lead role:

| PTL Owns | PTL Does Not Own |
| --- | --- |
| strategic evaluation, program orchestration, long-run delivery supervision, escalation timing | business-direction changes, product priorities, major compatibility commitments, cost tradeoffs |

## Milestone Direction

### M10: Strategic Evaluation

| Item | Current Meaning |
| --- | --- |
| Goal | evaluate where the project should go next, whether special governance / architecture work should be inserted, and whether earlier milestones or project positioning should change |
| Output | durable PTL strategic judgment and reviewable strategy surfaces, not automatic business-direction edits |
| Human Role | review and approve or reject strategy changes |
| Exit Criteria | strategy recommendations become explicit, reviewable, and tied to real repo evidence |

### M11: Program Orchestration

| Item | Current Meaning |
| --- | --- |
| Goal | coordinate multiple workstreams, slices, and execution agents instead of only one active execution line |
| Output | a durable PTL program board that tracks active streams, sequencing, parallelism, and orchestration checkpoints |
| Human Role | approve orchestration boundaries and escalation policy |
| Exit Criteria | the system can keep several related slices moving without constant human prompts |

| Current Boundary | Meaning |
| --- | --- |
| Already done now | a durable orchestration-truth layer inside one Codex: it knows active workstreams, parallel-safe boundaries, serial dependencies, and what PTL / delivery worker / docs-and-release currently own |
| Not done yet | a productized command that automatically spins up multiple desktop Codex sessions, dispatches work, and merges results back |
| Future path | only create a separate multi-executor orchestration layer if rollout evidence shows that the single-Codex orchestration truth is no longer enough |

### M12: Supervised Long-Run Delivery

| Item | Current Meaning |
| --- | --- |
| Goal | let the AI delivery system keep advancing long-running work until completion or a real business decision point |
| Output | longer-lived PTL-supervised execution runs with periodic checkpoints, automatic escalation, and durable recovery truth |
| Human Role | intervene when direction changes or tradeoffs need approval |
| Exit Criteria | humans mainly provide direction and decisions, not constant continuation prompts |

## Durable Surfaces

| Surface | Purpose |
| --- | --- |
| `.codex/strategy.md` | current strategic judgment, proposed track insertions, roadmap-change proposals, and human decision points |
| `.codex/program-board.md` | active workstreams, orchestration state, sequencing, parallel-safe slices, and supervising checkpoints; today it first carries the single-Codex coordination truth |
| `.codex/delivery-supervision.md` | checkpoint rhythm, automatic-continue boundaries, escalation timing, executor supervision loop, and backlog re-entry rules |

These should sit alongside existing control-surface files, not replace them.

For the current single-Codex orchestration model versus a future multi-executor layer, see:

- [orchestration-model.md](orchestration-model.md)

## Automation Boundary

| The System May Do Automatically | The System Must Escalate |
| --- | --- |
| propose governance or architecture side-tracks | change product direction |
| propose roadmap reshaping | change external promises |
| orchestrate multiple slices within an approved direction | change compatibility commitments |
| keep long-running work moving until a checkpoint | approve large cost or schedule shifts |
| re-prioritize technical sequence within approved scope | accept requirement changes without human review |

## Rollout Order

1. define the strategic-evaluation document shape and review contract
2. make strategy output evidence-backed rather than opinion-only
3. introduce a lightweight program board
4. allow orchestration across multiple slices only after the board and escalation rules are stable
5. only then consider longer supervised execution loops

## Current Approval Boundary

The direction is approved, but its authority remains bounded:

1. `project-assistant` may propose roadmap reshaping, governance tracks, and architecture tracks.
2. It may not auto-change business direction, compatibility promises, or external positioning without human approval.
3. M8 locale-aware output and M9 slimmer continue snapshots now survive as supporting backlog topics under M10 rather than as the mainline.
4. M11 has now closed its durable program board, orchestration boundary, and maintainer-facing snapshots. M12 has also closed supervised long-run delivery into a durable `delivery-supervision` surface.
5. The next step is rollout / friction collection rather than naming another internal milestone first; post-M12 direction should come from real adoption evidence.
6. If a future multi-desktop-Codex / multi-executor scheduler is needed, it should become a separate later layer rather than silently expanding M11's current scope.
