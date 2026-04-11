# Progress Reporting

Use this reference when the user asks:

- project progress
- current state
- where are we now
- what is done / in progress / next
- milestone status
- subproject status

## Source Priority

Build the answer from these sources in order:

1. `.codex/status.md`
2. `.codex/brief.md`
3. `.codex/plan.md`
4. `.codex/module-dashboard.md` and `.codex/modules/*.md` for large projects
5. `.codex/subprojects/*.md` for active or blocked areas
6. roadmap documents
7. tests, evals, audits, and generated reports as evidence

If the top three are missing, say the project lacks a reliable control surface and fall back to the best available docs with that caveat.

If `scripts/progress_snapshot.py` exists, run it first to generate a quick machine-checked control-surface summary.

If the session is visibly long or the user is losing track, suggest:

- `项目助手 压缩上下文`

Use `scripts/context_handoff.py` for that when available.

## Required Output Shape

Use this layout for medium and large projects:

```md
## Summary
- Overall:
- Current phase:
- Active slice:
- Main risk:

## Global View
| Area | Status | Current focus | Exit condition |
| --- | --- | --- | --- |

## Module View
| Module | Status | Already implemented | Remaining steps | Completion signal | Next checkpoint |
| --- | --- | --- | --- | --- | --- |

## Subprojects
| Subproject | Status | Current focus | Next checkpoint |
| --- | --- | --- | --- |

## Module Flow
```mermaid
flowchart TB
```

## Evidence
- Tests:
- Evals / reports:

## Next 3 Actions
1.
2.
3.
```

For small projects, compress this into a short paragraph plus `Next 3 Actions`.

## Mermaid Templates

### Phase Flow

```mermaid
flowchart LR
    A["Phase 1\nCompleted"] --> B["Phase 2\nCompleted"]
    B --> C["Phase 3\nActive"]
    C --> D["Phase 4\nNext"]
```

### Workstream Map

```mermaid
flowchart TB
    P["Project"] --> A["Core\nCompleted"]
    P --> B["Self-learning\nActive"]
    P --> C["Adapters\nActive"]
    P --> D["Policy rollout\nBlocked"]
```

### Milestone Ladder

```mermaid
flowchart LR
    M1["M1\nDone"] --> M2["M2\nDone"] --> M3["M3\nCurrent"] --> M4["M4\nNext"]
```

## Concision Rules

- report only active, blocked, or recently completed workstreams
- for large projects, include the key modules even if they are not active, when that improves orientation
- prefer one meaningful Mermaid diagram over several partial diagrams
- avoid repeating roadmap prose
- convert detailed evidence into one-line conclusions
- if confidence is low because the status docs are stale, say so in one line

## Trust Rules

Prefer this order of trust:

1. current status docs
2. current tests and evals
3. roadmap and durable docs
4. historical reports

Never present an old roadmap statement as current execution truth unless it is confirmed by the status layer or recent evidence.
