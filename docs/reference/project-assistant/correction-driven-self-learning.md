# Correction-Driven Self-Learning

[English](correction-driven-self-learning.md) | [中文](correction-driven-self-learning.zh-CN.md)

## Purpose

This document defines the first formal self-learning line for `project-assistant`:

`solve repeated user corrections inside Codex first.`

It does not try to build a general-purpose learning system immediately. The first durable capability should be:

`turn repeated user corrections into reviewable candidate rules, then promote them into a stable rule library only after user acceptance.`

## What This Solves First

Phase 1 only targets this class of problem:

- users keep correcting the same kind of assistant behavior in the same workspace or over long-term use
- the correction is no longer just a one-off preference and should become a default future behavior
- the user wants that improvement to leave the chat log and become visible, reviewable, accepted, and persistent

Typical examples:

- "stop opening with filler every time"
- "inspect code before making claims"
- "optimize for outcome first, not for planning prose first"
- "when planning, write the durable docs into the repo instead of only talking about them"
- "default to PTL / control-surface convergence instead of treating this like a one-shot prompt"

## What The Current Codebase Already Provides

This is not starting from zero.

The repo already has four important foundations:

| Foundation | Where it already exists | Why it matters |
| --- | --- | --- |
| host status surfaces | [../../../integrations/vscode-host/extension.js](../../../integrations/vscode-host/extension.js) | Tree View, Status Bar, notifications, workspaceState, recent events, and recent files already exist |
| daemon events and status | [../../../scripts/daemon_runtime.py](../../../scripts/daemon_runtime.py) | the runtime store, queue, events, and status snapshot are already in place |
| Codex workspace session discovery | [../../../integrations/vscode-host/extension.js](../../../integrations/vscode-host/extension.js) | the host already locates the latest local Codex session for the current workspace from `~/.codex/sessions/**/*.jsonl` |
| durable working method | [project-origin-and-working-method.md](project-origin-and-working-method.md), [ptl-daemon-mvp.md](ptl-daemon-mvp.md) | the skill already separates durable truth, review, checkpoints, and host/daemon responsibilities |

So the real gap is no longer "can the plugin show a hint?" The real gap is:

1. how candidate rules are extracted
2. how review and acceptance are defined
3. where accepted rules live so reinstall does not wipe them

## One-Line Boundary

Recommended boundary:

`auto-detect candidates, require human review, promote accepted rules, then apply them on the next turn.`

Not recommended:

`silently rewrite the assistant from raw chat logs.`

## Phase 1 User Experience

The first user-facing experience should be very concrete:

| Situation | Target behavior |
| --- | --- |
| the user repeats the same correction | the system clusters it into one candidate rule |
| a candidate appears | the VS Code host shows a dedicated `Learning Review` area in the sidebar |
| review is needed | the Status Bar shows a separate hint such as `PA Learn: 2 pending` |
| the user clicks the hint | the host opens a real review surface, not an ambiguous log |
| the user accepts | the rule is promoted into the stable rule library and affects future resume / new-thread turns |
| the user rejects or snoozes | the candidate is marked `rejected` or `snoozed` instead of repeatedly nagging |

## Recommended Data Flow

### 1. Capture

Phase 1 should prioritize the local Codex session records for the current workspace as the evidence source.

Input priority:

1. local session logs for the current workspace
2. host-generated continue / handoff / progress artifacts
3. only later: repo docs, devlogs, or external sources

### 2. Correction-Signal Detection

Phase 1 should not try to learn everything.

It should first recognize explicit correction signals such as:

- `不要 / 别 / 以后不要`
- `应该 / 要 / 需要`
- `先 ... 再 ...`
- `默认`
- `不要每次`
- `还是按 ...`

The goal is high-precision explicit correction capture, not broad fuzzy inference.

### 3. Candidate Normalization

The raw sentence should not become the rule directly.

Each candidate should first be normalized into a reviewable artifact with:

- raw evidence
- normalized rule text
- scope
- proposed landing target
- repetition count

### 4. Review

The host should surface candidates in a dedicated review area, not inside generic Recent Events.

Each candidate should support at least:

- `Accept as workspace rule`
- `Accept as user-global rule`
- `Reject`
- `Snooze`
- `Open evidence`

### 5. Promotion

Only explicit user acceptance should promote a candidate into a stable rule.

After promotion:

- write the rule into the stable rule library
- record the decision trail
- load it in daemon / host on the next resume path
- generate a policy-input artifact when needed for Codex / PTL consumption

## Suggested Candidate Schema

Phase 1 should at least include these fields:

| Field | Purpose |
| --- | --- |
| `id` | unique candidate id |
| `workspace_id` | workspace binding |
| `scope` | `workspace` or `user-global` |
| `source_session_id` | source session |
| `source_turn_ids` | evidence turns |
| `evidence_snippet` | short quote/snippet of the user correction |
| `normalized_rule` | normalized rule text |
| `rule_kind` | `communication / workflow / validation / architecture / docs / escalation` |
| `proposed_target` | where the rule should act: prompt supplement, checklist, review policy, etc. |
| `occurrence_count` | repetition count |
| `status` | `pending-review / accepted / rejected / snoozed / decayed` |
| `created_at` | first-seen time |
| `last_seen_at` | most recent repeat |
| `decision` | accept / reject / snooze trail |

