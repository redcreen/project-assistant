# Project Origin And Working Method

[English](project-origin-and-working-method.md) | [中文](project-origin-and-working-method.zh-CN.md)

## What This Is

This document records the **origin point** of `project-assistant`.

It answers two questions:

| Question | Answer |
| --- | --- |
| Where did this skill come from | It started from one concrete question about how to use Codex more reliably for real project delivery |
| What working method does it default to | clarify goals and method first, then let AI deliver inside durable plans, validation, and gates |

## This Is The Starting Point

`project-assistant` did not begin as a command list. It began with the question below.

That original wording is preserved so future maintainers can always see:

- what problem this skill was trying to solve
- why it emphasizes architecture, roadmap, test cases, development plans, long-run delivery, and durable recovery truth
- why it is not just “let the AI start coding immediately”

## Original Prompt (Preserved Verbatim)

> 我在使用codex开发一个项目时，发现先讨论清楚最终目标，然后在讨论实现方案，出系统架构文档  然后出roadmap 及test case，在出development plan，然后让ai按照plan去开发，会比较好； 这是ai编程的最佳实践么？ 还有哪些更好的方式么？ 我想把这个方法固化下来；  
> 包含开发项目的子项目或者阶段任务时也按照这个方法，这样会比较清晰，但不是知道这是不是最佳实践；  
> 同时我希望产出的这个最佳实践，可以像类似skill或者什么工具似的，可以引领我每次这样来做；

## Default Working Method Derived From That Prompt

| Order | Default Move | Why |
| --- | --- | --- |
| 1 | clarify the final goal first | converge on the intended outcome before implementation details pull the work sideways |
| 2 | discuss the implementation approach second | compare candidate paths and boundaries before writing code |
| 3 | write system architecture first | define modules, ownership, boundaries, and long-run evolution |
| 4 | then write the roadmap | decide the staged route before deciding detailed execution order |
| 5 | then define test cases / acceptance | define “done” before delivery starts drifting |
| 6 | then write the development plan | translate the staged route into a recoverable ordered plan |
| 7 | only then let AI deliver against the plan | make execution depend on durable repo truth instead of current chat memory |
| 8 | keep state, progress, devlog, and gates updated throughout delivery | keep the project recoverable, auditable, and handoff-ready |

## Is This Best Practice

| Conclusion | Explanation |
| --- | --- |
| It is very close to the most stable current AI-delivery practice | it matches the “human sets direction, AI executes inside durable plans, validation, and gates” model |
| It is not the only valid workflow | tiny fixes, urgent patches, and very small repos can use a lighter process |
| It is most valuable for medium+ projects and multi-session work | the longer and more complex the project, the more valuable this method becomes |

## When It Can Be Lighter

| Situation | Reasonable Shortcut |
| --- | --- |
| tiny one-file fix | skip a full roadmap and keep only goal, validation, and change rationale |
| clearly mechanical low-risk work | compress the architecture discussion, but still keep validation explicit |
| repo already has a stable roadmap / development plan | go straight to `project assistant continue` instead of rebuilding the whole front matter |
| high-risk architecture change | do not skip architecture docs, special-track judgment, or escalation boundaries |

## It Also Applies To Subprojects And Stage Tasks

| Situation | What To Do |
| --- | --- |
| subproject | define the subproject outcome, boundary, and acceptance first, then attach it to the main roadmap |
| stage task | define the stage goal and exit condition first, then break it into a development plan |
| long execution run | express it as an execution line + task board, not just “keep going” |
| worker stops | use PTL supervision + worker handoff so the project does not stop with the worker |

## How `project-assistant` Turns It Into A Tool

| Original Intent | Where It Lives Now |
| --- | --- |
| clarify the goal first | `brief / roadmap / strategy` |
| clarify the approach and boundaries next | `architecture / architecture retrofit / PTL review` |
| define stages before detailed execution | `roadmap / development-plan / plan` |
| let AI keep delivering against the plan | `execution line / progress / continue / handoff` |
| do not let the project stop inside a chat | `.codex/status.md`, `.codex/plan.md`, `devlog`, gates |
| keep a standing technical lead alive | `PTL supervision / program board / delivery supervision` |

## One-Line Summary

The origin of `project-assistant` is not “make AI write more code.”

It is:

**clarify goals, approach, architecture, roadmap, tests, and the development plan first, then let AI deliver inside durable repo truth and gates.**

## What This Method Is Actually Trying To Remove

This method is not trying to remove human judgment around requirements, direction, or major tradeoffs.

It is trying to remove repetitive process burden such as:

- turning goals into the first structured project-doc set
- keeping roadmap, test cases, development plan, and status surfaces minimally aligned
- restoring context, progress, and validation entry points across sessions
- making doc expectations, gates, and recovery truth part of the default workflow

So the real product stance should be:

`let humans focus on requirements, direction, boundaries, and tradeoffs, while AI and tooling absorb more of the process detail and process control burden.`

## Why Templated And Pre-Generated Docs Are Aligned With The Origin

If the goal is more professional and more disciplined project delivery, the doc layer should not need to grow from zero every time.

A better pattern is:

- use templated and pre-generated document scaffolds to establish durable truth quickly
- spend human attention on the parts that actually require judgment: goals, boundaries, approach deltas, staging tradeoffs, and acceptance
- treat templates as an accelerator into higher-quality discussion and delivery, not as the final artifact

In other words, templating is not there to add process weight. It is there to remove process friction.
