# Project Assistant

[English](README.md) | [中文](README.zh-CN.md)

> A Codex skill for project planning, retrofit, progress reporting, development logging, documentation governance, and context handoff.  
> It combines best practices from architects, tech leads, reviewers, QA owners, and technical writers to help Codex produce code and project systems that are cleaner, more elegant, more maintainable, and easier to evolve.

## Who This Is For

- Teams or solo developers who want Codex to drive delivery with a stable operating rhythm
- Repositories that need recoverable status, convergent retrofit, and readable docs
- Projects where current phase, next step, and change visibility must stay clear across sessions

## What This Is Today

| Item | Current Position |
| --- | --- |
| Product Role | an AI engineering delivery operating system for Codex-led work |
| Strongest At | planning, retrofit, architecture supervision, progress reporting, development logs, documentation governance, and context handoff |
| Human Still Owns | business direction, product priorities, compatibility promises, and major tradeoffs |
| Default Working Model | human sets direction; `project-assistant` plans, executes, validates, updates state, and escalates only when judgment is required |
| Core Standing Role | Project Technical Lead (PTL): inside an approved direction, it owns strategic judgment, program orchestration, long-run delivery supervision, and escalation timing |
| Active Strategic Direction | `M10 / M11 / M12` are complete; the next formal line is now `M13 PTL supervision loop`, then `M14 worker handoff and re-entry`, while `M15 selective multi-executor scheduling` stays evidence-gated for later |
| Current Program-Orchestration Boundary | stabilize the durable single-Codex orchestration truth and keep the project alive after a worker stops; automatic multi-desktop-Codex scheduling remains a future layer |
| Plain-Language Meaning Of `M14` | `when a worker stops, the project should not stop with it` |

## Where It Is Going

| Horizon | Focus |
| --- | --- |
| Current | build `M13 PTL supervision loop`: let the PTL watch the project continuously through periodic and event-driven checks instead of only appearing in chat |
| Next | build `M14 worker handoff and re-entry`: let the PTL catch the work when a worker stops at a checkpoint, times out, fails, or hands off |
| Later | build `M15 selective multi-executor scheduling`: only introduce real multi-executor dispatch when rollout evidence and disjoint write scopes both justify it |
| Strategy Entry | [Strategic Planning And Program Orchestration Direction](docs/reference/project-assistant/strategic-planning-and-program-orchestration.md) |

## Install

