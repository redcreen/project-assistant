# Document Standards

Use this reference to generate repo docs that are structured, readable, and maintainable.

This standard is influenced by:

- GitLab documentation style and folder structure
- Kubernetes documentation style guide
- Microsoft Learn style and voice guidance
- Diátaxis documentation model
- Vue / Element Plus / Ant Design / FastAPI documentation patterns

The goal is not to copy any one project. The goal is to generate documentation that is:

- easy to scan
- easy to resume from
- easy to translate or localize
- easy to keep current
- visually clear without decorative noise

## Non-Negotiable Rules

1. one document = one primary question
2. one audience per section
3. one content type per page
4. quick-start content must come before deep explanation
5. diagrams must clarify structure, not decorate the page

Do not mix tutorial, reference, architecture discussion, and roadmap status in the same page unless the page is explicitly a landing page.

## Canonical Document Stack

For a typical software repo, use this shape:

```text
README.md
docs/
  README.md
  architecture.md
  roadmap.md
  test-plan.md
  adr/
  how-to/
  reference/
```

Control-surface files under `.codex/` remain separate and are not replacements for user-facing docs.

## Document Roles

### README.md

Audience:

- first-time reader
- evaluator
- user or developer trying to get started fast

Primary job:

- explain what this project is
- explain why it exists
- show the fastest valid way to try it
- point to deeper docs

Must answer:

- what it is
- who it is for
- what problem it solves
- how to run or try it in the simplest path
- where deeper docs live

Must not become:

- a full architecture dump
- a changelog
- a roadmap log
- a giant FAQ

### docs/README.md

Audience:

- reader already inside the project

Primary job:

- act as documentation landing page
- route the reader by goal, not by internal file history

Use grouped links such as:

- getting started
- architecture
- how-to
- reference
- roadmap / planning
- testing / verification

### architecture.md

Audience:

- maintainers
- contributors
- advanced readers

Primary job:

- explain stable system shape and important design decisions

Must answer:

- system boundaries
- module inventory
- data / request / event flow
- key contracts
- operational concerns
- tradeoffs and non-goals

Must not contain:

- current sprint checklist
- status diary
- speculative backlog

### roadmap.md

Audience:

- maintainers
- collaborators
- stakeholders

Primary job:

- show milestone order, status, exit criteria, and what each milestone unlocks

Roadmap is not the same as current status.

### test-plan.md

Audience:

- maintainers
- QA
- contributors

Primary job:

- show how correctness is verified

Must answer:

- scope
- acceptance cases
- automated coverage
- manual checks
- release or merge gates

### adr/*.md

Audience:

- maintainers
- future reviewers

Primary job:

- record a durable design decision and its consequences

### how-to/*.md

Audience:

- user trying to complete a concrete task

Primary job:

- solve one goal-oriented problem with a clear procedure

### reference/*.md

Audience:

- user or developer already doing work

Primary job:

- provide exact facts: config, CLI flags, env vars, API contracts, schemas

## Content-Type Rule

Prefer the Diátaxis split:

- tutorial: learning by doing
- how-to: solve a practical task
- reference: exact facts
- explanation: concepts and design rationale

Map it into repo docs like this:

- `README.md` -> landing + quick start
- `docs/how-to/*.md` -> how-to
- `docs/reference/*.md` -> reference
- `docs/architecture.md` and ADRs -> explanation

Do not turn `README.md` into a hybrid of all four.

## Recommended Section Order

### README.md

Use this order:

1. one-line value proposition
2. optional badges or status line
3. who it is for
4. quick start
5. core capabilities
6. common workflows or examples
7. docs map
8. development / contribution
9. license

### architecture.md

Use this order:

1. purpose and scope
2. system context diagram
3. module inventory
4. core flows
5. interfaces and contracts
6. state / storage / data model
7. operational concerns
8. tradeoffs
9. related ADRs

### roadmap.md

Use this order:

1. roadmap scope
2. now / next / later summary
3. milestone table
4. dependencies and risks
5. change log only if needed

### test-plan.md

Use this order:

1. scope and risk
2. acceptance cases
3. automation coverage
4. manual checks
5. test data / fixtures
6. release gate

## Diagram Rules

Use diagrams deliberately.

Good diagram jobs:

- system context
- module relationships
- request / event / data flow
- phase or roadmap flow

Bad diagram jobs:

- decoration
- repeating the table with no added meaning
- showing every implementation detail

Rules:

- prefer Mermaid for generated docs
- keep one strong diagram near the top of a deep doc
- keep node labels short
- use a short lead-in sentence before the diagram
- the text must still stand on its own without the diagram

Recommended defaults:

- `architecture.md` -> system context + one core flow
- `roadmap.md` -> milestone flow
- `README.md` -> no diagram by default unless the product is workflow-heavy

## Visual Readability Rules

- keep opening paragraphs short
- prefer tables for structured comparisons, milestones, cases, or module summaries
- prefer ordered steps for setup or task execution
- use callouts sparingly
- avoid long walls of bullet points
- keep headings concrete and predictable

## Localization and Bilingual Rules

Write so translation is easy.

Rules:

- prefer concise, direct sentences
- avoid idioms and culture-specific jokes
- keep terminology stable
- use one canonical term for one concept

Default repo rule:

- living docs under `.codex/` should use one primary language
- durable public docs may be bilingual only if the repo explicitly wants that

When a repo requires bilingual public docs, use a switchable pair structure.

Public docs in this context means:

- `README.md`
- public pages under `docs/`

Required pattern:

- English canonical file: `README.md`, `docs/architecture.md`
- Chinese counterpart: `README.zh-CN.md`, `docs/architecture.zh-CN.md`

Required switch block at the top of both paired files:

```md
[English](README.md) | [中文](README.zh-CN.md)
```

Rules:

- do not do sentence-by-sentence duplication inside one file
- keep one language per file
- keep file pairs structurally aligned
- keep file names and anchors stable, with English as the unsuffixed canonical path
- when a public doc exists in one language, its counterpart must also exist
- README and docs landing pages must expose the language pair clearly

## Naming and Path Rules

- keep file names predictable: `architecture.md`, `roadmap.md`, `test-plan.md`
- use kebab-case for generated doc file names under `docs/`
- do not create multiple pages that answer the same question with slightly different names
- create `docs/README.md` when the docs directory becomes non-trivial

## “Beautiful by Default” Rule

Generated docs should feel calm and intentional, not over-designed.

Use:

- one strong opening paragraph
- one concise summary table where useful
- one meaningful diagram where useful
- short lists
- stable section order

Avoid:

- emoji-heavy headings
- badge clutter
- excessive blockquotes
- giant code dumps before explanation

## Completion Check

A generated doc is good enough when:

- a new reader can find the answer quickly
- the page has one obvious job
- the page structure can be predicted from the title
- diagrams and tables reduce effort instead of adding noise
- the doc can stay current without high maintenance cost
