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
| Project Origin | [Project Origin And Working Method](docs/reference/project-assistant/project-origin-and-working-method.md): the original question was whether it is more stable to clarify goals, approach, architecture, roadmap, test cases, and a development plan before AI delivery starts |
| Active Strategic Direction | `M10 / M11 / M12 / M13 / M14 / M16` are complete, and the `M17-M21 daemon-host baseline` is also complete; the repo is now in post-M21 hardening and dogfooding to decide release packaging and any farther host expansion |
| Current Program-Orchestration Boundary | stabilize the durable single-Codex orchestration truth and keep the project alive after a worker stops; automatic multi-desktop-Codex scheduling remains a future layer |
| Plain-Language Meaning Of `M14` | `when a worker stops, the project should not stop with it` |
| Plain-Language Meaning Of `M16` | `continue / progress / handoff` share one front door, upgrade old repos first, and only then render the first structured screen |
| Automatic `continue` Behavior | first read `.codex/control-surface.json`; if the control-surface version is old or missing required surface versions, apply the minimum safe upgrade before resuming through one canonical front door |

## Where It Is Going

| Horizon | Focus |
| --- | --- |
| Current | harden the newly shipped daemon-host baseline so the daemon runtime, queue, VS Code host, continue bridge, legacy rollout, docs, and gates stay aligned on one default fast path |
| Next | add clearer operator docs, release framing, and broader dogfooding evidence for the daemon-host baseline before deciding whether stronger host surfaces are warranted |
| Later | only reopen `M15` or introduce more aggressive host automation when the daemon-host baseline is stable, the single-Codex PTL model is still the bottleneck, and disjoint write scopes are explicit |
| Strategy Entry | [Strategic Planning And Program Orchestration Direction](docs/reference/project-assistant/strategic-planning-and-program-orchestration.md) |
| Method Origin | [Project Origin And Working Method](docs/reference/project-assistant/project-origin-and-working-method.md) |

## Install

One-line install from a stable tag:

```bash
curl -fsSL https://raw.githubusercontent.com/redcreen/project-assistant/v0.1.3/install.sh | bash
```

Manual install:

```bash
git clone --branch v0.1.3 https://github.com/redcreen/project-assistant.git ~/.codex/skills/project-assistant
```

Note: the current stable tag is still `v0.1.3`; the `M17-M21 daemon-host baseline` now lives on the repository mainline, and formal release packaging is the next closure step.

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
- `project-assistant daemon start`
- `project-assistant queue`

### Default Operator Fast Path

The daemon-host baseline is now the default fast path for real work.

- Start with the canonical front door: `bin/project-assistant` or `python3 scripts/project_assistant_entry.py`
- Typical operator commands: `continue`, `progress`, `handoff`, `daemon status`, and `queue`
- Treat `bootstrap_entry.py`, `retrofit_entry.py`, `continue_entry.py`, `progress_entry.py`, and `handoff_entry.py` as backend/debug entry points, not the first thing hosts or maintainers should call

## Core Capabilities

