# PTL Role And Governed Learning

[English](ptl-role-and-governed-learning.md) | [中文](ptl-role-and-governed-learning.zh-CN.md)

## Purpose

This document turns the current PTL discussion into an executable role definition.

It answers five questions:

1. what the PTL is responsible for
2. how the PTL can work reliably instead of staying as a chat reminder
3. whether PTL policy packs should be generated automatically
4. what humans still need to decide
5. how the same PTL mechanism applies to `style engine` and `openclaw-skills`

## One-Line Definition

The PTL is the technical lead control layer for a project.

It is not another chat persona and not a background business-code worker. It reviews AI worker action before and after execution, with focus on technical direction, boundaries, rules, reusability, and escalation.

In short:

`The PTL constrains AI work so it follows project goals, and turns repeated failures or corrections into reviewable project rules.`

## Why PTL Exists

AI workers in real repositories often fail in ways that are not raw coding failures:

- they fix symptoms instead of root causes
- they skip the smallest feasibility probe and invest heavily before proving the route can work
- they use non-reusable workarounds to improve one local result
- they treat one successful experiment as a project conclusion
- they forget existing project docs, boundaries, and release rules
- they lose project continuity after a stop, timeout, or failed run
- they receive the same human correction repeatedly, but the correction remains only in chat

The PTL turns these risks into an observable, governed, executable control layer.

## What PTL Is Not

| Not | Why |
| --- | --- |
| Not the product owner | business direction, cost, and external commitments remain human decisions |
| Not an organization-wide CTO | it operates at project or workspace scope |
| Not a background business-code writer | the first version protects the foreground write line |
| Not a silent self-modifier | learning outputs must become candidates before activation |
| Not a full-repo live scanner | reliability and latency require event and checkpoint behavior |
| Not a pile of hardcoded project branches | project differences belong in policy packs, not engine code |

## Core Responsibilities

### 1. Direction

The PTL decides whether the current work still belongs on the project line.

It answers:

- which active slice should continue
- whether the current work is mainline, experiment, support backlog, or fallback
- whether roadmap, development plan, and status have drifted
- whether to resequence the line or insert a governance slice

### 2. Boundaries

The PTL decides what can continue automatically and what must warn or escalate.

Typical boundaries include:

- business direction changes
- compatibility promises
- external-system writes
- cost or time boundaries
- release or user-visible behavior
- authoritative data-source changes

### 3. Feasibility First

The PTL must prove that the chosen route can plausibly work before allowing a long implementation run.

It should require the smallest useful feasibility probe when the task depends on an uncertain external surface, host capability, API, binary, plugin mechanism, protocol, or undocumented behavior.

It must answer:

- what exact assumption must be true
- what command, fixture, source check, or smoke proves it
- what result would make the route impossible or too expensive
- whether a cheaper path exists before writing production code or broad docs
- whether the work should stop, shrink, or switch layer before more implementation

### 4. Workaround Control

The PTL separates "works now" from "is maintainable".

It should catch:

- one-image tuning presented as a general method
- prompt, mask, seed, or temp-path dependencies
- adapters reimplementing business logic
- smoke tests that hit the wrong entry point
- project rules that exist in docs but not in execution gates

### 5. Rules And Gates

The PTL compiles project docs, module boundaries, tests, and human corrections into executable policy.

Rules should be read through:

- project policy
- module policy
- domain policy packs
- learned registry
- preflight gates
- checkpoint review

### 6. Continuity

The PTL keeps the project resumable after a worker stops.

It maintains:

- active slice
- execution line
- task board
- architecture signal
- escalation gate
- next checkpoint
- handoff and resume truth

### 7. Learning

The PTL learns from human behavior, AI failures, and project outcomes.

The learning loop is governed:

`signal -> candidate -> review -> accepted rule -> policy injection -> observation -> promotion or decay`

The PTL can discover and normalize. It must not silently legislate.

## Operating Levels

| Level | Responsibility | Performance Strategy | Blocking |
| --- | --- | --- | --- |
| L0 intent router | classify task type, module, risk, and policy packs | read small indexes and path rules | sync, target 0-3s |
| L1 preflight gate | decide `allow / warn / require-review / block` | deterministic rules before model calls | block only hard risk |
| L2 checkpoint PTL | review worker stop, validation failure, generation result, or release point | daemon background, writes status and events | non-blocking by default |
| L3 learning reviewer | analyze repeated corrections and failure patterns | async proposal generation | non-blocking |

The rule is simple:

- light checks run synchronously
- deep analysis runs in the background
- only high-risk accepted rules block
- learning produces proposals before activation

## Task Lifecycle

### Task Entry

The PTL creates a compact `PTL Card`.

| Field | Meaning |
| --- | --- |
| `intent` | task type, such as image generation, plugin release, or order adapter |
| `module` | affected module, such as `style engine`, `health`, or `order` |
| `risk` | `low / medium / high` |
| `feasibility_probe` | smallest proof needed for uncertain host, API, protocol, plugin, binary, or undocumented behavior |
| `policy_packs` | policy packs to load |
| `required_artifacts` | required outputs for the task |
| `decision` | `allow / warn / require-review / block` |

