# AI Coding Modes Comparison

[English](ai-coding-modes-comparison.md) | [中文](ai-coding-modes-comparison.zh-CN.md)

## Purpose

This document answers one question: compared with common AI coding modes discussed in 2026, what is `project-assistant` most like, and what is it explicitly not trying to be?

It uses the April 15, 2026 "six AI coding modes" article as a discussion taxonomy, not as a formal standards document.

## Short Answer

`project-assistant` is not a single mode.

Today it is closest to `Agentic Engineering + Harness Engineering`, while also absorbing parts of `SDD` and `BMAD`. It is intentionally not positioned as a default `Vibe Coding` tool, and it does not treat `Ralph Wiggum Loop` as its main delivery path.

## Comparison Table

| Mode | What this mode emphasizes | Current relationship to `project-assistant` | What already exists here | Current boundary |
| --- | --- | --- | --- | --- |
| `Vibe Coding` | natural-language exploration, fast code, low process | intentionally kept at a distance | natural-language exploration and quick drafting are still possible | this is not a one-shot prompt tool; it pulls work back into `plan / status / docs / validation` |
| `Agentic Engineering` | think first, break work down, execute, then accept or reject | core fit | `strategy / program-board / plan / status / delivery-supervision`, `continue / progress / handoff`, checkpoints, and escalation gates | humans still own business direction, compatibility promises, and cost/time boundary decisions |
| `Harness Engineering` | context, constraints, feedback loops, and entropy management around AI execution | core fit | control surfaces, docs system, validators, architecture triggers, worker handoff, and daemon-managed safe support tasks | this is not yet a fully autonomous multi-executor conflict-resolution system |
| `Ralph Wiggum Loop` | `PRD + checklist + clean-context` recursive execution | partially absorbed, not the default mainline | durable truth, checkpoints, worker handoff, queue / ETA, and resumable execution lines | no default background business-code writing and no encouragement of unbounded autonomous loops |
| `BMAD` | role-based agents for analysis, product, architecture, and execution | partially absorbed | PTL, worker, architecture supervision, and docs / release / governance surfaces already create role layering | this is not yet a full long-lived multi-role agent roster |
| `SDD` | spec-first execution with the spec as source of truth | strongly related, but not a pure implementation of it | roadmap, development plan, architecture, and `.codex/*` control surfaces jointly constrain execution | implementation is not yet unified under one fully executable spec workflow |

## A More Accurate Description Of The Current Capability

- `project-assistant` is closer to a repo operating layer than a prompt pattern.
- Its core value is not "write a bit more code for you", but "keep planning, execution, validation, progress, and handoff converged around the same durable truth".
- That is why it maps more naturally to `Harness Engineering`: what gets productized here is the runtime and governance environment, not a single chat turn.

## Why This Matters For Future Self-Learning

- The right learning targets are `spec / checklist / policy / review rule / escalation rule / template`, not hidden personality drift from raw conversations.
- PTL should consume experience that has already been promoted into stable artifacts; it should not rewrite itself outside governance.
- If conversation-derived learning is added later, the natural carrier is an artifact lifecycle such as `candidate -> review -> stable -> decay`.

## Related Internal Docs

- [orchestration-model.md](orchestration-model.md)
- [ptl-daemon-mvp.md](ptl-daemon-mvp.md)
- [strategic-planning-and-program-orchestration.md](strategic-planning-and-program-orchestration.md)
- [development-plan.md](development-plan.md)

## External References

- April 15, 2026 article "别再说 AI 编程就是 Vibe Coding 了！6 种主流模式一次讲清":
  `https://mbd.baidu.com/newspage/data/landingsuper?context=%7B%22nid%22%3A%22news_9381192559901099771%22%2C%22sourceFrom%22%3A%22bjh%22%7D&isBdboxFrom=1&pageType=1&rs=3339967809&ruk=AseIqI0YO6rBNSL13jIBSg&sid_for_share=&urlext=%7B%22cuid%22%3A%22_iB3uY8bvuYzi-fql8vAu_aO-8gsa2uFliv8i0i9vajx8S8I0OvgilfvQu5WfSOwM8VmA%22%7D`
- GitHub Spec Kit / Spec-Driven Development:
  `https://github.com/github/spec-kit`
- PMI Hybrid / fit-for-purpose:
  `https://www.pmi.org/blog/project-management-embraces-the-fit-for-purpose-approach`
- PMI Pulse 2025 / business acumen:
  `https://www.pmi.org/learning/thought-leadership/boosting-business-acumen`
- DORA 2025 / AI-assisted software development:
  `https://cloud.google.com/devops/state-of-devops`
- Atlassian System of Work:
  `https://www.atlassian.com/system-of-work`