- Create and maintain `.codex` control surfaces
- Maintain `.codex/doc-governance.json` as the Markdown-governance contract
- Plan work in verifiable slices
- Turn the active slice into a checkpoint-based long execution line instead of waiting for repeated "continue" prompts
- Show that execution line as a visible task board with done/total progress and a `Plan Link` back to the active slice
- Keep a compact architecture-supervision state and escalation gate beside the execution line
- Render `progress / continue / handoff` as maintainer-facing first screens instead of AI-only status dumps
- Make `continue` auto-detect when a repo's control-surface version is stale, and run the minimum safe upgrade instead of pushing that judgment onto the user
- Route `continue / progress / handoff` through one canonical front door instead of depending on the model to remember which script to call first
- Provide a local daemon runtime, queue / events control surface, and a protected foreground write lease so support work moves off the foreground coding lane
- Provide a VS Code host shell, live status, and a continue bridge so “the page is moving and the task is advancing” is a real operator experience instead of only a design note
- Promote architecture review automatically when the current slice shows ownership, boundary, or repeated-fix drift
- Surface a short `Usable Now` snapshot so you can see what is already ready to use
- Retrofit existing repos to convergence
- Report progress with global and module views
- Capture durable implementation reasoning as development logs
- Persist PTL strategic evaluation in `.codex/strategy.md`, including the boundary between system proposals and human approvals
- Persist PTL program orchestration in `.codex/program-board.md`, including workstreams, sequencing, parallel-safe boundaries, and executor inputs; today this first stabilizes a single-Codex coordinator mode
- Persist PTL supervised long-run delivery in `.codex/delivery-supervision.md`, including checkpoint rhythm, automatic-continue boundaries, escalation timing, and backlog re-entry rules
- Turn PTL supervision and worker handoff into `.codex/ptl-supervision.md` and `.codex/worker-handoff.md`, while keeping multi-executor entry conditions evidence-gated for later
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
- the PTL strategic-evaluation, program-orchestration, supervised-long-run-delivery, PTL-supervision, and worker-handoff layers are now real capabilities, not only direction documents
- `M16` now closes the unified front door, version preflight, and structured first-screen contract; desktop-host hard binding remains a later bridge problem
- `M17-M21` now close the daemon runtime, VS Code host shell, continue bridge, local validation, and legacy-rollout recovery into one daemon-host baseline
- the current orchestration layer is a durable single-Codex coordination brain, not yet a productized multi-desktop-Codex dispatcher
- `M13 / M14 / M16 / M17 / M18 / M19 / M20 / M21` are now closed; `M15` remains a later evidence-gated layer instead of an active promise

## Common Workflows

Default working style:

- you mainly provide business direction, priorities, and hard constraints
- `project-assistant` should usually plan, supervise, implement, validate, refresh status, and capture devlogs on its own
- it should only stop at checkpoints, blockers, or decisions that require user judgment
- its long-run execution should stay visible through an execution-task board, not disappear into free-form status prose
- during long retrofit or execution runs, it should also keep you oriented with short progress notes that say what is happening now, what just changed, and what checkpoint remains
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

Default behavior:

- automatically detect whether the repo is still on an older control-surface generation
- read `.codex/control-surface.json` first and compare the stored control-surface version plus surface versions against the current schema
- if the control-surface version is stale or required surface versions are missing, apply the minimum safe upgrade first
- emit the structured continue panel first, then append any "this round changed" note; do not start with a long prose summary
- only then resume and continue the active execution line
- if the run is long, keep the user oriented with short visible progress notes instead of going silent

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
- [Orchestration And Entry Model](docs/reference/project-assistant/orchestration-model.md)
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

- `scripts/project_assistant_entry.py`
- `scripts/sync_entry_routing.py`
- `scripts/validate_entry_routing.py`
- `scripts/sync_dogfooding_evidence.py`
- `scripts/validate_dogfooding_evidence.py`
- `scripts/daemon_entry.py`
- `scripts/daemon_runtime.py`
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
- `scripts/validate_daemon_runtime.py`
- `scripts/validate_vscode_host_extension.py`
- `scripts/validate_daemon_host_mvp.py`
- `scripts/validate_daemon_legacy_rollout.py`
- `scripts/capability_snapshot.py`
- `scripts/progress_snapshot.py`
- `scripts/context_handoff.py`
- `scripts/release_skill.py`

### Validation

```bash
python3 scripts/validate_control_surface.py /path/to/repo --format text
python3 scripts/validate_docs_system.py /path/to/repo --format text
python3 scripts/validate_public_docs_i18n.py /path/to/repo --format text
python3 scripts/validate_entry_routing.py /path/to/repo --format text
python3 scripts/validate_dogfooding_evidence.py /path/to/repo --format text
python3 scripts/validate_markdown_governance.py /path/to/repo --format text
python3 scripts/validate_doc_quality.py /path/to/repo --format text
python3 scripts/validate_control_surface_quality.py /path/to/repo --format text
python3 scripts/validate_development_log.py /path/to/repo --format text
python3 scripts/validate_architecture_retrofit.py /path/to/repo --format text
python3 scripts/validate_daemon_runtime.py /path/to/repo --format text
python3 scripts/validate_vscode_host_extension.py /path/to/repo --format text
python3 scripts/validate_daemon_host_mvp.py /path/to/repo --format text
python3 scripts/validate_daemon_legacy_rollout.py /path/to/repo --format text
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