### Before Execution

The PTL preflights:

- read current `.codex/*` truth
- read project and module policy
- classify changed paths and task intent
- identify uncertain assumptions and run the smallest feasibility probe first
- check required artifacts
- stop or resequence if the basic probe fails
- give the worker a short brief

### During Execution

The PTL should not hover over the worker.

It listens for:

- path triggers
- test result changes
- gate failures
- worker stops
- human corrections
- key artifact creation

### After Checkpoint

The PTL reviews:

- whether the result met the checkpoint goal
- whether feasibility assumptions were proven before implementation widened
- whether the right layer was used
- whether a workaround was introduced
- whether plan, status, or devlog should be updated
- whether a learning candidate appeared
- whether to continue, resequence, warn, or escalate

## How Policy Packs Are Generated

Policy packs should mostly be generated by the PTL as candidates. Humans decide and calibrate.

### Sources

| Source | PTL Automation | Human Role |
| --- | --- | --- |
| explicit project docs | extract seeded project policy candidates | confirm before first activation when needed |
| existing tests and smoke checks | identify gate evidence | usually no line-by-line approval |
| repeated human corrections | aggregate into learning proposals | confirm |
| repeated AI failure or workaround | normalize into failure patterns | confirm upgrade |
| business direction, external writes, cost boundaries | propose only | must approve |

### Rule Status

| Status | Meaning |
| --- | --- |
| `candidate` | discovered but not active |
| `observe` | record hits only |
| `warn` | warn but allow |
| `require-review` | require human review before continuing |
| `block` | block mainline, release, or external writes |
| `accepted` | human accepted into stable policy |
| `rejected` | human rejected |
| `decayed` | superseded or no longer useful |

### Scope

| Scope | Use |
| --- | --- |
| `project-local` | current project only |
| `module-local` | current module only, such as `order` or `health` |
| `domain-pack` | reusable in similar projects, such as image generation or plugin runtime |
| `user-global` | long-term collaboration preference |
| `global-promoted` | high-confidence cross-project rule |

## What Humans Need To Do

Humans should not maintain large rule files by hand.

Humans mainly decide:

| Responsibility | Meaning |
| --- | --- |
| direction | project goal, business boundary, cost, and external commitments |
| rule approval | whether a PTL proposal is valid and where it applies |
| block upgrade | which warnings should become hard blockers |
| conflict resolution | how to resolve project rules, personal preferences, and domain-pack rules |

Humans should not need to:

- write policy packs from scratch
- remind PTL to read docs
- judge every low-risk path manually
- repeat the same correction indefinitely

## Stable Activation

PTL reliability depends on four surfaces.

| Surface | Requirement |
| --- | --- |
| entry | run L0/L1 before `continue / execute / release / script / host action` |
| rules | compile policy into machine-readable form |
| status | show signal and pending review in host UI and `.codex/status.md` |
| evidence | every hit, block, allow, and learning candidate records evidence |

Docs without entry hooks do not activate PTL.

Entry hooks without rules create an empty shell.

Rules without status reduce user trust.

Status without evidence cannot improve reliably.

## Performance Principles

The PTL must not slow down primary development.

The first version should follow:

| Principle | Meaning |
| --- | --- |
| small input | read only intent, changed paths, policy hash, and required artifacts |
| small output | return decision, reason, and required action |
| event-driven | run at task entry, checkpoint, validation change, and human correction |
| cache-first | compiled policy packs have hashes and are reused when unchanged |
| background analysis | deep review, learning, and promotion run in the daemon |
| rare hard blocks | only accepted high-risk rules block |

## Case 1: Style Engine

`style engine` PTL mainly prevents image-generation work from degrading into non-reusable workarounds.

### Policy Packs

- `project-local: style-engine`
- `domain-pack: image-generation`
- `module-local: product-restyle-lab`
- `learned-registry: image-generation corrections`

### Typical Gates

| Scenario | PTL Behavior |
| --- | --- |
| mainline image validation lacks `product_surface_spec` | block |
| `method_contract_audit` or `mask_refinement_audit` is missing | block or require review |
| historical mask, seed, or denoise is used as selection strategy | block after rule acceptance |
| manual prompt, temp params, or fallback generation | warn and mark `not reusable` |
| one-image result improves but does not transfer to a new white model | warn and create learning candidate |
| docs prohibit hardcoding but code bypasses the rule | require review and suggest escalation |

The PTL must not ask only whether the image looks good. It must ask whether the method can transfer.

## Case 2: OpenClaw Skills

`openclaw-skills` PTL mainly protects multi-skill, plugin, runtime, adapter, and release boundaries.

### Policy Packs

- `project-local: openclaw-skills`
- `module-local: health`
- `module-local: order`
- `domain-pack: plugin-runtime`
- `domain-pack: local-first-data`
- `release-pack: public-skill-release`

