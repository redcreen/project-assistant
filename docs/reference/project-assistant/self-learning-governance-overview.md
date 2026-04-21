# Self-Learning Governance Overview

[English](self-learning-governance-overview.md) | [中文](self-learning-governance-overview.zh-CN.md)

## Purpose

This document consolidates the current self-learning discussion for `project-assistant` into one reviewable overview.

It answers six questions:

1. what problem we are actually solving
2. whether this is the same as the earlier `growware` contract discussion
3. how far rule separation has already gone in the current project
4. how rules should be layered and governed going forward
5. what kinds of learning assets should exist
6. which assets can later guide AI behavior in new projects

## One-Line Conclusion

The real goal is not "make the assistant secretly smarter."

The real goal is:

`let project-assistant act as an upstream governance layer that continuously turns human behavior and assistant failures into reviewable improvement proposals, then promotes accepted proposals into rules, judges, gates, templates, and regression assets that can constrain later AI work.`

## The Real Problem Definition

The first symptom was:

`stop making me repeat the same corrections.`

But that is only the symptom.

The upgraded problem definition is:

`build a governed self-improvement loop for the assistant, and make that loop valuable not only inside the current project but also across future projects.`

## Non-Goals

The current goal is not:

- silently rewriting the assistant without review
- turning raw chat history directly into durable rules
- building a broad "memory system" before the rule model is clear
- mixing project rules, personal preferences, and runtime state
- using the install directory as the primary learning store

## Relationship To Growware

This discussion did not start from zero.

The `growware` repo already contains a more mature contract stack that is directly relevant here:

- `shared-policy-contract`
- `policy-loading`
- `learning-writeback`
- `regression-assets`

## Where The Two Discussions Already Agree

| Topic | `growware` contract position | current `project-assistant` discussion |
| --- | --- | --- |
| rule ownership | rules belong to the project, not the executor | agreed |
| doc vs machine layer | humans edit docs, executors load machine policy | agreed |
| runtime rule invention | when policy is unclear, the executor must not invent rules from chat memory | agreed |
| learning writeback | resolved work should become a proposal, not silently active policy | agreed |
| reusable assets | resolved work should later become `rule / judge / regression asset / deferred-gap` style assets | agreed |

## Where They Are Not The Same

| Dimension | `growware` emphasizes | current `project-assistant` discussion emphasizes |
| --- | --- | --- |
| center of gravity | how project policy becomes executable machine policy | how experience is first learned from human corrections and assistant failures |
| main scope | project-level policy and executor contracts | user/workspace/project/cross-project promotion paths |
| first priority | source policy, machine layer, approval contract | proposals, review, promotion, rule library |
| primary risk | executors must not become lawmakers | assistants must not secretly learn and rewrite themselves |

So the two systems are not in conflict.

They are better understood as upstream and downstream layers:

- `growware` is closer to the project-policy execution layer
- this `project-assistant` design is closer to the upstream learning and promotion layer

## Current Rule Separation State

The project already separates several kinds of "rules," but not all of them.

### Layers That Already Exist

| Layer | Current landing surface | State |
| --- | --- | --- |
| tool defaults | `SKILL.md`, [../../../agents/openai.yaml](../../../agents/openai.yaml) | present |
| repo durable rules | `.codex/*`, `docs/*`, `.codex/doc-governance.json` | present |
| runtime state | `~/.codex/daemon/<repo-id>/`, VS Code `workspaceState` | present |

### Layers That Are Not Fully Implemented Yet

| Layer | Current state |
| --- | --- |
| learned rule library | designed, not fully implemented |
| cross-project promoted rule library | still planning-stage only |
| stable precedence across project-local / user-global / domain / global layers | not yet encoded as a hard contract |

## Recommended Rule Layering Model

To avoid future confusion, the rule model should be fixed into five layers.

### 1. shipped-base

Sources:

- `SKILL.md`
- `agents/openai.yaml`
- fixed contracts shipped in the skill repo

Properties:

- versioned with the tool
- upgradeable and overwriteable
- must not be directly rewritten by the learning loop

### 2. project-policy

Sources:

- repo-owned policy docs, architecture, roadmap, test-plan, `.codex/doc-governance.json`, and other durable truth

Properties:

- owned by the project
- versioned in Git
- reviewable and durable

### 3. machine policy layer

Sources:

- compiled machine-readable outputs derived from project policy sources

Properties:

- this is what executors actually load
- assistants should not invent this layer at runtime from memory

### 4. learned registry

Sources:

- human corrections
- human behavior
- assistant failures
- failure close-outs
- repeated review and approval outcomes

Properties:

- starts as candidate / proposal records
- becomes stable only after review
- can have `project-local`, `workspace-local`, `user-global`, `domain-pack`, and `global-promoted` variants

### 5. runtime state

Sources:

- daemon runtime
- VS Code host `workspaceState`
- recent events, files, and automation state

Properties:

- not durable rule truth
- may be discarded and rebuilt
- must not become the long-term rule store

## Learning Asset Types

To avoid calling everything a "rule," the learning layer should be limited to these six asset types:

| Asset Type | Meaning | Example |
| --- | --- | --- |
| `communication rule` | answer/collaboration preference | give the result first; inspect code before making claims |
| `workflow rule` | execution sequence or process habit | goal -> approach -> architecture -> roadmap -> test-plan -> implementation |
| `judge` | evaluation or decision logic | what counts as drift; when escalation becomes mandatory |
| `gate/checklist` | pre-execution or close-out gates | behavior changes must add validation; schema changes must include migration |
| `template/playbook` | reusable startup or phase template | default new-project doc set and workflow pack |
| `regression asset` | future prevention artifact | test, fixture, replay, failure pattern |