## Where Stable Rules Should Actually Act

Accepted rules should not directly patch:

- `SKILL.md`
- [../../../agents/openai.yaml](../../../agents/openai.yaml)
- files inside the installed skill directory

Phase 1 should instead treat stable rules as:

`extra policy-input artifacts injected during the next resume / new-thread / host-generated prompt path.`

This gives three benefits:

1. no patching inside the installed skill
2. no reinstall wipeout
3. clearer review, export, and decay governance

## Plugin And Status Bar Changes

The host already has a main status item and a Tree View.

Phase 1 should add these UI surfaces:

### Tree View

Add a `Learning Review` group containing at least:

- pending candidate count
- per-candidate summaries
- click-through into the review surface
- accept / reject / snooze actions

### Status Bar

Add a dedicated Status Bar item instead of mixing learning signals into the current `PA: running` item.

Suggested labels:

- `PA Learn: 2 pending`
- `PA Learn: review needed`
- `PA Learn: clean`

Click behavior:

- open the learning review view
- when there is only one candidate, jump directly to that candidate

### Notifications

Only notify on these edges:

- the first new pending candidate appears
- pending review count changes from `0 -> N`
- a candidate is successfully promoted

Do not replay notifications on every polling cycle.

## What The Daemon Needs

Phase 1 does not require complex daemon-side learning logic, but it does need a minimal event contract:

| Event | Meaning |
| --- | --- |
| `learning_candidate_detected` | a new candidate rule was found |
| `learning_review_needed` | there are pending candidates |
| `learning_rule_promoted` | a candidate was accepted and promoted |
| `learning_rule_rejected` | a candidate was rejected |

And the status snapshot should grow:

| Field | Meaning |
| --- | --- |
| `learningSummary.pendingReview` | pending review count |
| `learningSummary.acceptedRules` | accepted stable rule count |
| `learningSummary.lastCandidateAt` | most recent candidate time |
| `learningSummary.lastPromotedAt` | most recent promotion time |

## Where The Rule Library Should Live

This is the key architectural decision.

### Where It Should Not Live

- not in `~/.codex/skills/project-assistant/`
- not in the extension install directory
- not only in the daemon runtime store

Why:

- skill reinstall can replace the install directory
- extension update can replace extension code
- the daemon runtime store is runtime state, not durable truth

### Recommended Placement

Phase 1 should use a host-neutral registry root:

- `~/.codex/registry/project-assistant/workspaces/<workspace-id>/candidates.jsonl`
- `~/.codex/registry/project-assistant/workspaces/<workspace-id>/stable-rules.json`
- `~/.codex/registry/project-assistant/global/stable-rules.json`

With this shape:

- reinstalling the `project-assistant` skill does not overwrite rules
- updating the VS Code extension does not overwrite rules
- the daemon can keep treating `~/.codex/daemon/<repo-id>/` as runtime store only
- future consumers can read from the same canonical root

### Should Anything Be Written Into The Repo?

By default, no.

Local learned rules should not automatically write into the repo.

Only when the user explicitly chooses to export a rule into repo policy should the system write something like:

- `.codex/policy-input/learning-rules.json`
- `.codex/policy-input/learning-rules.md`

That is an export path, not the default storage path.

## This Answers The Reinstall Question

The answer is direct:

`if learned rules live in the install directory, reinstall may overwrite them; if learned rules live in a separate registry root, reinstall should not overwrite them.`

So this capability must separate installable code from learned data.

## PTL's Role Here

Putting this capability under the PTL role is reasonable, but the boundary must stay tight.

PTL should:

- detect learning-worthy candidates
- write them as reviewable artifacts
- consume stable rules in future execution

PTL should not:

- bypass user review
- rewrite its own installed prompt directly
- treat a single emotional correction as a long-term rule

## Recommended Delivery Phases

### Phase 1

`reviewable correction learning`

Goal:

- extract explicit corrections from local Codex sessions
- create pending candidates
- surface them in the host sidebar and Status Bar
- support accept / reject / snooze
- write accepted rules into a separate durable rule library

### Phase 2

`stable rule consumption`

Goal:

- load stable rules into continue / handoff / auto-resume / new-thread flows
- affect prompt supplements, review checklists, and plan preflight first
- avoid patching installed skill code

### Phase 3

`governance and decay`

Goal:

- add conflict / superseded / decay handling
- handle workspace-rule vs global-rule conflicts
- support explicit export into repo policy-input artifacts

## Current Recommendation

If only one high-value learning slice is chosen first, it should be:

`reviewable correction learning, not a broad memory system.`

Why:

- it produces direct user value
- the evidence source is clear
- the host and Status Bar already have a delivery surface
- the persistence boundary can be defined cleanly from day one

## Related Docs

- [project-origin-and-working-method.md](project-origin-and-working-method.md)
- [ptl-daemon-mvp.md](ptl-daemon-mvp.md)
- [host-resume-bridge.md](host-resume-bridge.md)
- [orchestration-model.md](orchestration-model.md)
- [ai-coding-modes-comparison.md](ai-coding-modes-comparison.md)
