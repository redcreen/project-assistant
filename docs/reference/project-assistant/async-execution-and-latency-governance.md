# Async Execution And Latency Governance

[English](async-execution-and-latency-governance.md) | [中文](async-execution-and-latency-governance.zh-CN.md)

## Purpose

This note turns the user-reported speed problem into a named design track and now records the chosen direction:

`daemon-first PTL scheduling, with a write-safe fast-upgrade version that improves coding speed first and validates older features immediately after.`

It answers:

`which work should stay synchronous, which work should default to async, and what architecture should carry that policy long term?`

## North-Star Alignment

This track cannot be designed only as “build a faster executor.”

It still has to serve the original purpose of `project-assistant`:

`help humans write project code in a more disciplined and professional way while keeping their attention on requirements, direction, boundaries, and tradeoffs instead of process detail and process control.`

So latency work here is not about adding a heavier control layer. It is about moving process burden off the human path.

## Templated And Pre-Generated Docs As An Accelerator

This track should not focus only on async execution. It should also speed up the doc layer.

One direction is now explicitly aligned:

- add templated and pre-generated document scaffolds where they reduce time-to-truth
- use them to establish the first version of `brief / architecture / roadmap / test-plan / development-plan / status`
- keep human attention on the parts that actually need discussion and judgment

The boundary is equally important:

- templates are an accelerator, not new process weight
- pre-generated content should stay trim, editable, and incrementally refreshable
- template completeness must not be allowed to hurt first-screen speed or mainline flow

## Problem Statement

The issue is no longer “some scripts feel slow.”

The user is explicitly reporting that:

- too much work still runs synchronously and interrupts the active coding line
- the skill feels too heavy for day-to-day development
- if the experience stays this slow, the skill risks being removed entirely
- PTL behavior should feel like pre-briefing, review, and checkpoint feedback, not constant inline interference

This means the problem is now a product-retention problem, not only a local optimization problem.

## Hard Requirements

| Requirement | Meaning |
| --- | --- |
| async by default when safe | any task that does not need to block the active write lane should move to a background lane |
| sync work must stay very short | the preferred sync budget is tighter than “about a minute”; long inline blocking should become exceptional |
| long tasks need ETA | users should know whether to wait, keep coding, or leave the task running |
| the main write line stays protected | background work must not compete with or randomly interrupt the active coding thread |
| PTL should supervise, not hover | the PTL should act through pre-briefing, checkpoint review, and event-driven escalation |

## Updated Direction

The target architecture is now:

`daemon-first PTL scheduler`

But the implementation strategy is:

`write-safe fast upgrade first`

That means:

- move background-capable work behind a persistent daemon quickly
- improve the user’s coding speed first
- keep business-code writes on the protected foreground lane in the first upgrade
- validate older feature families one by one after the daemon baseline lands

With one additional method constraint:

- neither the daemon nor the template system may pull the human back into process-heavy control work

## Options Re-evaluated

| Option | Shape | Current Judgment |
| --- | --- | --- |
| A. keep the current sync model and only optimize scripts | local speed fixes only | rejected; not enough to save usability |
| B. add a background-first execution model without a persistent daemon | rules first, runtime later | useful as a stepping stone, but no longer the target architecture |
| C. build a daemon-like always-on PTL scheduler | persistent runtime, queue, ETA, checkpoint review, background execution | chosen target architecture |

## Chosen Architecture

### 1. Foreground / Background Split

| Lane | What Belongs Here | First-Version Rule |
| --- | --- | --- |
| protected foreground write lane | active code-writing task, user-facing judgment, short safety checks | keep exactly one primary write lane |
| background checkpoint lane | validators, snapshots, progress/handoff generation, docs sync, control-surface refresh, benchmark/audit work | async by default |
| background long-run lane | long scans, release-ready checks, packaging, repo-wide retrofit analysis | async with ETA |

### 2. Sync Budget

Recommended operating bands for the fast upgrade:

| Band | Rule |
| --- | --- |
| `0-10s` | may run inline silently |
| `10-30s` | may run inline, but should report expectation |
| `>30s` | should default to background unless the user explicitly wants to wait |
| `>60s` | should not block inline by default |

### 3. PTL Behavior

The daemon-backed PTL should work like this:

1. pre-brief the worker before the slice starts
2. let the worker run without constant interference
3. watch queue events, failures, completions, and checkpoints
4. review at checkpoints
5. escalate only on boundary, priority, compatibility, cost, or policy changes

## Why Daemon-First

| Benefit | Why it matters |
| --- | --- |
| coding speed improves first | background-capable support work stops blocking the mainline |
| ETA becomes natural | a daemon can own queue state, runtime, and duration bands |
| PTL becomes realistic | supervision turns into checkpoint/event logic instead of inline micromanagement |
| validation becomes easier to stage | once the daemon baseline lands, older features can be re-verified one family at a time |
| template generation is easier to move off the mainline | scaffold generation and doc-alignment refreshes can run behind active coding |

## Risks

| Risk | Why it matters | First mitigation |
| --- | --- | --- |
| background work touches the wrong files | could corrupt the protected write lane | first upgrade keeps business-code writes out of daemon automation |
| daemon state drifts from durable truth | users see inconsistent status | keep durable control truth in `.codex/*` and separate runtime queue state |
| the daemon becomes a black box | users stop trusting the system | require queue status, ETA, cancel, retry, and clear task ownership |
| rollout gets too big | fast upgrade never ships | ship a narrow MVP first, then validate older features in slices |

## Fast Upgrade Version

The first upgrade should optimize for immediate developer experience, not completeness.

### Scope

- persistent local PTL daemon
- task queue with `queued/running/waiting-checkpoint/completed/failed/cancelled`
- ETA or duration bands
- one protected foreground write lane
- background execution for safe support-work families only
- fast paths for templated and pre-generated document scaffolds
- checkpoint-based result reporting
- kill switch and fallback to the current non-daemon path

### Not In First Version

- automatic background business-code writes
- multi-worker code-edit scheduling
- cross-host or multi-desktop orchestration
- aggressive auto-resequencing of the main write line
- extra foreground blocking in the name of “fuller templates”

## Validation Strategy After The Fast Upgrade

Do not wait for every old feature to be daemon-native before shipping the first upgrade.

Ship the fast upgrade first, then validate older features in ordered slices:

1. daemon queue health, ETA, cancel, retry, and checkpoint reporting
2. `continue / progress / handoff`
3. `bootstrap / retrofit / docs-retrofit`
4. control-surface and docs validators
5. development-log and release-adjacent flows
6. broader rollout verification on representative repos

## Proposed Rollout

| Phase | Goal |
| --- | --- |
| Phase 1 | design and lock the daemon-first architecture plus the write-safe fast upgrade scope |
| Phase 2 | ship the PTL daemon fast upgrade to speed up active coding |
| Phase 3 | validate the previous feature set one family at a time on top of the daemon baseline |
| Phase 4 | widen async coverage only after the baseline is trusted |

## Open Decisions

1. Which local runtime store should hold daemon queue state?
2. What exact command/UI surface should expose queue status, ETA, cancel, and retry?
3. Which validator and sync families enter the first daemon-managed set?
4. What should the first “feature re-validation” order be after the upgrade lands?