### Health Gates

| Scenario | PTL Behavior |
| --- | --- |
| OCR or sidecar extraction becomes authoritative fact | block |
| health input bypasses unified intake | block |
| wrong smoke path replaces gateway `before_dispatch` validation | block or require review |
| live turn contradicts smoke evidence | reopen module |

### Order Gates

| Scenario | PTL Behavior |
| --- | --- |
| adapter reimplements order business logic | block |
| code bypasses `order_runtime_api.py` and calls lower scripts directly | block |
| ERP or warehouse real writes start before dry-run contract | block |
| order truth moves into OpenClaw, MCP, Hermes, or JuShuiTan | require review or block |

### Workspace Gates

| Scenario | PTL Behavior |
| --- | --- |
| root docs start owning subproject business plans again | warn or require review |
| `health` and `order` boundaries mix | require review |
| release lacks i18n, install, smoke, or devlog evidence | block release |

## Engine Versus Project Rules

The PTL engine must stay generic.

Project differences belong in policy packs.

Correct shape:

```text
PTL gate engine
+ project policy
+ module policy
+ domain pack
+ learned registry
+ runtime state
```

Wrong shape:

```text
if repo == "style engine" then ...
if repo == "openclaw-skills" then ...
```

The first shape can be reviewed, learned, and reused.

The second shape is hardcoding.

## Acceptance Criteria

PTL is truly working only when:

1. a new project can generate initial project-policy candidates
2. low-risk rules can start in observe or warn mode
3. high-risk block rules have human acceptance records
4. the host shows current PTL signal
5. clicking the signal shows the hit rule and evidence
6. the worker receives a short PTL Card before execution
7. uncertain host, API, protocol, plugin, binary, or undocumented routes have recorded feasibility probes before implementation
8. checkpoint review runs after worker stop
9. repeated corrections create learning candidates
10. reinstalling the skill does not overwrite accepted rules
11. new projects can reuse domain-pack and global-promoted experience

## Minimal Delivery Order

Do not start with full automatic learning.

Recommended order:

1. implement the generic PTL gate engine policy input format
2. generate seeded project policy candidates from existing docs
3. show PTL signal and pending review in the host
4. run low-risk rules in observe or warn mode first
5. offer accept / reject / snooze for high-risk rules
6. write accepted rules into learned registry or project policy
7. inject accepted rules into the next resume or new thread
8. let the daemon handle repeated corrections, failure patterns, and cross-project promotion

## Current Implementation Status

The minimum governed loop described here is implemented:

| Capability | Status | Landing Point |
| --- | --- | --- |
| Generic PTL gate policy input format | done | `scripts/ptl_gate.py`, `.codex/ptl-policy/project-policy.json` |
| Seeded project policy candidates | done | generated from control surface, project docs, and domain packs |
| Host PTL signal | done | VS Code host status bar / tree view plus `preflight.json` |
| Pending learning review | done | `.codex/ptl-policy/learning-review.json` and `scripts/ptl_learning.py panel` |
| Human confirmation task inside the loop | done | pending review syncs a `PTL-LEARNING-REVIEW` / `human-decision` task; it supports `全部接受` and partial replies such as `接受 1/2，3 稍后`; unfinished decisions stay pending, and once review finishes the task closes and the runner can continue |
| Human prompt format | done | confirmation prompts render `# 需要你确认`, a minimal reply format, and a numbered list so the required action is obvious |
| Low-risk observe / warn operation | done | PTL policy `severity / decision` |
| accept / reject / snooze | done | `scripts/ptl_learning.py accept/reject/snooze` plus host commands |
| Persistent accepted rules | done | `~/.codex/project-assistant/learned-registry.json`, outside the skill install directory so reinstall does not overwrite it |
| Accepted rule injection on the next round | done | `ptl_gate.py preflight` turns the learned registry into `learned.*` rules |
| Repeated corrections create candidates | done | Codex App hook and preflight event-driven scans over message ingress |
| Semantic induction candidates | done | `ptl_learning.py` groups repeated correction messages by semantic concept pairs, such as human decision plus clear reply format or human decision plus loop continuity; candidates still require human review before taking effect |
| Feasibility-first duty | done | core contract, PTL learning pattern, and accepted rule injection |

The current implementation is a governed baseline: repeated corrections are grouped by explicit patterns and lightweight semantic concept pairs, then humans review candidates before they affect policy. Cross-project auto-promotion and rule decay can still improve, but they no longer block the governed learning loop from being usable.

## Target State

The final PTL is not a more talkative AI role.

It is:

`a project technical lead that discovers risks, normalizes rule candidates, observes rule impact, proposes upgrades, and asks humans only when project constraints or hard blocks change.`

Humans own direction and decisions.

PTL owns discovery, feasibility validation, normalization, enforcement, and continuity.

Workers own implementation.

Keeping those roles separate is what makes long-running AI-assisted projects stable.