One-line install from a stable tag:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.3/install.sh | bash
```

Manual install:

```bash
git clone --branch v0.1.3 https://github.com/redcreen/project-assistant.git ~/.codex/skills/project-assistant
```

## Minimal Configuration

No extra configuration is required.

Simplest path:

1. install to `~/.codex/skills/project-assistant`
2. start a new Codex session
3. run `project assistant menu`

Optional overrides:

```bash
PROJECT_ASSISTANT_REF=v0.1.3 PROJECT_ASSISTANT_DIR="$HOME/.codex/skills/project-assistant" bash install.sh
```

## Quick Start

Use one simple entry:

- `project assistant`

Primary human windows:

- `project assistant menu`
- `project assistant progress`
- `project assistant architecture`
- `project assistant devlog`

Background flows (usually automatic):

- `project assistant start this project`
- `project assistant continue`
- `project assistant architecture retrofit`
- `project assistant retrofit`
- `project assistant docs retrofit`
- `project assistant handoff`

## Core Capabilities

- Create and maintain `.codex` control surfaces
- Maintain `.codex/doc-governance.json` as the Markdown-governance contract
- Plan work in verifiable slices
- Turn the active slice into a checkpoint-based long execution line instead of waiting for repeated "continue" prompts
- Show that execution line as a visible task board with done/total progress and a `Plan Link` back to the active slice
- Keep a compact architecture-supervision state and escalation gate beside the execution line
- Render `progress / continue / handoff` as maintainer-facing first screens instead of AI-only status dumps
- Promote architecture review automatically when the current slice shows ownership, boundary, or repeated-fix drift
- Surface a short `Usable Now` snapshot so you can see what is already ready to use
- Retrofit existing repos to convergence
- Report progress with global and module views
- Capture durable implementation reasoning as development logs
- Persist PTL strategic evaluation in `.codex/strategy.md`, including the boundary between system proposals and human approvals
- Persist PTL program orchestration in `.codex/program-board.md`, including workstreams, sequencing, parallel-safe boundaries, and executor inputs; today this first stabilizes a single-Codex coordinator mode
- Persist PTL supervised long-run delivery in `.codex/delivery-supervision.md`, including checkpoint rhythm, automatic-continue boundaries, escalation timing, and backlog re-entry rules
- Persist the formal roadmap meaning of the PTL supervision loop, worker handoff/re-entry, and future multi-executor entry conditions instead of leaving them as chat-only ideas
- Normalize durable docs into a standard system
- Emit a compact context handoff for the next thread

## Ready to Use Now

Stable workflows that are already proven on representative repos:

- `project assistant retrofit`
- `project assistant docs retrofit`
- `project assistant architecture retrofit`
- `project assistant progress`
- `project assistant handoff`

What this means:

- planning, execution, architecture supervision, and development-log capture are now default-on behaviors in the main operating model
- the skill is no longer only a planning scaffold; it has already been used to converge lightweight repos and larger doc-heavy repos
- `progress`, `handoff`, the control surface, and validation gates now describe the same current truth
- representative medium and large repos now show clearer maintainer-facing first screens, not only raw slice names
- at least one architecture-review path now auto-escalates from current-slice drift instead of depending only on manual prompts
- the PTL strategic-evaluation, program-orchestration, and supervised-long-run-delivery layers are now real capabilities, not only direction documents
- the current orchestration layer is a durable single-Codex coordination brain, not yet a productized multi-desktop-Codex dispatcher
- the next formal line is now `M13 / M14 / M15`: first PTL supervision loop, then worker handoff and re-entry, and only then selective multi-executor scheduling

## Common Workflows

Default working style:

- you mainly provide business direction, priorities, and hard constraints
- `project-assistant` should usually plan, supervise, implement, validate, refresh status, and capture devlogs on its own
- it should only stop at checkpoints, blockers, or decisions that require user judgment
- its long-run execution should stay visible through an execution-task board, not disappear into free-form status prose
- the architecture layer should keep showing whether the assistant can continue automatically, should raise-but-continue, or must stop for user judgment
- progress and handoff should also tell you which capabilities are already usable now
- `continue` should default to a compact progress snapshot; use `project assistant progress` when you want the full dashboard

### Start or take over a project

```text
project assistant start this project
```

### Report current progress

```text
project assistant progress
```

### Continue the current execution line

```text
project assistant continue
```

### Review the current direction at the architecture level

```text
project assistant architecture
```

Most common:

- `project assistant architecture review`

When to use it:

- before changing code, if you want a higher-level check on the direction
- when the implementation is drifting toward hardcoded shortcuts
- when you want to test the abstraction boundary before adding more code

### Retrofit architecture, not only docs or control surface

```text
project assistant architecture retrofit
```

Use it when the repo needs an architecture-first correction:

- the real problem is boundary drift, not only missing docs
- duplicate architecture docs or wrong-layer fixes keep accumulating
- repeated fixes suggest the source of truth or module boundaries are wrong

### Retrofit the whole repo

```text
project assistant retrofit
```

Default scope:

- control-surface retrofit
- documentation retrofit
- full Markdown-tree governance retrofit
- validation gates

Use this when the repo mainly needs convergence and cleanup.
If the real problem is architectural drift, use `project assistant architecture retrofit` directly.

### Focus on docs only

```text
project assistant docs retrofit
```

### Record a durable implementation note

```text
project assistant devlog
```

### Prepare a new thread

```text
project assistant handoff
```

## Documentation Map

- [Docs Home](docs/README.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Strategic Direction](docs/reference/project-assistant/strategic-planning-and-program-orchestration.md)
- [Test Plan](docs/test-plan.md)
- [Development Log](docs/devlog/README.md)
- [ADR Index](docs/adr/README.md)
- [Skill Contract](SKILL.md)
- [References](references/README.md)

## Development

### Repository Layout

```text
project-assistant/
├── .codex/
├── SKILL.md
├── VERSION
├── install.sh
├── README.md
├── README.zh-CN.md
├── docs/
├── agents/
├── references/
└── scripts/
```

### Key Scripts

- `scripts/sync_control_surface.py`
- `scripts/validate_control_surface.py`
- `scripts/sync_docs_system.py`
- `scripts/sync_markdown_governance.py`
- `scripts/validate_docs_system.py`
- `scripts/validate_public_docs_i18n.py`
- `scripts/validate_markdown_governance.py`
- `scripts/validate_doc_quality.py`
- `scripts/validate_control_surface_quality.py`
- `scripts/sync_execution_line.py`
- `scripts/sync_architecture_supervision.py`
- `scripts/sync_architecture_retrofit.py`
- `scripts/validate_gate_set.py`
- `scripts/validate_release_readiness.py`
- `scripts/write_development_log.py`
- `scripts/validate_development_log.py`
- `scripts/validate_architecture_retrofit.py`
- `scripts/capability_snapshot.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`
- `scripts/release_skill.py`

### Validation

```bash
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/validate_docs_system.py /path/to/repo --format text
python3 scripts/validate_public_docs_i18n.py /path/to/repo --format text
python3 scripts/validate_markdown_governance.py /path/to/repo --format text
python3 scripts/validate_doc_quality.py /path/to/repo --format text
python3 scripts/validate_control_surface_quality.py /path/to/repo --format text
python3 scripts/validate_development_log.py /path/to/repo --format text
python3 scripts/validate_architecture_retrofit.py /path/to/repo --format text
python3 scripts/validate_gate_set.py /path/to/repo --profile fast
python3 scripts/validate_gate_set.py /path/to/repo --profile deep
python3 scripts/validate_gate_set.py /path/to/repo --profile release
```

### Release

When a feature improvement is stable and validations pass, use a short release command:

```text
project assistant release patch
```

Equivalent script command:

```bash
python3 scripts/release_skill.py patch
```

Stricter release protection uses the same gate profile:

```bash
python3 scripts/validate_gate_set.py /path/to/repo --profile release
```

What it does:

- bump `VERSION`
- update the tag-based install URLs in both README files
- update `install.sh`
- create a release commit
- create a git tag

Short release hint for maintainers:

```text
Ready to release. Run: project assistant release patch
```

## License

Use the repository's chosen license and contribution policy.