## Learning Signals

The current learning design should prioritize four signal families:

1. explicit human correction
2. implicit human behavior
3. assistant-side failure
4. long-run outcomes

### 1. Explicit Human Correction

Examples:

- "do not answer like this"
- "inspect the code first"
- "default to the result first"

### 2. Implicit Human Behavior

Examples:

- the user keeps skipping one class of output
- the user repeatedly adds the same missing information
- the user repeatedly rejects one class of answer shape

### 3. Assistant Failure

Examples:

- tests fail
- validators fail
- plans are repeatedly reverted
- the same mistake class reappears

### 4. Long-Run Outcomes

Examples:

- which workflows consistently converge faster
- which patterns consistently cause drift, rework, or misjudgment

## Recommended Learning Loop

The loop should be:

`signal -> candidate/proposal -> human review -> accepted stable asset -> local/domain/global promotion -> periodic decay or supersede`

The two critical properties are:

- a proposal is not an active rule
- promotion must preserve provenance and decision trail

## What Project Assistant Should Do First

Among all possible self-learning directions, the most reasonable first slice is still:

`reviewable correction learning`

That means:

- read explicit corrections from local Codex sessions for the current workspace
- generate candidate rules
- surface them clearly in the host sidebar and Status Bar
- let the user accept / reject / snooze
- load accepted rules into later resume / new-thread flows

This is the entry point, not the end state.

## The Larger Goal: Cross-Project Learning

The higher-value capability is the next layer:

`let project-assistant learn from multiple projects, then bring mature experience into new projects to constrain and guide AI behavior.`

So after Phase 1, the system must support:

- `project-local` learning
- `domain-pack` promotion
- `global-promoted` promotion

## What Should Stay Project-Local

The following should usually not be promoted easily:

- business-specific rules
- repo-structure-specific rules
- project-specific approval flows
- project-specific workarounds
- purely personal expression preferences

One-line test:

`if it is not clearly true outside the current project, keep it project-local.`

## What Can Be Brought Into New Projects

These are the most promising cross-project assets:

- `workflow rule`
- `judge`
- `gate/checklist`
- `template/playbook`

They are good candidates because they:

- repeat across projects
- do not depend on one business domain
- reduce rework, misjudgment, or repeated correction
- can be expressed clearly as rules, judges, gates, or templates

## Promotion Path

### project-local

Rules repeatedly validated inside the current project.

### domain-pack

Rules repeatedly validated inside similar projects.

Examples:

- SaaS backend
- CLI tools
- rich frontend apps
- AI agent systems
- VS Code extensions

### global-promoted

High-confidence rules that still hold across domains and project types.

## Suggested Promotion Thresholds

### candidate -> accepted local

Requires at least:

- clear evidence
- a stable expression as rule, judge, or checklist
- human acceptance
- no conflict with active project policy

### accepted local -> domain-pack

Requires at least:

- validity in two or more similar projects
- repeated acceptance or retention
- clear evidence of benefit
- a clear applicability boundary

### domain-pack -> global-promoted

Requires at least:

- continued validity across domains
- low conflict rate
- independence from one business meaning
- stricter human review

## Recommended Precedence Stack

To keep layers from fighting, use this precedence:

`project policy > project-local accepted rules > domain-pack > user-global accepted rules > global-promoted > shipped-base > runtime hints`

This implies:

- project policy always outranks learned rules
- runtime hints must never override durable rules

## Reinstall And Persistence

The discussion has already converged on one hard rule:

`installable code != learned data`

### Where Learned Data Should Not Live

- the skill install directory
- the extension install directory
- the daemon runtime store

### Recommended Placement

The future learned registry should live in a separate root such as:

- `~/.codex/registry/project-assistant/workspaces/<workspace-id>/candidates.jsonl`
- `~/.codex/registry/project-assistant/workspaces/<workspace-id>/stable-rules.json`
- `~/.codex/registry/project-assistant/global/stable-rules.json`

### Export Into The Project

Only after explicit approval should accepted learning be exported into the repo machine-policy layer, for example:

- `.codex/policy-input/learning-rules.json`
- `.codex/policy-input/learning-rules.md`

## Consolidated Outcome Of This Discussion

At this point, the discussion can be reduced to these statements:

1. the self-learning goal for `project-assistant` is not just reducing repeated correction; it is building a governed self-improvement loop
2. the larger value is not inside `project-assistant` alone, but in carrying mature experience into new projects to guide AI behavior
3. the `growware` contracts already define the project-policy execution layer; `project-assistant` still needs the upstream learning, proposal, promotion, rule-library, and cross-project promotion layer
4. rules must be layered explicitly so install-time defaults, project policy, learned rules, and runtime state no longer blur together
5. `reviewable correction learning` is still the right first slice, but the long-term target must expand into a multi-asset system covering `rule / judge / gate / template / regression asset`

## Recommended Next Step

If the discussion should turn into a stricter design contract, the next things worth freezing are:

1. the learning-asset schema
2. promotion / decay rules
3. precedence and conflict handling across rule layers
4. promotion thresholds for project-local, domain-pack, and global-promoted assets

## Related Docs

- [correction-driven-self-learning.md](correction-driven-self-learning.md)
- [project-origin-and-working-method.md](project-origin-and-working-method.md)
- [ptl-daemon-mvp.md](ptl-daemon-mvp.md)
- [host-resume-bridge.md](host-resume-bridge.md)
- [ai-coding-modes-comparison.md](ai-coding-modes-comparison.md)
- `growware` repo: `shared-policy-contract`
- `growware` repo: `policy-loading`
- `growware` repo: `learning-writeback`
- `growware` repo: `regression-assets`
