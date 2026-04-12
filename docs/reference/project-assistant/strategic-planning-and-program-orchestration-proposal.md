# Strategic Planning And Program Orchestration Proposal

[English](strategic-planning-and-program-orchestration-proposal.md) | [中文](strategic-planning-and-program-orchestration-proposal.zh-CN.md)

## Purpose

This document proposes the next major layer above the current `project-assistant` operating model:

- strategic evaluation
- program orchestration
- supervised long-run delivery

It is not active implementation truth yet. It is the proposal that should be reviewed before becoming roadmap work.

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

## Proposed Role Model

| Layer | Primary Owner | Responsibility |
| --- | --- | --- |
| Business Direction | human | define needs, priorities, product direction, and major tradeoffs |
| Strategic Planning | AI strategic planner | decide what should happen next, whether special governance / architecture tracks should be inserted, whether roadmap structure should change, and whether project positioning should be elevated |
| Program Orchestration | AI program orchestrator | manage multiple workstreams, slices, dependencies, and execution agents over time |
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

## Proposed Milestones

### M10: Strategic Evaluation

| Item | Proposed Meaning |
| --- | --- |
| Goal | evaluate where the project should go next, whether special governance / architecture work should be inserted, and whether earlier milestones or project positioning should change |
| Output | durable strategic proposal, not automatic roadmap edits |
| Human Role | review and approve or reject strategy changes |
| Exit Criteria | strategy recommendations become explicit, reviewable, and tied to real repo evidence |

### M11: Program Orchestration

| Item | Proposed Meaning |
| --- | --- |
| Goal | coordinate multiple workstreams, slices, and execution agents instead of only one active execution line |
| Output | a durable program board that tracks active streams, sequencing, parallelism, and orchestration checkpoints |
| Human Role | approve orchestration boundaries and escalation policy |
| Exit Criteria | the system can keep several related slices moving without constant human prompts |

### M12: Supervised Long-Run Delivery

| Item | Proposed Meaning |
| --- | --- |
| Goal | let the AI delivery system keep advancing long-running work until completion or a real business decision point |
| Output | longer-lived supervised execution runs with periodic checkpoints, automatic escalation, and durable recovery truth |
| Human Role | intervene when direction changes or tradeoffs need approval |
| Exit Criteria | humans mainly provide direction and decisions, not constant continuation prompts |

## Proposed New Durable Surfaces

| Surface | Purpose |
| --- | --- |
| `.codex/strategy.md` | current strategic judgment, proposed track insertions, roadmap-change proposals, and human decision points |
| `.codex/program-board.md` | active workstreams, orchestration state, sequencing, parallel-safe slices, and supervising checkpoints |

These should sit alongside existing control-surface files, not replace them.

## Automation Boundary

| The System May Do Automatically | The System Must Escalate |
| --- | --- |
| propose governance or architecture side-tracks | change product direction |
| propose roadmap reshaping | change external promises |
| orchestrate multiple slices within an approved direction | change compatibility commitments |
| keep long-running work moving until a checkpoint | approve large cost or schedule shifts |
| re-prioritize technical sequence within approved scope | accept requirement changes without human review |

## Suggested Rollout Order

1. define the strategic-evaluation document shape and review contract
2. make strategy output evidence-backed rather than opinion-only
3. introduce a lightweight program board
4. allow orchestration across multiple slices only after the board and escalation rules are stable
5. only then consider longer supervised execution loops

## Review Questions

Before promoting this proposal into active roadmap work, confirm:

1. should `project-assistant` remain a single-repo delivery system, or expand into a multi-repo/multi-agent orchestrator?
2. should strategic evaluation remain proposal-only, or eventually gain authority to rewrite roadmap sections automatically under gates?
3. what is the acceptable limit for “automatic long-run work” before human re-approval is required?
4. what durable evidence must exist before the system is allowed to insert governance or architecture side-tracks by itself?

## Current Recommendation

Do not activate this layer immediately.

Finish:

- M8 locale-aware internal output
- M9 slimmer continue / resume

Then revisit this proposal and decide whether it becomes:

- a new milestone line in the roadmap
- an experimental mode
- or a separate skill/plugin layer above `project-assistant`
